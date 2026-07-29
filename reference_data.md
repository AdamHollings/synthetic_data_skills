Objective. Turn a scattered set of assets into one modular, agent-callable data capability covering the modalities the use-cases need.



 - Map tools available to us: 

NHSE Assets

These are assets developed by us which could be re-used.

Asset	Description	Code Link	Issues / Considerations	Use?	Added? (Date + Name)
NHSSynth	Generates useful synthetic data.	nhsengland/NHSSynth: Package to accompany P41	Could be hard to set up, particularly on FDP.	
Yes - As inspiration



SynPathD	A library for generating synthetic electronic health records in FHIR v4 format using agent-based modeling to simulate patient pathways.	nhsx/SynPath: Proof Of Concept - Open Patient Pathway Generator using and an agent based approach	Could be hard to set up, particularly on FDP.	Yes - As inspiration	
PrivFingerprint	Scores the privacy risk of free text data.	nhsengland/privfp-experiments: Exploration and experiment repository for extending privfp-poc	PoC needed to run on WSL due to using Julia and OpenJDK. May be hard to transfer exactly onto FDP.	Yes - As inspiration	
SCN	Creates synthetic patient pathways and corresponding clinical notes.	nhsengland/synthetic_clinical_notes: LLM pipeline to generate synthetic patient pathways, with corresponding clinical notes.	Easy to set up on FDP.	Yes - As inspiration	
PrivacyLeakage	 Investigating Privacy Risks and Mitigations in Healthcare Language Models	nhsengland/priv-lm-health-extended: Continuation of the work Investigating Privacy Risks and Mitigations in Healthcare Language Models - NHS England PhD Internship Project	Could be hard to set up, particularly on FDP.	Yes - As inspiration	
SAS - Synthetic Adversarial Suite	Toolbox for Adversarial Privacy Auditing of Synthetic Data	alan-turing-institute/tapas	
Yes - As inspiration	
NDRS Pseudonomiser	


Yes - As inspiration	
Synthetic Panels	Generates a synthetic panel of respondents to respond to messaging.	nhsengland/synthetic_panels	Still WIP and unproved	Yes - As inspiration	
SyntheaUK	SWPC UK Synthea Version	nhsengland/swpc_synthea: SWPC UK Synthea Version. Documentation can be found:	Could be hard to set up, particularly on FDP.	Yes - As inspiration	
Artificial HES data	
Artificial data pilot - NHS England Digital	
Yes - As inspiration	
DLH_007: Synthetic Data for Data Linkage Evaluation	Framework for generating synthetic linked datasets to evaluate and benchmark data linkage methods without real patient data.	Confluence: DLH_007	Active research project in the Data Linkage Hub, might not be ready yet. 	Unsure	


Open-source Assets

These are assets not developed by us, but open and useful for the AI incubator.

Asset	Description	Code / Doc Link	Issues / Considerations	Use?	Added? (Date + Name)
Synthea	open-source, synthetic patient generator that models the medical history of synthetic patients	Synthea	We have synthea uk.	No	
PySim	PySim is a python extension that enables the user to create simulations based on differential equations.	Tutorial — PySim 2.4.0 documentation	A python library so easy for an agent to use.
Possibly set up as a Claude Skill.	Yes - Claude Skill with detailed explanation and code examples.	
Python Faker	 Faker is a Python package that generates fake data for yo. Whether you need to bootstrap your database, create good-looking XML documents, fill-in your persistence to stress test it, or anonymize data taken from a production service, Faker is for you.	 joke2k/faker: Faker is a Python package that generates fake data for you. 
Welcome to Faker’s documentation! — Faker 40.31.0 documentation	
A python library so easy for an agent to use.

Possibly set up as a Claude Skill.

No statistical realism or correlations between fields; great for scaffolding, weak for clinically plausible records

Yes - Claude Skill with detailed explanation and code examples.



Mimesis	Faker alternative — faster, typed providers, includes basic health attributes (blood type, height, weight)	https://github.com/lk-geimfari/mimesis	
A python library so easy for an agent to use.

Possibly set up as a Claude Skill.

Same limitation as Faker (no inter-field logic); easy to extend with custom medical providers

Yes - Claude Skill with detailed explanation and codeexamples.



Plaitpy	Define generators in YAML templates with distributions and conditional logic	https://github.com/plaitpy/plaitpy	
Lets you encode correlations (e.g. age ↔ condition prevalence); project is not very actively maintained

Maybe - Claude Skill with detailed explanation and code examples.

Risk: Not well maintained.



Synth Gauge	SynthGauge is a Python library to evaluate synthetically generated data. 
The library provides a range of metrics and visualisations for assessing and comparing distributions of features between real and synthetic data.

At its core is the Evaluator class, which provides a consistent interface for applying a range of metrics to the data. By creating several Evaluator instances, you can easily evaluate synthetic data generated from a range of methods in a consistent and comparable manner.

e.g. make blood types.

Welcome to the SynthGauge Documentation — SynthGauge 2.1.0 documentation	
A python library so easy for an agent to use.

Possibly set up as a Claude Skill.

Yes - Claude Skill with detailed explanation and code examples.



Synthetic Data Vault	The Synthetic Data Vault (SDV) is a Python library designed to be your one-stop shop for creating tabular synthetic data.	Welcome to the SDV! | Synthetic Data Vault	Cost money!	No - money.	
synthcity	
A library for generating and evaluating synthetic tabular data. Aimed at use cases in ML fairness, privacy, and data augmentation. It covers a range of tabular modalities: static data, regular and irregular time series, data with censoring, multi-source and composite data. 
It scores re-identification risk from the synthetic set and tests whether sensitive attributes can be predicted from quasi-identifiers using XGBoost or a neural net. 
Most comprehensive open-source suite: many generation methods plus fidelity, utility, and privacy evaluation metrics; healthcare plugins (survival, time series)

Generators — synthcity documentation

https://github.com/vanderschaarlab/synthcity

Steeper learning curve and heavier dependencies (PyTorch); permissive license	Maybe - pytorch might make this hard on the FDP. 	
Synth Pop	The synthpop package makes a synthetic version of individual-level data	synthpop - Get started	Uses R so may not want to use for now.	No - R	
DataSynthesizer	Lightweight Bayesian-network generator with differential privacy modes
https://github.com/DataResponsibly/DataSynthesizer	Simple and fast, but lower fidelity than SDV/Synthcity for complex data; limited maintenance	Yes - Claude Skill with detailed explanation and code examples.	
Hapnest	A novel approach for efficiently generating diverse individual-level genotypic and phenotypic data	
HAPNEST: efficient, large-scale generation and evaluation of synthetic datasets for genotypes and phenotypes | Bioinformatics | Oxford Academic



A synthetic dataset of 1 008 000 individuals and nine traits for 6.8 million common variants is available at https://www.ebi.ac.uk/biostudies/studies/S-BSST936. 


No - approach.	
medigan	
Library of pre-trained GANs for synthetic medical images (mammography, brain MRI, chest X-ray, endoscopy, cardiac MRI)

RichardObi/medigan: medigan - A Python Library of Pretrained Generative Models for Medical Image Synthesis	Imaging only; GPU recommended; limited to the modalities its pre-trained models cover	Maybe - GPU needed. Need to work out how to load and run large models on the FDP.	
Asset to create medical / image data (e.g. MonAI - chest X-rays)	
Lots of chest X-ray assets available. 

RoentMod: a synthetic chest X-ray modification model to identify and correct image interpretation model shortcuts | npj Digital Medicine	
Maybe, need plan for using large models on FDP.	
Asset to create voice data / transcripts	
Many text to speech models on Hugging face
Datasets exist to help make synthetic data (with methodology) - NoteChat
Text-to-Speech Models – Hugging Face
NoteChat: A Dataset of Synthetic Patient-Physician Conversations Conditioned on Clinical Notes - ACL Anthology
if using HuggingFace models, need to learn to integrate them into the FDP. 
Maybe, need plan for using large models on FDP.	
Datasets (MIMIC)	
MIMIC-IV v3.1



NeuroKit2	Simulates realistic ECG (including 12-lead), PPG, respiration (RSP), EDA, and EMG signals with a couple lines of code; also handles processing/feature extraction	
https://github.com/neuropsychology/NeuroKit

Example signals simulation: Simulate Artificial Physiological Signals — NeuroKit2 0.2.13.dev214 documentation

The most mature, easy-to-implement option for physiological waveforms; EEG support is present but less developed than ECG/PPG — pair with MNE for EEG-heavy work	Yes - Claude Skill with detailed explanation and code examples.	
MNE-Python	Not a generator per se, but widely used for simulating and processing EEG/MEG signals with realistic source models	
https://mne.tools/stable/index.html

Steeper learning curve; better suited if you need neurologically grounded EEG rather than quick mock signals	Maybe - not a generator.	
Mandrova	Generic sensor data generator — stationary, non-stationary, or fully custom signal schemes defined via simple config	
https://github.com/makinarocks/Mandrova

Lightweight and flexible for arbitrary sensor streams (e.g. bed pressure mats, room sensors); not health-specific, and not actively maintained since ~2019	No - not maintained	
SciKit Digital Health (SKDH)	Processes and derives digital biomarkers (gait, sit-to-stand, activity, sleep) from wearable accelerometer data; useful as the "realism check" for synthetic wearable output	
https://github.com/PfizerRD/scikit-digital-health

Primarily an analysis/processing toolkit, not a generator — pair it with a GAN/simulation step to validate that synthetic wearable signals look plausible	Maybe	
Bark	Expressive generative audio model that can produce speech plus non-speech sounds (coughs, sighs, pauses) — useful for realistic clinical audio	
https://github.com/suno-ai/bark

Good for adding non-speech clinical audio events; slower inference, GPU strongly recommended	

pyttsx3 / eSpeak	Simple offline TTS, no deep learning required, few lines of code	
Using pyttsx3 — pyttsx3 2.6 documentation

Fast and dependency-light, but robotic voice quality — fine for placeholder audio, not for realism-sensitive PoCs	

SDialog	MIT-licensed toolkit for generating persona-driven multi-agent dialogues (e.g. Doctor/Patient personas) with structured JSON export, and can synthesize matching audio with room-acoustics simulation	
https://sdialog.github.io/

Looks really good!	Yes - should be able to link to any LLM we can use.	
NoteChat-style multi-agent LLM pipelines	Not a pip-installable library, but a well-documented pattern: use cooperative LLM agents playing "doctor" and "patient" roles, conditioned on clinical notes, to generate realistic dialogue transcripts	
https://arxiv.org/abs/2310.15959

This is an architecture you'd implement with your own agent framework (e.g. Claude agents) rather than a library — very well suited to "agentic PoC generator" since it's LLM-driven role-play	Yes - inspiration.	
HaploDynamics	Generates realistic VCF (variant call format) genotype data from scratch — no input files needed; lets you specify population, linkage disequilibrium levels, and rare mutation rates	
https://github.com/remytuyeras/HaploDynamics

Purpose-built for quick VCF benchmarking data; good "Faker equivalent" for genomics — easy to implement, few lines of code	Yes - should be able to link to any LLM we can use.	
msprime	Coalescent (backwards-in-time) simulator for population genetics; generates ancestry and genetic variation data at scale via a simple Python API, storing results as efficient tree sequences	
tskit-dev/msprime: Simulate ARGs and genomic sequence data using population genetic models

Introduction — Msprime manual

The standard for population-scale genomic simulation (used to simulate ~1.4M genomes); steeper learning curve than HaploDynamics, but far more powerful for demographic realism	Yes - Need to understand better.	
stdpopsim	Community-maintained library of standardized, pre-built population genetic models (human and other species) that run on top of msprime or SLiM	
https://github.com/popsim-consortium/stdpopsim

Great if you want biologically validated, published demographic models rather than building your own from scratch; adds a dependency on msprime/SLiM	Yes - Need to understand better.	
GeneSNAKE	Generates biologically realistic gene regulatory networks (GRNs) and corresponding perturbation-induced expression data for benchmarking	
https://www.biorxiv.org/content/10.1101/2025.11.10.685583v1

Very new (Nov 2025); useful if your PoC involves gene expression/regulatory dynamics rather than just genotype data	Maybe - Yes - Need to understand better.	


Considerations

Lots of our tools are out of date
Do we let tools inspire claude, or does it actively use the tools?
How do we let claude interact with privacy tech without ingesting real data? e.g. If PrivFP identifies a data collision and claude sees the output - is this a data breach?
Decision - inspiration approach


 - Map the longlist's data/modality requirements against current capability and record the gaps (which modalities/generation capabilities are missing).

Modality Gaps

Asset	Gap Assessment
single-table from meta data	Not a gap
multi-table from meta data	Split a single table, can be more complex — but SDV and Synthcity both handle relational schemas natively, so tooling exists.
create a synthetic version from real data. 	Lots of synthetic tools already (SDV, Synthcity, DataSynthesizer, dpart)
create a synthetic version from intelligence. 	Gap: Will need research and evaluate to asses whether a tool 
longitudinal data - sequencing or time series.	Synthea/SyntheaUK generate longitudinal EHR event sequences natively; SynPath's agent-based pathway modelling is a strong UK-specific reference. TimeGAN (ydata-synthetic) and Synthcity's time-series plugins cover generic tabular series. Partial Gap: turning a cross-sectional schema into a temporally coherent multi-visit trajectory
modaility - text (semi-structred and unstructured) hand-written vs computer written. 	Gap: Handwritten / scanned in letters.
images -> video. 
images (CT, MRI, pathology, histologoy, plus dicom	Significant Gap: Whilst lots of image generation models exist for various medical image types, generating videos is incredibly computationally expensive. Ease of image generation on the FDP is still an unknown. 
signals (e.g. heartrate monitor) PSG signals, wearables, phone. e-health and m-health, eeg, ecg, dopler waveforms.	Small gap: NeuroKit2 strong for ECG/PPG/EDA/EMG/respiration; EEG weaker (lean on MNE). PSG remains a specific gap (no single tool for a coherent multi-channel sleep montage). Doppler/ultrasound waveforms essentially unaddressed. Phone/mHealth passive-sensing generation still thin (SKDH processes but doesn't generate)
audio (speech) 	Reasonably covered for normal speech (Coqui, Bark, pyttsx3; SDialog for dialogue). Gap remains: pathological/abnormal speech (dysarthria, stroke, Parkinsonian, pediatric) for diagnostic-from-speech PoCs
genomics - lots of omics.	Partial coverage, unchanged. DNA/variant solid (HaploDynamics, msprime, stdpopsim); RNA-seq/single-cell decent but often needs seed data (scReadSim, simATAC). Gaps: proteomics, metabolomics, epigenomics/methylation, microbiome have little dedicated tooling; cross-omics biological coherence remains active research
Privacy / disclosure risk of synthetic output	No large gap du to NHS tooling. Gap with image data.
Other Considerations:

1. Cross-modal patient coherence is the biggest gap
Every tool we've covered generates its modality in isolation. Synthea gives you a patient, NeuroKit gives you an ECG, HaploDynamics gives you a VCF, Coqui gives you audio — but nothing off-the-shelf guarantees the diabetic patient's genomics, wearable trends, lab values, and clinical note all tell the same story. There is a research precedent worth knowing about: the "Coherent Data Set" project layers structured Synthea data into a longitudinal patient-level EHR that merges ECGs, MRI imaging, clinical notes, and genomic data using standard FHIR resources whenever a synthetic patient experiences a relevant event. But it's narrowly cardiovascular-disease-focused and more a research artifact than a general-purpose toolkit — you'd need to replicate its approach rather than pip-install it. More broadly, recent generative diffusion approaches like "Coherent Denoising" are being built specifically to fill in missing modalities for a patient in a way that stays consistent with what's already known about them, which tells you this is still an active research problem, not a solved one.

2. Longitudinal/temporal realism
Most generators produce a snapshot or independent draws, not a trajectory. A real disease has a story arc — labs drift, medications change, wearable signals shift as a condition progresses or resolves. Synthea is the exception (it's built for this), but stitch a genomics tool, a signal simulator, and an LLM-based dialogue generator together and you'll likely get three independent timelines that don't agree with each other.



Suggestions:

Using many of our past tools/epos will be difficult due to the many different set-ups and systems needed. Particularly if on the FDP. We should instead incorportate them as inspiration for Claude, rather than working tools.
Some open source libraries (e.g. Faker) should be integrated as tools.


Evaluation Considerations: 

We want our PoC generator to evaluate the quality of the synthetic data it is generating. It should asses the following axes:

Fidelity — does it look like real data? This splits into levels. Univariate (do individual column distributions match?) is easy and table-stakes. Multivariate (are correlations and joint distributions preserved?) is where most tools are weak and where your coherence problem shows up as a number. For a healthcare generator specifically, statistical fidelity isn't enough — you also need clinical fidelity: does the data obey domain logic a clinician would catch instantly (no pregnant males, lab values consistent with the stated diagnosis, plausible medication-condition pairings)? That last one rarely has an off-the-shelf metric and is usually a rules-based sanity layer you write yourself.

Utility — is it useful for the task? The gold standard is TSTR (Train on Synthetic, Test on Real): train a model on your synthetic data, evaluate it on held-out real data, and compare to the same model trained on real data. If synthetic-trained performance is close, the data carries the signal that matters. This is more meaningful than any distributional metric because it measures fitness for the actual downstream purpose — and for a PoC generator, "does a model trained on this behave sensibly" is often the real question anyway. The lighter cousin is "does an ML model do about as well," and the honest check is whether a classifier can distinguish synthetic from real (if it can trivially, fidelity is poor; if it can't at all, watch for the privacy problem below).

Privacy — does it leak? Critically, high fidelity and strong privacy are in tension: data that perfectly reproduces real records is both maximally faithful and maximally leaky. This is exactly what the NHS/Turing tools in your table address — TAPAS/SAS for adversarial attacks (can an attacker infer real records from synthetic ones?), PrivFingerprint for free-text leakage. Naive checks like "is any synthetic row identical to a real row" are necessary but nowhere near sufficient — membership-inference and attribute-inference attacks are the real test. For healthcare this axis is non-negotiable, not optional polish.

Suggestion:

Build evaluation in as a standard report per generated dataset