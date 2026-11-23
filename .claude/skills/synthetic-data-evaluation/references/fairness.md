# Fairness

Synthetic data can perpetuate, amplify, or flatten real-world health disparities. The default is
faithful reproduction: the evaluation measures whether disparities match the reference, not
whether they exist. Fairness-adjusted generation (deliberately rebalancing outcomes) is opt-in;
when used, the evaluation detects and reports it rather than flagging it as an error.

## Contents

- Philosophy
- Protected characteristics
- Medium fidelity checks (advisory)
- High fidelity checks (mandatory)
- Fairness-adjusted generation
- RAG bands
- Tools
- Reference sources

## Philosophy

Synthetic data should reproduce real-world disparities faithfully. A stillbirth rate ratio of
2.3× for Black vs White women (MBRRACE-UK) is a fact about the healthcare system. Flattening it
produces unrealistic data; amplifying it compounds the harm. The evaluation's job is to detect
deviation from published patterns in either direction.

Fairness-adjusted generation — deliberately rebalancing outcomes to reduce disparities — is a
separate, opt-in mode. When applied, the evaluation should report it, still check plausibility
per subgroup, and note that disparity ratios differ from published stats by design.

## Protected characteristics

Standard set for NHS datasets, covering Equality Act 2010 characteristics where the dataset
collects them:

| Characteristic | Typical field | Published stats available? |
| --- | --- | --- |
| Ethnicity | EthnicCategory, Ethnicity | Yes — NHS Maternity Statistics, MBRRACE-UK, HES |
| Age band | Age at event | Yes — most NHS publications |
| Sex | PersonPhenotypicSex, Gender | Yes — most NHS publications |
| Deprivation quintile | IMD decile/quintile (from postcode) | Yes — PHE, OHID Fingertips |
| Geography | Region, ICB, provider | Yes — regional breakdowns common |
| Disability | Disability status | Sparse — dataset-dependent |
| Religion | ReligionCode | Sparse — dataset-dependent |

Not all datasets contain all characteristics. The dataset reference file (e.g. msds.md) should
note which are available. Check only what the dataset contains — do not penalise absence of a
field the dataset does not collect.

## Medium fidelity checks (advisory)

Compare against published stats, not real microdata. Advisory at Medium — record whether each
was run or skipped, and why.

### 1. Representation adequacy

Are protected group proportions correct vs published demographics?

| Check | Method | Reference | Good value |
| --- | --- | --- | --- |
| Group prevalence | Hellinger distance: synthetic vs published demographic distribution | Published demographics (ONS, NHS Maternity Stats) | Same bands as L1: < 0.1 good, > 0.3 investigate |

A generator that undersamples a minority group produces unrealistic data for downstream use.

### 2. Outcome disparity preservation

For key outcomes, compute the disparity ratio (rate in group A / rate in group B) in both
synthetic and published reference.

| Check | Method | Reference | Good value |
| --- | --- | --- | --- |
| Disparity ratio | Ratio of outcome rates across groups, synthetic vs published | Published outcome disparities (MBRRACE-UK, NHS stats by ethnicity) | Synthetic ratio within 20% of published ratio |

Example: MBRRACE-UK reports 2.3× stillbirth rate ratio Black vs White. Synthetic should show
roughly 1.8–2.8.

### 3. Per-subgroup distribution check

Run L1 metrics (Hellinger, KS) within each protected group for key outcome fields, not just
overall. A generator can achieve overall Hellinger 0.05 while being 0.4 within a minority
subgroup — the minority distribution is wrong but invisible in the aggregate.

Advisory at Medium (computationally expensive on large datasets). Mandatory at High.

### 4. Intersectional coverage

Generators can produce correct marginals but collapse rare intersections to zero records.

| Check | Method | Good value |
| --- | --- | --- |
| Intersection presence | Count records for key 2-way and 3-way intersections of protected characteristics | > 0 records per intersection that should exist given cohort size |
| Intersection plausibility | Record counts vs marginal probabilities | Within order of magnitude of expected count |

Example for MSDS with 5,000 records:

| Intersection (Ethnicity × Age band) | Expected % | Expected count | Flag if |
| --- | --- | --- | --- |
| White British, 25–29 | ~25% | ~1,250 | < 500 |
| Black Caribbean, 30–34 | ~1.5% | ~75 | 0 records |
| Bangladeshi, 20–24 | ~0.8% | ~40 | 0 records |
| Mixed White/Black, 35–39 | ~0.3% | ~15 | 0 records |

### 5. Conditional relationship equity

Do key conditional relationships from the sampling chain work correctly within each subgroup?
Compare per-subgroup conditional distributions using Hellinger or Cramér's V against published
subgroup-specific rates where available.

Example: BMI→GDM risk should differ by ethnicity (higher baseline for South Asian women). If the
generator applies a single global rate, the conditional relationship is clinically wrong for
non-majority groups.

### 6. Missingness equity

Cross-reference — covered in `fidelity.md` missingness section ("Fairness interaction" row). That
check assesses whether missingness rates correlate with protected characteristics. This entry
exists so the checklist is complete; the method and thresholds live in fidelity.md.

## High fidelity checks (mandatory)

All Medium checks become mandatory and are validated against real microdata rather than published
stats. Plus:

### 7. Amplification check

Are disparities wider in synthetic than in real? A generator can amplify real disparities if
conditional sampling chains overfit to majority-group patterns.

| Check | Method | Good value |
| --- | --- | --- |
| Amplification ratio | (Synthetic disparity ratio) / (Real disparity ratio) | 0.8–1.2: preserved, not amplified or flattened |

Amplification ratio > 1.2: generator is amplifying disparities. < 0.8: flattening them. Both
are problems unless fairness-adjusted generation was requested.

### 8. Downstream fairness (TSTR disaggregated)

When TSTR runs (see `utility.md`), disaggregate by protected group. Compare performance across
groups for the synthetic-trained model vs the real-trained model.

| Check | Method | Good value |
| --- | --- | --- |
| Performance gap | Per-group AUC gap: (AUC_majority − AUC_minority), synthetic-trained vs real-trained | Synthetic-trained gap no wider than real-trained gap |
| Equalized odds gap | Difference in TPR and FPR across groups | Synthetic-trained gap ≤ real-trained gap |

If the synthetic-trained model has a larger fairness gap than the real-trained model, the
synthetic data has amplified bias.

### 9. Per-subgroup distribution validation

Full per-group Hellinger/KS against real microdata for all outcome fields × all available
protected characteristics. Same bands as L1 but computed within each subgroup.

### 10. Subgroup mode collapse

Compute Gower nearest-neighbour distances within each protected subgroup. A minority subgroup
with tighter Gower distances than the majority has fewer distinct records — the generator
collapsed diversity for that group.

## Fairness-adjusted generation

When the user opts into fairness-adjusted generation, the evaluation should:

- Report that fairness adjustment was applied (REPORT.md section 7)
- Compute disparity ratios and note they differ from published stats by design
- Still check per-subgroup distributions for plausibility — adjusted is not arbitrary
- Still check intersectional coverage and mode collapse

## RAG bands

| Check | Green | Amber | Red |
| --- | --- | --- | --- |
| Representation (Hellinger) | < 0.1 | 0.1–0.3 | > 0.3 |
| Disparity ratio preservation | Within 20% of published | 20–50% off | > 50% off or reversed |
| Per-subgroup Hellinger/KS | Same bands as L1 | Same bands as L1 | Same bands as L1 |
| Intersectional coverage | All expected intersections present | Some missing but marginals correct | Key intersections missing |
| Amplification ratio (High) | 0.8–1.2 | 0.5–0.8 or 1.2–1.5 | < 0.5 or > 1.5 |
| Downstream fairness gap (High) | Synthetic gap ≤ real gap | Synthetic gap 1–1.5× real gap | Synthetic gap > 1.5× real gap |

## Tools

No dedicated fairness tool is sanctioned. The checks use the same metrics as fidelity (Hellinger,
KS, Cramér's V, Gower) applied per subgroup. synthcity includes ML fairness metrics but carries
a PyTorch dependency — same caveat as for its other features.

## Reference sources for disparity data

| Source | Coverage | Use for |
| --- | --- | --- |
| MBRRACE-UK | Perinatal outcomes by ethnicity | Maternity outcome disparities — the primary source |
| NHS Maternity Statistics | Demographics and outcomes by ethnicity, age, region | Representation and outcome rates |
| OHID Fingertips | Health inequalities by deprivation, ethnicity, region | Deprivation-linked outcomes |
| ONS | Population demographics by ethnicity, age, geography | Demographic representation |
| PHE / UKHSA | Health outcomes by deprivation quintile | Deprivation-linked health disparities |
