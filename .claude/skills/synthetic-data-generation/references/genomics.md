# Genomics and omics

## Applies to

Genotypes and variants (VCF), population structure, gene expression and regulatory dynamics, other
omics layers. Coverage is partial: variants solid, expression workable, several layers with little
tooling.

Determine first whether the PoC needs variants (genotype, VCF) or expression (what genes are
doing). They route to different tools.

## Tools

| Tool | Use for | Verdict | Constraints |
| --- | --- | --- | --- |
| HaploDynamics (`github.com/remytuyeras/HaploDynamics`) | VCF genotype data from scratch, no input files; parameters for population, linkage disequilibrium, rare mutation rates | Use | Purpose-built for quick VCF benchmarking data |
| msprime (`github.com/tskit-dev/msprime`) | Coalescent simulation of ancestry and genetic variation at population scale; tree-sequence output | Use, after evaluation | Audit records that it needs to be understood better. Steeper than HaploDynamics. Do not commit to msprime deliverables before working through the manual |
| stdpopsim (`github.com/popsim-consortium/stdpopsim`) | Standardised, published demographic models (human and other species) running on msprime or SLiM | Use, after evaluation | Same "understand better" caveat. SLiM is a separate non-Python simulator — check which backend a model needs before assuming pip is sufficient |
| GeneSNAKE (bioRxiv `biorxiv.org/content/10.1101/2025.11.10.685583v1`) | Gene regulatory networks and perturbation-induced expression data for benchmarking | Maybe | Published November 2025; maturity and packaging unproven. Flag its newness before depending on it |

HaploDynamics is seed-free, which matters here: it generates from parameters rather than fitting to
real data. See `from-intelligence.md`.

## Excluded

- **Hapnest** — ruled out on approach. Its published dataset remains usable as a comparator:
  1,008,000 individuals, nine traits, 6.8 million common variants, EBI BioStudies `ebi.ac.uk/biostudies/studies/S-BSST936`.

## Gaps

- Variants are solid; other layers thin out quickly.
- **RNA-seq and single-cell**: workable but usually require seed data. The audit names scReadSim
  and simATAC in passing, with no assessment, links or setup notes. If the project has no real
  omics data, these may be unusable.
- **Proteomics, metabolomics, epigenomics/methylation, microbiome**: little dedicated tooling, none
  in the audit. Do not promise these modalities.
- **Cross-omics coherence** is active research. Generating a genotype and an expression profile
  consistent with each other and with the phenotype is unsolved.

## Coherence

- The genotype must support the phenotype in the patient state, and the ancestry implied by the
  demographics.
- Population parameters (ancestry, LD structure) come from the cohort definition, not tool
  defaults.
- Genomics has no timeline: a genotype is fixed for life, so attach it to the patient rather than
  an encounter. Expression data is time- and state-dependent and tracks the story arc.
- Where a PoC links variants to outcomes, assign variants from the patient state rather than
  deriving state from randomly generated variants, or the demonstrated association is an artefact.

## Report

Contributes to report sections 4 (tool, version, seed, population parameters) and 6
(genotype–phenotype links asserted).

## Evaluation

Genotype-versus-phenotype consistency belongs in the clinical rules layer —
`synthetic-data-evaluation`, `references/fidelity.md`. Genomic data is highly identifying: if it
may leave the environment, `references/privacy.md` is mandatory.
