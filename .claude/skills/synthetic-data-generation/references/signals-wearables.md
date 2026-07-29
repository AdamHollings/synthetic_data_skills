# Physiological signals and wearables

## Applies to

ECG (including 12-lead), PPG, respiration, EDA, EMG, EEG, heart-rate traces, accelerometry and
phone passive sensing, PSG montages, Doppler waveforms. Scored as a small gap: strong for common
waveforms, thin at the edges listed below.

## Tools

| Tool | Use for | Verdict | Constraints |
| --- | --- | --- | --- |
| NeuroKit2 (`github.com/neuropsychology/NeuroKit`) | ECG (incl. 12-lead), PPG, respiration (RSP), EDA, EMG. Also processing and feature extraction | Use | EEG present but less developed than ECG/PPG |
| MNE-Python (`mne.tools/stable`) | EEG/MEG with realistic source models | Maybe | Not a generator per se; steeper learning curve. Use when EEG realism is load-bearing |
| PySim | Simulations based on differential equations: mechanisms, pharmacokinetics, progression driving a measurement | Use | Not health-specific, not a waveform generator |
| SKDH (`github.com/PfizerRD/scikit-digital-health`) | Derives digital biomarkers (gait, sit-to-stand, activity, sleep) from wearable accelerometer data. Use as a realism check on synthetic output | Maybe | Analysis toolkit, not a generator — must be paired with a generation step |
| synthcity time-series plugins | Irregular or censored numeric series that are not waveforms | Maybe | PyTorch — see `tabular.md` |

NeuroKit2 both generates and processes, giving an internal consistency check: generate at a target
heart rate, run its own processing over the result, confirm derived features match.

Prefer NeuroKit2 for anything it simulates; use PySim when the requirement is a mechanism rather
than a realistic-looking trace, or when a signal must follow a story arc.

## Excluded

- **Mandrova** (`github.com/makinarocks/Mandrova`) — generic sensor generator (stationary, non-stationary or
  custom schemes via config), flexible for arbitrary streams such as bed pressure mats or room
  sensors, not health-specific. Unmaintained since ~2019. Raise with the user before considering
  it for a non-clinical sensor stream.

## Gaps

- EEG weaker than ECG/PPG; use MNE where it matters.
- **PSG**: no single tool produces a coherent multi-channel sleep montage. Independently generated
  channels will not agree with each other or with a sleep-stage label. Flag before promising sleep
  data.
- **Doppler and ultrasound waveforms**: unaddressed by any assessed asset.
- **Phone / mHealth passive sensing**: thin. SKDH processes wearable data but does not generate it.
  Expect to write the generator against an activity/sleep pattern in the patient state, then
  validate with SKDH.

## Coherence

- Drive generation parameters from the patient state, not defaults. Heart rate, HRV, respiratory
  rate and rhythm follow from conditions, medications (a beta-blocker changes the heart rate to
  generate), age and fitness.
- If the pathway records deterioration between two encounters, signals at those encounters must
  differ in the corresponding direction.
- Attach signals to pathway events (`healthcare-ehr.md`) with the event timestamp.
- Channels generated for the same moment (ECG, PPG, respiration) share the same underlying cardiac
  and respiratory timing; do not draw them independently.

## Report

Contributes to report sections 4 (tool, version, seed and physiological parameters per signal) and
6 (which patient-state fields set those parameters).

## Evaluation

Round-trip through a processing library — NeuroKit2 feature extraction, SKDH for accelerometry —
and compare derived features against what the patient state implies. Distributional and
cross-modal checks: `synthetic-data-evaluation`, `references/fidelity.md`.
