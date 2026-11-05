#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
teflon_export.py - export TEFLoN2 genotypes as VCF and GFA

Reads the per-sample files written by teflon_genotype.py
(4-genotypes/samples/<sample>.genotypes.txt) and writes, in addition to the
historical text outputs:

  * a multi-sample VCF (v4.2), one record per TE insertion site
  * a GFA 1.0 genotyping graph, one reference path per sequence and
    (optionally) one path per sample and sequence

VCF conventions
---------------
* TE absent from the reference (de novo)       -> ALT <INS:ME:FAMILY>, TE allele = 1
* TE annotated in the reference (REFTE flag)   -> ALT <DEL:ME:FAMILY>, TE allele = 0
  (the reference carries the TE, so "absent from the sample" is the ALT allele)
* INFO/TEAF is always the frequency of the *TE-present* allele
  (present = 1, heterozygous/polymorphic = 0.5, absent = 0, no_data ignored).
* FORMAT: GT:AF:PR:AR:AM = genotype, allele frequency of the sample, reads
  supporting presence / absence / ambiguous.
* GT depends on --data-type: haploid -> "0"/"1", diploid -> "0/0","0/1","1/1",
  pooled -> "0"/"1" for fixed calls and "." for polymorphic calls
  (the pooled allele frequency is in FORMAT/AF). no_data is always missing.

GFA conventions
---------------
* Backbone segments (S) = reference intervals between consecutive breakpoints
  (sequence "*", length in LN).
* De novo insertion  -> one TE segment inserted between the two flanking
  backbone segments (optional route, the reference adjacency link is kept).
* Reference TE       -> a bypass link (L) skipping the reference interval of
  the TE; the interval itself stays in the backbone.
* Path REF_<chrom> follows the reference. Path <sample>_<chrom> follows the
  homozygous TE calls of the sample: present de novo TEs are traversed, absent
  reference TEs are bypassed. Heterozygous, polymorphic and no_data calls
  follow the reference allele.
* Known limitation: a de novo TE located exactly on the boundary of an absent
  reference TE, and two directly adjacent absent reference TEs, cannot both be
  represented in a single path (the second one is ignored).

Coordinates of the genotype files are used as is (assumed 1-based positions).
"""
import argparse
import datetime
import itertools
import os
import re
import subprocess
import sys
import tempfile
from collections import OrderedDict, defaultdict
from contextlib import ExitStack

NO_REF = {"-", "NA", ".", ""}


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def sanitize(value):
    """Make a string safe for VCF INFO / ALT fields and GFA tags."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(value)) or "."


def fmt_freq(value):
    """-9 (TEFLoN2 'no data') becomes '.'"""
    try:
        if float(value) == -9:
            return "."
    except ValueError:
        return "."
    return str(value)


class FastaIndex:
    """Minimal random access to a FASTA (builds a .fai like samtools faidx)."""

    def __init__(self, fasta):
        self.path = fasta
        fai = fasta + ".fai"
        if os.path.exists(fai):
            with open(fai) as fin:
                rows = [l.rstrip("\n").split("\t")[:5] for l in fin if l.strip()]
            rows = [(r[0], int(r[1]), int(r[2]), int(r[3]), int(r[4])) for r in rows]
        else:
            rows = self._scan(fasta)
            try:
                with open(fai, "w") as fout:
                    for r in rows:
                        fout.write("\t".join(str(x) for x in r) + "\n")
            except OSError:
                pass  # read-only directory: keep the index in memory
        self.idx = OrderedDict((r[0], r[1:]) for r in rows)
        self.order = {name: i for i, name in enumerate(self.idx)}
        self.fh = open(fasta, "rb")

    @staticmethod
    def _scan(fasta):
        rows, name, length, offset, lw, lb, pos = [], None, 0, 0, 0, 0, 0
        with open(fasta, "rb") as fin:
            for raw in fin:
                if raw.startswith(b">"):
                    if name is not None:
                        rows.append((name, length, offset, lw, lb))
                    name = raw[1:].split()[0].decode()
                    length, offset, lw, lb = 0, pos + len(raw), 0, 0
                else:
                    stripped = raw.rstrip(b"\r\n")
                    if lw == 0 and stripped:
                        lw, lb = len(stripped), len(raw)
                    length += len(stripped)
                pos += len(raw)
        if name is not None:
            rows.append((name, length, offset, lw, lb))
        return rows

    def length(self, chrom):
        return self.idx[chrom][0]

    def base(self, chrom, pos):
        """Reference base at 1-based position, 'N' if out of range."""
        length, offset, lw, lb = self.idx[chrom]
        if pos < 1 or pos > length or lw == 0:
            return "N"
        p = pos - 1
        self.fh.seek(offset + (p // lw) * lb + (p % lw))
        return self.fh.read(1).decode().upper() or "N"


class Site:
    __slots__ = ("chrom", "pos", "end", "svtype", "teid", "fam", "order",
                 "strand", "refid", "teaf", "ns")

    def __init__(self, chrom, pos, end, svtype, teid, fam, order, strand, refid):
        self.chrom, self.pos, self.end, self.svtype, self.teid = chrom, pos, end, svtype, teid
        self.fam, self.order, self.strand, self.refid = fam, order, strand, refid
        self.teaf, self.ns = None, 0


def parse_line(line):
    """Last 6 fields: presents absents ambiguous freq interpretation teID."""
    f = line.rstrip("\n").split("\t")
    if len(f) < 15:
        raise ValueError("unexpected genotype line (%d fields): %s" % (len(f), line[:120]))
    pre = f[:-6]
    presents, absents, ambiguous, freq, interp, teid = f[-6:]
    return pre, int(presents), int(absents), int(ambiguous), freq, interp, teid


def make_site(pre, teid):
    chrom, start, stop = pre[0], pre[1], pre[2]
    fam, order, strand, refid = pre[3], pre[4], pre[5], pre[6]
    nums = [int(x) for x in (start, stop) if x.isdigit()]
    if not nums:
        return None
    pos, end = min(nums), max(nums)
    is_ref = refid not in NO_REF
    svtype = "DEL" if (is_ref and end > pos) else "INS"
    if svtype == "INS":
        end = pos
    return Site(chrom, pos, end, svtype, teid, fam, order, strand, refid)


def genotype(interp, dtype, te, other):
    if dtype == "diploid":
        return {"present": te + "/" + te, "absent": other + "/" + other,
                "heterozygous": "0/1"}.get(interp, "./.")
    return {"present": te, "absent": other}.get(interp, ".")


def load_popfreq(path):
    with open(path) as fin:
        header = fin.readline().rstrip("\n").split("\t")
        pops = [h.replace("_popFrequency", "") for h in header[10:]]
        table = {}
        for line in fin:
            x = line.rstrip("\n").split("\t")
            if len(x) > 10:
                table[x[9]] = x[10:]
    return pops, table


# ----------------------------------------------------------------------------
# VCF
# ----------------------------------------------------------------------------
def vcf_header(args, samples, fai, pops):
    h = ["##fileformat=VCFv4.2",
         "##fileDate=%s" % datetime.date.today().strftime("%Y%m%d"),
         "##source=TEFLoN2 teflon_export.py",
         "##reference=%s" % os.path.abspath(args.fasta),
         "##TEFLoN2_datatype=%s" % args.dataType]
    for name, (length, _, _, _) in fai.idx.items():
        h.append("##contig=<ID=%s,length=%d>" % (name, length))
    h += ['##ALT=<ID=INS:ME,Description="Insertion of a mobile element absent from the reference">',
          '##ALT=<ID=DEL:ME,Description="Mobile element annotated in the reference; ALT = absent from the sample">',
          '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="INS: TE absent from the reference; DEL: TE annotated in the reference">',
          '##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the site">',
          '##INFO=<ID=SVLEN,Number=1,Type=Integer,Description="Length of the reference interval spanned by the TE (negative, DEL only)">',
          '##INFO=<ID=TEID,Number=1,Type=String,Description="TEFLoN2 insertion identifier">',
          '##INFO=<ID=TEFAM,Number=1,Type=String,Description="TE family (hierarchy level 1)">',
          '##INFO=<ID=TEORDER,Number=1,Type=String,Description="TE order/class (hierarchy level 2)">',
          '##INFO=<ID=STRAND,Number=1,Type=String,Description="TE orientation (. if unknown)">',
          '##INFO=<ID=REFTE,Number=0,Type=Flag,Description="Insertion matches a TE annotated in the reference">',
          '##INFO=<ID=REFID,Number=1,Type=String,Description="Identifier of the matching reference TE">',
          '##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of samples with data">',
          '##INFO=<ID=TEAF,Number=1,Type=Float,Description="Frequency of the TE-present allele across samples (present=1, het/polymorphic=0.5, absent=0)">']
    for pop in pops:
        h.append('##INFO=<ID=TEAF_%s,Number=1,Type=Float,Description="Frequency of the TE-present allele in population %s (read-based)">'
                 % (sanitize(pop), pop))
    h += ['##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype (allele 1 = INS TE present, or DEL TE absent)">',
          '##FORMAT=<ID=AF,Number=1,Type=Float,Description="Frequency of TE-present reads in the sample (. if no data)">',
          '##FORMAT=<ID=PR,Number=1,Type=Integer,Description="Reads supporting TE presence">',
          '##FORMAT=<ID=AR,Number=1,Type=Integer,Description="Reads supporting TE absence">',
          '##FORMAT=<ID=AM,Number=1,Type=Integer,Description="Ambiguous reads">',
          "\t".join(["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT"] + samples)]
    return h


def write_vcf(args, samples, files, fai, popfreq):
    pops, poptab = popfreq if popfreq else ([], {})
    outdir = os.path.dirname(os.path.abspath(args.vcf))
    sites, skipped, last_key, is_sorted = [], 0, None, True
    tmp = tempfile.NamedTemporaryFile("w", dir=outdir, suffix=".unsorted", delete=False)
    try:
        with ExitStack() as stack:
            fhs = [stack.enter_context(open(p)) for p in files]
            for lines in itertools.zip_longest(*fhs):
                if None in lines:
                    raise SystemExit("ERROR: sample genotype files do not have the same number of lines")
                parsed = [parse_line(l) for l in lines]
                teid = parsed[0][6]
                if any(p[6] != teid or p[0][:3] != parsed[0][0][:3] for p in parsed):
                    raise SystemExit("ERROR: samples disagree on insertion %s (files must come from the same catalog)" % teid)
                site = make_site(parsed[0][0], teid)
                if site is None or site.chrom not in fai.idx:
                    skipped += 1
                    continue
                te, other = ("1", "0") if site.svtype == "INS" else ("0", "1")
                total, n, cols = 0.0, 0, []
                for _, pr, ab, am, freq, interp, _ in parsed:
                    cols.append("%s:%s:%d:%d:%d" % (genotype(interp, args.dataType, te, other),
                                                    fmt_freq(freq), pr, ab, am))
                    if interp == "present":
                        total, n = total + 1, n + 1
                    elif interp in ("heterozygous", "polymorphic"):
                        total, n = total + 0.5, n + 1
                    elif interp == "absent":
                        n += 1
                site.ns = n
                site.teaf = round(total / n, 4) if n else None
                sites.append(site)

                info = ["SVTYPE=" + site.svtype, "END=%d" % site.end]
                if site.svtype == "DEL":
                    info.append("SVLEN=%d" % -(site.end - site.pos))
                info += ["TEID=" + sanitize(site.teid), "TEFAM=" + sanitize(site.fam),
                         "TEORDER=" + sanitize(site.order), "STRAND=" + sanitize(site.strand)]
                if site.refid not in NO_REF:
                    info += ["REFTE", "REFID=" + sanitize(site.refid)]
                info.append("NS=%d" % n)
                if site.teaf is not None:
                    info.append("TEAF=%s" % site.teaf)
                if teid in poptab:
                    for pop, val in zip(pops, poptab[teid]):
                        if fmt_freq(val) != ".":
                            info.append("TEAF_%s=%s" % (sanitize(pop), val))
                alt = "<%s:ME:%s>" % (site.svtype, sanitize(site.fam))
                rec = "\t".join([site.chrom, str(site.pos), sanitize(teid),
                                 fai.base(site.chrom, site.pos), alt, ".", ".",
                                 ";".join(info), "GT:AF:PR:AR:AM"] + cols)
                key = (fai.order[site.chrom], site.pos)
                if last_key is not None and key < last_key:
                    is_sorted = False
                last_key = key
                tmp.write("%d\t%d\t%s\n" % (key[0], key[1], rec))
        tmp.close()

        src_path = tmp.name
        if not is_sorted:
            sorted_path = tmp.name + ".sorted"
            env = dict(os.environ, LC_ALL="C")
            subprocess.check_call(["sort", "-t", "\t", "-k1,1n", "-k2,2n", "-s",
                                   "-T", outdir, "-o", sorted_path, tmp.name], env=env)
            src_path = sorted_path
        with open(args.vcf, "w") as fout, open(src_path) as fin:
            fout.write("\n".join(vcf_header(args, samples, fai, pops)) + "\n")
            for line in fin:
                fout.write(line.split("\t", 2)[2])
        if src_path != tmp.name:
            os.remove(src_path)
    finally:
        if not tmp.closed:
            tmp.close()
        os.remove(tmp.name)
    print("VCF written: %s (%d sites, %d skipped without usable coordinates)"
          % (args.vcf, len(sites), skipped))
    return sites


# ----------------------------------------------------------------------------
# GFA
# ----------------------------------------------------------------------------
def walk(chrom, nseg, ins_at, dels_at, state):
    """Path of one sample through the chromosome graph (list of 'node+')."""
    out, j, landed = [], 0, False
    while j < nseg:
        if not landed:
            jump = -1
            for b, teid in dels_at.get(j, ()):
                if state.get(teid) == "absent" and b > jump:
                    jump = b
            if jump > j:
                j, landed = jump, True
                continue
            for teid in ins_at.get(j, ()):
                if state.get(teid) == "present":
                    out.append(teid + "+")
        landed = False
        out.append("%s_%d+" % (chrom, j))
        j += 1
    for teid in ins_at.get(nseg, ()):
        if state.get(teid) == "present":
            out.append(teid + "+")
    return out


def write_gfa(args, samples, files, fai, sites):
    by_chrom = defaultdict(list)
    for s in sites:
        by_chrom[s.chrom].append(s)
    graph, skipped_del = OrderedDict(), 0

    with open(args.gfa, "w") as out:
        out.write("H\tVN:Z:1.0\n")
        for chrom in fai.idx:
            length = fai.length(chrom)
            ss = by_chrom.get(chrom, [])
            cuts = {0, length}
            for s in ss:
                cuts.add(min(s.pos, length))
                cuts.add(min(s.end, length))
            cuts = sorted(cuts)
            nseg = len(cuts) - 1
            if nseg < 1:
                continue
            ci = {c: i for i, c in enumerate(cuts)}
            for j in range(nseg):
                out.write("S\t%s_%d\t*\tLN:i:%d\n" % (chrom, j, cuts[j + 1] - cuts[j]))
            for j in range(nseg - 1):
                out.write("L\t%s_%d\t+\t%s_%d\t+\t0M\n" % (chrom, j, chrom, j + 1))

            ins_at, dels_at, linked = defaultdict(list), defaultdict(list), set()
            for s in ss:
                a, b = ci[min(s.pos, length)], ci[min(s.end, length)]
                tags = "TF:Z:%s\tTO:Z:%s" % (sanitize(s.fam), sanitize(s.order))
                if s.svtype == "INS":
                    ins_at[a].append(s.teid)
                    node_tags = tags + ("" if s.teaf is None else "\tAF:f:%s" % s.teaf)
                    out.write("S\t%s\t*\t%s\n" % (s.teid, node_tags))
                    if a > 0:
                        out.write("L\t%s_%d\t+\t%s\t+\t0M\n" % (chrom, a - 1, s.teid))
                    if a < nseg:
                        out.write("L\t%s\t+\t%s_%d\t+\t0M\n" % (s.teid, chrom, a))
                elif a > 0 and b < nseg and b > a:
                    dels_at[a].append((b, s.teid))
                    if (a, b) not in linked:
                        linked.add((a, b))
                        out.write("L\t%s_%d\t+\t%s_%d\t+\t0M\tTE:Z:%s\t%s\n"
                                  % (chrom, a - 1, chrom, b, s.teid, tags))
                else:
                    skipped_del += 1
            for a, ids in ins_at.items():
                for t1, t2 in itertools.combinations(ids, 2):
                    out.write("L\t%s\t+\t%s\t+\t0M\n" % (t1, t2))
            graph[chrom] = (nseg, ins_at, dels_at)
            out.write("P\tREF_%s\t%s\t*\n" % (chrom, ",".join("%s_%d+" % (chrom, j) for j in range(nseg))))

        if args.gfaPaths == "samples":
            for sample, path in zip(samples, files):
                state = {}
                with open(path) as fin:
                    for line in fin:
                        p = parse_line(line)
                        state[p[6]] = p[5]
                for chrom, (nseg, ins_at, dels_at) in graph.items():
                    steps = walk(chrom, nseg, ins_at, dels_at, state)
                    out.write("P\t%s_%s\t%s\t*\n" % (sanitize(sample), chrom, ",".join(steps)))
    msg = "GFA written: %s (%d sequences)" % (args.gfa, len(graph))
    if skipped_del:
        msg += ", %d reference TEs without bypass link (touch a sequence end)" % skipped_del
    print(msg)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Export TEFLoN2 genotypes to VCF and GFA")
    ap.add_argument("-wd", dest="wd", required=True, help="TEFLoN2 working directory (data_output_PREFIX)")
    ap.add_argument("-s", dest="samples", required=True, help="sample_names.txt (path<TAB>id)")
    ap.add_argument("-f", dest="fasta", required=True, help="original reference genome (fasta)")
    ap.add_argument("-dt", dest="dataType", default="pooled", choices=["haploid", "diploid", "pooled"])
    ap.add_argument("--vcf", help="output VCF path")
    ap.add_argument("--gfa", help="output GFA path")
    ap.add_argument("--gfa-paths", dest="gfaPaths", default="samples", choices=["samples", "reference"],
                    help="samples: one path per sample and sequence (large files); reference: reference path only")
    ap.add_argument("--pop-freq", dest="popFreq", default=None,
                    help="all_frequency.population.genotypes.txt, adds INFO/TEAF_<population>")
    args = ap.parse_args()
    if not args.vcf and not args.gfa:
        ap.error("give at least one of --vcf / --gfa")

    with open(args.samples) as fin:
        samples = [l.split()[1] for l in fin if l.strip()]
    files = [os.path.join(args.wd, "4-genotypes", "samples", s + ".genotypes.txt") for s in samples]
    missing = [f for f in files if not os.path.exists(f)]
    if missing:
        sys.exit("ERROR: missing genotype files, e.g. %s" % missing[0])

    fai = FastaIndex(args.fasta)
    popfreq = load_popfreq(args.popFreq) if args.popFreq else None
    for p in (args.vcf, args.gfa):
        if p:
            os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)

    sites = None
    if args.vcf:
        sites = write_vcf(args, samples, files, fai, popfreq)
    if args.gfa:
        if sites is None:  # GFA only: run the VCF pass into a temporary file
            args.vcf = args.gfa + ".tmp.vcf"
            sites = write_vcf(args, samples, files, fai, popfreq)
            os.remove(args.vcf)
            args.vcf = None
        write_gfa(args, samples, files, fai, sites)


if __name__ == "__main__":
    main()
