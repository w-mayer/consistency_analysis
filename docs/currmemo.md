**TO:** Contracts Team

**FROM:** Will Mayer

**DATE:** January 15, 2026

**SUBJECT:** Database-Wide Multi-Industry NAICS Classification
(NAICS_All)

**Problem**

Current contract entry practices typically only assign one NAICS code
per contract, which prevents accurate service-level classification for
agreements that cover multiple services.

Assigning only one NAICS code per contract therefore significantly
limits service- or industry-specific queries. The results of such
queries inevitably include false positive results, miss contracts, and
require additional manual filtering based on implicit knowledge of
contract data. Although the NAICS2 field was created to mitigate these
issues, its lack of operational standards and inherent limitations has
led to its underutilization (only 8.3% of records entered in the last
year included a NAICS2 value).

# Decision Requested: Repurpose the underutilized NAICS2 field to store multiple semicolon-delimited NAICS codes per contract.

**What Changes**

1.  **For researchers:** Secondary services become queryable (e.g., a
    road department contract covering sewer work will appear in sewer
    queries.) **Service-level analyses** (e.g., all contracts covering
    water infrastructure specifically) become possible for the first
    time.

2.  **For DRS staff:** wide contracts require identifying all applicable
    NAICS codes instead of selecting one "primary" code.

3.  **Net cost:** approximately 35 added staff hours/year to implement
    for PWD contracts (approximately 500 contracts/year.) Time cost
    scales proportionally to other multi-service categories.

**How Will Query Performance Change?**

A pilot evaluated the new system with three coders classifying 10
contracts. The small sample size limits precision, but results indicate
that under the new system, NAICS queries will capture 84% of relevant
contracts. The 84% capture rate breaks down by service type: core
government services show near-perfect agreement, while general support
roles show more variation.[^1]\
\
**What Does It Cost?**

Estimates based on public works contracts (approximately 500
contracts/year):[^2]

  -----------------------------------------------------------------------
  **Metric**        **Current**       **New System**    **Change**
  ----------------- ----------------- ----------------- -----------------
  Annual            8.25 hrs./year    45.5 hrs./year    **+37.25
  Classification                                        hrs./year**
  Time                                                  

  Query and         \-                1.6--3.6          **1.6--3.6
  Filtering Time                      hrs./year         hrs./year**
  Reduction                                             

  **Net Annual      \-                \-                **+34--36
  Impact**                                              hrs./year (18
                                                        min/week per
                                                        staff)**
  -----------------------------------------------------------------------

**\
What Problems Remain?**

1.  **Historical records.** Pre-implementation wide contracts keep
    single code classification. Mitigated by opportunistic
    reclassification when staff access records.

2.  **Variation in general support roles.** Coders show 44-67%
    agreement on support roles (mechanics, technicians, etc.) but show
    92-100% agreement on core services (roads, police, etc.) This
    has limited practical impact: queries targeting specific occupations
    like mechanics are better served by SOC job codes, not NAICS
    industry codes. For core government services, the primary use case,
    reliability is high.

# Implementation Requirements

1.  Finalize classification handbook, including explicit guidance on
    Construction (23xxx) vs. Administrative Support (56xxx) classification
    (addresses 47% of disagreements).

2.  Update data entry validation rules.

3.  Conduct staff training (approximately two hrs.)

4.  Establish quarterly QA review.

Estimated timeline: 4--6 weeks.

# What Does the Team Gain?

## Benefit 1: More Services Become Queryable

*Current state:* DRS classifies a wide contract covering roads, sewers,
and parks under one industry. If coded as "roads," researchers searching
for sewer contracts will never find it. The sewer service is not
recorded in any queryable field.

*NAICS_All:* The same contract receives codes for roads, sewers, and
parks. Researchers searching for any of these services will find the
contract, provided they use recommended query strategies.[^3]

*Evidence:* Review of public works records identified at least 101 wide
contracts currently classified with a single code. Each covers services
that are currently invisible to NAICS queries.

*Training Exercise Evidence:* Under the status quo, at most one service
is findable per contract. Under NAICS_All, a single coder captures
approximately 84% of identifiable services. The 84% rate decomposes
predictably:[^4]

  -----------------------------------------------------------------------
  **Service Category**      **Coders Finding**    **Interpretation**
  ------------------------- --------------------- -----------------------
  Construction (roads,      3.0 / 3 (100%)        Highly reliable
  bridges, utilities)

  Public Administration     2.75 / 3 (92%)        Very reliable
  (police, courts, fire)

  Administrative Support    2.6 / 3 (87%)         Good reliability

  Professional Services     2.0 / 3 (67%)         Moderate reliability
  (engineering, surveying)

  Repair & Maintenance      1.33 / 3 (44%)        Variable; consider
  (mechanics, custodians)                         SOC codes
  -----------------------------------------------------------------------

*Note: "Coders Finding" shows the average number of coders (out of 3)
who identified a service when it exists. Core services (Construction,
Public Admin) achieve 92-100% identification; support roles
(Repair & Maintenance) show more variation.*

*Note:* *Under the status quo, each contract receives exactly one code,
which may or may not reflect the contract's core function. Only that
code is findable; all other covered services are invisible to NAICS
queries. Under NAICS_All, \~84% of identifiable services are captured.*

Core government services show near-perfect agreement. When roads,
utilities, police, or fire services exist in a contract, coders reliably
identify them (92 -- 100%). **These are the services for which NAICS
queries are most frequently used.**

General support roles show 44-67% agreement (see table above). A mechanic
could reasonably be classified under construction (supporting road
crews), auto repair (city fleet maintenance), or facilities support.
However, this variation has limited practical impact: queries targeting
specific occupations are better served by SOC queries. NAICS classifies
industries, not occupations, so this variation reflects **using the
wrong tool for the job.**

*Note on Query Complexity:* The new system requires researchers to
understand multi-code queries. Appendix III provides recommended query
templates for common searches. The added query complexity is modest and
is offset by eliminating the status quo requirement to manually filter
false positives from results sets.

[Benefit 2: More Precise, Standardized Classification]{.underline}

*Current state:* Staff use NAICS codes in non-standard ways that create
systematic false positives. The internal convention uses NAICS 926120
("Administration of Transportation Programs") to mean "public works
departments primarily covering road maintenance." But the NAICS
definition includes airports, port authorities, and parking garages.

Consequently, a researcher querying for road maintenance using our
shorthand (926120) retrieves contracts covering transportation
administration that have nothing to do with road maintenance. Analysis
of 967 records classified under our "road maintenance" convention found
at least 15% false positives (employers that do not perform road
maintenance but share the same catch-all classification.)

This internal shorthand exists only in institutional knowledge and
deviates from official NAICS definitions.

*NAICS_All:* The new system uses NAICS codes according to their official
definitions. Road construction is classified under 237310, not 926120,
and port authorities receive their correct codes (926120.) This
eliminates false positives at the source and makes classification more
transparent, auditable, and consistent with federal definitions.

[Benefit 3: Remaining False Positives are More Self-Evident]{.underline}

*Current state:* When false positives appear in result sets, researchers
must review non-standard fields (contract text, remarks, etc.) to
determine the relevance of a given record. There is no way to
systematically filter at the service level.

*NAICS_All:* Under the new system, each contract clearly displays all
covered industries. Researchers can immediately see whether a contract
covers the service they need without reading the full document. For
example, a contract coded as 237310 + 221310 (road construction + water
supply) is visibly different from one coded as 237310 + 238210 (road
construction + electrical work.)

[Benefit 4: Simplified Staff Decision-Making]{.underline}

*Current state:* Staff must decide which service is "primary," a
judgement that varies by the analyst.

*NAICS_All:* Subjective judgement is replaced by a series of binary
questions: "Does this contract cover X?" If so, the code is assigned. No
prioritization is needed.

# What Does the Solution Cost?

Implementing NAICS_All requires added upfront classification time for
wide contracts, partially offset by reduced query and filtering time.
This cost applies proportionally to any contract category covering
multiple services. PWD records are used here as a representative example
to quantify the impact.

*Evidence:* PWD contracts are used to estimate effort because they are
often wide and represent approximately 8.4% of annual contract volume
(approximately 500 contracts/year.) The cost estimates below reflect
this volume and would scale proportionally to other categories of
multi-service contracts.[^5]

Under the current system, staff assign a single "primary" NAICS code,
requiring minimal review time. Under the new system, staff find all
applicable services, increasing classification time for multi-service
records.

## Table I: Estimated Annual Time Impact (PWD Contracts as Worked Example)

  -----------------------------------------------------------------------
  **Metric**        **Current**       **New System**    **Change**
  ----------------- ----------------- ----------------- -----------------
  Annual            8.25 hrs./year    45.5 hrs./year    **+37.25
  Classification                                        hrs./year**
  Time                                                  

  Query and         \-                1.6--3.6          **1.6--3.6
  Filtering Time                      hrs./year         hrs./year**
  Reduction                                             

  **Net Annual      \-                \-                **+34--36
  Impact**                                              hrs./year (18
                                                        min/week per
                                                        staff)**
  -----------------------------------------------------------------------

*Note:* Estimates are based on approximately 500 annual PWD contracts.
Net impact equals roughly 18 minutes per week per staff member. Costs
scale proportionally to other multi-service contract categories.

# Why Hasn't NAICS2 Solved This Problem?

The NAICS2 field currently exists in the database but is rarely used.
Field availability alone is insufficient without clear operational
standards.

*Current usage:* Only 500 of 6,015 records entered in the last year
(approximately 8.3% of volume) use the NAICS2 field. The remaining
approximately 91.7% of records rely on single-code classification even
though many would require multi-code classification under the new
framework.

*Why underutilization occurs:* Staff lack clear guidance on when and how
to use the NAICS2 field. Without standardized rules, staff default to
single-code classification to avoid subjective judgement calls about
which secondary code to prioritize.

*NAICS_All solution:* Replacing the NAICS2 field with NAICS_All and
operationalizing the NAICS_All field with clear assignment policies
encourages more correct and consistent use of the field. Explicit
standards and upfront planning regarding (1) when to use several codes,
(2) standardized formatting, (3) validation rules at data entry, and (4)
staff training encourage staff to use NAICS_All to classify each record
with the breadth of industries covered by the contract.

**What Problems Remain?**

[Problem 1: Construction vs. Administrative Code Confusion (Priority)]{.underline}

The training exercise revealed that **47% of classification
disagreements** stem from a single confusion pattern: coders disagree on
whether a role belongs under Construction (23xxx) or Administrative
Support (56xxx) codes.

For example, "Building Maintenance" was coded as 236220 (Commercial
Building Construction) by one coder, 561210 (Facilities Support
Services) by another, and 237310 (Highway/Road Construction) by a third.
The coders disagreed on whether the role *directly performs*
construction work or *supports* facility operations.

*Resolution:* This confusion is addressable through a clear handbook
rule. The handbook should specify: use Construction (23xxx) when the
role directly performs physical construction, repair, or infrastructure
work; use Administrative/Support (56xxx) when the role supports
operations without directly performing construction.

[Problem 2: Variation in General Support Roles]{.underline}

General support roles show inherent coding variation that cannot easily
be eliminated through training and guidance (44-67% agreement vs.
92-100% for core services).

Roles like mechanics, maintenance technicians, and custodians were coded
under different NAICS prefixes depending on contract context. For
example, in Whatcom County's CBA, all coders agreed on construction and
public administration codes, but disagreed on support, repair, and
professional service codes. The disagreement stemmed from roles like
"custodian," "maintenance technician," and "GIS technician" that could
reasonably belong in multiple departments.

This variation has limited practical impact on most queries because
NAICS classifies industries, not occupations. Researchers targeting
specific occupations (like auto mechanics) should target SOC codes, not
NAICS codes. For NAICS queries targeting general support roles,
researchers should search multiple related code families and expect to
capture 40-50% of relevant contracts.[^6]

[Problem 3: Historical Records]{.underline}

Wide pre-implementation contracts will not be automatically enriched
with multiple codes.

*Impact:* A contract covering water, sewer, and road maintenance will
remain classified under its original single code (e.g., "926130") unless
manually updated.

*Mitigation:* When staff access older records, they should reclassify
opportunistically (adds approximately 2-3 minutes per accessed
contract). Gradual improvement occurs naturally without dedicated
resources. This approach depends on access patterns; often accessed
records will be updated sooner, while rarely accessed records may remain
single-coded indefinitely.

*If needed:* A targeted reclassification project could backfill
high-priority records (approximately 81-171 hours depending on scope).
This can be evaluated if needs for historical analysis emerge.

[Problem 4: Classification Incentives]{.underline}

The new system creates an incentive to code comprehensively, which could
lead to over-coding (e.g., adding codes for services that are only
tangentially present.)

*Mitigation:* The handbook emphasizes coding services that are genuinely
covered by the contract, not those that are merely mentioned or implied.
QA review will check for systematic over-coding and provide feedback.

### Appendix I: Time Cost Calculations

*Scope of Change:* Using PWD records as a working example, analysis of
all contracts entered in the past 12 months found at least 495 PWD
contracts. This accounts for 8.4% of total annual contract volume.

*Current Data Entry Time:*

- DRS reviews contract text to classify as 926120 or 926130.

- Staff estimate this takes 30--90 seconds per contract.

- Annual time investment: 60 seconds \* 495 contracts/year = 8.25
  hours/year

*New Data Entry Time: Timing Exercise with DRS Staff*

- DRS uses the handbook checklist to find all applicable services.

- Timing exercise with DRS staff on 3 sample contracts showed:

  - Simple/narrow contracts (single service): 1--5 minutes.

  - Complex/wide contracts (several services): 5--10 minutes.

- The new process names all covered services, generating more complete
  data at modest added time.

- Annual time investment:

  - Assuming approximately 50% of PWD contracts are narrow and 50% are
    wide. This rough estimate is based on sample review during the
    timing exercise and initial project scope analysis. Both types
    require more thorough classification than the current system, but
    wide contracts require entering multiple codes.

  - If the actual distribution skews toward wide contracts (e.g., 70%
    wide), annual classification time would increase to approximately
    55--60 hours. Conversely, if more contracts are narrow, costs would
    be lower.

  - Simple contracts = 248 contracts/year \* 3 minutes = 12.4 hours/year

  - Complex contracts: 248 contracts/year \* 8 minutes = 33.1 hours/year

- Gross annual increase: 45.5 hours/year

  - 45.5 hours/year divided by 2,080 hours = 2.1% of one FTE's annual
    capacity

  - With 3 DRS staff, gross annual increase per DRS staff = 45.5
    hours/year divided by 3 staff divided by 2,080 hours = 0.7% of each
    person's annual capacity. This comes out to **be approximately 18
    minutes per week on average per staff member.**

*Return on Investment*

The primary benefit is eliminating manual filtering required to isolate
specific contract types, illustrated here with PWD contracts to answer
requests for the Public Services Division. The same efficiency gains
would apply to queries for other wide contract categories. Under the new
system, service-specific queries (e.g., NAICS_All LIKE \"\*237310\*\")
return only contracts covering the relevant service, reducing false
positive risk and the need for manual review.

Salesforce case history shows analysts run approximately one PWD-related
query per month (approximately 12/year). Examples include:

- Four specific requests for road maintenance units.

- Seven wage comparison studies for various public works related roles.

- Two contract samplings of municipal sewer authorities.

*Per-query time savings:*

- Current: 10--20 minutes of manual cleanup

- New: approximately 2 minutes of spot-checking, no manual cleanup

- Estimated time saved per query: 8--18 minutes.

*Annual Query Time Savings:*

- 12 queries/year \* (8--18 minutes/query) = 1.6--3.6 hours/year

- This estimate is intentionally conservative. It does not include real
  benefits that are harder to quantify:

  - Quick lookups (which in practice also require manual filtering.)

  - Multistep analyses requiring repeated queries.

  - Time saved by eliminating either/or classification ambiguity.

  - Time saved by reducing misclassification-driven rework and
    filtering.

- If these excluded benefits were included, query time savings could
  plausibly reach 5--10 hours/year, further offsetting classification
  costs.

*Net Annual Impact and Overall Assessment:*

- Gross classification time: 45.5 hours/year (less than 1 hour/week.)

- Query and filtering time reduction: 1.6--3.6 hours/year.

- **Net increase in staff time: 34--36 hours/year.**

- New system enables service-level analyses (water, sewer, solid waste,
  etc.) that were previously impossible.

The new system requires added upfront classification time, partially
offset by query time savings. Strategic benefits further offset the
added cost:

- Accurate multi-service classifications eliminate the 10--15%
  false-positive rate.

- Granular service-level analyses become possible for the first time.

- Institutional-knowledge dependency decreases with standardized NAICS
  use.

### Appendix II: Training Exercise Analysis

Three coders independently classified 10 contracts under the proposed
NAICS_All system. Each coder produced a complete code set for each
contract. Then, we simulated queries against each coder's codes to
answer: what percentage of relevant contracts would a researcher find
using different search strategies?

**Sample:** Three coders working independently classified 10 contracts
selected for varying classification difficulty:

- Three "easy" contracts with narrow scope (road commission, highway
  department)

- Two "medium" contracts with wider scope (thruway authority, all public
  works)

- Five "hard" contracts with widest scope (county-wide CBA, entire city
  government)

**Procedure:**

- Round 1: 7 contracts classified with general guidance.

- Round 2: 3 contracts classified with detailed handbook and feedback
  from Round 1.

- Different contracts were used in each round, so comparisons between
  rounds are directional only.

**Methodology:**

For each contract, we computed the union of all NAICS prefixes assigned
by any coder. If at least one coder found a service, we treated it as if
it exists in the contract. This is a conservative methodology: it may
include services that are genuinely ambiguous or debatable whether the
given service is present in the contract. This means our capture rates
(84% overall, 44-67% for support services) are likely to understate
performance on *clearly identifiable services.* The tradeoff is to
ensure that we did not miss real services present in contracts.

For each coder, we calculated what fraction of the union they captured.
This answers: "if a service exists in a contract, what is the
probability that a single coder includes it in their classification?"

**Results:**

*Finding 1: Per-Coder Capture Rate*

When a service exists in a contract, a single coder captures it **84% of
the time** on average. All three coders performed in a similar range
(78--90%,) indicating this reflects task difficulty rather than
individual skill differences.

**This is the core comparison to the status quo:** Under NAICS_All, a
single coder captures 84% of identifiable services. Under the status
quo, exactly one code is assigned per contract, regardless of a) how
many services the contract actually covers, and b) whether that code
accurately reflects the contract's core function.

*Finding 2: 84% Capture Rate Decomposes by Service Type*

  -----------------------------------------------------------------------
  **Service Category**      **Avg. Coder          **Query Reliability**
                            Agreement**           
  ------------------------- --------------------- -----------------------
  Construction (roads,      3.0 / 3 coders        Excellent
  bridges, utilities                              
  infrastructure)                                 

  Public administration     2.75 / 3              Very good
  (police, courts, fire)                          

  Administrative support    2.6 / 3               Good

  Professional services     2.0 / 3               Moderate
  (engineering, surveying)                        

  Repair and Maintenance    1.33 / 3              Variable
  -----------------------------------------------------------------------

**\
Core government services:** When roads, utilities, police, or fire
services exist in a contract, coders reliably identify them. These are
the services for which NAICS queries are designed.

**General support roles:** mechanics, custodians, and maintenance
technicians show the most variation. As shown in the table above,
Repair & Maintenance averages 1.33 / 3 coders (44%), while Professional
Services averages 2.0 / 3 (67%). This pattern was consistent across
rounds, suggesting it reflects genuine ambiguity rather than coder error.

**The variation concentrates where it matters least.** NAICS is an
industry classification system, and queries targeting specific
occupations are better served by SOC codes. For industry-level queries
(roads, utilities, etc.), the appropriate use case for NAICS, coder
agreement is near-perfect.

*Finding 3: Methodology Matters More Than Difficulty*

Overall classification agreement improved from **48.2%** (Round 1,
role-level coding) to **94.4%** (Round 2, service-level coding). This
56 percentage point improvement demonstrates that process design, not
contract complexity, is the primary driver of reliability.

| Round | Methodology | Agreement | 95% CI |
|-------|------------|-----------|--------|
| Round 1 | Role-level (infer from job titles) | 48.2% | [35.7%, 62.5%] |
| Round 2 | Service-level (identify services directly) | 94.4% | [83.3%, 100%] |

*Note: Confidence intervals reflect sample size (n=56 Round 1; n=18
Round 2). Different contracts were used in each round, so comparisons
are directional.*

*Finding 4: Variation by Contract Scope*

  -----------------------------------------------------------------------
                                      **Agreement**
  ----------------------------------- -----------------------------------
  Narrow (road commission)            Near-perfect

  Wide (county CBAs, city             67--82%
  governments)                        
  -----------------------------------------------------------------------

For narrow contracts covering clear industries, all coders identified
identical services. The improvement in findability concentrates in wide
contracts where multiple services create classification ambiguity.

**Why Variation Occurs**

Coding variation concentrates in:

1.  Wide contracts (not narrow ones)

2.  General support roles (not core services)

3.  Roles with ambiguous departmental attribution

For example, as discussed, Whatcom County's CBA revealed that coders
tend to agree on core services but diverge on general support roles.

**What This Means for Query Performance**

*For Core Government Services:* Queries will be highly reliable. When
road maintenance, utilities, police, or fire services exist in a
contract, coders consistently identify them.

*For General Support Roles:* Queries will find approximately half of
relevant contracts. The other half are coded under different but equally
reasonable categories. Queries targeting specific occupations should use
SOC codes, which classify job titles directly.

*The Tradeoff:* We gain the ability to query for multiple services per
contract, with near-perfect reliability for core government services.
The variation in general support roles has limited practical impact
because those queries should use SOC codes anyways.

**Limitations**

These findings are based on 10 contracts and 3 coders. The sample was
selected to represent different classification difficulties and was not
randomly drawn from the population. Results should be interpreted
directionally, and specific percentages should be treated as
approximate, not precise predictions of production performance.

*Key Uncertainties:*

- Sample size: the consistency of the support role agreement rates
  (44-67%) across rounds provides some evidence of stability, but
  production performance will likely differ somewhat.

- Coder attention: coders worked carefully with time to review.
  Production coding under time pressure might show lower capture rates,
  though the handbook and training are designed to maintain quality.

- Generalization: results are based on PWD contracts as a sample of
  multi-service CBAs. Other categories of contracts may show different
  agreement patterns.

*This Analysis Cannot Prove:*

- That production performance will match exercise performance.

- That the 44-67% support role rates generalize to all categories of wide contracts.

- That staff will consistently apply the new system without ongoing
  training.

**Despite these limitations, the core finding is robust:** NAICS_All
enables capture of 84% of identifiable services (vs. exactly one
identifiable service under the status quo), with near-perfect
reliability for core government services. The variation concentrates in
general support roles which are better served by SOC queries. Even if
production capture rates are lower, multiple codes will still capture
more services than one code.

### Appendix III: Recommended Query Approaches

Based on our testing, these search strategies minimize the risk of
missing contracts. Public sector queries should always be run with Trade
= PSD001 to exclude private sector contractors performing similar work.

**Core Government Services (high reliability; use NAICS)**

  -----------------------------------------------------------------------
  **Query Topic**         **NAICS Query**  **Notes**
  ----------------------- ---------------- ------------------------------
  Road construction       237310           Road maintenance is
                                           consistently coded

  Police protection       922120           Police protection is
                                           consistently coded

  Fire protection         922160           Fire protection is
                                           consistently coded

  Water and sewer         2213xx OR 237xxx Includes utility system
                                           construction codes to ensure
                                           capture of "Other Heavy and
                                           Civil Engineering"
  -----------------------------------------------------------------------

**General Support Roles (consider SOC queries first; if NAICS needed,
search multiple families)**

  -----------------------------------------------------------------------
  **Query Topic**         **NAICS Query**  **Better Alternative**
  ----------------------- ---------------- ------------------------------
  Building and facilities 236xxx OR 561xxx SOC codes for specific
  work                    OR 237xxx        occupations

  Fleet and mechanics     237xxx OR 811xxx SOC codes for auto mechanics,
                                           service technicians

  All infrastructure work 237xxx OR 238xxx Broad capture; expect manual
                          OR 221xxx OR     filtering
                          561xxx           
  -----------------------------------------------------------------------

"OR" searches (looking for multiple code families) are essential for
general support services because NAICS classifies industries, not
occupations. For queries targeting specific job titles, SOC codes
provide more reliable results.

[^1]: See Benefit 1: "Secondary Services," and Appendix II: "Training
    Exercise Analysis"

[^2]: See "What Does it Cost?", and Appendix I: "Time Cost
    Calculations."

[^3]: See Appendix III: "Recommended Query Strategies."

[^4]: See Appendix II: "Training Exercise Analysis."

[^5]: See Appendix I: "Time Cost Calculations."

[^6]: See Appendix III: "Recommended Query Strategies."
