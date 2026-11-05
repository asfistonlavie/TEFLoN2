#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
teflon2_configure.py - interactive configuration of the TEFLoN2 Snakemake pipeline

Writes config.yaml (comments of the template are preserved, the previous file is
backed up) without editing it by hand.

  python3 teflon2_configure.py              # interactive
  python3 teflon2_configure.py --yes        # accept every detected/default value
  python3 teflon2_configure.py --set PARAMS.GENERAL.PREFIX=run2 --yes

Two situations are detected automatically:
  * FIRST RUN : no config.yaml, or a config.yaml still holding the template
                placeholders, and no previous data_output_* folder
                -> full guided setup (tools, inputs, mode, parameters, population)
  * NEW RUN   : a filled config.yaml and/or previous runs exist
                -> menu: update the existing run (add samples, change settings),
                   start a new run (new prefix), or re-genotype only
                   (new thresholds, keeps mapping/discover/count results)
Only the Python standard library is needed.
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys

PLACEHOLDERS = ("/path/to/", "name_run", "name_reference_file", "name_annotation_file")
STEPS = [("0-reference", "reference preparation"), ("1-mapping", "mapping / discover"),
         ("2-preliminaryResults", "collapse"), ("3-countPos", "count"),
         ("4-genotypes", "genotype"), ("5-export", "VCF/GFA export"), ("6-report", "HTML report")]

EXTRA_BLOCKS = {
    ("PARAMS", "EXPORT"): [
        "  EXPORT:",
        "    USE: 1                            # [optional] 1: also write a VCF and a GFA (5-export/); 0: skip",
        "    GFA_PATHS: \"samples\"              # [optional] \"samples\": one path per sample and sequence (large); \"reference\": reference path only",
        "    COMPRESS: 0                       # [optional] 1: also write .vcf.gz + .tbi (requires bgzip and tabix)"],
    ("PARAMS", "REPORT"): [
        "  REPORT:",
        "    USE: 1                            # [optional] 1: build the HTML quality/results report (6-report/); 0: skip",
        "    MIN_COVERAGE: 5                   # [optional] samples below this mean coverage are flagged",
        "    MIN_MAPPED: 80                    # [optional] samples below this % of mapped reads are flagged",
        "    MIN_PROPERLY_PAIRED: 80           # [optional] samples below this % of properly paired reads are flagged",
        "    GENE_ANNOTATION: \"\"                # [optional] gene annotation (GFF3 or GTF, .gz allowed): adds genes and the impact of the TEs to the genome browser of the report",
        "    GENE_FLANK: 2000                  # [optional] a TE within this distance (bp) of a gene is called upstream / downstream"],
}
# keys added one by one to a block that already exists in an older configuration file
EXTRA_KEYS = {
    ("PARAMS", "REPORT", "GENE_ANNOTATION"): "GENE_ANNOTATION: \"\"                # [optional] gene annotation (GFF3 or GTF, .gz allowed) for the genome browser of the report",
    ("PARAMS", "REPORT", "GENE_FLANK"): "GENE_FLANK: 2000                  # [optional] distance (bp) for an upstream / downstream TE",
}

LINE = re.compile(r"^(\s*)([A-Za-z0-9_]+):(.*)$")


# ----------------------------------------------------------------------------
# comment-preserving YAML editing (the config is a plain nested mapping)
# ----------------------------------------------------------------------------
def split_value(rest):
    rest = rest.strip()
    if rest[:1] in ('"', "'"):
        end = rest.find(rest[0], 1)
        return rest[1:end], rest[end + 1:]
    m = re.match(r"^(.*?)(\s+#.*)?$", rest)
    return m.group(1).strip(), m.group(2) or ""


class Config:
    def __init__(self, lines):
        self.lines = lines

    @classmethod
    def load(cls, path):
        with open(path) as f:
            return cls(f.read().splitlines())

    def _walk(self):
        stack = []
        for i, line in enumerate(self.lines):
            if line.lstrip().startswith("#") or not line.strip():
                continue
            m = LINE.match(line)
            if not m:
                continue
            indent = len(m.group(1))
            while stack and stack[-1][0] >= indent:
                stack.pop()
            path = tuple(k for _, k in stack) + (m.group(2),)
            stack.append((indent, m.group(2)))
            yield i, path, indent, m.group(3)

    def has(self, path):
        return any(p == tuple(path) for _, p, _, _ in self._walk())

    def get(self, path, default=""):
        for _, p, _, rest in self._walk():
            if p == tuple(path):
                return split_value(rest)[0]
        return default

    def set(self, path, value):
        path = tuple(path)
        if not self.has(path) and path[:2] in EXTRA_BLOCKS and not self.has(path[:2]):
            self._append_block(path[:2])
        if not self.has(path) and path in EXTRA_KEYS and self.has(path[:2]):
            last = max(i for i, p, _, _ in self._walk() if p[:2] == path[:2])
            indent = next(ind for i, p, ind, _ in self._walk() if p[:2] == path[:2] and len(p) == 3)
            self.lines.insert(last + 1, " " * indent + EXTRA_KEYS[path])
        for i, p, indent, rest in self._walk():
            if p == path:
                _, tail = split_value(rest)
                text = str(value) if isinstance(value, int) else '"%s"' % value
                self.lines[i] = "%s%s: %s%s" % (" " * indent, path[-1], text, (" " + tail.strip()) if tail.strip() else "")
                return
        raise KeyError(".".join(path))

    def _append_block(self, key):
        last = max(i for i, p, _, _ in self._walk() if p[0] == key[0])
        self.lines[last + 1:last + 1] = [""] + EXTRA_BLOCKS[key]

    def save(self, path):
        with open(path, "w") as f:
            f.write("\n".join(self.lines) + "\n")


# ----------------------------------------------------------------------------
# prompts
# ----------------------------------------------------------------------------
class Prompt:
    def __init__(self, yes=False):
        self.yes = yes

    def _read(self, text):
        if self.yes:
            return ""
        try:
            return input(text).strip()
        except EOFError:
            return ""

    def ask(self, text, default="", check=None, required=False):
        while True:
            shown = " [%s]" % default if default not in ("", None) else ""
            ans = self._read("%s%s: " % (text, shown))
            if ans == "":
                ans = str(default) if default is not None else ""
            elif ans == "-":
                ans = ""
            if required and ans == "":
                if self.yes:
                    sys.exit("ERROR: no value available for required setting: %s" % text)
                print("  a value is required")
                continue
            msg = check(ans) if (check and ans != "") else None
            if msg:
                if self.yes:
                    print("  warning: %s" % msg)
                    return ans
                print("  %s" % msg)
                continue
            return ans

    def yesno(self, text, default=True):
        ans = self._read("%s [%s]: " % (text, "Y/n" if default else "y/N")).lower()
        return default if ans == "" else ans.startswith("y")

    def choose(self, text, options, default=0):
        print(text)
        for i, o in enumerate(options, 1):
            print("  %d) %s" % (i, o))
        while True:
            ans = self._read("Choice [%d]: " % (default + 1))
            if ans == "":
                return default
            if ans.isdigit() and 1 <= int(ans) <= len(options):
                return int(ans) - 1
            if self.yes:
                return default
            print("  enter a number between 1 and %d" % len(options))


def is_file(base=None):
    def check(p):
        full = os.path.join(base, p) if base else p
        return None if os.path.isfile(full) else "file not found: %s" % full
    return check


def is_int(p):
    return None if re.fullmatch(r"\d+", p) else "enter a positive integer"


def is_float01(p):
    try:
        return None if 0 <= float(p) <= 1 else "enter a value between 0 and 1"
    except ValueError:
        return "enter a number between 0 and 1"


# ----------------------------------------------------------------------------
# detection helpers
# ----------------------------------------------------------------------------
def list_files(folder, exts=None):
    if not os.path.isdir(folder):
        return []
    out = [f for f in sorted(os.listdir(folder)) if os.path.isfile(os.path.join(folder, f))]
    return [f for f in out if not exts or f.lower().endswith(exts)]


def detect_samples(data_dir):
    ids = set()
    for sub in ("reads1", "reads2", "reads", "bam"):
        for f in list_files(os.path.join(data_dir, "samples", sub)):
            if not re.search(r"\.(fastq|fq|bam)(\.gz)?$", f):
                continue
            name = re.sub(r"\.(fastq|fq|bam)(\.gz)?$", "", f)
            if sub in ("reads1", "reads2"):
                name = re.sub(r"[_.](1|2|r1|r2|R1|R2)$", "", name)
            ids.add(name)
    return sorted(ids)


def previous_runs(roots):
    runs = {}
    for root in roots:
        if not os.path.isdir(root or "."):
            continue
        for d in sorted(os.listdir(root or ".")):
            full = os.path.join(root, d)
            if d.startswith("data_output_") and os.path.isdir(full):
                done = [s for s, _ in STEPS if os.path.isdir(os.path.join(full, s))]
                runs[full] = done
    return runs


def looks_like_template(cfg):
    text = "\n".join(cfg.lines)
    return any(p in text for p in PLACEHOLDERS)


def which_default(cfg, dep, key, exe):
    cur = cfg.get((dep, key))
    if cur and "/path/to" not in cur and os.path.exists(cur):
        return cur
    return shutil.which(exe) or ""


def read_population(path):
    groups = {}
    with open(path) as f:
        for line in f:
            x = line.rstrip("\n").split("\t")
            if len(x) >= 2:
                groups[x[0]] = x[1]
    return groups


# ----------------------------------------------------------------------------
# wizard sections
# ----------------------------------------------------------------------------
def section(title):
    print("\n== %s" % title)


def configure_tools(cfg, ui, dep, need_rm, need_fastp):
    section("Tools")
    tools = [("PYTHON3", "python3", True), ("BWA", "bwa", True), ("SAMTOOLS", "samtools", True), ("AWK", "awk", True),
             ("FASTP", "fastp", need_fastp), ("REPEATMASKER", "RepeatMasker", need_rm)]
    for key, exe, needed in tools:
        if not needed and not cfg.has((dep, key)):
            continue
        default = which_default(cfg, dep, key, exe) or (shutil.which(exe.lower()) or "")
        label = "Path to %s%s" % (exe, "" if needed else " (not needed for this setup, '-' to leave empty)")
        val = ui.ask(label, default, check=lambda p: None if os.path.exists(p) else "path not found: %s" % p,
                     required=needed)
        if cfg.has((dep, key)):
            cfg.set((dep, key), val if val else "/path/to/%s" % exe)


def configure_inputs(cfg, ui, opts):
    section("Input data")
    data_dir = ui.ask("Input data folder (contains reference/, library/, samples/)",
                      cfg.get(("DATA_INPUT", "WORKING_DIRECTORY"), "data_input"),
                      check=lambda p: None if os.path.isdir(p) else "folder not found")
    cfg.set(("DATA_INPUT", "WORKING_DIRECTORY"), data_dir)

    genomes = list_files(os.path.join(data_dir, "reference"), (".fa", ".fasta", ".fna", ".fa.gz", ".fasta.gz"))
    if genomes:
        cur = cfg.get(("DATA_INPUT", "GENOME"))
        idx = ui.choose("Reference genome:", genomes, genomes.index(cur) if cur in genomes else 0)
        genome = genomes[idx]
    else:
        genome = ui.ask("Reference genome file name (in %s/reference)" % data_dir, cfg.get(("DATA_INPUT", "GENOME")),
                        check=is_file(os.path.join(data_dir, "reference")), required=True)
    cfg.set(("DATA_INPUT", "GENOME"), genome)

    lib_dir = os.path.join(data_dir, "library")
    beds = list_files(lib_dir, (".bed", ".gff", ".gff3", ".gtf"))
    mode = ui.choose("How do you provide the TE annotation of the reference?",
                     ["I have an annotation file + TE hierarchy file (TEFLoN2 prep_annotation)",
                      "I only have a TE library: annotate the genome with RepeatMasker (prep_custom)"],
                     0 if beds else 1)
    libs = list_files(lib_dir, (".fa", ".fasta", ".fna"))
    if not libs and ui.yesno("No TE library found in %s. Download the latest Dfam library now?" % lib_dir, True):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install", "download_dfam.py")
        taxon = ui.ask("Restrict to a name pattern (regular expression, empty = all curated families)", "")
        cmd = [sys.executable, script, "-o", lib_dir] + (["--filter", taxon] if taxon else [])
        if subprocess.call(cmd) == 0:
            libs = list_files(lib_dir, (".fa", ".fasta", ".fna"))
    lib = ""
    if libs:
        cur = cfg.get(("DATA_INPUT", "LIBRARY"))
        names = libs + ["(none)"] if mode == 0 else libs
        i = ui.choose("TE library:", names, libs.index(cur) if cur in libs else 0)
        lib = "" if names[i] == "(none)" else names[i]
    elif mode == 1:
        lib = ui.ask("TE library file name (in %s)" % lib_dir, "", check=is_file(lib_dir), required=True)
    cfg.set(("DATA_INPUT", "LIBRARY"), lib)

    levels = ["family", "order"]
    if mode == 0:
        ann = ui.ask("Annotation file name (in %s)" % lib_dir, beds[0] if beds else cfg.get(("DATA_INPUT", "ANNOTATION")),
                     check=is_file(lib_dir), required=True)
        hier_c = list_files(lib_dir, (".txt", ".tsv"))
        cur = cfg.get(("DATA_INPUT", "HIERARCHY"))
        hier = ui.ask("TE hierarchy file name (in %s)" % lib_dir, cur if cur in hier_c else (hier_c[0] if hier_c else ""),
                      check=is_file(lib_dir), required=True)
        cfg.set(("DATA_INPUT", "ANNOTATION"), ann)
        cfg.set(("DATA_INPUT", "HIERARCHY"), hier)
        if os.path.isfile(os.path.join(lib_dir, hier)):
            with open(os.path.join(lib_dir, hier)) as f:
                header = f.readline().rstrip("\n").split("\t")
            levels = header[1:] or levels
        print("  hierarchy levels found: %s" % ", ".join(levels))
    else:
        cfg.set(("DATA_INPUT", "ANNOTATION"), "")
        cfg.set(("DATA_INPUT", "HIERARCHY"), "")
        species = ui.ask("Species name for RepeatMasker (empty to use only the library)", cfg.get(("PARAMS", "PREP_CUSTOM", "SPECIES")))
        cfg.set(("PARAMS", "PREP_CUSTOM", "SPECIES"), species)
        levels = ["family", "class"]
    opts["custom"] = mode == 1
    opts["levels"] = levels
    opts["data_dir"] = data_dir

    samples = detect_samples(data_dir)
    print("  %d sample(s) detected in %s/samples: %s%s" % (len(samples), data_dir, ", ".join(samples[:6]),
                                                          " ..." if len(samples) > 6 else ""))
    opts["samples"] = samples
    if not samples:
        print("  warning: no sample found (expected reads1/, reads2/, reads/ or bam/ under %s/samples)" % data_dir)


def configure_run(cfg, ui, opts):
    section("Run settings")
    cur = cfg.get(("PARAMS", "GENERAL", "PREFIX"))
    if cur == "name_run":
        cur = "run1"
    prefix = ui.ask("Run name (PREFIX; results go to data_output_<PREFIX>)", cur, required=True,
                    check=lambda p: None if re.fullmatch(r"[A-Za-z0-9._-]+", p) else "use letters, digits, . _ - only")
    cfg.set(("PARAMS", "GENERAL", "PREFIX"), prefix)
    cfg.set(("PARAMS", "GENERAL", "WORKING_DIRECTORY"),
            ui.ask("Output parent folder (empty = current directory)", cfg.get(("PARAMS", "GENERAL", "WORKING_DIRECTORY"))))
    mem = ui.ask("Memory per job in MB", cfg.get(("PARAMS", "GENERAL", "MEMORY"), "30000"), check=is_int)
    cfg.set(("PARAMS", "GENERAL", "MEMORY"), int(mem))
    threads = ui.ask("Threads per step (max)", min(16, os.cpu_count() or 4), check=is_int)
    for key in [("COMPRESS", "THREADS"), ("FILTERFASTQ", "THREADS"), ("SAMTOOLS", "THREADS"), ("PREP_CUSTOM", "THREADS"),
                ("DISCOVER", "THREADS"), ("COLLAPSE", "THREADS"), ("COUNT", "THREADS")]:
        if cfg.has(("PARAMS",) + key):
            cfg.set(("PARAMS",) + key, int(threads))
    fq = ui.yesno("Filter the reads with fastp before mapping?", cfg.get(("PARAMS", "FILTERFASTQ", "USE")) == "1")
    cfg.set(("PARAMS", "FILTERFASTQ", "USE"), 1 if fq else 0)
    opts["fastp"] = fq
    return prefix


def configure_steps(cfg, ui, opts):
    section("Discover / collapse / count")
    lv = opts["levels"]
    for key, default in (("LEVEL_HIERARCHY1", lv[0]), ("LEVEL_HIERARCHY2", lv[-1])):
        cur = cfg.get(("PARAMS", "DISCOVER", key))
        i = ui.choose("TE hierarchy %s (%s):" % (key[-1], "finest grouping" if key.endswith("1") else "coarser grouping"),
                      lv, lv.index(cur) if cur in lv else lv.index(default))
        cfg.set(("PARAMS", "DISCOVER", key), lv[i])
    q = ui.ask("Minimum mapping quality", cfg.get(("PARAMS", "DISCOVER", "QUALITY"), "20"), check=is_int)
    for step in ("DISCOVER", "COLLAPSE", "COUNT"):
        cfg.set(("PARAMS", step, "QUALITY"), q)
    cfg.set(("PARAMS", "COLLAPSE", "THRESHOLD_SAMPLE"),
            ui.ask("Collapse: min reads per TE in at least one sample", cfg.get(("PARAMS", "COLLAPSE", "THRESHOLD_SAMPLE"), "1"), check=is_int))
    cfg.set(("PARAMS", "COLLAPSE", "THRESHOLD_ALL"),
            ui.ask("Collapse: min reads per TE over all samples", cfg.get(("PARAMS", "COLLAPSE", "THRESHOLD_ALL"), "1"), check=is_int))


def configure_genotype(cfg, ui, opts):
    section("Genotyping")
    types = ["haploid", "diploid", "pooled"]
    cur = cfg.get(("PARAMS", "GENOTYPE", "DATA_TYPE"), "pooled")
    cfg.set(("PARAMS", "GENOTYPE", "DATA_TYPE"), types[ui.choose("Data type of the samples:", types, types.index(cur) if cur in types else 2)])
    cfg.set(("PARAMS", "GENOTYPE", "THRESHOLD_LOWER"),
            ui.ask("Min adjusted read count at a site (lower = no data)", cfg.get(("PARAMS", "GENOTYPE", "THRESHOLD_LOWER"), "1"), check=is_int))
    cfg.set(("PARAMS", "GENOTYPE", "THRESHOLD_HIGHER"),
            ui.ask("Max adjusted read count at a site (empty = mean + 2 SD)", cfg.get(("PARAMS", "GENOTYPE", "THRESHOLD_HIGHER")), check=is_int))
    if ui.yesno("Change the sample frequency thresholds (default: absent < 0.05, present > 0.95)?", False):
        cfg.set(("PARAMS", "GENOTYPE", "SAMPLE", "THRESHOLD_ABSENCE"), ui.ask("  absence threshold", "0.05", check=is_float01))
        cfg.set(("PARAMS", "GENOTYPE", "SAMPLE", "THRESHOLD_PRESENCE"), ui.ask("  presence threshold", "0.95", check=is_float01))

    section("Populations")
    cur = cfg.get(("PARAMS", "GENOTYPE", "POPULATION", "FILE"))
    pop = ui.ask("Population file (tab-delimited: sample<TAB>population; empty = no population analysis)", cur,
                 check=is_file())
    cfg.set(("PARAMS", "GENOTYPE", "POPULATION", "FILE"), pop)
    if pop and os.path.isfile(pop):
        groups = read_population(pop)
        counts = {}
        for g in groups.values():
            counts[g] = counts.get(g, 0) + 1
        print("  %d populations: %s" % (len(counts), ", ".join("%s (%d)" % kv for kv in sorted(counts.items()))))
        missing = sorted(set(opts.get("samples", [])) - set(groups))
        unknown = sorted(set(groups) - set(opts.get("samples", []))) if opts.get("samples") else []
        if missing:
            print("  warning: samples without population: %s" % ", ".join(missing[:8]))
        if unknown:
            print("  warning: population file lists unknown samples: %s" % ", ".join(unknown[:8]))
        if ui.yesno("Change the population frequency thresholds (default 0.05 / 0.95)?", False):
            cfg.set(("PARAMS", "GENOTYPE", "POPULATION", "THRESHOLD_ABSENCE"), ui.ask("  absence threshold", "0.05", check=is_float01))
            cfg.set(("PARAMS", "GENOTYPE", "POPULATION", "THRESHOLD_PRESENCE"), ui.ask("  presence threshold", "0.95", check=is_float01))


def configure_outputs(cfg, ui):
    section("Outputs")
    use = ui.yesno("Write the VCF + GFA genotyping graph?", cfg.get(("PARAMS", "EXPORT", "USE"), "1") != "0")
    cfg.set(("PARAMS", "EXPORT", "USE"), 1 if use else 0)
    if use:
        paths = ["samples", "reference"]
        cur = cfg.get(("PARAMS", "EXPORT", "GFA_PATHS"), "samples")
        cfg.set(("PARAMS", "EXPORT", "GFA_PATHS"),
                paths[ui.choose("GFA paths (one path per sample gives large files for many samples):",
                                ["samples (one path per sample and sequence)", "reference (reference path only)"],
                                paths.index(cur) if cur in paths else 0)])
        comp = ui.yesno("Also write a bgzip-compressed, tabix-indexed VCF (needs bgzip and tabix)?",
                        cfg.get(("PARAMS", "EXPORT", "COMPRESS"), "0") == "1" and bool(shutil.which("bgzip")))
        cfg.set(("PARAMS", "EXPORT", "COMPRESS"), 1 if comp else 0)
    rep = ui.yesno("Build the HTML quality/results report?", cfg.get(("PARAMS", "REPORT", "USE"), "1") != "0")
    cfg.set(("PARAMS", "REPORT", "USE"), 1 if rep else 0)
    if rep and ui.yesno("Change the QC flags (coverage < 5x, mapped < 80 %, properly paired < 80 %)?", False):
        cfg.set(("PARAMS", "REPORT", "MIN_COVERAGE"), int(ui.ask("  minimum mean coverage", "5", check=is_int)))
        cfg.set(("PARAMS", "REPORT", "MIN_MAPPED"), int(ui.ask("  minimum % mapped reads", "80", check=is_int)))
        cfg.set(("PARAMS", "REPORT", "MIN_PROPERLY_PAIRED"), int(ui.ask("  minimum % properly paired reads", "80", check=is_int)))

    if rep and ui.yesno("Add a gene annotation (GFF3/GTF) to the genome browser, to see the impact of the TEs on genes?",
                        bool(cfg.get(("PARAMS", "REPORT", "GENE_ANNOTATION"), "").strip('"'))):
        cur = cfg.get(("PARAMS", "REPORT", "GENE_ANNOTATION"), "").strip('"')
        cfg.set(("PARAMS", "REPORT", "GENE_ANNOTATION"), ui.ask("  path to the GFF3/GTF file", cur, check=is_file(), required=True))
        cfg.set(("PARAMS", "REPORT", "GENE_FLANK"), int(ui.ask("  distance (bp) for an upstream / downstream TE", "2000", check=is_int)))

    section("Where to stop")
    stops = ["Run the whole pipeline", "Stop after reference preparation", "Stop after discover",
             "Stop after collapse", "Stop after count"]
    keys = [None, ("PREP_ANNOTATION", "PREP_CUSTOM"), ("DISCOVER",), ("COLLAPSE",), ("COUNT",)]
    i = ui.choose("How far should this run go?", stops, 0)
    for group in keys[1:]:
        for k in group:
            if cfg.has(("PARAMS", k, "STOP")):
                cfg.set(("PARAMS", k, "STOP"), 0)
    if keys[i]:
        for k in keys[i]:
            if cfg.has(("PARAMS", k, "STOP")):
                cfg.set(("PARAMS", k, "STOP"), 1)


# ----------------------------------------------------------------------------
def regenotype(prefix_dirs, ui):
    folder = prefix_dirs[0]
    targets = [os.path.join(folder, d) for d in ("4-genotypes", "5-export", "6-report") if os.path.isdir(os.path.join(folder, d))]
    if not targets:
        print("  nothing to remove: no genotype results in %s" % folder)
        return
    print("  these folders will be deleted so that Snakemake recomputes them:")
    for t in targets:
        print("    %s" % t)
    if ui.yesno("Delete them? (mapping, discover and count results are kept)", False):
        for t in targets:
            shutil.rmtree(t)
        print("  done")


def main():
    ap = argparse.ArgumentParser(description="Interactive configuration of TEFLoN2")
    ap.add_argument("-c", "--config", default="config.yaml", help="configuration file to read and write (default: config.yaml)")
    ap.add_argument("--yes", action="store_true", help="non-interactive: accept the detected/default values")
    ap.add_argument("--set", action="append", default=[], metavar="A.B.C=value", help="force a value (can be repeated)")
    args = ap.parse_args()
    ui = Prompt(args.yes)

    template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
    if not os.path.exists(args.config):
        if not os.path.exists(template):
            sys.exit("ERROR: no config file and no template found")
        shutil.copy(template, args.config)
        print("Created %s from the template" % args.config)
    cfg = Config.load(args.config)
    dep = "DEPENDANCES" if cfg.has(("DEPENDANCES",)) else "DEPENDENCIES"
    roots = {".", cfg.get(("PARAMS", "GENERAL", "WORKING_DIRECTORY"), "") or "."}
    runs = previous_runs(sorted(roots))
    first = looks_like_template(cfg) and not runs

    print("TEFLoN2 configuration - %s" % ("FIRST RUN: guided setup" if first else "existing configuration detected"))
    opts = {}
    mode = "full"
    if not first:
        if runs:
            print("\nPrevious runs:")
            for r, done in runs.items():
                print("  %s: %s" % (r, ", ".join(s for s, _ in STEPS if s in done) or "empty"))
        prefix_now = cfg.get(("PARAMS", "GENERAL", "PREFIX"))
        choice = ui.choose("\nWhat do you want to do?",
                           ["Start a NEW run (new run name, review all settings)",
                            "UPDATE the current run '%s' (add samples / change settings; finished steps are not redone)" % prefix_now,
                            "RE-GENOTYPE the current run with new thresholds (keeps mapping, discover and count)",
                            "Only change the outputs (VCF/GFA/report) of the current run"], 0)
        if choice == 2:
            wd = cfg.get(("PARAMS", "GENERAL", "WORKING_DIRECTORY"), "")
            regenotype([os.path.join(wd, "data_output_" + prefix_now)], ui)
            mode = "genotype"
        elif choice == 3:
            mode = "outputs"
        elif choice == 1:
            mode = "update"
        else:
            mode = "new"

    if mode in ("full", "new", "update"):
        configure_inputs(cfg, ui, opts)
        prefix = configure_run(cfg, ui, opts)
        configure_tools(cfg, ui, dep, opts["custom"], opts["fastp"])
        if mode == "new" and any(p.endswith("data_output_" + prefix) for p in runs):
            print("  note: '%s' already exists, Snakemake will reuse its finished steps. Choose another name for a fresh run." % prefix)
        configure_steps(cfg, ui, opts)
    if mode in ("full", "new", "update", "genotype"):
        if not opts.get("samples"):
            opts["samples"] = detect_samples(cfg.get(("DATA_INPUT", "WORKING_DIRECTORY"), "data_input"))
        configure_genotype(cfg, ui, opts)
    if mode in ("full", "new", "update", "outputs"):
        configure_outputs(cfg, ui)

    for item in args.set:
        key, _, val = item.partition("=")
        cfg.set(tuple(key.split(".")), int(val) if val.isdigit() else val)

    section("Summary")
    for path in [("DATA_INPUT", "GENOME"), ("DATA_INPUT", "ANNOTATION"), ("DATA_INPUT", "LIBRARY"), ("PARAMS", "GENERAL", "PREFIX"),
                 ("PARAMS", "GENOTYPE", "DATA_TYPE"), ("PARAMS", "GENOTYPE", "POPULATION", "FILE"),
                 ("PARAMS", "EXPORT", "USE"), ("PARAMS", "REPORT", "USE")]:
        print("  %-42s %s" % (".".join(path), cfg.get(path) or "-"))
    if ui.yesno("\nWrite %s?" % args.config, True):
        if os.path.exists(args.config):
            backup = "%s.bak-%s" % (args.config, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
            shutil.copy(args.config, backup)
            print("  previous file saved as %s" % backup)
        cfg.save(args.config)
        cores = cfg.get(("PARAMS", "COUNT", "THREADS"), "8")
        print("  wrote %s" % args.config)
        print("\nNext:\n  snakemake --configfile %s --cores %s -n     # dry run\n  snakemake --configfile %s --cores %s"
              % (args.config, cores, args.config, cores))
    else:
        print("  nothing written")


if __name__ == "__main__":
    main()
