# strand-advisor

**strand-advisor** is a command-line tool for generating *ground-truth Strand-seq datasets* for benchmarking structural variant (SV) callers.

It wraps **VISOR (HACk + SHORtS)** with additional logic to:
- simulate Strand-seq inheritance states (WW / WC / CW / CC)
- generate negative control cells (`--refcells`)
- apply *realistic sparse haplotagging* using SNP-site overlap
- keep genome truth (SVs) cleanly separated from technical annotations (HP tags)

The tool is designed for **HPC usage** and produces fully reproducible run outputs.

---

## Conceptual pipeline

1. **Truth genomes (SV-only)** are generated upstream using `VISOR HACk`
2. **Strand-seq reads** are simulated using `VISOR SHORtS`
3. **Inheritance states** are assigned per cell and chromosome
4. **Sparse haplotags** are added post hoc based on downsampled SNP sites
5. Final BAMs + truth metadata are written to a run-specific output directory

SNPs are *not* baked into the simulated genome; haplotags are treated as a technical layer.

---

## Requirements

- VISOR (v1.1.3 tested)
- samtools
- awk, shuf
- Python 3 (for haplotagging helper)

---

## Required inputs

### 1. Reference FASTA
Set via environment variable:
```bash
export REF_FASTA=/path/to/GRCh38_full_analysis_set_plus_decoy_hla.fa
```
