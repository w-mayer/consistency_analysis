# =============================================================================
# NAICS CONSISTENCY ANALYSIS: IDEAL WORKFLOW REFACTOR
# =============================================================================
"""
This notebook implements the 6-phase ideal workflow for analyzing
inter-coder reliability in NAICS classification.

PHASE 1: Data Preparation (including normalization FIRST)
PHASE 2: Descriptive Analysis (coder profiles, identification overlap)
PHASE 3: Core Metrics (classification agreement with CIs)
PHASE 4: Diagnostic Analysis (disagreement taxonomy, confusion matrix)
PHASE 5: Impact Simulation (query performance)
PHASE 6: Synthesis (summary tables, recommendations)

All metrics computed on NORMALIZED service names unless explicitly noted.
"""

# =============================================================================
# IMPORTS
# =============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from collections import defaultdict
from scipy import stats
# Levenshtein is optional - only needed for discovery phase
try:
    from Levenshtein import ratio as levenshtein_ratio
    HAS_LEVENSHTEIN = True
except ImportError:
    HAS_LEVENSHTEIN = False
    def levenshtein_ratio(s1, s2):
        """Fallback: simple similarity based on shared characters."""
        if not s1 or not s2:
            return 0.0
        set1, set2 = set(s1.lower()), set(s2.lower())
        return len(set1 & set2) / len(set1 | set2)

# Set random seed for reproducibility
np.random.seed(42)

# =============================================================================
# PHASE 1: DATA PREPARATION
# =============================================================================
# Goal: Load, clean, and normalize data BEFORE any analysis
# =============================================================================

# -----------------------------------------------------------------------------
# 1.1 Load Raw Data
# -----------------------------------------------------------------------------

def load_data(filepath):
    """Load raw CSV data."""
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows from {filepath}")
    return df

# -----------------------------------------------------------------------------
# 1.2 Basic Cleaning
# -----------------------------------------------------------------------------

def clean_data(df):
    """
    Apply basic cleaning operations:
    - Strip whitespace from string columns
    - Extract NAICS prefix
    - Flag multi-code entries
    - Create lookup keys
    """
    df = df.copy()
    
    # Strip whitespace from key columns
    df['Contract'] = df['Contract'].str.strip()
    df['Service_Raw'] = df['Service_Raw'].str.strip()
    
    # Extract 2-digit prefix
    df['prefix'] = df['NAICS_Raw'].astype(str).str[:2]
    df['prefix'] = df['prefix'].replace('na', np.nan)
    
    # Flag rows with valid NAICS
    df['has_naics'] = df['NAICS_Raw'].notna() & (df['NAICS_Raw'] != '')
    
    # Flag multi-code entries (semicolon-delimited)
    df['is_multicode'] = df['NAICS_Raw'].str.contains(';', na=False)
    
    # Create lookup key for service matching
    df['lookup_key'] = df['Contract'] + '|' + df['Service_Raw']
    
    print(f"Cleaning complete. {df['has_naics'].sum()} rows with valid NAICS.")
    print(f"Multi-code entries: {df['is_multicode'].sum()}")
    
    return df

# -----------------------------------------------------------------------------
# 1.3 Service Name Normalization (THE KEY STEP - DO THIS EARLY)
# -----------------------------------------------------------------------------

# Define equivalence mappings based on manual review of fuzzy clusters
SERVICE_EQUIVALENCES = {
    'Equipment operator': [
        'Equipment operator',
        'Heavy equipment operator', 
        'Motor equipment operator',
        'Senior heavy equipment operator',
    ],
    'Mechanic': [
        'Mechanic',
        'Mechanic II',
    ],
    'Groundskeeper': [
        'Groundskeeper',
        'Groundskeeping',
    ],
    'Fire protection': [
        'Fire protection',
        'Fire prevention',
    ],
    'Sewage treatment': [
        'Sewage treatment',
        'Sewage related',
    ],
    'Road maintenance': [
        'Road maintenance',
        'Highway and road maintenance',
        'Road related',
    ],
    'Traffic control': [
        'Traffic control crew',
        'Traffic maintenance',
        'Traffic and vegetation control',
        'Traffic and vegetation control mechanic',
    ],
    'Truck driver': [
        'Truck driver',
        'Truck driver apprentice',
    ],
    'Building maintenance': [
        'Building maintenance',
        'Building and grounds maintenance',
    ],
    'Parks maintenance': [
        'Park maintenance',
        'Parks and landscaping',
    ],
    'Sewer maintenance': [
        'Sewer maintenance',
        'Sewer repair',
        'Sewer line maintenance',
    ],
    'Recreation': [
        'Recreation',
        'Recreation programs',
        'Recreation and lifeguards',
    ],
    'Engineering': [
        'Engineering',
        'Engineering ',  # trailing space variant
    ],
    'Surveying': [
        'Surveying',
        'Land surveyor',
        'County surveyor',
    ],
}

def build_normalization_map(equivalences):
    """Build mapping from variant names to canonical names."""
    norm_map = {}
    for canonical, variants in equivalences.items():
        for variant in variants:
            norm_map[variant.lower().strip()] = canonical
    return norm_map

def normalize_service_names(df, equivalences=SERVICE_EQUIVALENCES):
    """
    Apply service name normalization to dataframe.
    Creates 'Service_Normalized' column.
    """
    df = df.copy()
    norm_map = build_normalization_map(equivalences)
    
    def normalize(service_name):
        if pd.isna(service_name):
            return service_name
        key = service_name.lower().strip()
        return norm_map.get(key, service_name)
    
    df['Service_Normalized'] = df['Service_Raw'].apply(normalize)
    
    # Report normalization impact
    raw_unique = df['Service_Raw'].nunique()
    norm_unique = df['Service_Normalized'].nunique()
    merged = raw_unique - norm_unique
    
    print(f"Service name normalization complete.")
    print(f"  Unique services (raw): {raw_unique}")
    print(f"  Unique services (normalized): {norm_unique}")
    print(f"  Services merged: {merged}")
    
    return df

# -----------------------------------------------------------------------------
# 1.4 Fuzzy Matching Discovery (for identifying new equivalences)
# -----------------------------------------------------------------------------

def discover_similar_services(df, threshold=0.7):
    """
    Use Levenshtein ratio to find potentially equivalent service names.
    Run this ONCE to build SERVICE_EQUIVALENCES, then hardcode the results.
    
    Returns list of (service1, service2, similarity) tuples.
    """
    services = df['Service_Raw'].unique()
    similar_pairs = []
    
    for i, s1 in enumerate(services):
        for s2 in services[i+1:]:
            ratio = levenshtein_ratio(s1.lower(), s2.lower())
            if ratio >= threshold:
                similar_pairs.append((s1, s2, ratio))
    
    return sorted(similar_pairs, key=lambda x: -x[2])

def cluster_similar_services(df, threshold=0.7):
    """
    Build connected components of similar service names.
    Returns list of sets, where each set is a cluster of similar names.
    """
    services = df['Service_Raw'].unique()
    
    # Build adjacency list
    similar = defaultdict(set)
    for i, s1 in enumerate(services):
        for s2 in services[i+1:]:
            ratio = levenshtein_ratio(s1.lower(), s2.lower())
            if ratio >= threshold:
                similar[s1].add(s2)
                similar[s2].add(s1)
    
    # Find connected components (DFS)
    visited = set()
    clusters = []
    
    for service in services:
        if service not in visited and service in similar:
            cluster = set()
            stack = [service]
            while stack:
                s = stack.pop()
                if s not in visited:
                    visited.add(s)
                    cluster.add(s)
                    stack.extend(similar[s] - visited)
            if len(cluster) > 1:
                clusters.append(cluster)
    
    return clusters

# -----------------------------------------------------------------------------
# 1.5 Validation
# -----------------------------------------------------------------------------

def validate_preparation(df):
    """Run validation checks on prepared data."""
    checks = []
    
    # Check 1: Service_Normalized exists
    checks.append(('Service_Normalized column exists', 'Service_Normalized' in df.columns))
    
    # Check 2: No null contracts
    checks.append(('No null Contract IDs', df['Contract'].notna().all()))
    
    # Check 3: Normalization reduced unique count
    raw = df['Service_Raw'].nunique()
    norm = df['Service_Normalized'].nunique()
    checks.append((f'Normalization merged services ({raw} → {norm})', norm < raw))
    
    # Check 4: Expected columns present
    expected = ['Contract', 'Difficulty', 'Service_Raw', 'Service_Normalized', 
                'Coder', 'Round', 'NAICS_Raw', 'prefix']
    checks.append(('All expected columns present', all(c in df.columns for c in expected)))
    
    print("\nData Preparation Validation:")
    print("-" * 50)
    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check_name}")
    
    all_passed = all(passed for _, passed in checks)
    print("-" * 50)
    print(f"  {'All checks passed!' if all_passed else 'SOME CHECKS FAILED'}")
    
    return all_passed


# =============================================================================
# PHASE 2: DESCRIPTIVE ANALYSIS
# =============================================================================
# Goal: Understand coder behavior and identification patterns
# =============================================================================

# -----------------------------------------------------------------------------
# 2.1 Coder Behavior Profiles
# -----------------------------------------------------------------------------

def analyze_coder_profiles(df):
    """
    Analyze how each coder uses different NAICS code families.
    Returns DataFrame with coder prefix usage percentages.
    """
    # Count prefix usage by coder
    prefix_counts = (
        df[df['prefix'].notna()]
        .groupby(['Coder', 'prefix'])
        .size()
        .rename('n')
        .reset_index()
    )
    
    # Calculate percentages
    prefix_counts['pct'] = (
        prefix_counts['n'] / 
        prefix_counts.groupby('Coder')['n'].transform('sum') * 100
    )
    
    # Pivot for comparison
    pivot = prefix_counts.pivot(index='Coder', columns='prefix', values='pct').fillna(0)
    
    # Get top 5 prefixes overall
    top_prefixes = (
        prefix_counts.groupby('prefix')['n'].sum()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )
    
    print("\nCoder Prefix Usage (% of each coder's assignments):")
    print("-" * 60)
    print(pivot[top_prefixes].round(1).to_string())
    
    return pivot, top_prefixes

def identify_coder_tendencies(pivot, top_prefixes):
    """
    Identify systematic coder tendencies based on deviation from mean.
    """
    print("\nCoder Tendencies (deviation from group mean):")
    print("-" * 60)
    
    for prefix in top_prefixes:
        col = pivot[prefix]
        mean = col.mean()
        for coder in col.index:
            val = col[coder]
            diff = val - mean
            if abs(diff) > 5:  # More than 5pp deviation
                direction = "favors" if diff > 0 else "underuses"
                print(f"  {coder} {direction} {prefix}xxx: {val:.1f}% vs {mean:.1f}% mean ({diff:+.1f}pp)")

# -----------------------------------------------------------------------------
# 2.2 Identification Overlap Analysis
# -----------------------------------------------------------------------------

def analyze_identification_overlap(df, service_col='Service_Normalized'):
    """
    Analyze how often coders identify the same services.
    
    Returns:
    - overlap_stats: Dict with overlap statistics by round
    - service_coder_counts: DataFrame with coder counts per service
    """
    # Count coders per service per contract
    service_coders = (
        df.groupby(['Contract', 'Round', service_col])['Coder']
        .apply(lambda x: set(x))
        .reset_index()
    )
    service_coders['num_coders'] = service_coders['Coder'].apply(len)
    
    # Compute overlap statistics by round
    overlap_stats = {}
    for round_num in df['Round'].unique():
        round_data = service_coders[service_coders['Round'] == round_num]
        total = len(round_data)
        
        all_three = (round_data['num_coders'] == 3).sum()
        two_coders = (round_data['num_coders'] == 2).sum()
        one_coder = (round_data['num_coders'] == 1).sum()
        
        overlap_stats[round_num] = {
            'total_services': total,
            'all_3_coders': all_three,
            'all_3_pct': all_three / total * 100 if total > 0 else 0,
            '2_coders': two_coders,
            '2_coders_pct': two_coders / total * 100 if total > 0 else 0,
            '1_coder': one_coder,
            '1_coder_pct': one_coder / total * 100 if total > 0 else 0,
        }
    
    print("\nIdentification Overlap by Round:")
    print("-" * 60)
    print(f"{'Metric':<30} {'Round 1':>12} {'Round 2':>12}")
    print("-" * 60)
    for metric in ['all_3_pct', '2_coders_pct', '1_coder_pct']:
        label = metric.replace('_pct', '').replace('_', ' ').title()
        r1 = overlap_stats.get(1, {}).get(metric, 0)
        r2 = overlap_stats.get(2, {}).get(metric, 0)
        print(f"{label:<30} {r1:>11.1f}% {r2:>11.1f}%")
    
    return overlap_stats, service_coders


# =============================================================================
# PHASE 3: CORE METRICS
# =============================================================================
# Goal: Compute classification agreement with confidence intervals
# All metrics use NORMALIZED service names
# =============================================================================

# -----------------------------------------------------------------------------
# 3.1 Bootstrap Confidence Intervals
# -----------------------------------------------------------------------------

def bootstrap_ci(data, statistic=np.mean, n_bootstrap=1000, ci=0.95):
    """
    Calculate bootstrap confidence interval for a statistic.
    
    Parameters:
    - data: array-like of values
    - statistic: function to compute (default: mean)
    - n_bootstrap: number of bootstrap samples
    - ci: confidence level (default: 95%)
    
    Returns: (point_estimate, lower_bound, upper_bound)
    """
    data = np.array(data)
    n = len(data)
    
    if n == 0:
        return (np.nan, np.nan, np.nan)
    
    point_estimate = statistic(data)
    
    # Bootstrap resampling
    bootstrap_stats = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats.append(statistic(sample))
    
    alpha = 1 - ci
    lower = np.percentile(bootstrap_stats, alpha/2 * 100)
    upper = np.percentile(bootstrap_stats, (1 - alpha/2) * 100)
    
    return (point_estimate, lower, upper)

# -----------------------------------------------------------------------------
# 3.2 Classification Agreement
# -----------------------------------------------------------------------------

def get_overlapping_services(df, service_col='Service_Normalized'):
    """
    Get services identified by 2+ coders within each contract.
    
    Returns DataFrame with columns:
    - Contract, Service, Coders (list), NAICS_codes (list), num_coders
    """
    service_groups = df.groupby(['Contract', 'Round', 'Difficulty', service_col]).agg({
        'Coder': list,
        'NAICS_Raw': list
    }).reset_index()
    
    service_groups['num_coders'] = service_groups['Coder'].apply(len)
    overlaps = service_groups[service_groups['num_coders'] >= 2].copy()
    
    return overlaps

def check_agreement(naics_list):
    """
    Check if all NAICS codes in list are identical.
    Returns: True (agree), False (disagree), or None (insufficient data)
    """
    codes = [str(c).strip() for c in naics_list if pd.notna(c) and str(c).strip()]
    if len(codes) < 2:
        return None
    return len(set(codes)) == 1

def compute_agreement_rate(df, service_col='Service_Normalized', with_ci=True):
    """
    Compute classification agreement rate for overlapping services.
    
    Returns dict with:
    - agreement_rate: point estimate
    - ci_lower, ci_upper: 95% CI bounds
    - n: number of overlapping services
    - agreements: count of agreements
    """
    overlaps = get_overlapping_services(df, service_col)
    
    if len(overlaps) == 0:
        return None
    
    # Check agreement for each overlap
    overlaps['agreed'] = overlaps['NAICS_Raw'].apply(check_agreement)
    
    # Filter to valid comparisons
    valid = overlaps[overlaps['agreed'].notna()]
    
    if len(valid) == 0:
        return None
    
    # Compute agreement
    agreements = valid['agreed'].astype(int).tolist()
    n = len(agreements)
    agree_count = sum(agreements)
    
    if with_ci:
        point, lower, upper = bootstrap_ci(agreements)
    else:
        point = np.mean(agreements)
        lower, upper = np.nan, np.nan
    
    return {
        'agreement_rate': point,
        'ci_lower': lower,
        'ci_upper': upper,
        'n': n,
        'agreements': agree_count
    }

def compute_agreement_matrix(df, service_col='Service_Normalized'):
    """
    Compute agreement rates by Round and Difficulty.
    
    Returns DataFrame with agreement metrics for each segment.
    """
    results = []
    
    # Overall
    overall = compute_agreement_rate(df, service_col)
    if overall:
        results.append({'Segment': 'Overall', **overall})
    
    # By Round
    for round_num in sorted(df['Round'].unique()):
        df_round = df[df['Round'] == round_num]
        rate = compute_agreement_rate(df_round, service_col)
        if rate:
            results.append({'Segment': f'Round {round_num}', **rate})
    
    # By Difficulty
    for diff in ['Easy', 'Medium', 'Hard']:
        df_diff = df[df['Difficulty'] == diff]
        rate = compute_agreement_rate(df_diff, service_col)
        if rate:
            results.append({'Segment': diff, **rate})
    
    # By Round × Difficulty
    for round_num in sorted(df['Round'].unique()):
        for diff in ['Easy', 'Medium', 'Hard']:
            df_subset = df[(df['Round'] == round_num) & (df['Difficulty'] == diff)]
            rate = compute_agreement_rate(df_subset, service_col)
            if rate:
                results.append({'Segment': f'R{round_num} {diff}', **rate})
    
    results_df = pd.DataFrame(results)
    return results_df

def print_agreement_table(results_df):
    """Pretty print agreement results."""
    print("\nClassification Agreement (Normalized Service Names, 95% CI):")
    print("-" * 70)
    print(f"{'Segment':<15} {'Agreement':>12} {'95% CI':>20} {'n':>8}")
    print("-" * 70)
    
    for _, row in results_df.iterrows():
        rate = row['agreement_rate'] * 100
        ci_low = row['ci_lower'] * 100
        ci_high = row['ci_upper'] * 100
        ci_str = f"[{ci_low:.1f}%, {ci_high:.1f}%]"
        print(f"{row['Segment']:<15} {rate:>11.1f}% {ci_str:>20} {row['n']:>8}")

# -----------------------------------------------------------------------------
# 3.3 Pairwise Coder Analysis
# -----------------------------------------------------------------------------

def compute_pairwise_agreement(df, service_col='Service_Normalized'):
    """
    Compute agreement rates for each coder pair.
    
    Returns DataFrame with pairwise agreement statistics.
    """
    overlaps = get_overlapping_services(df, service_col)
    
    # For each overlap, get coder-code pairs
    pair_agreements = defaultdict(list)
    
    for _, row in overlaps.iterrows():
        coders = row['Coder']
        codes = row['NAICS_Raw']
        
        # Build coder -> code mapping
        coder_codes = dict(zip(coders, codes))
        
        # Check each pair
        for c1, c2 in combinations(sorted(coder_codes.keys()), 2):
            code1 = str(coder_codes[c1]).strip() if pd.notna(coder_codes[c1]) else ''
            code2 = str(coder_codes[c2]).strip() if pd.notna(coder_codes[c2]) else ''
            
            if code1 and code2:
                agreed = code1 == code2
                pair_agreements[(c1, c2)].append(1 if agreed else 0)
    
    # Compute statistics
    results = []
    for pair, agreements in pair_agreements.items():
        point, lower, upper = bootstrap_ci(agreements)
        results.append({
            'Coder_Pair': f"{pair[0]}-{pair[1]}",
            'agreement_rate': point,
            'ci_lower': lower,
            'ci_upper': upper,
            'n': len(agreements)
        })
    
    return pd.DataFrame(results)

def compute_jaccard_similarity(df, service_col='Service_Normalized'):
    """
    Compute Jaccard similarity of code sets between coders for each contract.
    
    Returns DataFrame with Jaccard metrics per contract.
    """
    results = []
    
    for contract in df['Contract'].unique():
        df_contract = df[df['Contract'] == contract]
        difficulty = df_contract['Difficulty'].iloc[0]
        round_num = df_contract['Round'].iloc[0]
        
        # Get code sets by coder
        coder_codes = {}
        for coder in df_contract['Coder'].unique():
            coder_df = df_contract[df_contract['Coder'] == coder]
            codes = set()
            for naics in coder_df['NAICS_Raw'].dropna():
                # Handle multi-codes
                for code in str(naics).split(';'):
                    code = code.strip()
                    if code:
                        codes.add(code)
            coder_codes[coder] = codes
        
        # Compute pairwise Jaccard
        jaccard_scores = []
        pairs = []
        for c1, c2 in combinations(sorted(coder_codes.keys()), 2):
            set1, set2 = coder_codes[c1], coder_codes[c2]
            if set1 or set2:  # At least one non-empty
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                jaccard = intersection / union if union > 0 else 0
                jaccard_scores.append(jaccard)
                pairs.append((c1, c2, jaccard))
        
        results.append({
            'Contract': contract,
            'Difficulty': difficulty,
            'Round': round_num,
            'mean_jaccard': np.mean(jaccard_scores) if jaccard_scores else np.nan,
            'min_jaccard': np.min(jaccard_scores) if jaccard_scores else np.nan,
            'pairs': pairs
        })
    
    return pd.DataFrame(results)


# =============================================================================
# PHASE 4: DIAGNOSTIC ANALYSIS
# =============================================================================
# Goal: Understand WHERE and WHY disagreements occur
# =============================================================================

# -----------------------------------------------------------------------------
# 4.1 Disagreement Taxonomy
# -----------------------------------------------------------------------------

def extract_disagreements(df, service_col='Service_Normalized'):
    """
    Extract all disagreements with details for categorization.
    
    Returns DataFrame with disagreement details.
    """
    overlaps = get_overlapping_services(df, service_col)
    overlaps['agreed'] = overlaps['NAICS_Raw'].apply(check_agreement)
    
    disagreements = overlaps[overlaps['agreed'] == False].copy()
    
    # Add analysis columns
    def get_prefixes(codes):
        prefixes = set()
        for c in codes:
            if pd.notna(c):
                code_str = str(c).split(';')[0][:2]
                if code_str and code_str != 'na':
                    prefixes.add(code_str)
        return prefixes
    
    disagreements['prefixes'] = disagreements['NAICS_Raw'].apply(get_prefixes)
    disagreements['same_prefix'] = disagreements['prefixes'].apply(lambda x: len(x) == 1)
    disagreements['unique_codes'] = disagreements['NAICS_Raw'].apply(
        lambda x: sorted(set(str(c) for c in x if pd.notna(c)))
    )
    
    return disagreements

def categorize_disagreement(row):
    """
    Categorize a disagreement by type.
    Returns category string.
    """
    if row['same_prefix']:
        return 'Granularity (same prefix)'
    
    prefixes = row['prefixes']
    
    # Check for common confusion patterns
    if {'23', '56'} & prefixes and len(prefixes) == 2:
        return 'Construction vs Admin (23/56)'
    if {'22', '23'} & prefixes and len(prefixes) == 2:
        return 'Utilities vs Construction (22/23)'
    if {'54', '92'} & prefixes:
        return 'Professional vs Public Admin (54/92)'
    
    return 'Other substantive'

def analyze_disagreement_taxonomy(df, service_col='Service_Normalized'):
    """
    Categorize all disagreements and compute distribution.
    """
    disagreements = extract_disagreements(df, service_col)
    
    if len(disagreements) == 0:
        print("No disagreements found!")
        return None
    
    disagreements['category'] = disagreements.apply(categorize_disagreement, axis=1)
    
    # Compute distribution
    category_counts = disagreements['category'].value_counts()
    category_pcts = (category_counts / len(disagreements) * 100).round(1)
    
    print("\nDisagreement Taxonomy:")
    print("-" * 60)
    print(f"Total disagreements: {len(disagreements)}")
    print()
    for cat, count in category_counts.items():
        pct = category_pcts[cat]
        print(f"  {cat:<35} {count:>3} ({pct:>5.1f}%)")
    
    # Compute addressable percentage
    granularity = category_counts.get('Granularity (same prefix)', 0)
    addressable = len(disagreements) - granularity  # All non-granularity are "addressable"
    addressable_pct = (len(disagreements) - granularity) / len(disagreements) * 100
    
    print()
    print(f"  Granularity (low impact): {granularity} ({granularity/len(disagreements)*100:.1f}%)")
    print(f"  Substantive (addressable): {addressable} ({addressable_pct:.1f}%)")
    
    return disagreements

# -----------------------------------------------------------------------------
# 4.2 Prefix Confusion Matrix
# -----------------------------------------------------------------------------

def build_confusion_matrix(df, service_col='Service_Normalized'):
    """
    Build matrix showing which NAICS prefixes are confused with each other.
    """
    disagreements = extract_disagreements(df, service_col)
    
    confusion_counts = defaultdict(int)
    
    for _, row in disagreements.iterrows():
        prefixes = sorted(row['prefixes'])
        for p1, p2 in combinations(prefixes, 2):
            confusion_counts[(p1, p2)] += 1
    
    # Build matrix
    all_prefixes = sorted(set(p for pair in confusion_counts.keys() for p in pair))
    matrix = pd.DataFrame(0, index=all_prefixes, columns=all_prefixes)
    
    for (p1, p2), count in confusion_counts.items():
        matrix.loc[p1, p2] = count
        matrix.loc[p2, p1] = count
    
    return matrix, confusion_counts

def print_confusion_pairs(confusion_counts, top_n=10):
    """Print top confused prefix pairs."""
    PREFIX_NAMES = {
        '22': 'Utilities',
        '23': 'Construction',
        '48': 'Transportation',
        '54': 'Professional',
        '56': 'Admin/Support',
        '71': 'Recreation',
        '81': 'Repair/Maint',
        '92': 'Public Admin',
    }
    
    print("\nTop Confused Prefix Pairs:")
    print("-" * 60)
    
    sorted_pairs = sorted(confusion_counts.items(), key=lambda x: -x[1])[:top_n]
    for (p1, p2), count in sorted_pairs:
        name1 = PREFIX_NAMES.get(p1, '?')
        name2 = PREFIX_NAMES.get(p2, '?')
        print(f"  {p1} ({name1}) ↔ {p2} ({name2}): {count} disagreements")

# -----------------------------------------------------------------------------
# 4.3 Cross-Contract Consistency
# -----------------------------------------------------------------------------

def analyze_cross_contract_consistency(df, service_col='Service_Normalized'):
    """
    Check if the same service gets the same code across different contracts.
    """
    # Group by normalized service name across ALL contracts
    service_codes = df.groupby(service_col).agg({
        'NAICS_Raw': lambda x: [c for c in x.dropna().unique()],
        'Contract': lambda x: list(x.unique()),
    }).reset_index()
    
    service_codes['num_contracts'] = service_codes['Contract'].apply(len)
    
    # Only analyze services in 2+ contracts
    multi_contract = service_codes[service_codes['num_contracts'] >= 2].copy()
    
    # Check consistency
    def get_unique_primary_codes(codes):
        """Get unique primary codes (first code if multi-code)."""
        primary = set()
        for c in codes:
            if pd.notna(c):
                primary.add(str(c).split(';')[0])
        return sorted(primary)
    
    multi_contract['unique_codes'] = multi_contract['NAICS_Raw'].apply(get_unique_primary_codes)
    multi_contract['num_codes'] = multi_contract['unique_codes'].apply(len)
    multi_contract['is_consistent'] = multi_contract['num_codes'] == 1
    
    # Report
    consistent = multi_contract['is_consistent'].sum()
    total = len(multi_contract)
    
    print("\nCross-Contract Consistency:")
    print("-" * 60)
    print(f"Services appearing in 2+ contracts: {total}")
    print(f"Consistently coded: {consistent} ({consistent/total*100:.1f}%)")
    print(f"Inconsistently coded: {total - consistent} ({(total-consistent)/total*100:.1f}%)")
    
    # Show inconsistent services
    inconsistent = multi_contract[~multi_contract['is_consistent']].sort_values('num_codes', ascending=False)
    
    if len(inconsistent) > 0:
        print("\nInconsistent Services (need handbook guidance):")
        for _, row in inconsistent.head(10).iterrows():
            print(f"  {row[service_col]:<35} → {row['unique_codes']}")
    
    return multi_contract


# =============================================================================
# PHASE 5: IMPACT SIMULATION
# =============================================================================
# Goal: Quantify how coder disagreement affects search performance
# =============================================================================

# -----------------------------------------------------------------------------
# 5.1 Query Scenario Definition
# -----------------------------------------------------------------------------

QUERY_SCENARIOS = {
    'road_maintenance': ['237310', '237'],
    'police_services': ['922120', '922'],
    'water_utilities': ['221310', '221'],
    'sewer_services': ['221320', '237110', '221', '237'],
    'fire_protection': ['922160', '922'],
    'parks_recreation': ['712190', '713940', '561730', '712', '713', '561'],
    'building_maintenance': ['236220', '561210', '236', '561'],
    'administrative': ['921130', '921190', '921'],
    'professional_services': ['541330', '541370', '541512', '541'],
    'corrections': ['922140', '922'],
}

# -----------------------------------------------------------------------------
# 5.2 Query Matching Functions
# -----------------------------------------------------------------------------

def get_codes_set(naics_str):
    """Parse NAICS codes from semicolon-delimited string into a set."""
    if pd.isna(naics_str) or naics_str == '':
        return set()
    return set(str(naics_str).strip().split(';'))

def query_matches(code_set, query_codes):
    """
    Check if a code set satisfies a query.
    Returns True if ANY code matches ANY query code (exact or prefix).
    """
    for code in code_set:
        code_str = str(code).strip()
        for query in query_codes:
            query_str = str(query).strip()
            if code_str == query_str or code_str.startswith(query_str):
                return True
    return False

# -----------------------------------------------------------------------------
# 5.3 Query Simulation
# -----------------------------------------------------------------------------

def simulate_query_performance(df, service_col='Service_Normalized'):
    """
    Simulate query performance for all contracts.
    
    Returns:
    - results: List of per-contract simulation results
    - summary: Aggregate statistics
    """
    results = []
    
    for contract in df['Contract'].unique():
        df_contract = df[df['Contract'] == contract]
        difficulty = df_contract['Difficulty'].iloc[0]
        
        # Build code sets for each coder
        codes_by_coder = {}
        for coder in df_contract['Coder'].unique():
            coder_df = df_contract[df_contract['Coder'] == coder]
            codes = set()
            for naics in coder_df['NAICS_Raw'].dropna():
                codes.update(get_codes_set(naics))
            codes_by_coder[coder] = codes
        
        # Union of all coders
        union_codes = set.union(*codes_by_coder.values()) if codes_by_coder else set()
        
        # Test each query
        contract_result = {
            'contract': contract,
            'difficulty': difficulty,
            'union_hits': [],
            'coder_hits': {c: [] for c in codes_by_coder},
        }
        
        for query_name, query_codes in QUERY_SCENARIOS.items():
            union_hit = query_matches(union_codes, query_codes)
            contract_result['union_hits'].append(union_hit)
            
            for coder, codes in codes_by_coder.items():
                coder_hit = query_matches(codes, query_codes)
                contract_result['coder_hits'][coder].append(coder_hit)
        
        results.append(contract_result)
    
    return results

def compute_miss_rates(simulation_results):
    """
    Compute miss rates from simulation results.
    
    Returns DataFrame with per-contract miss rates by coder.
    """
    rows = []
    
    for result in simulation_results:
        union_hits = sum(result['union_hits'])
        
        if union_hits > 0:
            row = {
                'Contract': result['contract'],
                'Difficulty': result['difficulty'],
                'Union_Hits': union_hits,
            }
            
            for coder, hits in result['coder_hits'].items():
                coder_hits = sum(hits)
                miss_rate = (union_hits - coder_hits) / union_hits * 100
                row[f'{coder}_Hits'] = coder_hits
                row[f'{coder}_Miss%'] = miss_rate
            
            rows.append(row)
    
    return pd.DataFrame(rows)

def summarize_query_performance(miss_rates_df):
    """
    Summarize query performance across contracts.
    """
    print("\nQuery Performance Simulation Results:")
    print("-" * 70)
    
    # Per-contract results
    print("\nPer-Contract Miss Rates:")
    coder_cols = [c for c in miss_rates_df.columns if c.endswith('_Miss%')]
    display_cols = ['Contract', 'Difficulty', 'Union_Hits'] + coder_cols
    print(miss_rates_df[display_cols].to_string(index=False))
    
    # Aggregate by difficulty
    print("\nAverage Miss Rate by Difficulty:")
    for diff in ['Easy', 'Medium', 'Hard']:
        df_diff = miss_rates_df[miss_rates_df['Difficulty'] == diff]
        if len(df_diff) > 0:
            avg_miss = df_diff[coder_cols].mean().mean()
            print(f"  {diff}: {avg_miss:.1f}%")
    
    # Overall
    overall_avg = miss_rates_df[coder_cols].mean().mean()
    print(f"\nOverall average single-coder miss rate: {overall_avg:.1f}%")
    
    return overall_avg


# =============================================================================
# PHASE 6: SYNTHESIS
# =============================================================================
# Goal: Combine all findings into summary tables and recommendations
# =============================================================================

# -----------------------------------------------------------------------------
# 6.1 Summary Metrics Table
# -----------------------------------------------------------------------------

def generate_summary_table(df, service_col='Service_Normalized'):
    """
    Generate the key metrics summary table for executive reporting.
    """
    metrics = {}
    
    # Classification agreement
    r1_hard = df[(df['Round'] == 1) & (df['Difficulty'] == 'Hard')]
    r2_hard = df[(df['Round'] == 2) & (df['Difficulty'] == 'Hard')]
    
    r1_rate = compute_agreement_rate(r1_hard, service_col)
    r2_rate = compute_agreement_rate(r2_hard, service_col)
    
    if r1_rate:
        metrics['R1 Hard Agreement'] = f"{r1_rate['agreement_rate']*100:.1f}%"
    if r2_rate:
        metrics['R2 Hard Agreement'] = f"{r2_rate['agreement_rate']*100:.1f}%"
        metrics['R2 Hard 95% CI'] = f"[{r2_rate['ci_lower']*100:.1f}%, {r2_rate['ci_upper']*100:.1f}%]"
    
    # Improvement
    if r1_rate and r2_rate:
        improvement = (r2_rate['agreement_rate'] - r1_rate['agreement_rate']) * 100
        metrics['Improvement (R1→R2)'] = f"{improvement:+.0f}pp"
    
    print("\n" + "="*70)
    print("EXECUTIVE SUMMARY METRICS")
    print("="*70)
    for metric, value in metrics.items():
        print(f"  {metric:<30} {value}")
    
    return metrics

# -----------------------------------------------------------------------------
# 6.2 Visualization Suite
# -----------------------------------------------------------------------------

def plot_agreement_comparison(results_df, output_path=None):
    """
    Create grouped bar chart comparing Round 1 vs Round 2 agreement by difficulty.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract Round × Difficulty data
    r1_data = results_df[results_df['Segment'].str.startswith('R1')]
    r2_data = results_df[results_df['Segment'].str.startswith('R2')]
    
    difficulties = ['Easy', 'Medium', 'Hard']
    x = np.arange(len(difficulties))
    width = 0.35
    
    r1_rates = [r1_data[r1_data['Segment'] == f'R1 {d}']['agreement_rate'].values[0] * 100 
                if len(r1_data[r1_data['Segment'] == f'R1 {d}']) > 0 else 0 
                for d in difficulties]
    r2_rates = [r2_data[r2_data['Segment'] == f'R2 {d}']['agreement_rate'].values[0] * 100 
                if len(r2_data[r2_data['Segment'] == f'R2 {d}']) > 0 else 0 
                for d in difficulties]
    
    bars1 = ax.bar(x - width/2, r1_rates, width, label='Round 1 (Role-level)', color='steelblue')
    bars2 = ax.bar(x + width/2, r2_rates, width, label='Round 2 (Service-level)', color='darkorange')
    
    ax.set_xlabel('Contract Difficulty')
    ax.set_ylabel('Classification Agreement (%)')
    ax.set_title('Classification Agreement by Round and Difficulty')
    ax.set_xticks(x)
    ax.set_xticklabels(difficulties)
    ax.legend()
    ax.set_ylim(0, 105)
    
    # Add value labels
    for bar in bars1 + bars2:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{height:.0f}%',
                       xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig

def plot_coder_profiles(pivot, top_prefixes, output_path=None):
    """
    Create radar/spider chart of coder prefix usage profiles.
    """
    from math import pi
    
    categories = top_prefixes
    N = len(categories)
    
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # Complete the loop
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    colors = {'D': 'blue', 'G': 'green', 'W': 'orange'}
    
    for coder in pivot.index:
        values = pivot.loc[coder, top_prefixes].values.tolist()
        values += values[:1]  # Complete the loop
        
        ax.plot(angles, values, 'o-', linewidth=2, label=coder, color=colors.get(coder, 'gray'))
        ax.fill(angles, values, alpha=0.1, color=colors.get(coder, 'gray'))
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([f'{p}xxx' for p in categories])
    ax.set_title('Coder NAICS Prefix Usage Profiles')
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig

def plot_miss_rate_heatmap(miss_rates_df, output_path=None):
    """
    Create heatmap of miss rates by contract and coder.
    """
    # Prepare data
    coder_cols = [c for c in miss_rates_df.columns if c.endswith('_Miss%')]
    plot_data = miss_rates_df.set_index('Contract')[coder_cols]
    plot_data.columns = [c.replace('_Miss%', '') for c in plot_data.columns]
    
    fig, ax = plt.subplots(figsize=(8, 10))
    
    sns.heatmap(plot_data, annot=True, fmt='.0f', cmap='RdYlGn_r',
                vmin=0, vmax=60, ax=ax, cbar_kws={'label': 'Miss Rate (%)'})
    
    ax.set_title('Query Miss Rates by Contract and Coder')
    ax.set_xlabel('Coder')
    ax.set_ylabel('Contract')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_full_analysis(filepath):
    """
    Execute the complete analysis workflow.
    """
    print("="*70)
    print("NAICS CONSISTENCY ANALYSIS - FULL WORKFLOW")
    print("="*70)
    
    # -------------------------------------------------------------------------
    # PHASE 1: DATA PREPARATION
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("PHASE 1: DATA PREPARATION")
    print("="*70)
    
    df = load_data(filepath)
    df = clean_data(df)
    df = normalize_service_names(df)
    
    if not validate_preparation(df):
        raise ValueError("Data preparation validation failed!")
    
    # -------------------------------------------------------------------------
    # PHASE 2: DESCRIPTIVE ANALYSIS
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("PHASE 2: DESCRIPTIVE ANALYSIS")
    print("="*70)
    
    pivot, top_prefixes = analyze_coder_profiles(df)
    identify_coder_tendencies(pivot, top_prefixes)
    
    overlap_stats, service_coders = analyze_identification_overlap(df)
    
    # -------------------------------------------------------------------------
    # PHASE 3: CORE METRICS
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("PHASE 3: CORE METRICS")
    print("="*70)
    
    results_df = compute_agreement_matrix(df)
    print_agreement_table(results_df)
    
    print("\nPairwise Coder Agreement:")
    pairwise = compute_pairwise_agreement(df)
    print(pairwise.to_string(index=False))
    
    print("\nJaccard Similarity by Contract:")
    jaccard_df = compute_jaccard_similarity(df)
    print(jaccard_df[['Contract', 'Difficulty', 'Round', 'mean_jaccard']].to_string(index=False))
    
    # -------------------------------------------------------------------------
    # PHASE 4: DIAGNOSTIC ANALYSIS
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("PHASE 4: DIAGNOSTIC ANALYSIS")
    print("="*70)
    
    disagreements = analyze_disagreement_taxonomy(df)
    
    confusion_matrix, confusion_counts = build_confusion_matrix(df)
    print_confusion_pairs(confusion_counts)
    
    cross_contract = analyze_cross_contract_consistency(df)
    
    # -------------------------------------------------------------------------
    # PHASE 5: IMPACT SIMULATION
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("PHASE 5: IMPACT SIMULATION")
    print("="*70)
    
    simulation_results = simulate_query_performance(df)
    miss_rates_df = compute_miss_rates(simulation_results)
    avg_miss = summarize_query_performance(miss_rates_df)
    
    # -------------------------------------------------------------------------
    # PHASE 6: SYNTHESIS
    # -------------------------------------------------------------------------
    print("\n" + "="*70)
    print("PHASE 6: SYNTHESIS")
    print("="*70)
    
    summary = generate_summary_table(df)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    
    return {
        'df': df,
        'results_df': results_df,
        'pairwise': pairwise,
        'jaccard_df': jaccard_df,
        'disagreements': disagreements,
        'confusion_matrix': confusion_matrix,
        'cross_contract': cross_contract,
        'miss_rates_df': miss_rates_df,
        'summary': summary,
        'pivot': pivot,
        'top_prefixes': top_prefixes,
    }


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    INPUT_FILE = "data/consistency_analysis.csv"
    
    results = run_full_analysis(INPUT_FILE)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    plot_agreement_comparison(results['results_df'], 'figures/agreement_comparison.png')
    plot_coder_profiles(results['pivot'], results['top_prefixes'], 'figures/coder_profiles.png')
    plot_miss_rate_heatmap(results['miss_rates_df'], 'figures/miss_rate_heatmap.png')
    
    print("\nDone!")