#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_dfam.py - download the latest Dfam TE library and convert it to a FASTA usable by TEFLoN2

Dfam (https://www.dfam.org) is the open TE database distributed with RepeatMasker.
(Repbase is a licensed resource from GIRI and cannot be downloaded automatically:
 obtain it from https://www.girinst.org and pass the resulting FASTA to TEFLoN2 yourself.)

Two modes
---------
1. default (no dependency): downloads the *curated-only EMBL* export of the release,
   verifies its md5 checksum, and converts it to FASTA (>name#Type/SubType).
   The file covers all taxa; use --filter to keep names matching a regular expression.
2. --taxon "Anopheles": downloads the FamDB root partition and the curated-consensus
   partition(s), then extracts the families of the taxon (and its ancestors/descendants)
   with famdb.py (needs h5py). EXPERIMENTAL: the exact file names of the FamDB v3
   components are discovered from the server index, not hard-coded.

The release is `current` (= latest) unless --release X.Y is given. The release number,
the checksums and the date are recorded in DFAM_VERSION.json for reproducibility.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from urllib.parse import urljoin

BASE_URL = "https://www.dfam.org"


def fetch(url, retries=3, binary=False):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TEFLoN2-installer"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as exc:  # network errors are retried
            last = exc
            time.sleep(2 * (i + 1))
    raise SystemExit("ERROR: cannot fetch %s (%s)" % (url, last))


def list_dir(url):
    """Names of the files linked from a server directory index."""
    html = fetch(url if url.endswith("/") else url + "/")
    names = []
    for href in re.findall(r'href="([^"?#]+)"', html):
        if href.startswith(("/", "..")) or href.endswith("/"):
            continue
        names.append(os.path.basename(href))
    return sorted(set(names))


def download(url, dest, expected_md5=None):
    print("  downloading %s" % url)
    req = urllib.request.Request(url, headers={"User-Agent": "TEFLoN2-installer"})
    md5 = hashlib.md5()
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as out:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            md5.update(chunk)
            out.write(chunk)
    if expected_md5 and md5.hexdigest() != expected_md5:
        os.remove(dest)
        raise SystemExit("ERROR: md5 mismatch for %s" % os.path.basename(dest))
    return md5.hexdigest()


def remote_md5(base, name):
    try:
        txt = fetch(urljoin(base, name + ".md5sum"), retries=1)
    except SystemExit:
        return None
    m = re.search(r"\b([0-9a-f]{32})\b", txt)
    return m.group(1) if m else None


def release_version(base_release_url, requested):
    try:
        notes = fetch(urljoin(base_release_url, "relnotes.txt"), retries=1)
        m = re.search(r"Dfam[ _-]*(?:release\s*)?v?(\d+\.\d+)", notes, re.I)
        if m:
            return m.group(1)
    except SystemExit:
        pass
    return requested


def embl_to_fasta(embl_paths, fasta_path, name_filter=None):
    """Convert Dfam EMBL records (NM/ID, Type/SubType, SQ) to >name#Type/SubType FASTA."""
    rx = re.compile(name_filter) if name_filter else None
    n_in = n_out = 0
    with open(fasta_path, "w") as out:
        for path in embl_paths:
            op = gzip.open if path.endswith(".gz") else open
            with op(path, "rt") as fin:
                name = acc = typ = sub = None
                seq, in_seq = [], False
                for line in fin:
                    code = line[:2]
                    if code == "ID":
                        acc = line[5:].split(";")[0].strip()
                        name, typ, sub, seq, in_seq = None, None, None, [], False
                    elif code == "NM" and name is None:
                        name = line[5:].strip()
                    elif code == "CC":
                        m = re.search(r"\bSubType:\s*(\S+)", line)
                        if m:
                            sub = m.group(1)
                        m = re.search(r"\bType:\s*(\S+)", line)
                        if m:
                            typ = m.group(1)
                    elif code == "SQ":
                        in_seq = True
                    elif line.startswith("//"):
                        n_in += 1
                        label = re.sub(r"[#\s/]", "_", name or acc or "unnamed")
                        cls = typ or "Unknown"
                        if sub:
                            cls += "/" + sub
                        if seq and (rx is None or rx.search(label) or rx.search(cls)):
                            s = "".join(seq).upper()
                            out.write(">%s#%s\n" % (label, cls))
                            for i in range(0, len(s), 60):
                                out.write(s[i:i + 60] + "\n")
                            n_out += 1
                        in_seq = False
                    elif in_seq:
                        seq.append(re.sub(r"[^A-Za-z]", "", line))
    return n_in, n_out


def find_famdb(explicit, outdir):
    for cand in (explicit, shutil.which("famdb.py"), os.path.join(outdir, "FamDB", "famdb.py")):
        if cand and os.path.exists(cand):
            return cand
    print("  famdb.py not found: cloning https://github.com/Dfam-consortium/FamDB")
    subprocess.check_call(["git", "clone", "--depth", "1", "https://github.com/Dfam-consortium/FamDB.git",
                           os.path.join(outdir, "FamDB")])
    return os.path.join(outdir, "FamDB", "famdb.py")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--outdir", default="data_input/library", help="output directory (default: data_input/library)")
    ap.add_argument("--release", default="current", help="'current' (latest, default) or a release such as 3.9")
    ap.add_argument("--taxon", help="extract the families of this taxon with FamDB (e.g. 'Anopheles')")
    ap.add_argument("--filter", help="regular expression: keep only entries whose name or class matches (EMBL mode)")
    ap.add_argument("--famdb", help="path to famdb.py (taxon mode)")
    ap.add_argument("--base-url", default=BASE_URL, help=argparse.SUPPRESS)
    ap.add_argument("--dry-run", action="store_true", help="only list what would be downloaded")
    ap.add_argument("--force", action="store_true", help="download again even if the files already exist")
    args = ap.parse_args()

    rel_url = "%s/releases/%s/" % (args.base_url.rstrip("/"), args.release)
    fam_url = rel_url + "families/"
    version = release_version(rel_url, args.release)
    os.makedirs(args.outdir, exist_ok=True)
    record = {"release_requested": args.release, "release_version": version, "source": fam_url,
              "date": datetime.date.today().isoformat(), "files": {}}

    if args.taxon:
        names = list_dir(fam_url + "FamDB")
        h5 = [n for n in names if re.search(r"\.h5(\.gz)?$", n)]
        root = [n for n in h5 if re.search(r"\.0\.h5", n)]
        cc = [n for n in h5 if re.search(r"(^|[_.-])cc([_.-]|\d)", n, re.I)]
        wanted = sorted(set(root + cc))
        print("Dfam %s - FamDB files selected: %s" % (version, ", ".join(wanted) or "none"))
        if not wanted:
            sys.exit("Could not identify the root / curated-consensus files automatically.\n"
                     "Use FamDB's interactive downloader instead: utils/download_dfam.py "
                     "(https://github.com/Dfam-consortium/FamDB), or run without --taxon.")
        if args.dry_run:
            return
        famdir = os.path.join(args.outdir, "FamDB_dfam_%s" % version)
        os.makedirs(famdir, exist_ok=True)
        for n in wanted:
            dest = os.path.join(famdir, n)
            if os.path.exists(dest) and not args.force:
                continue
            record["files"][n] = download(fam_url + "FamDB/" + n, dest, remote_md5(fam_url + "FamDB/", n))
            if n.endswith(".gz"):
                with gzip.open(dest, "rb") as fin, open(dest[:-3], "wb") as fout:
                    shutil.copyfileobj(fin, fout)
                os.remove(dest)
        famdb = find_famdb(args.famdb, args.outdir)
        fasta = os.path.join(args.outdir, "Dfam_%s_%s.fasta" % (version, re.sub(r"\W+", "_", args.taxon)))
        with open(fasta, "w") as out:
            subprocess.check_call([sys.executable, famdb, "-i", famdir, "families", "-ad",
                                   "--include-class-in-name", "-f", "fasta_name", args.taxon], stdout=out)
    else:
        names = list_dir(fam_url)
        embl = [n for n in names if re.match(r"Dfam-curated_only-\d+\.embl\.gz$", n)] or \
               [n for n in names if re.match(r"Dfam-curated_only.*\.embl\.gz$", n)]
        print("Dfam %s - curated EMBL files: %s" % (version, ", ".join(embl) or "none"))
        if not embl:
            sys.exit("No curated EMBL export found at %s" % fam_url)
        if args.dry_run:
            return
        local = []
        for n in embl:
            dest = os.path.join(args.outdir, n)
            if not os.path.exists(dest) or args.force:
                record["files"][n] = download(fam_url + n, dest, remote_md5(fam_url, n))
            local.append(dest)
        label = re.sub(r"\W+", "_", args.filter) if args.filter else "curated"
        fasta = os.path.join(args.outdir, "Dfam_%s_%s.fasta" % (version, label))
        n_in, n_out = embl_to_fasta(local, fasta, args.filter)
        print("  %d records read, %d written to %s" % (n_in, n_out, fasta))

    with open(os.path.join(args.outdir, "DFAM_VERSION.json"), "w") as f:
        json.dump(record, f, indent=2)
    print("\nDone. Use it in config.yaml:\n  DATA_INPUT:\n    LIBRARY: \"%s\"" % os.path.basename(fasta))
    print("Recorded: %s" % os.path.join(args.outdir, "DFAM_VERSION.json"))


if __name__ == "__main__":
    main()
