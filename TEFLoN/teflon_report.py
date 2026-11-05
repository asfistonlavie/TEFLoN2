#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
teflon_report.py - interactive HTML report of a TEFLoN2 run

Builds ONE self-contained HTML file (no internet access needed, no server) with:
  1. quality of the input data   (samtools stats + coverage of every sample, QC flags)
  2. TE landscape                (reference / de novo insertions, TE order, family, sequence)
  3. per-sample results          (present / polymorphic / absent / no data, TE load vs coverage)
  4. population results          (TEs per population, private / shared TEs, frequency spectra,
                                  comparison of the two frequency methods, PCA of the samples)

Inputs read from the TEFLoN2 working directory (data_output_<PREFIX>):
  sample_names.txt, 1-mapping/<sample>.sorted.stats.txt, 1-mapping/<sample>.sorted.cov.txt,
  4-genotypes/samples/<sample>.genotypes.txt, and, with a population file,
  4-genotypes/populations/all_frequency.population.genotypes{,2}.txt

numpy is needed for the population analyses and the PCA (everything else is pure Python).

Usage:
  python3 teflon_report.py -wd data_output_run1 [-pop population.txt] [-o report.html]
"""
import argparse
import datetime
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from teflon_export import NO_REF  # noqa: E402

try:
    import numpy as np
except ImportError:  # population analyses are skipped
    np = None

CODE = {"absent": 0, "present": 1, "heterozygous": 2, "polymorphic": 2}   # anything else = 3 (no data)


# ----------------------------------------------------------------------------
# input quality
# ----------------------------------------------------------------------------
def parse_stats(path):
    """Fields of the 'SN' summary of samtools stats."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            if line.startswith("SN\t"):
                parts = line.rstrip("\n").split("\t")
                m = re.match(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?", parts[2].strip()) if len(parts) > 2 else None
                if m:
                    out[parts[1].rstrip(":")] = float(m.group(0))
    return out


def parse_cov(path):
    res = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                m = re.match(r"\s*(Average|Stdev)\s*=\s*([-+0-9.eE]+)", line)
                if m:
                    res[m.group(1)] = float(m.group(2))
    return res


def pct(a, b):
    return round(100.0 * a / b, 2) if b else None


def sample_qc(wd, sid, thr):
    st = parse_stats(os.path.join(wd, "1-mapping", sid + ".sorted.stats.txt"))
    cov = parse_cov(os.path.join(wd, "1-mapping", sid + ".sorted.cov.txt"))
    sub = parse_cov(os.path.join(wd, "1-mapping", sid + ".sorted.subsmpl.cov.txt"))
    raw = st.get("raw total sequences", 0)
    rec = {"id": sid,
           "raw_reads": int(raw) if raw else None,
           "pct_mapped": pct(st.get("reads mapped", 0), raw),
           "pct_properly_paired": pct(st.get("reads properly paired", 0), raw),
           "pct_duplicated": pct(st.get("reads duplicated", 0), raw),
           "pct_mq0": pct(st.get("reads MQ0", 0), raw),
           "error_rate": st.get("error rate"),
           "read_length": st.get("average length"),
           "insert_mean": st.get("insert size average"),
           "insert_sd": st.get("insert size standard deviation"),
           "cov_mean": cov.get("Average"), "cov_sd": cov.get("Stdev"),
           "cov_subsampled": sub.get("Average")}
    flags = []
    if not st:
        flags.append("no samtools stats")
    if rec["cov_mean"] is not None and rec["cov_mean"] < thr["min_coverage"]:
        flags.append("low coverage")
    if rec["pct_mapped"] is not None and rec["pct_mapped"] < thr["min_mapped"]:
        flags.append("low mapping rate")
    if rec["pct_properly_paired"] is not None and rec["pct_properly_paired"] < thr["min_pp"]:
        flags.append("low properly-paired rate")
    if rec["pct_duplicated"] is not None and rec["pct_duplicated"] > 30:
        flags.append("high duplication")
    rec["flags"] = flags
    return rec


# ----------------------------------------------------------------------------
# genotypes
# ----------------------------------------------------------------------------
def read_sites(path):
    sites = []
    with open(path) as f:
        for line in f:
            x = line.rstrip("\n").split("\t")
            if len(x) < 15:
                continue
            sites.append((x[0], x[3], x[4], x[6] not in NO_REF, x[-1]))   # chrom, family, order, is_ref, teID
    return sites


def read_calls(path, n):
    """One byte per site: 0 absent, 1 present, 2 het/polymorphic, 3 no data."""
    arr = bytearray([3]) * n
    with open(path) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            arr[i] = CODE.get(line.rsplit("\t", 2)[-2], 3)
    return arr


def top(counter_ref, counter_dn, n):
    names = sorted(set(counter_ref) | set(counter_dn), key=lambda k: -(counter_ref[k] + counter_dn[k]))[:n]
    return [{"name": k, "ref": counter_ref[k], "denovo": counter_dn[k]} for k in names]


def catalog_summary(sites):
    by_order_r, by_order_d, by_fam_r, by_fam_d, by_chr_r, by_chr_d = (Counter() for _ in range(6))
    for chrom, fam, order, is_ref, _ in sites:
        (by_order_r if is_ref else by_order_d)[order] += 1
        (by_fam_r if is_ref else by_fam_d)[fam] += 1
        (by_chr_r if is_ref else by_chr_d)[chrom] += 1
    n_ref = sum(1 for s in sites if s[3])
    return {"total": len(sites), "ref": n_ref, "denovo": len(sites) - n_ref,
            "by_order": top(by_order_r, by_order_d, 12), "by_family": top(by_fam_r, by_fam_d, 20),
            "by_chrom": top(by_chr_r, by_chr_d, 30)}


def sample_summary(sid, calls, sites, order_names):
    present = Counter()
    by_order = Counter()
    ref_p = dn_p = 0
    for code, s in zip(calls, sites):
        if code == 1:                       # fully present only, for the TE load numbers
            if s[3]:
                ref_p += 1
            else:
                dn_p += 1
            by_order[s[2]] += 1
        present[code] += 1
    return {"id": sid, "present": present[1], "poly": present[2], "absent": present[0], "nodata": present[3],
            "present_ref": ref_p, "present_denovo": dn_p,
            "by_order": [by_order[o] for o in order_names]}


# ----------------------------------------------------------------------------
# populations (numpy)
# ----------------------------------------------------------------------------
def read_population(path, samples):
    groups = OrderedDict()
    members = {}
    with open(path) as f:
        for line in f:
            x = line.rstrip("\n").split("\t")
            if len(x) >= 2 and x[0] in samples:
                members[x[0]] = x[1]
                groups.setdefault(x[1], []).append(x[0])
    return groups, members


def read_pop_freq(path):
    """{population: float array} from all_frequency.population.genotypes*.txt (-9 -> nan)."""
    with open(path) as f:
        header = f.readline().rstrip("\n").split("\t")
        pops = [h.replace("_popFrequency", "") for h in header[10:]]
        cols = [[] for _ in pops]
        ids = []
        for line in f:
            x = line.rstrip("\n").split("\t")
            ids.append(x[9])
            for j in range(len(pops)):
                try:
                    v = float(x[10 + j])
                except (ValueError, IndexError):
                    v = float("nan")
                cols[j].append(float("nan") if v == -9 else v)
    return ids, {p: np.array(c) for p, c in zip(pops, cols)}


def population_analysis(wd, M, sample_ids, groups, sites, order_names):
    sid_idx = {s: i for i, s in enumerate(sample_ids)}
    order_idx = np.array([order_names.index(s[2]) if s[2] in order_names else len(order_names) for s in sites])
    is_ref = np.array([s[3] for s in sites], dtype=bool)
    pops = list(groups)
    present, freq = {}, {}
    for p in pops:
        sub = M[[sid_idx[s] for s in groups[p]]]
        valid = sub != 3
        n = valid.sum(0)
        w = ((sub == 1).astype(np.float32) + 0.5 * (sub == 2)).sum(0)
        with np.errstate(invalid="ignore", divide="ignore"):
            f = np.where(n > 0, w / np.maximum(n, 1), np.nan)
        freq[p] = f
        present[p] = (f > 0)
    A = np.vstack([present[p] for p in pops])
    n_pops_present = A.sum(0)
    stats = []
    for k, p in enumerate(pops):
        f, pr = freq[p], present[p]
        stats.append({"name": p, "n": len(groups[p]), "te_present": int(pr.sum()),
                      "fixed": int((f == 1).sum()), "private": int((pr & (n_pops_present == 1)).sum()),
                      "ref": int((pr & is_ref).sum()), "denovo": int((pr & ~is_ref).sum()),
                      "by_order": np.bincount(order_idx[pr], minlength=len(order_names) + 1)[:len(order_names)].tolist()})
    shared = (A.astype(np.float32) @ A.T.astype(np.float32)).astype(int).tolist()
    codes = (A.astype(np.int64) * (1 << np.arange(len(pops)))[:, None]).sum(0)
    uniq, cnt = np.unique(codes[codes > 0], return_counts=True)
    upset = [{"pops": [pops[j] for j in range(len(pops)) if (int(u) >> j) & 1], "n": int(c)}
             for u, c in sorted(zip(uniq, cnt), key=lambda t: -t[1])[:15]]

    bins = np.linspace(0, 1, 11)
    source = "computed from the sample calls (present = 1, heterozygous/polymorphic = 0.5)"
    reads_file = os.path.join(wd, "4-genotypes", "populations", "all_frequency.population.genotypes.txt")
    samp_file = os.path.join(wd, "4-genotypes", "populations", "all_frequency.population.genotypes2.txt")
    methods = []
    sfs_src = freq
    if os.path.exists(reads_file):
        _, fr = read_pop_freq(reads_file)
        sfs_src, source = fr, "TEFLoN2 population frequencies, read-based method"
        if os.path.exists(samp_file):
            _, fs = read_pop_freq(samp_file)
            for p in pops:
                if p in fr and p in fs and len(fr[p]) == len(fs[p]):
                    ok = ~np.isnan(fr[p]) & ~np.isnan(fs[p])
                    if ok.sum() > 2 and fr[p][ok].std() > 0 and fs[p][ok].std() > 0:
                        methods.append({"pop": p, "r": round(float(np.corrcoef(fr[p][ok], fs[p][ok])[0, 1]), 4),
                                        "mad": round(float(np.abs(fr[p][ok] - fs[p][ok]).mean()), 4), "n": int(ok.sum())})
    sfs = {}
    for p in pops:
        v = sfs_src.get(p, freq[p])
        v = v[~np.isnan(v) & (v > 0)]
        sfs[p] = np.histogram(v, bins=bins)[0].astype(int).tolist()
    return {"names": pops, "stats": stats, "shared": shared, "upset": upset, "sfs": sfs,
            "sfs_source": source, "methods": methods}


def pca(M, sample_ids, max_sites=20000, seed=1):
    mean = np.where(M != 3, (M == 1) + 0.5 * (M == 2), np.nan).astype(np.float32)
    col = np.nanmean(mean, axis=0)
    poly = np.where((col > 0.02) & (col < 0.98))[0]
    if len(poly) < 10 or M.shape[0] < 3:
        return None
    rnd = np.random.RandomState(seed)
    sel = np.sort(rnd.choice(poly, min(max_sites, len(poly)), replace=False))
    X = mean[:, sel]
    idx = np.where(np.isnan(X))
    X[idx] = col[sel][idx[1]]
    X -= X.mean(0)
    U, S, _ = np.linalg.svd(X, full_matrices=False)
    ev = (S ** 2) / (S ** 2).sum()
    return {"samples": sample_ids, "pc1": (U[:, 0] * S[0]).round(4).tolist(), "pc2": (U[:, 1] * S[1]).round(4).tolist(),
            "ev": ev[:5].round(4).tolist(), "n_sites": int(len(sel))}


# ----------------------------------------------------------------------------
def browser_tab(args, files, sample_ids, members, groups, calls, notes):
    """Data of the genome browser tab (None if it cannot be built)."""
    import teflon_browser as tb
    fai = None
    if args.fasta:
        fai_path = args.fasta + ".fai"
        if os.path.exists(fai_path):
            fai = tb.read_fai(fai_path)
        else:
            try:
                from teflon_export import FastaIndex
                fai = OrderedDict((k, v[0]) for k, v in FastaIndex(args.fasta).idx.items())
            except Exception as exc:                       # genome missing or unreadable
                notes.append("genome browser: reference index not available (%s)." % exc)
    annotation = args.annotation if args.annotation and os.path.exists(args.annotation) else None
    if args.annotation and not annotation:
        notes.append("genome browser: annotation file not found (%s): genes are not shown." % args.annotation)
    try:
        return tb.build(files, sample_ids, members, groups, calls, tb.read_site_table(files[0]),
                        annotation=annotation, fai=fai, flank=args.flank)
    except Exception as exc:                               # never lose the rest of the report
        notes.append("genome browser could not be built: %s" % exc)
        return None


def main():
    ap = argparse.ArgumentParser(description="Interactive HTML report of a TEFLoN2 run")
    ap.add_argument("-wd", required=True, help="TEFLoN2 working directory (data_output_PREFIX)")
    ap.add_argument("-s", dest="samples", help="sample_names.txt (default: <wd>/sample_names.txt)")
    ap.add_argument("-pop", dest="population", default=None, help="population file (sample<TAB>population)")
    ap.add_argument("-o", dest="out", default=None, help="output HTML (default: <wd>/6-report/report.html)")
    ap.add_argument("--title", default=None)
    ap.add_argument("--min-coverage", type=float, default=5)
    ap.add_argument("--min-mapped", type=float, default=80)
    ap.add_argument("--min-properly-paired", type=float, default=80)
    ap.add_argument("-f", "--fasta", default=None, help="reference genome (its .fai gives the chromosome lengths) for the genome browser")
    ap.add_argument("--annotation", default=None, help="gene annotation (GFF3 or GTF, optionally .gz): adds genes and TE impact to the genome browser")
    ap.add_argument("--flank", type=int, default=2000, help="distance (bp) to a gene for an 'upstream'/'downstream' TE (default 2000)")
    ap.add_argument("--no-browser", action="store_true", help="do not build the genome browser tab")
    args = ap.parse_args()
    wd = args.wd.rstrip("/")
    out = args.out or os.path.join(wd, "6-report", "report.html")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    with open(args.samples or os.path.join(wd, "sample_names.txt")) as f:
        sample_ids = [l.split()[1] for l in f if l.strip()]
    thr = {"min_coverage": args.min_coverage, "min_mapped": args.min_mapped, "min_pp": args.min_properly_paired}
    gdir = os.path.join(wd, "4-genotypes", "samples")
    files = [os.path.join(gdir, s + ".genotypes.txt") for s in sample_ids]
    missing = [p for p in files if not os.path.exists(p)]
    if missing:
        sys.exit("ERROR: genotype file missing: %s" % missing[0])

    print("Reading %d samples ..." % len(sample_ids))
    qc = [sample_qc(wd, s, thr) for s in sample_ids]
    sites = read_sites(files[0])
    order_names = [k for k, _ in Counter(s[2] for s in sites).most_common(12)]
    catalog = catalog_summary(sites)
    calls = [read_calls(p, len(sites)) for p in files]
    samples = [sample_summary(s, c, sites, order_names) for s, c in zip(sample_ids, calls)]

    groups, members = (OrderedDict(), {})
    if args.population and os.path.exists(args.population):
        groups, members = read_population(args.population, set(sample_ids))
    for rec in qc + samples:
        rec["pop"] = members.get(rec["id"], "")
    cov = {r["id"]: r["cov_mean"] for r in qc}
    for s in samples:
        s["cov_mean"] = cov.get(s["id"])

    data = {"title": args.title or "TEFLoN2 report - %s" % os.path.basename(wd).replace("data_output_", ""),
            "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "run": os.path.basename(wd),
            "thresholds": thr, "n_samples": len(sample_ids), "n_sites": len(sites), "order_names": order_names,
            "qc": qc, "catalog": catalog, "samples": samples, "pops": None, "pca": None, "notes": []}
    if np is None:
        data["notes"].append("numpy is not installed: population analyses and PCA are not shown.")
    else:
        M = np.vstack([np.frombuffer(c, dtype=np.uint8) for c in calls])
        if groups:
            data["pops"] = population_analysis(wd, M, sample_ids, groups, sites, order_names)
        elif args.population:
            data["notes"].append("none of the samples of the population file matches the run samples.")
        data["pca"] = pca(M, sample_ids)
        if data["pca"]:
            data["pca"]["pop"] = [members.get(s, "") for s in sample_ids]

    if not args.no_browser:
        data["browser"] = browser_tab(args, files, sample_ids, members, groups, calls, data["notes"])

    tpl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_template.html")
    with open(tpl) as f:
        html = f.read()
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    with open(out, "w") as f:
        f.write(html.replace("__TEFLON2_DATA__", payload).replace("__TEFLON2_TITLE__", data["title"]))
    print("Report written: %s" % out)


if __name__ == "__main__":
    main()
