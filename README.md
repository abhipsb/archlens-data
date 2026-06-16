# archlens-data

This repository contains the canonical data definitions and scoring primitives used by ArchLens for architecture assessments grounded in ATAM-style scenarios and SARM-aligned questions.

Its main value for replication is consistency: if you use these files unchanged, you can reproduce the same scenario-to-question coverage and the same weighted scoring behavior used by ArchLens.

## Why This Repo Matters for Replication

To replicate ArchLens faithfully, you need three things:

1. A stable question bank with quality-attribute metadata and severity weights.
2. A stable set of architecture scenarios with importance labels and acceptance criteria.
3. A stable mapping between scenarios and questions (including per-link weight).

This repository provides all three in versionable CSV files, plus Python constants and ORM models that define how the data is interpreted at runtime.

## Repository Contents and Importance

### Data files (primary replication artifacts)

- `sarm_questions.csv`
	- Purpose: Canonical question bank.
	- Key columns: `question_key`, `text`, `quality_attribute`, `weight_label`, `category`.
	- Why important: This determines what is asked during assessment and how each question contributes to attribute-level scores.

- `atam_scenarios.csv`
	- Purpose: Canonical ATAM-like scenario set.
	- Key columns: `scenario_id`, `attribute`, `importance`, `scenario_text`, `acceptance_criteria`.
	- Why important: This defines the stress cases and quality concerns used to structure evaluation and utility-tree reasoning.

- `scenario_question_mappings.csv`
	- Purpose: Join table linking scenarios to relevant questions.
	- Key columns: `scenario_id`, `question_key`, `tag`, `weight`.
	- Why important: This captures traceability and weighting between scenario intent and question evidence. Changing this file changes coverage and weighted outcomes.

### Code files (interpretation and schema contracts)

- `constants.py`
	- Purpose: Shared scoring constants and trade-off rule effects.
	- Includes:
		- `COMPLIANCE_SCORE` mapping (`Yes`, `Partial`, `No`, `NotApplicable`).
		- `WEIGHT_MAP` severity multipliers (`Catastrophic` to `Negligible`).
		- `calculate_scores(...)` weighted aggregation logic.
		- `TRADEOFF_RULES` quality-attribute impact templates for selected decisions.
	- Why important: This file defines the exact math and decision-impact assumptions. Reproducibility depends on using these mappings unchanged.

- `models.py`
	- Purpose: SQLAlchemy data model for persisting assessments and templates.
	- Defines entities for:
		- Projects, assessments, and per-assessment question responses.
		- Scenario templates and selected assessment scenarios.
		- Scenario-question mappings and scenario-question association instances.
		- Utility tree nodes and business-driver links.
		- AI insights and snapshot hashes.
	- Why important: This is the structural contract of ArchLens state. It ensures CSV seed data, assessment events, and scoring inputs are represented consistently.

### Governance and usage

- `LICENSE`
	- Apache 2.0 license for use, redistribution, and derivative work.

- `README.md`
	- This document.

## Data Relationship Overview

The core flow is:

1. `atam_scenarios.csv` defines scenario intent.
2. `scenario_question_mappings.csv` links each scenario to one or more questions.
3. `sarm_questions.csv` provides the question semantics and quality-attribute labels.
4. Runtime responses are scored using `constants.py` weight and compliance maps.
5. Persisted records follow the ORM schema in `models.py`.

## Replication Checklist

Use this checklist when reproducing ArchLens results:

1. Keep CSV identifiers stable (`scenario_id`, `question_key`).
2. Load all three CSV files together (questions, scenarios, mappings).
3. Preserve scoring constants in `constants.py` (`COMPLIANCE_SCORE`, `WEIGHT_MAP`).
4. Preserve mapping weights in `scenario_question_mappings.csv`.
5. Use the same schema semantics defined in `models.py`.
6. Record any local modifications to questions, scenarios, weights, or scoring maps because they will change outcomes.

## Notes for Researchers and Practitioners

- If you adapt scenarios or question text, treat those as experimental variants and report deltas from this baseline.
- If you add new quality attributes, also update scoring and mapping logic to avoid silent weighting bias.
- If you compare runs across datasets, ensure the same scoring constants are applied; otherwise score differences are not directly comparable.