#!/usr/bin/env python3
"""Offline test of install/download_dfam.py against a local fake Dfam server."""
import gzip, hashlib, os, subprocess, sys, tempfile, threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from functools import partial

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBL = """ID   DF000000001; DF000000001; linear; DNA; STD; UNC; 12 BP.
NM   AluY
CC   RepeatMasker Annotations:
CC        Type: SINE
CC        SubType: Alu
SQ   Sequence 12 BP; 3 A; 3 C; 3 G; 3 T; 0 other;
     acgtacgtac gt        12
//
ID   DF000000002; DF000000002; linear; DNA; STD; UNC; 8 BP.
NM   Gypsy-1_AG
CC        Type: LTR
CC        SubType: Gypsy
SQ   Sequence 8 BP;
     ttttaaaa     8
//
"""


def main():
    srv = tempfile.mkdtemp()
    fam = os.path.join(srv, "releases", "current", "families")
    os.makedirs(fam)
    gz = os.path.join(fam, "Dfam-curated_only-1.embl.gz")
    with gzip.open(gz, "wt") as f:
        f.write(EMBL)
    md5 = hashlib.md5(open(gz, "rb").read()).hexdigest()
    open(gz + ".md5sum", "w").write("%s  Dfam-curated_only-1.embl.gz\n" % md5)
    open(os.path.join(srv, "releases", "current", "relnotes.txt"), "w").write("Dfam 4.0\nnotes\n")
    handler = partial(SimpleHTTPRequestHandler, directory=srv)
    handler.log_message = lambda *a, **k: None
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % httpd.server_port
    out = tempfile.mkdtemp()
    cmd = [sys.executable, os.path.join(ROOT, "install", "download_dfam.py"), "-o", out, "--base-url", base]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    fa = open(os.path.join(out, "Dfam_4.0_curated.fasta")).read()
    assert ">AluY#SINE/Alu\nACGTACGTACGT\n" in fa and ">Gypsy-1_AG#LTR/Gypsy\nTTTTAAAA\n" in fa, fa
    assert '"release_version": "4.0"' in open(os.path.join(out, "DFAM_VERSION.json")).read()
    # filter + checksum failure
    r = subprocess.run(cmd + ["--filter", "Gypsy", "--force"], capture_output=True, text=True)
    assert r.returncode == 0 and ">AluY" not in open(os.path.join(out, "Dfam_4.0_Gypsy.fasta")).read()
    open(gz + ".md5sum", "w").write("0" * 32 + "  x\n")
    r = subprocess.run(cmd + ["--force"], capture_output=True, text=True)
    assert r.returncode != 0 and "md5 mismatch" in (r.stderr + r.stdout)
    print("download_dfam tests OK")


main()
