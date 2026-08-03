# Tabular records

## Applies to

Flat or relational patient-like records: single table from schema or metadata, multi-table
schemas, a synthetic version of a real table, scaffolding rows. Single-table-from-metadata and
synthetic-from-real-data are covered, not gaps.

## Tools

| Tool | Use for | Verdict | Constraints |
| --- | --- | --- | --- |
| Faker (`github.com/joke2k/faker`) | Scaffolding: names, addresses, dates, identifiers | Use | No statistical realism, no inter-field correlation |
| Mimesis (`github.com/lk-geimfari/mimesis`) | Same as Faker, plus blood type, height, weight | Use | Same limitation; extensible with custom medical providers |
| DataSynthesizer (`github.com/DataResponsibly/DataSynthesizer`) | Bayesian-network generation where distributions matter; has differential-privacy modes | Use | Lower fidelity than SDV/synthcity on complex data; limited maintenance |
| Plaitpy (`github.com/plaitpy/plaitpy`) | YAML templates with distributions and conditional logic; encodes correlations explicitly (age ↔ condition prevalence) | Maybe | Not actively maintained — confirm before making it load-bearing |
| synthcity (`github.com/vanderschaarlab/synthcity`) | Broadest suite: many generators plus fidelity/utility/privacy metrics; static, regular and irregular time series, censored, multi-source, composite; survival and time-series healthcare plugins; scores re-identification risk and attribute inference via XGBoost or neural net | Maybe | PyTorch, heavy dependencies — flag before use. Permissive licence |
| NHSSynth (`github.com/nhsengland/NHSSynth`, P41) | VAE-based generation with differential privacy, from real seed data | Inspiration — see entry below | MIT, Python 3.11+, PyTorch, Poetry. Requires real seed data |

Not options until assessed. Ask the user before treating either as available:

- **Artificial HES data** — a reference point for artificial hospital activity data, but the audit
  records no description or link.
- **dpart** — named only as an existing tool for synthesising from real data; no link, verdict or
  setup notes recorded.

Faker and Mimesis produce no inter-field logic: nothing prevents a 3-year-old prescribed a statin.
Constrain them with the patient state.

## Inspiration entry

Read the source before reimplementing. Written from the repository on 2026-07-29. If a task needs
detail this does not cover, ask the user or fetch the URL — but the target environment may have no
outbound network, so do not make a fetch a dependency.

### NHSSynth

`github.com/nhsengland/NHSSynth` — MIT, Python 3.11+, PyTorch, Poetry (pip install also offered).
463 commits, under active development.

- **Pattern:** a variational autoencoder with differential privacy, wrapped in a modular pipeline
  where each module runs standalone via CLI or as part of a configured run, with saved parameter
  specifications for reproducibility.
- **Copy:** the config-driven reproducibility — a saved specification that regenerates a dataset
  exactly. That maps directly onto report section 4. Also the module-per-stage structure, which
  makes individual stages replaceable.
- **Substitute:** the generator itself. The VAE is not the transferable part for us; the pipeline
  discipline around it is.
- **Don't inherit:** PyTorch, the optional PyTorch CSPRNG extension for secure mode, and Poetry,
  unless running it directly.
- **Caveats:** **it requires real data** — inputs go in a `data` folder and the method fits to
  them, so it does not apply to the from-intelligence case at all. Differential privacy is a
  generation-side control, so if privacy is the binding constraint this is the class of answer,
  but DataSynthesizer offers DP modes without PyTorch. The audit's "hard to set up on FDP" is
  consistent with the PyTorch and Poetry dependencies.

## Excluded

- **SDV** — costs money.
- **synthpop** — R; avoids adding a second runtime.

## Multi-table / relational

Not a gap: SDV and synthcity handle relational schemas natively, and
splitting a single table is the simple route. SDV is excluded on cost and synthcity is
PyTorch-gated, so the practical options are synthcity with the environment flagged, or generating
a parent table and deriving children under the patient state. Confirm with the user.

## Gaps

- No easily installable generator combines high multivariate fidelity with a light dependency
  footprint. Faker/Mimesis are light and uncorrelated; DataSynthesizer is intermediate; synthcity
  buys fidelity with PyTorch.
- No tool here provides clinical plausibility. Encode it in the patient state; verify with the
  evaluation skill's clinical rules layer.

## Coherence

Tabular records are usually the spine other modalities read from. Labs must match the diagnosis,
medications must match conditions, all dates sit on the shared timeline. Generating tables from
one source and notes or signals from another loses coherence immediately.

## Report

Contributes to report sections 3 (cohort definition), 4 (tool, version, seed per table) and 6
(which fields the patient state fixed).

## Evaluation

Univariate and multivariate fidelity plus clinical rules — `synthetic-data-evaluation`,
`references/fidelity.md`. If real seed data was used, `references/privacy.md` is mandatory.
