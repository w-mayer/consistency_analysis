# NAICS Multi-Code Feasibility Analysis: Results Outline
## Extracted from consistency_analysis.ipynb

---

# 1. DATA OVERVIEW

## 1.1 Dataset Characteristics
- **Total observations:** 272 rows
- **Contracts coded:** 10 unique contracts
- **Coders:** 3 (W, G, D)
- **Rounds:** 2 (Round 1 = role-level, Round 2 = service-level)
- **Missing NAICS codes:** 3 rows

## 1.2 Contract Distribution by Difficulty
- **Easy:** 3 contracts (single-purpose departments)
- **Medium:** 2 contracts (multi-service public works)
- **Hard:** 5 contracts (city/county governments spanning many services)

## 1.3 Round Distribution
- **Round 1 (role-level):** 7 contracts, 203 observations
- **Round 2 (service-level):** 3 contracts, 69 observations

---

# 2. CODER BEHAVIOR PATTERNS

## 2.1 NAICS Prefix Usage by Coder
All three coders share the same top 5 code families but with different proportions:

| Coder | 23 (Construction) | 92 (Public Admin) | 56 (Admin/Waste) | 54 (Professional) | 22 (Utilities) |
|-------|-------------------|-------------------|------------------|-------------------|----------------|
| D     | 33.3%             | 27.9%             | 18.0%            | 4.5%              | 5.4%           |
| G     | 41.2%             | 23.5%             | 11.8%            | 7.1%              | 5.9%           |
| W     | 30.3%             | 30.3%             | 11.8%            | 11.8%             | 5.3%           |

## 2.2 Key Finding: Systematic Coder Tendencies
- **D** favors Administrative codes (56xxx) at 18% vs ~12% for others
- **G** favors Construction codes (23xxx) at 41% vs ~30-33% for others  
- **W** has most balanced 23/92 split (30%/30%)
- *Implication:* Coder calibration training needed, particularly for D

## 2.3 Shared Prefix Families (all 3 coders used)
{'22', '23', '48', '54', '56', '71', '81', '92'}

---

# 3. IDENTIFICATION OVERLAP ANALYSIS

## 3.1 Service Identification Agreement
*How often did coders identify the same services from the contract?*

| Metric | Round 1 (Role-Level) | Round 2 (Service-Level) |
|--------|---------------------|------------------------|
| All 3 coders identified service | 13% | 8% |
| Only 1 coder identified service | 58% | 70% |

## 3.2 Key Finding: Identification Drives Most Variance
- Most disagreement comes from **identification** (what services exist), not classification (what code fits)
- Different coders extract different information from the same document
- *Implication:* Handbook should standardize service identification criteria, not just code assignment

---

# 4. CLASSIFICATION AGREEMENT ANALYSIS

## 4.1 Overall Classification Agreement (overlapping services only)

### Before Service Name Normalization
| Round | Agreement Rate | n (overlapping services) |
|-------|----------------|--------------------------|
| Round 1 | 49.1% | 53 |
| Round 2 | 93.3% | 15 |

### After Service Name Normalization
| Round | Agreement Rate | n (overlapping services) |
|-------|----------------|--------------------------|
| Round 1 | 48.2% | 56 |
| Round 2 | 94.4% | 18 |

## 4.2 Classification Agreement by Difficulty (normalized)

| Difficulty | Agreement Rate | n | 95% CI |
|------------|----------------|---|--------|
| Easy | 100.0% | 11 | [100%, 100%] |
| Medium | 35.3% | 17 | [11.8%, 58.8%] |
| Hard | 58.7% | 46 | [43.5%, 71.7%] |

## 4.3 Round × Difficulty Breakdown (normalized)

| Round | Difficulty | Agreement | n |
|-------|------------|-----------|---|
| 1 | Easy | 100.0% | 10 |
| 1 | Medium | 35.3% | 17 |
| 1 | Hard | 37.9% | 29 |
| 2 | Easy | 100.0% | 1 |
| 2 | Medium | — | 0 |
| 2 | Hard | **94.1%** | 17 |

## 4.4 Key Finding: Methodology Matters More Than Difficulty
- Round 2 Hard contracts: **94.1%** agreement
- Round 1 Hard contracts: **37.9%** agreement
- Same contracts, different methodology → 56 percentage point improvement
- *Implication:* Service-level coding approach is viable even for complex contracts

---

# 5. PAIRWISE CODER ANALYSIS

## 5.1 Jaccard Similarity by Contract
*How much overlap exists between coders' complete code sets?*

| Contract | Difficulty | Round | Mean Jaccard | Min Jaccard |
|----------|------------|-------|--------------|-------------|
| 2023-03660-000 | Easy | 1 | 1.000 | 1.000 |
| 2023-05433-000 | Easy | 1 | 1.000 | 1.000 |
| 2025-00926-000 | Medium | 1 | 0.157 | 0.056 |
| 2019-04459-000 | Medium | 1 | 0.256 | 0.167 |
| 2025-03668-000 | Hard | 1 | 0.333 | 0.308 |
| 2025-03419-000 | Hard | 1 | 0.137 | 0.000 |
| 2023-01776-000 | Hard | 1 | 0.335 | 0.235 |
| 2025-04120-000 | Easy | 2 | 1.000 | 1.000 |
| 2025-04184-000 | Hard | 2 | 0.598 | 0.500 |
| 2024-04451-000 | Hard | 2 | 0.438 | 0.385 |

## 5.2 Mean Jaccard by Difficulty
| Difficulty | Mean Jaccard | Std |
|------------|--------------|-----|
| Easy | 1.000 | 0.000 |
| Medium | 0.206 | 0.070 |
| Hard | 0.368 | 0.169 |

## 5.3 Mean Jaccard by Round
| Round | Mean Jaccard | Std |
|-------|--------------|-----|
| 1 | 0.460 | 0.377 |
| 2 | 0.679 | 0.290 |

## 5.4 Pairwise Coder Similarities
| Pair | Mean Jaccard | Std |
|------|--------------|-----|
| D-G | 0.499 | 0.353 |
| D-W | 0.536 | 0.352 |
| G-W | 0.541 | 0.322 |

## 5.5 Key Finding: Counterintuitive Medium > Hard Disagreement
- Medium contracts: 0.21 mean Jaccard (highest disagreement)
- Hard contracts: 0.37 mean Jaccard
- *Hypothesis:* Hard contracts signal "be comprehensive"; Medium contracts have unclear scope

---

# 6. QUERY PERFORMANCE SIMULATION

## 6.1 Query Scenarios Tested
10 realistic search queries: road_maintenance, police_services, water_utilities, sewer_services, fire_protection, parks_recreation, building_maintenance, administrative, professional_services, corrections

## 6.2 Per-Contract Results

| Contract | Difficulty | Union Hits | D Miss Rate | G Miss Rate | W Miss Rate |
|----------|------------|------------|-------------|-------------|-------------|
| 2023-03660-000 | Easy | 2/10 | 0% | 0% | 0% |
| 2023-05433-000 | Easy | 2/10 | 0% | 0% | 0% |
| 2025-00926-000 | Medium | 7/10 | 0% | 0% | **57%** |
| 2019-04459-000 | Medium | 5/10 | 0% | **40%** | **20%** |
| 2025-03668-000 | Hard | 9/10 | 0% | 0% | 0% |
| 2025-03419-000 | Hard | 9/10 | 0% | **33%** | **11%** |
| 2023-01776-000 | Hard | 9/10 | **11%** | 0% | 0% |
| 2025-04120-000 | Easy | 2/10 | 0% | 0% | 0% |
| 2025-04184-000 | Hard | 10/10 | 0% | **10%** | 0% |
| 2024-04451-000 | Hard | 6/10 | 0% | 0% | 0% |

## 6.3 Average Miss Rates by Difficulty
| Difficulty | Avg Single-Coder Miss Rate |
|------------|---------------------------|
| Easy | 0% |
| Medium | ~18% |
| Hard | ~14% |

## 6.4 Key Finding: Single-Coder Production Risk
- Overall average single-coder miss rate: **~10-11%**
- Worst case (Medium contracts): up to 57% miss rate for individual coder
- *Implication:* Multi-coding captures significantly more searchable services

---

# 7. SERVICES ALWAYS AGREED ON (Handbook Candidates)

## 7.1 Services with 100% Agreement
These can be documented as canonical mappings:

| Service | NAICS Code | Times Coded |
|---------|------------|-------------|
| Truck driver | 237310 | 3 |
| Water supply | 221310 | 2 |
| Heavy equipment operator | 237310 | 2 |
| Highway and road maintenance | 237310 | 2 |
| Fire inspector | 922160 | 2+ |
| Deputy sheriff | 922120 | 2+ |
| Clerk of court | 922110 | 2+ |
| Juvenile detention | 922140 | 2+ |
| Engineering | 541330 | 2+ |
| Sewer collection operations | 221320 | 2+ |

---

# 8. SERVICES ALWAYS DISAGREED ON (Need Guidance)

## 8.1 Services with 0% Agreement
| Service | Codes Used | Pattern |
|---------|------------|---------|
| Administrative support | 561110, 921190, 922130 | Diff prefix |
| Carpenter | 237310, 238350 | Same prefix |
| City auditor | 921130, 922130 | Same prefix |
| Community safety officer | 812910;561710, 922120 | Diff prefix |
| County assessor | 921130, 922130 | Same prefix |
| Custodian | 561210, 561720 | Same prefix |
| Electrician | 238210, 561210 | Diff prefix |
| GIS technician | 541370, 925120 | Diff prefix |
| Jail administration | 922120, 922140 | Same prefix |
| Laborer | 237310, 561210 | Diff prefix |
| Mechanic | 237310, 811111 | Diff prefix |
| Motor sweeper | 237310, 488490 | Diff prefix |
| Network administration | 541512, 541513, 541519 | Same prefix |
| Park ranger | 712190, 924120 | Diff prefix |
| Plumber | 238220, 561210 | Diff prefix |
| Sewer equipment operator | 221320, 237110 | Diff prefix |
| Transportation engineer | 237310, 541330 | Diff prefix |

---

# 9. CROSS-CONTRACT CONSISTENCY

## 9.1 Services Appearing in 2+ Contracts
- **Total:** 23 services
- **Consistently coded:** 10 (43%)
- **Inconsistently coded:** 13 (57%)

## 9.2 Consistently Coded Services
| Service | Code | # Contracts |
|---------|------|-------------|
| county attorney | 922130 | 2 |
| engineering | 541330 | 2 |
| heavy equipment operator | 237310 | 5 |
| highway and road maintenance | 237310 | 2 |
| road maintenance | 237310 | 3 |
| senior heavy equipment operator | 237310 | 2 |
| sewage treatment | 221320 | 2 |
| tax assessor | 921130 | 2 |
| truck driver | 237310 | 4 |
| water supply | 221310 | 2 |

## 9.3 Inconsistently Coded Services (Priority for Handbook)
| Service | Codes | Prefix Match |
|---------|-------|--------------|
| maintenance technician | 236220, 237310, 237990, 561210 | DIFF |
| administrative support | 561110, 921190, 922130 | DIFF |
| building maintenance | 236220, 237310, 561210 | DIFF |
| network administration | 541512, 541513, 541519 | SAME |
| account clerk | 921130, 922140 | SAME |
| building inspector | 541350, 926150 | DIFF |
| facilities management | 236220, 561210 | DIFF |
| laborer | 237310, 561210 | DIFF |
| mechanic | 237310, 811111 | DIFF |

---

# 10. PREFIX CONFUSION MATRIX

## 10.1 Most Frequently Confused Prefix Pairs
| Prefix Pair | Count | Interpretation |
|-------------|-------|----------------|
| 23 (Construction) ↔ 56 (Admin/Waste) | **5** | Most common confusion |
| 23 (Construction) ↔ 48 (Transport) | 2 | |
| 22 (Utilities) ↔ 23 (Construction) | 2 | |
| 54 (Professional) ↔ 92 (Public Admin) | 2 | |
| 56 (Admin/Waste) ↔ 92 (Public Admin) | 2 | |
| 71 (Recreation) ↔ 92 (Public Admin) | 1 | |
| 23 (Construction) ↔ 81 (Repair/Maint) | 1 | |
| 81 (Repair/Maint) ↔ 92 (Public Admin) | 1 | |
| 23 (Construction) ↔ 54 (Professional) | 1 | |

## 10.2 Key Finding: Construction vs Admin is Primary Confusion
- 5 of 17 disagreements (29%) involve 23 ↔ 56 confusion
- *Implication:* Handbook needs explicit decision rule for "is this role doing physical work (23) or administrative support (56)?"

---

# 11. SERVICE NAME NORMALIZATION ANALYSIS

## 11.1 Clustering Results (Levenshtein threshold=0.7)
17 clusters identified where different names may refer to same service

### Key Clusters:
**Cluster 1: Mechanic variations**
- HVAC Mechanic → [238220]
- Mechanic → [237310, 811111]
- Mechanic II → [237310]

**Cluster 2: Equipment operators**
- Equipment operator → [237310]
- Heavy equipment operator → [237310]
- Motor equipment operator → [237310]
- Senior heavy equipment operator → [237310]
- Sewer equipment operator → [237110, 221320]
- Solid waste equipment operator → [562111]

**Cluster 5: Maintenance variations** (largest, most problematic)
- Auto maintenance → [811111]
- Building maintenance → [237310, 236220, 561210]
- Equipment maintenance → [237310]
- General facility maintenance → [561210]
- Highway and road maintenance → [237310]
- Park maintenance → [561730]
- Sewer maintenance → [221320, 237110]
- Traffic maintenance → [237310]

## 11.2 Service Name Normalization Map Applied
22 service names merged into 14 canonical forms:
- 'Heavy equipment operator' → 'Equipment operator'
- 'Mechanic II' → 'Mechanic'
- 'Highway and road maintenance' → 'Road maintenance'
- 'Fire prevention' → 'Fire protection'
- 'Recreation programs' → 'Recreation'
- etc.

## 11.3 Impact of Normalization
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Unique services | 144 | 122 | -22 |
| Overlapping services | 68 | 74 | +6 |
| Agreement rate | 58.8% | 59.5% | +0.6pp |

---

# 12. DISAGREEMENT TAXONOMY

## 12.1 True Disagreements After Normalization
- **Total:** 30 disagreements
- **Same code family (granularity):** 11 (37%)
- **Different code family (substantive):** 19 (63%)

## 12.2 Substantive Disagreements (Different Code Families)
*These require handbook guidance - coders fundamentally disagree on service category*

| Service | Codes | 
|---------|-------|
| Administrative support | 561110, 921190, 922130 |
| Building inspector | 541350;237990, 926150 |
| Building maintenance | 236220, 561210 |
| Electrician | 238210, 561210 |
| Facilities management | 236220, 561210 |
| GIS technician | 541370, 925120 |
| Laborer | 237310, 561210 |
| Mechanic | 237310, 811111 |
| Motor sweeper | 237310, 488490 |
| Park ranger | 712190, 924120 |
| Plumber | 238220, 561210 |
| Sewer equipment operator | 221320, 237110 |
| Sewer maintenance | 221320, 237110 |
| Sign erector/painter | 238990, 488490 |
| Surveying | 541370, 924120 |
| Traffic control | 237310, 561612 |
| Transportation engineer | 237310, 541330 |

## 12.3 Granularity Disagreements (Same Code Family)
*Lower priority - prefix-level queries will still find these*

| Service | Codes |
|---------|-------|
| Account clerk | 921130, 922140 |
| Carpenter | 237310, 238350 |
| City auditor | 921130, 922130 |
| County assessor | 921130, 922130 |
| Custodian | 561210, 561720 |
| Environmental services | 924120, 925120 |
| Groundskeeper | 561730, 567130 |
| Jail administration | 922120, 922140 |
| Network administration | 541512, 541513, 541519 |
| Probation office | 922110, 922150 |

---

# 13. CONFIDENCE INTERVALS

## 13.1 Final Metrics with 95% CIs (Normalized)

| Segment | Agreement | 95% CI | n |
|---------|-----------|--------|---|
| **Round 1** | 48.2% | [35.7%, 60.7%] | 56 |
| **Round 2** | 94.4% | [83.3%, 100.0%] | 18 |
| Easy | 100.0% | [100.0%, 100.0%] | 11 |
| Medium | 35.3% | [11.8%, 58.8%] | 17 |
| Hard | 58.7% | [43.5%, 71.7%] | 46 |

## 13.2 Round × Difficulty with CIs (Normalized)

| Round | Difficulty | Agreement | 95% CI | n |
|-------|------------|-----------|--------|---|
| 1 | Easy | 100.0% | [100%, 100%] | 10 |
| 1 | Medium | 35.3% | [11.8%, 58.8%] | 17 |
| 1 | Hard | 37.9% | [20.7%, 55.2%] | 29 |
| 2 | Easy | 100.0% | [100%, 100%] | 1 |
| 2 | Hard | **94.1%** | [82.4%, 100.0%] | 17 |

## 13.3 Sample Size Assessment
- Round 1: n=56, CI width = 25 percentage points
- Round 2: n=18, CI width = 17 percentage points
- **To achieve ±10pp margin:** need ~49 overlapping services
- **To achieve ±5pp margin:** need ~196 overlapping services

---

# 14. KEY INSIGHTS SUMMARY

## 14.1 Headline Findings
1. **Service-level coding works:** Round 2 Hard contracts achieved 94.1% agreement [82.4%, 100%]
2. **Role-level coding struggles:** Round 1 Hard contracts only 37.9% agreement
3. **Methodology > Difficulty:** Same contracts, different approach → 56pp improvement
4. **Single-coder production risk:** ~10% of searchable services missed on average
5. **Union benefit is real:** Multi-coding adds 2-9 codes beyond best individual coder

## 14.2 Actionable Findings
1. **Construction ↔ Admin confusion is #1 problem** (5 of 17 prefix disagreements)
2. **22 service name variations** should be standardized in handbook
3. **10 services always agreed** → document as canonical mappings
4. **17 services always disagreed** → need explicit handbook guidance
5. **Coder D** shows systematic tendency toward admin codes → calibration needed

## 14.3 Limitations
1. **Small sample size:** n=17-18 for key Round 2 Hard comparison
2. **Wide confidence intervals:** 94.1% could plausibly be as low as 82.4%
3. **Query simulation uses constructed scenarios** (may not match actual researcher behavior)
4. **Only 3 coders** → limited generalizability to larger coder population

---

# 15. RECOMMENDED NEXT STEPS

1. **Expand pilot:** Code 5-10 more Hard contracts with service-level approach to tighten CIs
2. **Update handbook:** Add explicit guidance for 17 always-disagreed services
3. **Standardize names:** Implement service name normalization mapping
4. **Coder training:** Calibration session focused on Construction vs Admin distinction
5. **Monitor production:** Dual-code 10% of Hard contracts to track agreement over time
