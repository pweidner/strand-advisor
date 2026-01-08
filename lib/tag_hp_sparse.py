#!/usr/bin/env python3
import sys
import argparse
from bisect import bisect_left

def parse_cigar_ref_len(cigar: str) -> int:
    """Reference-consuming length from CIGAR (M, D, N, =, X)."""
    if cigar == "*" or cigar == "":
        return 0
    num = 0
    ref_len = 0
    for ch in cigar:
        if ch.isdigit():
            num = num * 10 + int(ch)
        else:
            if ch in ("M", "D", "N", "=", "X"):
                ref_len += num
            # I, S, H, P do not consume reference
            num = 0
    return ref_len

def load_sites_bed(path: str):
    """
    Load BED sites into dict chrom -> sorted list of 0-based starts.
    Assumes BED is 0-based, half-open, and sites are 1bp (start,end = start+1),
    but works fine for short intervals too by using starts.
    """
    sites = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 3:
                continue
            chrom = fields[0]
            start = int(fields[1])
            sites.setdefault(chrom, []).append(start)
    for chrom in sites:
        sites[chrom].sort()
    return sites

def has_overlap(starts_sorted, aln_start0: int, aln_end0: int) -> bool:
    """Return True if any site start is within [aln_start0, aln_end0)."""
    i = bisect_left(starts_sorted, aln_start0)
    return i < len(starts_sorted) and starts_sorted[i] < aln_end0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", required=True, help="BED file of informative sites (0-based).")
    ap.add_argument("--hp", required=True, type=int, choices=[1,2], help="HP tag value to add when overlapping.")
    args = ap.parse_args()

    sites = load_sites_bed(args.sites)

    out = sys.stdout
    for line in sys.stdin:
        if line.startswith("@"):
            out.write(line)
            continue

        line = line.rstrip("\n")
        fields = line.split("\t")
        if len(fields) < 11:
            out.write(line + "\n")
            continue

        rname = fields[2]
        if rname == "*" or rname not in sites:
            out.write(line + "\n")
            continue

        pos1 = int(fields[3])  # 1-based
        cigar = fields[5]
        aln_start0 = pos1 - 1
        ref_len = parse_cigar_ref_len(cigar)
        aln_end0 = aln_start0 + ref_len if ref_len > 0 else aln_start0

        if aln_end0 <= aln_start0:
            out.write(line + "\n")
            continue

        if has_overlap(sites[rname], aln_start0, aln_end0):
            # add HP tag only if not already present
            if not any(t.startswith("HP:i:") for t in fields[11:]):
                out.write(line + f"\tHP:i:{args.hp}\n")
            else:
                out.write(line + "\n")
        else:
            out.write(line + "\n")

if __name__ == "__main__":
    main()
