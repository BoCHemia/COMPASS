#!/usr/bin/env python3
"""
Download the data and model files from Zenodo and install them
at the project root.

Steps:
  1. Download heavy_files.zip from Zenodo (resumes if interrupted).
  2. Verify its MD5 checksum.
  3. Extract it and move heavy_files/data and heavy_files/models to the project root.
  4. Delete the heavy_files folder (and the zip, unless --keep-zip is given).

Usage:
    python download_files.py [--force] [--keep-zip]

Only the Python standard library is used, so it can run before any
dependencies are installed.
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
ZENODO_URL = "https://zenodo.org/records/1234/files/heavy_files.zip"

# MD5 shown on the Zenodo record page next to the file.
# Leave as None to fetch it automatically from the Zenodo API.
EXPECTED_MD5 = None

FOLDERS = ("data", "models")          # folders to move to the project root
ROOT = Path(__file__).resolve().parent
ZIP_PATH = ROOT / "heavy_files.zip"
EXTRACT_DIR = ROOT / "heavy_files"
CHUNK_SIZE = 8 * 1024 * 1024          # 8 MB
USER_AGENT = "heavy-files-downloader/1.0"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def human(n_bytes): # make output human-readable
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} PB"


def fetch_md5_from_zenodo(url):
    """Get the file's MD5 from the Zenodo REST API."""
    match = re.search(r"zenodo\.org/records?/(\d+)/files/([^/?]+)", url)
    if not match:
        sys.exit("Could not parse record id from URL; set EXPECTED_MD5 manually.")
    record_id, filename = match.groups()
    api_url = f"https://zenodo.org/api/records/{record_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        record = json.load(resp)
    for f in record.get("files", []):
        if f.get("key") == filename:
            checksum = f.get("checksum", "")
            if checksum.startswith("md5:"):
                return checksum.split(":", 1)[1]
    sys.exit(f"MD5 for {filename} not found in Zenodo record {record_id}; "
             "set EXPECTED_MD5 manually.")


def download(url, dest):
    """Download url to dest, resuming a partial download if one exists."""
    existing = dest.stat().st_size if dest.exists() else 0
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(f"{url}{sep}download=1",
                                 headers={"User-Agent": USER_AGENT})
    if existing:
        req.add_header("Range", f"bytes={existing}-")
        print(f"Resuming download from {human(existing)}")

    try:
        resp = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code == 416:  # requested range not satisfiable -> file already complete
            print("File already fully downloaded.")
            return
        raise

    with resp:
        if existing and resp.status != 206:   # server ignored the Range header
            print("Server does not support resuming; restarting download.")
            existing = 0
        length = resp.headers.get("Content-Length")
        total = int(length) + existing if length else None

        done = existing
        start = time.time()
        with open(dest, "ab" if existing else "wb") as f:
            while chunk := resp.read(CHUNK_SIZE):
                f.write(chunk)
                done += len(chunk)
                speed = (done - existing) / max(time.time() - start, 1e-6)
                if total:
                    pct = 100 * done / total
                    print(f"\r  {human(done)} / {human(total)} ({pct:5.1f}%) "
                          f"at {human(speed)}/s   ", end="", flush=True)
                else:
                    print(f"\r  {human(done)} at {human(speed)}/s   ",
                          end="", flush=True)
        print()


def md5sum(path):
    h = hashlib.md5()
    size = path.stat().st_size
    done = 0
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
            done += len(chunk)
            print(f"\r  Hashing... {100 * done / size:5.1f}%", end="", flush=True)
    print()
    return h.hexdigest()


def find_source_dir(base):
    """Return the folder containing data/ and models/ (handles zips with or
    without a top-level heavy_files/ folder)."""
    for candidate in (base / "heavy_files", base):
        if all((candidate / name).is_dir() for name in FOLDERS):
            return candidate
    sys.exit(f"Could not find {', '.join(FOLDERS)} inside the extracted archive.")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing data/ and models/ folders")
    parser.add_argument("--keep-zip", action="store_true",
                        help="keep heavy_files.zip after extraction")
    args = parser.parse_args()

    # Refuse to clobber existing folders unless asked to
    existing = [name for name in FOLDERS if (ROOT / name).exists()]
    if existing and not args.force:
        sys.exit(f"Already present at project root: {', '.join(existing)}. "
                 "Use --force to overwrite.")

    # 1. Download
    print(f"[1/4] Downloading {ZENODO_URL}")
    try:
        download(ZENODO_URL, ZIP_PATH)
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        sys.exit(f"Download failed ({e}). Re-run the script to resume.")

    # 2. Verify checksum
    print("[2/4] Verifying MD5 checksum")
    expected = (EXPECTED_MD5 or fetch_md5_from_zenodo(ZENODO_URL)).lower()
    actual = md5sum(ZIP_PATH)
    if actual != expected:
        ZIP_PATH.unlink()
        sys.exit(f"MD5 mismatch!\n  expected: {expected}\n  got:      {actual}\n"
                 "The corrupted file was deleted. Please re-run the script.")
    print(f"  OK ({actual})")

    # 3. Extract
    print("[3/4] Extracting archive")
    tmp_dir = ROOT / ".heavy_files_extract"
    shutil.rmtree(tmp_dir, ignore_errors=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        needed = sum(info.file_size for info in zf.infolist())
        free = shutil.disk_usage(ROOT).free
        if needed > free:
            sys.exit(f"Not enough disk space: need {human(needed)}, "
                     f"have {human(free)}.")
        members = zf.infolist()
        for i, member in enumerate(members, 1):
            zf.extract(member, tmp_dir)
            print(f"\r  {i}/{len(members)} files", end="", flush=True)
    print()

    # 4. Move folders to the project root and clean up
    print("[4/4] Moving folders to project root")
    source = find_source_dir(tmp_dir)
    for name in FOLDERS:
        target = ROOT / name
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(source / name), str(target))
        print(f"  {name}/ -> {target}")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    shutil.rmtree(EXTRACT_DIR, ignore_errors=True)
    if not args.keep_zip:
        ZIP_PATH.unlink()
        print("  Removed heavy_files.zip")

    print("Done! Heavy files are installed.")


if __name__ == "__main__":
    main()
