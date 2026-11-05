#!/usr/bin/env python3
"""Build a synthetic TEFLoN2 run (12 samples, 3 populations) and generate the HTML report.

Usage: python3 tests/test_teflon_report.py [output_dir]
The synthetic run (data_output_demo/, population.txt) and report.html are left in output_dir.
"""
import json, os, random, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "TEFLoN"))
from teflon_scripts import genotyper_poolType as pt
from teflon_scripts import pop_frequency as pf
from teflon_scripts import pop_frequency2 as pf2


def build(tmp, n_sites=3000):
    rnd = random.Random(3)
    wd = os.path.join(tmp, "data_output_demo")
    sdir = os.path.join(wd, "4-genotypes", "samples"); pdir = os.path.join(wd, "4-genotypes", "populations"); mdir = os.path.join(wd, "1-mapping")
    for d in (sdir, pdir, mdir): os.makedirs(d)
    pops = {"coluzzii_BF": 5, "gambiae_BF": 4, "gambiae_GA": 3}
    members = [(p, "%s_%d" % (p, i)) for p, n in pops.items() for i in range(n)]
    orders = ["tir", "ltr", "line", "sine", "mites"]
    sites = []
    for k in range(n_sites):
        ref = rnd.random() < 0.4
        sites.append(("2R" if k % 2 else "3L", "fam%d" % rnd.randint(1, 15), rnd.choice(orders),
                      "FBti%d" % k if ref else "-", k * 100 + 10, k * 100 + (350 if ref else 11)))
    # allele frequencies: population specific so that private / shared insertions exist
    base = {p: {k: rnd.random() for k in range(n_sites)} for p in pops}
    for pop, sid in members:
        cov = rnd.uniform(3, 60)
        with open(os.path.join(sdir, sid + ".genotypes.txt"), "w") as f:
            for k, (chrom, fam, order, refid, a, b) in enumerate(sites):
                fr = base[pop][k] ** 3 if (k % 3) else base[pop][k]
                present = rnd.random() < fr
                p_reads, a_reads = (rnd.randint(2, 12), 0) if present else (0, rnd.randint(1, 12))
                if rnd.random() < 0.03: p_reads, a_reads = 0, 0
                line = [chrom, str(a), str(b), fam, order, "+", refid, "+", "-", str(p_reads), str(a_reads), "1", "0", "0"]
                fq = pt.fq(line)
                if fq == -9: interp = "no data"
                elif fq > 0.95: interp = "present"
                elif fq < 0.05: interp = "absent"
                else: interp = "polymorphic"
                f.write("\t".join(line[:9] + [str(p_reads), str(a_reads), "1", str(fq), interp, "te%d" % k]) + "\n")
        n = int(5e7 * cov / 150)
        mapped = n * rnd.uniform(0.7, 0.99)
        open(os.path.join(mdir, sid + ".sorted.stats.txt"), "w").write(
            "# samtools stats\nSN\traw total sequences:\t%d\nSN\treads mapped:\t%d\nSN\treads properly paired:\t%d\n"
            "SN\treads duplicated:\t%d\nSN\treads MQ0:\t%d\nSN\terror rate:\t%.4f\nSN\taverage length:\t150\n"
            "SN\tinsert size average:\t%.1f\nSN\tinsert size standard deviation:\t%.1f\n"
            % (n, mapped, mapped * rnd.uniform(0.7, 0.98), n * rnd.uniform(0.01, 0.4), n * 0.02, rnd.uniform(0.005, 0.02), rnd.uniform(300, 420), rnd.uniform(30, 90)))
        open(os.path.join(mdir, sid + ".sorted.cov.txt"), "w").write("Average =  %.4f\nStdev =  %.4f\n" % (cov, cov / 3))
        open(os.path.join(mdir, sid + ".sorted.subsmpl.cov.txt"), "w").write("Average =  %.4f\nStdev =  1\n" % (3 * 0.9))
    samples = os.path.join(wd, "sample_names.txt")
    open(samples, "w").write("".join("/x/%s.bam\t%s\n" % (s, s) for _, s in members))
    popf = os.path.join(tmp, "population.txt")
    open(popf, "w").write("".join("%s\t%s\n" % (s, p) for p, s in members))
    pf.all_frequency(samples, sdir, pt, 0.05, 0.95); pf2.all_frequency(samples, sdir, 0.05, 0.95)
    for g in pops:
        mem = [s for p, s in members if p == g]
        pf.pop_frequency(mem, g, pdir, sdir, pt, 0.05, 0.95)
        pf2.pop_frequency(mem, g, pdir, sdir, 0.05, 0.95)
    pf.pop_frequency_all(popf, pdir); pf2.pop_frequency_all(popf, pdir)
    # a reference genome long enough for the synthetic coordinates (used by the export test)
    rg = random.Random(9)
    with open(os.path.join(tmp, "genome.fa"), "w") as f:
        for c in ("2R", "3L"):
            s = "".join(rg.choice("ACGT") for _ in range(n_sites * 100 + 1000))
            f.write(">%s\n" % c)
            for i in range(0, len(s), 70): f.write(s[i:i + 70] + "\n")
    # a gene annotation (GFF3 and the same genes as GTF) covering the synthetic coordinates
    ar = random.Random(5)
    gff, gtf = ["##gff-version 3"], []
    for c in ("2R", "3L"):
        for gi in range(n_sites * 100 // 2500):
            s = gi * 2500 + 150; e = s + ar.randint(600, 1800); st = ar.choice("+-"); gid = "AGAP%s%04d" % (c, gi)
            gff.append("%s\tsrc\tgene\t%d\t%d\t.\t%s\t.\tID=%s;Name=%s" % (c, s, e, st, gid, "gene" + str(gi) if gi % 3 else gid))
            gff.append("%s\tsrc\tmRNA\t%d\t%d\t.\t%s\t.\tID=%s-RA;Parent=%s" % (c, s, e, st, gid, gid))
            mid = (s + e) // 2
            ex = [(s, s + 150), (mid - 100, mid + 100), (e - 200, e)]
            for a, b in ex:
                gff.append("%s\tsrc\texon\t%d\t%d\t.\t%s\t.\tID=%s-ex%d;Parent=%s-RA" % (c, a, b, st, gid, a, gid))
                gtf.append('%s\tsrc\texon\t%d\t%d\t.\t%s\t.\tgene_id "%s"; transcript_id "%s-RA";' % (c, a, b, st, gid, gid))
            for a, b in ex[1:]:
                gff.append("%s\tsrc\tCDS\t%d\t%d\t.\t%s\t0\tID=%s-cds%d;Parent=%s-RA" % (c, a + 10, b - 10, st, gid, a, gid))
                gtf.append('%s\tsrc\tCDS\t%d\t%d\t.\t%s\t0\tgene_id "%s"; transcript_id "%s-RA";' % (c, a + 10, b - 10, st, gid, gid))
    open(os.path.join(tmp, "annotation.gff3"), "w").write("\n".join(gff) + "\n")
    open(os.path.join(tmp, "annotation.gtf"), "w").write("\n".join(gtf) + "\n")
    return wd, popf


if __name__ == "__main__":
    tmp = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()
    os.makedirs(tmp, exist_ok=True)
    wd, popf = build(tmp)
    out = os.path.join(tmp, "report.html")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "TEFLoN", "teflon_report.py"), "-wd", wd, "-pop", popf, "-o", out,
                        "-f", os.path.join(tmp, "genome.fa"), "--annotation", os.path.join(tmp, "annotation.gff3")],
                       capture_output=True, text=True)
    print(r.stdout, r.stderr[-1500:])
    assert r.returncode == 0
    html = open(out).read()
    data = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1).replace("<\\/", "</"))
    assert data["n_samples"] == 12 and data["n_sites"] == 3000
    assert len(data["pops"]["names"]) == 3 and data["pca"] and data["pops"]["methods"]
    assert sum(1 for q in data["qc"] if q["flags"]) >= 1
    b = data["browser"]
    n = len(b["s"])
    assert n == 3000 and b["has_genes"] and len(b["genes"]["s"]) > 100 and [c["name"] for c in b["chroms"]] == ["2R", "3L"]
    assert b["chroms"][0]["length"] == 3000 * 100 + 1000          # from the .fai of genome.fa
    assert all(b["c"][i] <= b["c"][i + 1] for i in range(n - 1)) and all(b["s"][i] <= b["s"][i + 1] for i in range(n - 1) if b["c"][i] == b["c"][i + 1])
    assert len(b["calls"]) == n and len(b["calls"][0]) == 12 and len(b["pf"]) == 3 and max(b["q"]) <= 100
    from collections import Counter
    imp = Counter(b["impacts"][i] for i in b["i"])
    assert len(imp) >= 5, imp                                         # CDS, exon, intron, up/downstream, intergenic all occur
    # independent check of the positional classification with brute force on 300 sites
    G = b["genes"]
    def brute(k):
        c, s, e = b["c"][k], b["s"][k], b["e"][k]; best = (5, 10**9)
        for g in range(len(G["s"])):
            if G["c"][g] != c: continue
            gs, ge = G["s"][g], G["e"][g]
            if gs <= e and ge >= s:
                cds = any(G["cds"][g][i] <= e and G["cds"][g][i + 1] >= s for i in range(0, len(G["cds"][g]), 2))
                exn = any(G["ex"][g][i] <= e and G["ex"][g][i + 1] >= s for i in range(0, len(G["ex"][g]), 2))
                cand = (0 if cds else 1 if exn else 2, 0)
            elif e < gs - 2000 or s > ge + 2000: continue
            else:
                before = e < gs; d = gs - e if before else s - ge
                cand = (3 if (before == (G["st"][g] != "-")) else 4, d)
            best = min(best, cand)
        return best[0]
    assert all(brute(k) == b["i"][k] for k in range(0, n, 10)), "impact mismatch"
    # GTF + gz gives the same genes
    import gzip, shutil
    sys.path.insert(0, os.path.join(ROOT, "TEFLoN"))
    import teflon_browser as tb
    with open(os.path.join(os.path.dirname(popf), "annotation.gtf"), "rb") as fi, gzip.open(os.path.join(os.path.dirname(popf), "annotation.gtf.gz"), "wb") as fo: shutil.copyfileobj(fi, fo)
    g1 = tb.parse_annotation(os.path.join(os.path.dirname(popf), "annotation.gff3")); g2 = tb.parse_annotation(os.path.join(os.path.dirname(popf), "annotation.gtf.gz"))
    assert len(g1) == len(g2) and all(a["exons"] == c["exons"] and a["cds"] == c["cds"] and (a["start"], a["end"]) == (c["start"], c["end"]) for a, c in zip(g1, g2))
    print("browser:", dict(imp))
    print("flagged samples:", [(q["id"], q["flags"]) for q in data["qc"] if q["flags"]][:3])
    print("pops:", [(s["name"], s["te_present"], s["private"]) for s in data["pops"]["stats"]])
    print("methods:", data["pops"]["methods"])
    print("REPORT:", out)
