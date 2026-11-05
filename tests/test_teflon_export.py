#!/usr/bin/env python3
"""
Tests for TEFLoN/teflon_export.py

Fixtures are produced with the real TEFLoN2 writers (pseudo2refConvert,
pop_frequency, pop_frequency2) so the exporter is checked against the actual
format of the *.genotypes.txt files. Run:  python3 tests/test_teflon_export.py
"""
import os
import random
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEFLON = os.path.join(ROOT, "TEFLoN")
sys.path.insert(0, TEFLON)
from teflon_scripts import genotyper_poolType as pt          # noqa: E402
from teflon_scripts import pseudo2refConvert as p2rC          # noqa: E402
from teflon_scripts import pop_frequency as pf                # noqa: E402
from teflon_scripts import pop_frequency2 as pf2              # noqa: E402

EXPORT = os.path.join(TEFLON, "teflon_export.py")


def write_fasta(path, seqs):
    rnd = random.Random(1)
    with open(path, "w") as f:
        for name, n in seqs.items():
            s = "".join(rnd.choice("ACGT") for _ in range(n))
            f.write(">%s description\n" % name)
            for i in range(0, n, 60):
                f.write(s[i:i + 60] + "\n")


def run_export(wd, samples, fasta, *extra):
    cmd = [sys.executable, EXPORT, "-wd", wd, "-s", samples, "-f", fasta] + list(extra)
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout
    return r.stdout


def parse_gfa(path):
    S, L, P = {}, set(), {}
    for line in open(path):
        f = line.rstrip("\n").split("\t")
        if f[0] == "S":
            S[f[1]] = f[2:]
        elif f[0] == "L":
            L.add((f[1], f[2], f[3], f[4]))
        elif f[0] == "P":
            P[f[1]] = f[2].split(",")
    return S, L, P


def check_gfa_consistency(path):
    S, L, P = parse_gfa(path)
    for a, oa, b, ob in L:
        assert a in S and b in S, "link to unknown segment %s %s" % (a, b)
    for name, steps in P.items():
        for st in steps:
            assert st[:-1] in S, "%s: unknown node %s" % (name, st)
        for x, y in zip(steps, steps[1:]):
            assert (x[:-1], x[-1], y[:-1], y[-1]) in L, "%s: missing edge %s -> %s" % (name, x, y)
    return S, L, P


def test_real_format():
    tmp = tempfile.mkdtemp()
    wd = os.path.join(tmp, "data_output_t")
    sdir = os.path.join(wd, "4-genotypes", "samples")
    pdir = os.path.join(wd, "4-genotypes", "populations")
    os.makedirs(os.path.join(sdir, "pseudoSpace"))
    os.makedirs(pdir)
    fasta = os.path.join(tmp, "ref.fa")
    write_fasta(fasta, {"2R": 5000, "3L": 3000})

    # pseudo -> reference map: a 300 bp TE removed between pseudo 1000 and 1001 on 2R
    pm = {"2R": [i + 1 if i < 1000 else i + 301 for i in range(4000)],
          "3L": [i + 1 for i in range(3000)]}

    # chr start stop fam order strand refID 5'sc 3'sc  (presents, absents, ambiguous) per sample A,B,C
    sites = [
        ("2R", "1000", "1001", "gypsy", "ltr", "+", "FBti1", "+", "+", [(10, 0, 1), (0, 10, 0), (5, 5, 0)]),
        ("2R", "2000", "-", "copia", "ltr", "+", "-", "+", "-", [(8, 0, 0), (0, 9, 0), (0, 0, 3)]),
        ("2R", "-", "2500", "mariner", "tir", "-", "-", "-", "+", [(0, 7, 0), (6, 0, 0), (9, 0, 0)]),
        ("2R", "2010", "2011", "bs", "non-ltr", "+", "-", "+", "+", [(4, 0, 0), (4, 0, 0), (4, 0, 0)]),
        ("3L", "500", "-", "hAT", "tir", "-", "-", "+", "-", [(5, 5, 0), (0, 5, 0), (5, 0, 0)]),
        ("2R", "3000", "3001", "pogo", "tir", "+", "-", "+", "+", [(9, 0, 0), (9, 0, 0), (0, 9, 0)]),
    ]
    names = ["A", "B", "C"]
    for k, name in enumerate(names):
        pseudo = os.path.join(sdir, "pseudoSpace", name + ".pseudoSpace.genotypes.txt")
        with open(pseudo, "w") as f:
            for s in sites:
                p, a, m = s[9][k]
                line = list(s[:9]) + [str(p), str(a), str(m), "0", "0"]
                f.write("\t".join(line) + "\t%s\n" % pt.fq(line))
        p2rC.pseudo2refConvert_portal(pseudo, pm, os.path.join(sdir, name + ".genotypes.txt"),
                                      "diploid", 0.05, 0.95)

    samples = os.path.join(wd, "sample_names.txt")
    with open(samples, "w") as f:
        for n in names:
            f.write("/x/%s.bam\t%s\n" % (n, n))
    popf = os.path.join(tmp, "population.txt")
    with open(popf, "w") as f:
        f.write("A\tpop1\nB\tpop1\nC\tpop2\n")

    pf.all_frequency(samples, sdir, pt, 0.05, 0.95)
    pf2.all_frequency(samples, sdir, 0.05, 0.95)
    for g in ("pop1", "pop2"):
        pf.pop_frequency([n for n, gg in (l.split() for l in open(popf)) if gg == g], g, pdir, sdir, pt, 0.05, 0.95)
    pf.pop_frequency_all(popf, pdir)

    vcf, gfa = os.path.join(tmp, "o", "t.vcf"), os.path.join(tmp, "o", "t.gfa")
    print(run_export(wd, samples, fasta, "-dt", "diploid", "--vcf", vcf, "--gfa", gfa,
                     "--pop-freq", os.path.join(pdir, "all_frequency.population.genotypes.txt")))

    # ---- VCF
    recs = [l.rstrip("\n").split("\t") for l in open(vcf) if not l.startswith("#")]
    assert len(recs) == 6, len(recs)
    keys = [({"2R": 0, "3L": 1}[r[0]], int(r[1])) for r in recs]
    assert keys == sorted(keys), "VCF is not sorted"
    byid = {r[2]: r for r in recs}
    gt = lambda r: [x.split(":")[0] for x in r[9:]]
    r1 = byid["te01"]
    assert r1[4] == "<DEL:ME:gypsy>" and "SVLEN=-301" in r1[7] and "REFTE" in r1[7], r1[:8]
    assert gt(r1) == ["0/0", "1/1", "0/1"], gt(r1)           # present, absent, het (TE allele = REF here)
    assert "TEAF=0.5" in r1[7], r1[7]
    r2 = byid["te02"]
    assert r2[4] == "<INS:ME:copia>" and gt(r2) == ["1/1", "0/0", "./."], gt(r2)
    assert "TEAF_pop1=" in r2[7], r2[7]
    assert all(len(r[3]) == 1 and r[3] in "ACGT" for r in recs)

    import pysam  # strict VCF parsing (hard requirement of the test-suite)
    vf = pysam.VariantFile(vcf)
    assert len(list(vf)) == 6
    print("pysam parsed the VCF without error")

    # ---- GFA
    S, L, P = check_gfa_consistency(gfa)
    assert set(P) >= {"REF_2R", "REF_3L", "A_2R", "B_2R", "C_2R", "A_3L"}, sorted(P)
    assert "te02+" in P["A_2R"] and "te02+" not in P["B_2R"]     # de novo present only in A
    assert not any(st.startswith("te") for st in P["REF_2R"])
    # B lacks the reference TE te01 -> its path skips the interior segments, A keeps them
    assert len(P["B_2R"]) < len(P["A_2R"]) + 1, (len(P["B_2R"]), len(P["A_2R"]))
    print("real-format test OK")

    # GFA only / reference-only paths
    gfa2 = os.path.join(tmp, "o", "only.gfa")
    run_export(wd, samples, fasta, "-dt", "diploid", "--gfa", gfa2, "--gfa-paths", "reference")
    S2, L2, P2 = check_gfa_consistency(gfa2)
    assert set(P2) == {"REF_2R", "REF_3L"}
    assert not os.path.exists(gfa2 + ".tmp.vcf")
    print("GFA-only / reference-only OK")


def test_fuzz_paths():
    """Random sites (including adjacent / nested ones): every sample path must follow existing edges."""
    rnd = random.Random(7)
    for trial in range(30):
        tmp = tempfile.mkdtemp()
        wd = os.path.join(tmp, "wd")
        sdir = os.path.join(wd, "4-genotypes", "samples")
        os.makedirs(sdir)
        fasta = os.path.join(tmp, "ref.fa")
        write_fasta(fasta, {"c1": 400, "c2": 250})
        n_s, n_sites = 4, 40
        spec = []
        for i in range(n_sites):
            chrom = rnd.choice(["c1", "c2"])
            a = rnd.randint(1, 240)
            if rnd.random() < 0.5:
                spec.append((chrom, a, a + rnd.randint(1, 60), "R%d" % i))   # reference TE
            else:
                spec.append((chrom, a, a, "-"))                            # de novo
        names = ["s%d" % k for k in range(n_s)]
        for name in names:
            with open(os.path.join(sdir, name + ".genotypes.txt"), "w") as f:
                for i, (chrom, a, b, ref) in enumerate(spec):
                    st = rnd.choice(["present", "absent", "polymorphic", "no_data"])
                    freq = {"present": "1.0", "absent": "0.0", "polymorphic": "0.5", "no_data": "-9"}[st]
                    start, stop = (str(a), str(b)) if b > a else (str(a), "-")
                    f.write("\t".join([chrom, start, stop, "fam", "ord", "+", ref, "+", "+",
                                       "1", "1", "0", freq, st, "te%02d" % (i + 1)]) + "\n")
        samples = os.path.join(wd, "sample_names.txt")
        with open(samples, "w") as f:
            for n in names:
                f.write("x\t%s\n" % n)
        gfa = os.path.join(tmp, "o.gfa")
        run_export(wd, samples, fasta, "-dt", "haploid", "--vcf", os.path.join(tmp, "o.vcf"), "--gfa", gfa)
        check_gfa_consistency(gfa)
    print("fuzz test OK (30 random graphs, all sample paths follow existing edges)")


if __name__ == "__main__":
    test_real_format()
    test_fuzz_paths()
    print("ALL TESTS PASSED")
