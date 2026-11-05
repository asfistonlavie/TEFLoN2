#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
teflon_browser.py - data of the "Genome browser" tab of the TEFLoN2 HTML report

* reads the TE insertion sites (coordinates, family, order, reference TE or de novo)
* computes the frequency of every site (all samples and per population) from the
  "freq" column of the per-sample genotype files
* optionally reads a gene annotation (GFF3 or GTF, plain or .gz) and classifies the
  position of every TE relative to the genes

Impact classes (positional annotation, NOT a functional prediction: the reading
frame, the TE orientation and the splice sites are not evaluated):

  CDS                  the site overlaps a coding sequence (CDS) of a gene
  UTR / non-coding exon  overlaps an exon but no CDS
  intron               inside the gene body, outside the exons
  upstream             within --flank bp before the gene (strand-aware)
  downstream           within --flank bp after the gene (strand-aware)
  intergenic           none of the above

When a site is related to several genes, the most severe class (first in the list
above) wins; ties are broken by distance. Reference TEs span an interval and are
classified with the whole interval; de novo insertions are points.
Coordinates of the genotype files and of the annotation are both assumed 1-based.
"""
import bisect
import gzip
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from teflon_export import NO_REF, parse_line, make_site  # noqa: E402

try:
    import numpy as np
except ImportError:
    np = None

IMPACTS = ["CDS", "UTR / non-coding exon", "intron", "upstream", "downstream", "intergenic"]
NODATA = 255

GENE_TYPES = {"gene", "ncrna_gene", "pseudogene", "transposable_element_gene", "protein_coding_gene"}


# ----------------------------------------------------------------------------
# annotation
# ----------------------------------------------------------------------------
def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def _attrs(text):
    text = text.strip()
    if '"' in text or (" " in text and "=" not in text):          # GTF
        return dict((k, v) for k, v in re.findall(r'(\w+)\s+"([^"]*)"', text))
    out = {}                                                      # GFF3
    for part in text.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def _merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def parse_annotation(path):
    """-> list of genes (dicts: chrom, start, end, strand, id, name, exons, cds), unsorted."""
    genes = OrderedDict()
    tx2gene = {}
    parts = []                                    # exon / CDS records resolved at the end
    with _open(path) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            x = line.rstrip("\n").split("\t")
            if len(x) < 9:
                continue
            try:
                s, e = int(x[3]), int(x[4])
            except ValueError:
                continue
            chrom, ftype, strand, a = x[0], x[2], x[6], _attrs(x[8])
            low = ftype.lower()
            if low in GENE_TYPES:
                gid = a.get("ID") or a.get("gene_id")
                if not gid:
                    continue
                gid = gid.replace("gene:", "", 1) if gid.startswith("gene:") else gid
                genes[gid] = {"chrom": chrom, "start": s, "end": e, "strand": strand, "id": gid,
                              "name": a.get("Name") or a.get("gene_name") or a.get("gene") or gid,
                              "exons": [], "cds": []}
            elif low in ("exon", "cds"):
                if "gene_id" in a:                                        # GTF
                    gid = a["gene_id"]
                else:                                                     # GFF3
                    gid = (a.get("Parent") or "").split(",")[0]
                    gid = tx2gene.get(gid, gid)
                parts.append((low, gid, chrom, s, e, strand, a))
            elif low.endswith("rna") or low.endswith("transcript"):
                tid = a.get("ID") or a.get("transcript_id")
                par = (a.get("Parent") or a.get("gene_id") or "").split(",")[0]
                if tid and par:
                    tx2gene[tid] = par
    for low, gid, chrom, s, e, strand, a in parts:
        gid = tx2gene.get(gid, gid)
        gid = gid.replace("gene:", "", 1) if gid.startswith("gene:") else gid
        g = genes.get(gid)
        if g is None:                                      # no gene record: build it from its exons
            g = genes[gid] = {"chrom": chrom, "start": s, "end": e, "strand": strand, "id": gid,
                              "name": a.get("gene_name") or gid, "exons": [], "cds": []}
        g["start"], g["end"] = min(g["start"], s), max(g["end"], e)
        (g["cds"] if low == "cds" else g["exons"]).append([s, e])
    out = []
    for g in genes.values():
        g["cds"] = _merge(g["cds"])
        g["exons"] = _merge(g["exons"] + g["cds"]) or [[g["start"], g["end"]]]
        out.append(g)
    return out


def read_fai(path):
    out = OrderedDict()
    with open(path) as fh:
        for line in fh:
            x = line.split("\t")
            if len(x) >= 2:
                out[x[0]] = int(x[1])
    return out


def _norm(name):
    return re.sub(r"^chr", "", name, flags=re.I).lower()


def map_chroms(names, known):
    """{annotation name -> report name}, matching exactly or ignoring a 'chr' prefix."""
    exact = {n: n for n in known}
    loose = {_norm(n): n for n in known}
    return {n: exact.get(n) or loose.get(_norm(n)) for n in names}


# ----------------------------------------------------------------------------
# impact of the TEs on genes
# ----------------------------------------------------------------------------
class GeneIndex:
    def __init__(self, genes):
        self.genes = genes                                  # sorted by (chrom, start)
        self.by_chrom = {}
        for i, g in enumerate(genes):
            self.by_chrom.setdefault(g["chrom"], []).append(i)
        self.starts, self.maxlen = {}, {}
        for c, idx in self.by_chrom.items():
            self.starts[c] = [genes[i]["start"] for i in idx]
            self.maxlen[c] = max(genes[i]["end"] - genes[i]["start"] + 1 for i in idx)

    @staticmethod
    def _hit(intervals, s, e):
        return any(a <= e and b >= s for a, b in intervals)

    def classify(self, chrom, s, e, flank):
        """-> (impact index, gene index or -1)"""
        idx = self.by_chrom.get(chrom)
        if not idx:
            return 5, -1
        starts = self.starts[chrom]
        lo = bisect.bisect_left(starts, s - flank - self.maxlen[chrom])
        hi = bisect.bisect_right(starts, e + flank)
        best = (5, 10 ** 12, -1)
        for j in range(lo, hi):
            gi = idx[j]
            g = self.genes[gi]
            if g["end"] < s - flank or g["start"] > e + flank:
                continue
            if g["start"] <= e and g["end"] >= s:
                if self._hit(g["cds"], s, e):
                    imp = 0
                elif self._hit(g["exons"], s, e):
                    imp = 1
                else:
                    imp = 2
                dist = 0
            else:
                before = e < g["start"]
                dist = (g["start"] - e) if before else (s - g["end"])
                up = before if g["strand"] != "-" else not before
                imp = 3 if up else 4
            if (imp, dist) < best[:2]:
                best = (imp, dist, gi)
        return best[0], best[2]


# ----------------------------------------------------------------------------
# sites and frequencies
# ----------------------------------------------------------------------------
def read_site_table(path):
    """TE sites of a genotype file, in file order."""
    out = []
    with open(path) as fh:
        for line in fh:
            try:
                pre, _, _, _, _, _, teid = parse_line(line)
            except ValueError:
                out.append(None)
                continue
            out.append(make_site(pre, teid))
    return out


def read_freqs(path, n):
    """uint8 percent (0-100) of the TE-present allele per site; 255 = no data."""
    arr = bytearray([NODATA]) * n
    with open(path) as fh:
        for i, line in enumerate(fh):
            if i >= n:
                break
            f = line.rstrip("\n").rsplit("\t", 3)
            try:
                v = float(f[1])
            except (ValueError, IndexError):
                continue
            if 0 <= v <= 1:
                arr[i] = int(round(v * 100))
    return arr


def mean_freq(rows, cols):
    """Mean over the samples with data, per site -> list of int percent (-1 = no data)."""
    n = len(rows[0]) if rows else 0
    if np is not None:
        M = np.vstack([np.frombuffer(r, dtype=np.uint8) for r in rows])[cols].astype(np.float64)
        ok = M != NODATA
        cnt = ok.sum(axis=0)
        tot = np.where(ok, M, 0).sum(axis=0)
        res = np.where(cnt > 0, np.rint(tot / np.maximum(cnt, 1)), -1)
        return [int(v) for v in res]
    res = []
    for k in range(n):
        vals = [rows[c][k] for c in cols if rows[c][k] != NODATA]
        res.append(int(round(sum(vals) / len(vals))) if vals else -1)
    return res


def build(files, sample_ids, members, groups, calls, sites_full, annotation=None, fai=None, flank=2000,
          max_call_cells=3000000, log=print):
    """Return the JSON-serialisable dict used by the browser tab (or None if nothing to show)."""
    n = len(sites_full)
    ok = [k for k in range(n) if sites_full[k] is not None]
    if not ok:
        return None
    freq_rows = [read_freqs(f, n) for f in files]

    # chromosomes ----------------------------------------------------------
    present = OrderedDict()
    for k in ok:
        present.setdefault(sites_full[k].chrom, 0)
    lengths = dict(fai) if fai else {}
    if lengths:
        chroms = [c for c in lengths if c in present] + [c for c in present if c not in lengths]
    else:
        chroms = sorted(present, key=lambda c: (_norm(c).isdigit() is False, int(_norm(c)) if _norm(c).isdigit() else 0, c))

    # annotation (only the sequences that carry TE sites are shown) ----------
    cidx = {c: i for i, c in enumerate(chroms)}
    genes, notes = [], []
    if annotation:
        raw = parse_annotation(annotation)
        mp = map_chroms({g["chrom"] for g in raw}, chroms)
        kept = []
        for g in raw:
            m = mp.get(g["chrom"])
            if m:
                g["chrom"] = m
                kept.append(g)
        if not kept:
            notes.append("no sequence of the annotation matches a sequence carrying TE sites: genes are not shown.")
        else:
            genes = sorted(kept, key=lambda g: (cidx[g["chrom"]], g["start"], g["end"]))
            log("annotation: %d genes on %d sequences read from %s" % (len(genes), len({g["chrom"] for g in genes}), os.path.basename(annotation)))
    for g in genes:
        lengths[g["chrom"]] = max(lengths.get(g["chrom"], 0), g["end"])
    gindex = GeneIndex(genes) if genes else None

    # site order: by chromosome then position -------------------------------
    ok.sort(key=lambda k: (cidx[sites_full[k].chrom], sites_full[k].pos, sites_full[k].end))
    fams = sorted({sites_full[k].fam for k in ok})
    orders = sorted({sites_full[k].order for k in ok})
    fam_i, ord_i = {f: i for i, f in enumerate(fams)}, {o: i for i, o in enumerate(orders)}
    all_cols = list(range(len(files)))
    q_all = mean_freq(freq_rows, all_cols)
    pop_names = list(groups.keys())
    q_pop = []
    for p in pop_names:
        cols = [sample_ids.index(s) for s in groups[p]]
        q_pop.append(mean_freq(freq_rows, cols))

    out = {"chroms": [], "orders": orders, "fams": fams, "impacts": IMPACTS, "pops": pop_names,
           "c": [], "s": [], "e": [], "f": [], "o": [], "r": [], "q": [], "i": [], "g": [], "id": [], "rid": [],
           "pf": [[] for _ in pop_names], "notes": notes, "flank": flank, "has_genes": bool(genes)}
    for k in ok:
        s = sites_full[k]
        out["c"].append(cidx[s.chrom]); out["s"].append(s.pos); out["e"].append(s.end)
        out["f"].append(fam_i[s.fam]); out["o"].append(ord_i[s.order])
        out["r"].append(1 if s.refid not in NO_REF else 0)
        out["q"].append(q_all[k]); out["id"].append(s.teid); out["rid"].append("" if s.refid in NO_REF else s.refid)
        for j in range(len(pop_names)):
            out["pf"][j].append(q_pop[j][k])
        if gindex:
            imp, gi = gindex.classify(s.chrom, s.pos, s.end, flank)
        else:
            imp, gi = 5, -1
        out["i"].append(imp); out["g"].append(gi)
    maxend = {}
    for k in ok:
        maxend[sites_full[k].chrom] = max(maxend.get(sites_full[k].chrom, 0), sites_full[k].end)
    for c in chroms:
        ln = lengths.get(c) or int(maxend.get(c, 1000) * 1.02) + 1
        out["chroms"].append({"name": c, "length": max(ln, maxend.get(c, 0))})
    if not fai:
        notes.append("no reference index (.fai): chromosome lengths are estimated from the data.")

    if genes:
        out["genes"] = {"c": [cidx.get(g["chrom"], 0) for g in genes], "s": [g["start"] for g in genes],
                        "e": [g["end"] for g in genes], "st": [g["strand"] for g in genes],
                        "id": [g["id"] for g in genes], "nm": [g["name"] for g in genes],
                        "ex": [[v for iv in g["exons"] for v in iv] for g in genes],
                        "cds": [[v for iv in g["cds"] for v in iv] for g in genes]}
    # per-sample calls (one char per sample), only when small enough
    if calls is not None and len(ok) * len(sample_ids) <= max_call_cells:
        out["samples"] = list(sample_ids)
        out["sample_pop"] = [members.get(s, "") for s in sample_ids]
        out["calls"] = ["".join(str(calls[j][k]) for j in range(len(sample_ids))) for k in ok]
    elif calls is not None:
        notes.append("per-sample calls are not embedded (more than %d site x sample values)." % max_call_cells)
    return out
