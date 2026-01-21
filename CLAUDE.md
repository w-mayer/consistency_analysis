# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python data analysis project for evaluating inter-coder reliability in NAICS (North American Industry Classification System) code assignment for public works contracts. The analysis determines whether multiple coders can consistently assign NAICS codes to contracts, comparing role-level vs service-level coding methodologies.

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main analysis scripts
python resources/c2.py    # Core 6-phase analysis workflow
python resources/c3.py    # Comprehensive query simulation analysis

# Start Jupyter for interactive analysis
jupyter lab consistency_analysis.ipynb
```

## Project Structure

```
/
├── consistency_analysis.ipynb   # Main interactive analysis notebook
├── data/
│   └── consistency_analysis.csv # Source data (Contract, Service_Raw, Coder, Round, NAICS_Raw, Difficulty)
├── resources/
│   ├── c2.py                    # Full analysis workflow (6 phases)
│   └── c3.py                    # Query simulation engine with visualizations
├── figures/                     # Generated visualization outputs
└── docs/                        # Method documentation and outlines
```

## Architecture

### Data Pipeline (c2.py)

The analysis follows a 6-phase workflow:

1. **Data Preparation**: Load CSV, clean data, normalize service names using `SERVICE_EQUIVALENCES` mapping
2. **Descriptive Analysis**: Coder behavior profiles, NAICS prefix usage patterns
3. **Core Metrics**: Classification agreement rates with bootstrap confidence intervals
4. **Diagnostic Analysis**: Disagreement taxonomy, prefix confusion matrix
5. **Impact Simulation**: Query performance testing against `QUERY_SCENARIOS`
6. **Synthesis**: Summary tables, visualizations

### Query Simulation (c3.py)

Simulates researcher queries across 8 categories (Construction, Public Admin, Support Services, Utilities, Professional, Recreation, Repair, Transportation) with 35 total query scenarios. Computes miss rates by coder, category, difficulty, and contract.

### Key Data Structures

- **Service normalization**: `SERVICE_EQUIVALENCES` dict maps variant names to canonical forms
- **Query definitions**: `QUERY_SCENARIOS` dict maps query names to NAICS code lists
- **Analysis outputs**: DataFrames with agreement rates, miss rates, confidence intervals

### Core Functions

- `normalize_service_names()`: Applies service name equivalence mapping
- `compute_agreement_rate()`: Calculates classification agreement with bootstrap CIs
- `run_simulation()`: Executes query simulation across all contracts
- `bootstrap_ci()`: Computes confidence intervals via resampling

## Dependencies

Core libraries: pandas, numpy, matplotlib, seaborn, scipy

Optional: Levenshtein (for fuzzy service name matching discovery)

## Data Schema

| Column | Description |
|--------|-------------|
| Contract | Contract identifier |
| Difficulty | Easy, Medium, Hard |
| Service_Raw | Coder-entered service name |
| Coder | D, G, or W |
| Round | 1 (role-level) or 2 (service-level) |
| NAICS_Raw | Assigned NAICS code(s), semicolon-delimited |
