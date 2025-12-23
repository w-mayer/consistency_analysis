# CONSISTENCY_METHOD.docx: Complete Outline (UPDATED)
## NAICS Multi-Service Coding Feasibility Analysis

---

# DOCUMENT PURPOSE

This document provides decision-makers with evidence to answer:

> **"Should we implement multi-service NAICS coding for public works contracts, and if so, under what conditions?"**

The analysis must translate statistical findings into actionable guidance for database architecture and workflow design.

---

# DOCUMENT STRUCTURE

```
1. EXECUTIVE SUMMARY (1 page)
   └── Decision recommendation with key numbers

2. BACKGROUND & METHODOLOGY (1-2 pages)
   ├── The database problem
   ├── Study design
   └── Analysis approach

3. RESULTS (4-5 pages)
   ├── 3.1 Can coders agree? (Classification agreement)
   ├── 3.2 Does the method matter? (Round comparison)
   ├── 3.3 What goes wrong? (Disagreement diagnosis)
   └── 3.4 Does it affect search? (Query simulation - EXPANDED)

4. SYNTHESIS: WHAT THIS MEANS FOR THE DATABASE (2 pages)
   ├── 4.1 The case for multi-coding
   ├── 4.2 Risks and mitigations
   └── 4.3 Implementation requirements

5. RECOMMENDATION (0.5 page)
   └── Go/no-go with conditions

APPENDIX
   ├── A: Data dictionary
   ├── B: Service normalization table
   ├── C: Full agreement tables
   └── D: Query scenario definitions (NEW)
```

---

# SECTION-BY-SECTION OUTLINE

## 1. EXECUTIVE SUMMARY

**Purpose:** Give busy executives the answer in 60 seconds.

**Frame:** "Here's what we tested, here's what we found, here's what to do."

### Content

#### Opening Statement (2 sentences)
> We tested whether multiple coders can reliably assign NAICS codes to public works contracts by having three coders independently classify 10 contracts using two different approaches. The results support implementing multi-service NAICS coding with targeted quality controls.

#### Key Findings Box

| Finding | Number | Implication |
|---------|--------|-------------|
| Service-level coding agreement | **94%** | The method works for complex contracts |
| Improvement from method change | **+56pp** | Process design matters more than contract difficulty |
| Overall single-coder miss rate | **30%** | Significant—but concentrated in specific categories |
| Highest-risk query categories | **Repair (50%), Support Services (46%)** | Handbook priority areas |
| Addressable disagreements | **63%** | Most problems are fixable with handbook updates |

#### Recommendation (1 paragraph)
> **Proceed with implementation.** Before launch, update the coding handbook with explicit guidance on (1) Construction vs. Administrative code assignment and (2) Repair/Support Services classification—the primary sources of query misses. Implement dual-coding quality checks for all Medium-difficulty contracts and 10% of Hard contracts. Monitor researcher feedback for false positive complaints.

#### Confidence Statement
> This recommendation is based on 74 service-level comparisons across 10 contracts and 350 simulated query-contract evaluations across 35 query types. The 94% classification agreement rate for complex contracts has a 95% confidence interval of [82%, 100%].

---

## 2. BACKGROUND & METHODOLOGY

**Purpose:** Establish credibility and explain what "agreement" means in this context.

### 2.1 The Database Problem

**Frame:** Why does this matter for researchers?

#### Content
- Public works contracts cover multiple services (roads, police, water, parks, etc.)
- Current approach: Single NAICS code per contract → Researchers miss relevant contracts
- Proposed approach: Multiple NAICS codes per contract → Better search coverage
- **The question:** Can coders reliably identify and classify multiple services?

#### Figure Placement: None (text only)

### 2.2 Study Design

**Frame:** What did we actually test?

#### Content

**Table: Study Structure**
| Element | Description |
|---------|-------------|
| Contracts | 10 public works contracts (3 Easy, 2 Medium, 5 Hard) |
| Coders | 3 trained analysts (Dylan, Greg, Will) |
| Rounds | Round 1: Role-level coding (7 contracts) / Round 2: Service-level coding (3 contracts) |
| Independence | Coders worked without seeing each other's assignments |

**Key Design Choice:** We tested two approaches:
- **Role-level (Round 1):** Coders list job titles and infer which service each supports
- **Service-level (Round 2):** Coders directly identify public services mentioned in contract

**Why this matters:** The Round 1 vs Round 2 comparison isolates the effect of *methodology* from contract difficulty.

### 2.3 Analysis Approach

**Frame:** How did we measure "agreement"?

#### Two-Stage Model

```
Stage 1: IDENTIFICATION          Stage 2: CLASSIFICATION
"What services are present?"     "What code fits this service?"
         ↓                                ↓
   Coders may identify           Given same service, coders
   different services            may assign different codes
```

**Why this decomposition matters:** 
- If disagreement is mostly at Stage 1 → Need better service extraction guidelines
- If disagreement is mostly at Stage 2 → Need better code assignment rules

#### Metrics Used

| Metric | Definition | Purpose |
|--------|------------|---------|
| Classification Agreement | % of overlapping services with identical codes | Core reliability measure |
| Jaccard Similarity | Code set overlap (intersection/union) | Contract-level completeness |
| Query Miss Rate | % of union-findable queries missed by single coder | Search impact |

#### Data Cleaning Note
> Service names were normalized before analysis to ensure "Mechanic" and "Mechanic II" are recognized as the same service. This reduced unique service names from 143 to 122 and ensures agreement rates reflect true classification differences, not naming variations.

---

## 3. RESULTS

### 3.1 Can Coders Agree on Classification?

**Purpose:** Answer the basic feasibility question.

**Frame:** "When coders identify the same service, do they assign the same code?"

#### Headline Finding
> **Yes.** Classification agreement reached 94% for complex contracts when using service-level coding.

#### Table: Classification Agreement by Round and Difficulty

| Segment | Agreement | 95% CI | n |
|---------|-----------|--------|---|
| **Round 2 Hard** | **94.1%** | [82.4%, 100%] | 17 |
| Round 2 Overall | 94.4% | [83.3%, 100%] | 18 |
| Round 1 Hard | 37.9% | [20.7%, 55.2%] | 29 |
| Round 1 Overall | 48.2% | [33.9%, 60.7%] | 56 |
| Easy (both rounds) | 100% | [100%, 100%] | 11 |
| Medium | 35.3% | [17.6%, 58.8%] | 17 |

#### Figure 1: Classification Agreement by Round and Difficulty
**Type:** Grouped bar chart
**X-axis:** Difficulty (Easy, Medium, Hard)
**Y-axis:** Agreement rate (0-100%)
**Groups:** Round 1 (blue), Round 2 (orange)
**Error bars:** 95% CI

**How to read it:** The dramatic difference between blue and orange bars for "Hard" contracts shows that methodology—not difficulty—drives reliability.

**Caption:** "Classification agreement for Hard contracts improved from 38% to 94% when switching from role-level to service-level coding. Error bars show 95% confidence intervals."

#### Interpretation for Decision-Makers
> The 94% agreement rate means that when two coders independently identify the same service in a contract, they assign identical NAICS codes 94% of the time. This exceeds typical inter-rater reliability thresholds (usually 80%) and indicates the classification task is feasible.

---

### 3.2 Does the Coding Method Matter?

**Purpose:** Isolate the effect of methodology from contract difficulty.

**Frame:** "Same contracts, different approach—what changes?"

#### Headline Finding
> **Yes, dramatically.** Switching from role-level to service-level coding improved Hard contract agreement by 56 percentage points.

#### The Controlled Comparison

| Metric | Round 1 (Role-Level) | Round 2 (Service-Level) | Change |
|--------|----------------------|------------------------|--------|
| Hard Contract Agreement | 37.9% | 94.1% | **+56pp** |
| Overlapping Services | 29 | 17 | — |

#### Why Role-Level Coding Fails
> Role-level coding requires coders to infer: "This person is a 'Maintenance Technician'—which service do they support?" Different coders make different inferences. Service-level coding asks directly: "What services does this contract cover?" This removes the inference step.

#### Figure 2: Round 1 vs Round 2 Improvement
**Type:** Before/after comparison (paired bars or slope chart)
**Left:** Round 1 Hard (37.9%)
**Right:** Round 2 Hard (94.1%)
**Annotation:** "+56 percentage points"

**How to read it:** The steep improvement shows that process design—not contract complexity—is the primary lever for reliability.

**Caption:** "For Hard contracts, service-level coding (Round 2) achieved 94% classification agreement versus 38% for role-level coding (Round 1)—a 56 percentage point improvement on the same contract types."

#### Interpretation for Decision-Makers
> This is the study's most important finding. It means we can achieve reliable multi-coding even for complex contracts by choosing the right methodology. The problem isn't that contracts are "too hard to code"—it's that role-level coding introduces unnecessary ambiguity.

---

### 3.3 What Goes Wrong When Coders Disagree?

**Purpose:** Diagnose disagreement patterns to identify fixes.

**Frame:** "Of the disagreements, what's causing them?"

#### Headline Finding
> **Most disagreements are fixable.** 37% are low-impact granularity differences; 47% stem from a single confusion pattern (Construction vs. Administrative codes).

#### Table: Disagreement Taxonomy

| Category | Count | % | Impact | Action |
|----------|-------|---|--------|--------|
| Construction vs Admin (23↔56) | 14 | 47% | HIGH | Handbook rule |
| Granularity (same prefix) | 11 | 37% | LOW | Accept or training |
| Professional vs Public Admin (54↔92) | 5 | 17% | MEDIUM | Handbook examples |

#### Figure 3: Disagreement Breakdown
**Type:** Donut chart or stacked bar
**Segments:** 
- Green: Granularity (37%) — "Low impact"
- Yellow: Addressable (47% + 17% = 63%) — "Fixable with handbook"
**Center label:** "63% addressable"

**How to read it:** The majority of disagreements are not random—they follow predictable patterns that can be addressed through clearer guidelines.

**Caption:** "Of 30 classification disagreements, 37% were granularity differences within the same code family (low search impact), and 63% followed addressable patterns—primarily confusion between Construction (23xxx) and Administrative Services (56xxx) codes."

#### The Construction vs. Administrative Problem

**Concrete example:**
> "Building Maintenance" was coded as:
> - 236220 (Commercial Building Construction) by Coder A
> - 561210 (Facilities Support Services) by Coder B
> - 237310 (Highway/Road Construction) by Coder C
>
> The coders disagreed on whether building maintenance is "doing construction work" (23xxx) or "supporting facilities" (56xxx). This ambiguity is addressable with a handbook rule.

#### Proposed Handbook Rule
> **Construction (23xxx):** Use when the role *directly performs* physical construction, repair, or infrastructure work.
> **Administrative/Support (56xxx):** Use when the role *supports* operations without directly performing construction.
>
> Example: A "Maintenance Technician" who repairs roads = 237310 (Construction). A "Maintenance Technician" who manages work orders = 561210 (Support).

#### Interpretation for Decision-Makers
> Disagreement is not random noise—it's concentrated in specific, predictable patterns. The single largest source (47%) is distinguishing construction work from administrative support. A clear handbook rule can eliminate this confusion.

---

### 3.4 Does Disagreement Affect Search Results?

**Purpose:** Translate classification variance into researcher-facing impact.

**Frame:** "If we use a single coder, how many relevant contracts will researchers miss?"

#### Headline Finding
> **Significant but concentrated impact.** Single-coder production would miss approximately 30% of query-relevant services overall, but this risk is concentrated in specific query categories (Repair: 50%, Support Services: 46%) and contract types (Medium: 43%).

#### Simulation Design
> We simulated 35 realistic researcher queries across 8 categories (Construction, Public Admin, Support Services, Utilities, Professional, Recreation, Repair, Transportation) against all 10 contracts. For each query-contract pair, we measured whether each coder's codes would return the contract in search results. The "union" represents what any coder would find; "misses" represent what a single coder would fail to find that others would capture.

#### Table: Overall Query Performance

| Metric | Value | 95% CI |
|--------|-------|--------|
| Total queries tested | 35 | — |
| Query-contract combinations | 350 | — |
| Union hits | 112 | — |
| **Average single-coder miss rate** | **30.4%** | [24%, 37%] |

#### Table: Miss Rates by Query Category

| Category | Union Hits | Avg Miss Rate | 95% CI | Risk Level |
|----------|------------|---------------|--------|------------|
| **Repair** | 6 | **50.0%** | [28%, 72%] | 🔴 HIGH |
| **Support Services** | 13 | **46.2%** | [31%, 62%] | 🔴 HIGH |
| Transportation | 1 | 33.3% | [0%, 100%] | 🟡 LOW n |
| Professional | 3 | 33.3% | [0%, 67%] | 🟡 LOW n |
| Public Admin | 5 | 26.7% | [7%, 47%] | 🟡 MEDIUM |
| Construction | 29 | 23.0% | [15%, 32%] | 🟢 MODERATE |
| Recreation | 3 | 22.2% | [0%, 45%] | 🟡 LOW n |
| Utilities | 5 | 13.3% | [0%, 33%] | 🟢 LOW |

#### Figure 4: Query Miss Rates by Category
**File:** `fig_category_miss_rates.png`
**Type:** Horizontal bar chart with error bars
**X-axis:** Average single-coder miss rate (%)
**Y-axis:** Query category
**Color scale:** Red-Yellow-Green based on miss rate
**Annotation:** Red dashed line at overall average (30.1%)

**How to read it:** Categories above the red line are higher risk; categories below are safer for single-coder production. Repair and Support Services stand out as highest risk.

**Caption:** "Query miss rates by category. Repair (50%) and Support Services (46%) show substantially higher miss rates than the overall average (30%). Error bars show 95% confidence intervals."

---

#### Table: Miss Rates by Difficulty

| Difficulty | Contracts | Union Hits | Avg Miss Rate | 95% CI |
|------------|-----------|------------|---------------|--------|
| Easy | 3 | 6 | **0.0%** | [0%, 0%] |
| **Medium** | 2 | 24 | **43.1%** | [32%, 54%] |
| Hard | 5 | 82 | 28.9% | [23%, 35%] |

#### The Medium > Hard Paradox

> Counter-intuitively, Medium contracts have higher miss rates (43%) than Hard contracts (29%). 
>
> **Hypothesis:** Hard contracts signal "be comprehensive" to coders, leading to thorough coverage. Medium contracts have ambiguous scope, leading coders to make different completeness decisions.
>
> **Implication:** Consider dual-coding ALL Medium contracts, not just a sample of Hard contracts.

#### Figure 5: Category × Difficulty Interaction
**File:** `fig_difficulty_category_heatmap.png`
**Type:** Heatmap
**Rows:** Query categories
**Columns:** Difficulty (Easy, Medium, Hard)
**Color scale:** Green (0%) to Red (67%)

**How to read it:** The darkest red cells indicate the highest-risk combinations. Medium-difficulty contracts show consistently higher miss rates across categories than Hard contracts.

**Caption:** "Miss rates by query category and contract difficulty. Medium contracts show the highest miss rates across most categories, with Repair + Medium (67%) and Support Services + Medium (67%) as the highest-risk combinations."

---

#### High-Risk Combinations

| Category × Difficulty | Miss Rate | Action |
|-----------------------|-----------|--------|
| **Repair + Medium** | **66.7%** | Mandatory dual-coding |
| **Support Services + Medium** | **66.7%** | Mandatory dual-coding |
| Repair + Hard | 46.7% | Priority for handbook |
| Support Services + Hard | 37.0% | Priority for handbook |
| Utilities + Medium | 33.3% | Monitor |
| Transportation + Medium | 33.3% | Monitor |

---

#### Coder × Category Patterns

#### Figure 6: Coder × Category Heatmap
**File:** `fig_coder_category_heatmap.png`
**Type:** Heatmap
**Rows:** Query categories
**Columns:** Coders (D, G, W)
**Color scale:** Green (0%) to Red (100%)

**How to read it:** Red cells indicate which coder struggles with which categories. This reveals systematic patterns that can be addressed through targeted training.

**Caption:** "Miss rates by coder and query category. G shows the highest overall miss rate (32.1%) with particular weakness in Support Services (53.8%), Recreation (66.7%), and Transportation (100%). W shows the lowest overall miss rate (27.7%)."

#### Table: Worst Performer by Category

| Category | Worst Coder | Miss Rate |
|----------|-------------|-----------|
| Construction | G | 27.6% |
| Public Admin | G | 40.0% |
| Support Services | **G** | **53.8%** |
| Recreation | **G** | **66.7%** |
| Transportation | **G** | **100%** |
| Professional | D | 66.7% |
| Repair | All equal | 50.0% |
| Utilities | D, W tied | 20.0% |

**Key Insight:** G shows systematic weakness across multiple categories. Targeted calibration training for G is warranted.

---

#### Contract-Level Risk

#### Figure 7: Contract × Coder Heatmap
**File:** `fig_contract_heatmap.png`
**Type:** Heatmap
**Rows:** Contracts (labeled with difficulty)
**Columns:** Coders (D, G, W)
**Color scale:** Green (0%) to Red (57%)

**How to read it:** Red rows indicate high-risk contracts regardless of coder. Red cells within a row indicate coder-specific problems.

**Caption:** "Query miss rates by contract and coder. The two Medium contracts (2019-04459-000 and 2025-00926-000) show the highest miss rates (47% and 41% average), confirming the Medium > Hard paradox."

#### Table: Contract Risk Ranking

| Contract | Difficulty | Avg Miss | Max Miss | Variance | Risk |
|----------|------------|----------|----------|----------|------|
| 2025-03419-000 | Hard | 48.9% | 53.3% | 3.1 | 🔴 |
| **2019-04459-000** | **Medium** | **46.7%** | **60.0%** | 12.5 | 🔴 |
| **2025-00926-000** | **Medium** | **40.5%** | **57.1%** | 18.7 | 🔴 |
| 2023-01776-000 | Hard | 31.5% | 38.9% | 6.9 | 🟡 |
| 2025-03668-000 | Hard | 26.2% | 35.7% | 8.9 | 🟡 |
| 2024-04451-000 | Hard | 25.5% | 41.2% | 11.1 | 🟡 |
| 2025-04184-000 | Hard | 14.8% | 33.3% | 13.9 | 🟢 |
| Easy contracts (3) | Easy | 0.0% | 0.0% | 0.0 | 🟢 |

---

#### Risk Prioritization Summary

#### Table: Category Risk Scores (Miss Rate × Frequency)

| Category | Miss Rate | Union Hits | Risk Score | Priority |
|----------|-----------|------------|------------|----------|
| **Construction** | 23.0% | 29 | **6.7** | 1 (volume) |
| **Support Services** | 46.2% | 13 | **6.0** | 2 (rate + volume) |
| Repair | 50.0% | 6 | 3.0 | 3 (rate) |
| Public Admin | 26.7% | 5 | 1.3 | 4 |
| Professional | 33.3% | 3 | 1.0 | 5 |
| Utilities | 13.3% | 5 | 0.7 | Low |
| Recreation | 22.2% | 3 | 0.7 | Low |
| Transportation | 33.3% | 1 | 0.3 | Low (n=1) |

**Interpretation:** Risk score = miss rate × hit frequency. Construction and Support Services have the highest impact because they combine moderate-to-high miss rates with high query frequency.

---

#### Interpretation for Decision-Makers

> **The 30% overall miss rate is concerning but manageable.** The miss rate is not uniform—it's concentrated in:
>
> 1. **Two query categories:** Repair (50%) and Support Services (46%) account for most of the risk
> 2. **One difficulty level:** Medium contracts (43%) are worse than Hard (29%)
> 3. **One coder:** G (32%) shows systematic weakness across categories
>
> **This concentration is good news:** It means targeted interventions can dramatically reduce the overall miss rate without requiring universal dual-coding.

---

## 4. SYNTHESIS: WHAT THIS MEANS FOR THE DATABASE

**Purpose:** Translate statistical findings into database architecture and workflow decisions.

### 4.1 The Case for Multi-Service Coding

**Frame:** "Why should we do this?"

#### Evidence Summary

| Question | Evidence | Confidence |
|----------|----------|------------|
| Is multi-coding *feasible*? | 94% agreement on Hard contracts | HIGH |
| Does method matter? | 56pp improvement from methodology change | HIGH |
| Are disagreements *addressable*? | 63% follow fixable patterns | HIGH |
| Is search impact *acceptable*? | 30% miss rate (concentrated) | MODERATE |

#### Benefits of Multi-Coding

1. **Improved search coverage:** Contracts appear in more relevant query results
2. **Reduced false negatives:** Researchers find contracts they would otherwise miss
3. **Richer metadata:** Each contract tagged with all applicable service categories
4. **Future-proofing:** Supports more granular filtering as database grows

#### The Cost of NOT Multi-Coding

> If we continue single-code assignment, researchers searching for specific services will systematically miss:
> - 50% of Repair-related contracts
> - 46% of Support Services contracts
> - 43% of Medium-difficulty contracts
>
> These are not edge cases—Support Services and Construction are among the most frequently searched categories.

---

### 4.2 Risks and Mitigations

**Frame:** "What could go wrong, and how do we prevent it?"

#### Risk 1: False Positives (Over-Coding)

**The concern:** Multi-coding may add codes that don't belong, causing researchers to retrieve irrelevant contracts.

**Evidence:** This study measured recall (are we missing codes?) but not precision (are we adding wrong codes?). False positive risk is **unknown**.

**Mitigation:**
- Monitor researcher complaints about irrelevant results
- Sample-audit "extra" codes quarterly
- Set maximum codes per contract (e.g., 10) to prevent over-identification

#### Risk 2: Cross-Contract Inconsistency

**The concern:** The same service (e.g., "Police") might get different codes in different contracts.

**Evidence:** Only 39% of services appearing in 2+ contracts are coded consistently. This is concerning.

**Mitigation:**
- Build service-to-code lookup table for common services (see Appendix B)
- Implement consistency checks in data entry system
- Quarterly audits of high-volume services

#### Risk 3: Coder Drift

**The concern:** Individual coders develop idiosyncratic habits that diverge from guidelines.

**Evidence:** 
- Pairwise agreement varies: G-W: 81%, D-W: 68%, D-G: 58%
- G shows systematic weakness: 32.1% overall miss rate, worst in 5/8 query categories

**Mitigation:**
- Targeted calibration training for G (priority: Support Services, Recreation)
- Monthly coder reliability monitoring using query simulation
- Automated flagging when coder's prefix distribution deviates from norm

#### Risk 4: Query Category Concentration

**The concern:** High miss rates in Repair (50%) and Support Services (46%) may significantly degrade researcher experience.

**Evidence:** These two categories account for 19 of 112 union hits (17%) but contribute disproportionately to missed results.

**Mitigation:**
- Handbook updates specifically for Repair and Support Services classification
- Dual-code all contracts likely to contain these service types
- Consider separate validation workflow for these categories

#### Risk 5: Medium Contracts Underperformance

**The concern:** Medium contracts show 43% miss rate—worse than Hard contracts.

**Evidence:** Medium contracts have ambiguous scope, leading to inconsistent completeness decisions.

**Mitigation:**
- **Dual-code ALL Medium contracts** (not just a sample)
- Develop clearer "scope boundary" guidelines for Medium contracts
- Consider reclassifying contracts by "scope clarity" rather than "difficulty"

#### Risk 6: Sample Size Uncertainty

**The concern:** With only 17 overlapping services in Round 2 Hard, can we trust the 94% number?

**Evidence:** 95% CI is [82%, 100%]. We can be confident true agreement exceeds 80%, but not that it exceeds 90%.

**Mitigation:**
- Pilot with larger sample (50+ contracts) before full rollout
- Accept 80% as floor, not 94% as expectation

---

### 4.3 Implementation Requirements

**Frame:** "What do we need to do this right?"

#### Pre-Launch Requirements

| Requirement | Rationale | Owner | Timeline |
|-------------|-----------|-------|----------|
| Handbook: Construction vs Admin rule | Addresses 47% of classification disagreements | Training Lead | 2 weeks |
| Handbook: Repair category guidance | Addresses 50% query miss rate | Training Lead | 2 weeks |
| Handbook: Support Services guidance | Addresses 46% query miss rate | Training Lead | 2 weeks |
| Handbook: 10 high-variance services | Addresses cross-contract inconsistency | Training Lead | 2 weeks |
| Service name normalization table | Ensures consistent service identification | Data Team | 1 week |
| Coder calibration session (G priority) | Addresses G's systematic weakness | Training Lead | 1 day |

#### Quality Control Framework

| Mechanism | Scope | Frequency | Action Threshold |
|-----------|-------|-----------|------------------|
| Dual-coding | **ALL Medium contracts** | Ongoing | Agreement <80% triggers review |
| Dual-coding | 10% of Hard contracts | Ongoing | Agreement <80% triggers review |
| Query simulation | Monthly sample | Monthly | Category miss rate >40% triggers review |
| Consistency audit | Services in 5+ contracts | Quarterly | >20% inconsistency triggers handbook update |
| Researcher feedback | All contracts | Ongoing | >5% complaint rate triggers investigation |
| Coder monitoring | All coders | Monthly | Miss rate >35% triggers calibration |

#### Database Schema Implications

| Current | Proposed |
|---------|----------|
| Single NAICS_Code field | NAICS_Codes array (max 10) |
| No service-level data | Service_Tags array linking to codes |
| No confidence metadata | Coder_Count field (1, 2, or 3) |
| No category metadata | Query_Category field (for monitoring) |

---

## 5. RECOMMENDATION

**Purpose:** Clear go/no-go with conditions.

### Decision

> **PROCEED with multi-service NAICS coding implementation.**

### Conditions

1. **Before launch:**
   - [ ] Update handbook with Construction vs. Administrative decision rule
   - [ ] Update handbook with Repair category classification guidance
   - [ ] Update handbook with Support Services classification guidance
   - [ ] Add guidance for 10 highest-variance services
   - [ ] Complete coder calibration session (priority: G)
   - [ ] Validate on 25 additional contracts (target: >85% agreement)

2. **At launch:**
   - [ ] Implement dual-coding for **ALL Medium contracts**
   - [ ] Implement dual-coding for 10% of Hard contracts
   - [ ] Deploy consistency checks for high-volume services
   - [ ] Establish researcher feedback channel
   - [ ] Establish monthly query simulation monitoring

3. **Ongoing:**
   - [ ] Monthly coder reliability monitoring (query simulation)
   - [ ] Monthly coder miss rate tracking (threshold: 35%)
   - [ ] Quarterly cross-contract consistency audits
   - [ ] Quarterly category miss rate review
   - [ ] Annual handbook review based on accumulated disagreement patterns

### Success Criteria (6-month review)

| Metric | Target | Action if Not Met |
|--------|--------|-------------------|
| Classification agreement (dual-coded) | >85% | Additional training |
| Cross-contract consistency | >60% | Handbook expansion |
| Researcher false positive complaints | <5% | Audit over-coding |
| Repair category miss rate | <35% | Targeted handbook update |
| Support Services miss rate | <35% | Targeted handbook update |
| Medium contract miss rate | <30% | Expand dual-coding |
| Overall query miss rate | <25% | Review methodology |

---

## APPENDICES

### Appendix A: Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| Contract | String | Contract identifier |
| Difficulty | Enum | Easy, Medium, Hard |
| Service_Raw | String | Coder-entered service name |
| Service_Normalized | String | Canonical service name |
| Coder | Enum | D, G, W |
| Round | Int | 1 (role-level) or 2 (service-level) |
| NAICS_Raw | String | Assigned code(s), semicolon-delimited |

### Appendix B: Service Normalization Table

| Canonical Name | Variants |
|----------------|----------|
| Equipment operator | Heavy equipment operator, Motor equipment operator, Senior heavy equipment operator |
| Mechanic | Mechanic II |
| Road maintenance | Highway and road maintenance, Road related |
| Traffic control | Traffic control crew, Traffic maintenance, Traffic and vegetation control |
| Building maintenance | Building and grounds maintenance |
| Sewer maintenance | Sewer repair, Sewer line maintenance |
| ... | ... |

### Appendix C: Full Agreement Tables

[Include complete Round × Difficulty breakdown with all confidence intervals]

### Appendix D: Query Scenario Definitions (NEW)

| Category | Queries | NAICS Codes Searched |
|----------|---------|---------------------|
| Construction | road_maintenance, highway_construction, commercial_building, utility_line_construction, specialty_trades, infrastructure_general | 237310, 237, 236220, 236, 237110, 237130, 238xxx |
| Public Admin | police_services, fire_protection, corrections, administrative_executive, courts_legal | 922120, 922160, 922140, 921130, 921190, 922110, 922130 |
| Support Services | facilities_support, landscaping_services, security_services, waste_collection, office_support | 561210, 561730, 567130, 561612, 562111, 561110 |
| Utilities | water_supply, sewage_treatment, utilities_general | 221310, 221320, 221 |
| Professional | engineering_services, surveying_mapping, computer_services, inspection_services | 541330, 541370, 541512, 541350 |
| Recreation | fitness_recreation, nature_parks, recreation_general | 713940, 712190, 71 |
| Repair | auto_repair, personal_services, repair_general | 811111, 811310, 812220, 81 |
| Transportation | towing_services, traffic_services, transportation_general | 488410, 488490, 488 |

---

# FIGURE SUMMARY (UPDATED)

| Figure | File | Type | Purpose | Placement |
|--------|------|------|---------|-----------|
| **Fig 1:** Agreement by Round/Difficulty | [to create] | Grouped bar | Show methodology > difficulty | Section 3.1 |
| **Fig 2:** Round 1 vs Round 2 | [to create] | Before/after | Emphasize 56pp improvement | Section 3.2 |
| **Fig 3:** Disagreement Taxonomy | [to create] | Donut | Show 63% addressable | Section 3.3 |
| **Fig 4:** Category Miss Rates | `fig_category_miss_rates.png` | Horizontal bar | Show category risk ranking | Section 3.4 |
| **Fig 5:** Category × Difficulty | `fig_difficulty_category_heatmap.png` | Heatmap | Show interaction effects | Section 3.4 |
| **Fig 6:** Coder × Category | `fig_coder_category_heatmap.png` | Heatmap | Show coder-specific patterns | Section 3.4 |
| **Fig 7:** Contract × Coder | `fig_contract_heatmap.png` | Heatmap | Show contract-level risk | Section 3.4 |
| **Fig 8:** Category × Difficulty Grouped | `fig_category_difficulty_grouped.png` | Grouped bar | Alternative view of interaction | Appendix or Section 3.4 |

---

# KEY MESSAGES FOR YOUR BOSS (UPDATED)

## The 30-Second Version

> "We tested whether coders can reliably assign multiple NAICS codes to contracts. Answer: Yes—94% classification agreement when using the right method. But query simulation reveals a 30% single-coder miss rate concentrated in two categories (Repair: 50%, Support Services: 46%) and one difficulty level (Medium: 43%). Recommendation: Implement with handbook updates, dual-code all Medium contracts, and targeted training for underperforming coder."

## The 5 Numbers That Matter

1. **94%** — Classification agreement for complex contracts (feasibility proven)
2. **56pp** — Improvement from methodology change (process > difficulty)
3. **30%** — Overall single-coder miss rate (significant but concentrated)
4. **50%/46%** — Miss rates for Repair/Support Services (handbook priority)
5. **43%** — Medium contract miss rate (dual-code all Medium contracts)

## The Risk Summary (UPDATED)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Coders can't agree | LOW (disproven) | — | — |
| Disagreements unfixable | LOW (63% addressable) | — | Handbook updates |
| Search degraded (overall) | MODERATE (30% miss) | HIGH | Dual-coding + handbook |
| Search degraded (Repair/Support) | HIGH (50%/46% miss) | HIGH | Priority handbook updates |
| Medium contracts underperform | HIGH (43% miss) | HIGH | Dual-code ALL Medium |
| False positives | UNKNOWN | MEDIUM | Monitor complaints |
| Cross-contract drift | MODERATE (39% consistent) | HIGH | Consistency audits |
| Coder G underperforms | HIGH (32% overall, worst in 5/8 categories) | MEDIUM | Targeted calibration |

## What You're Asking For (UPDATED)

> "Approval to implement multi-service NAICS coding with:
> 1. Two weeks for handbook updates (Construction vs Admin, Repair, Support Services)
> 2. One day for coder calibration (priority: G)
> 3. **Dual-coding ALL Medium contracts** (key change from original plan)
> 4. 10% dual-coding for Hard contracts
> 5. Monthly query simulation monitoring
> 6. Quarterly audit commitment
>
> In return: Reduction in researcher missed contracts from 30% to target <25%, with specific improvements in Repair (50%→35%) and Support Services (46%→35%) categories."
