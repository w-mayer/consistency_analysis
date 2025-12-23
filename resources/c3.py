# =============================================================================
# COMPREHENSIVE QUERY SIMULATION ANALYSIS
# =============================================================================
"""
Full statistical analysis of query performance using expanded query set.
Extracts all actionable insights for database decision-making.

Outputs:
- Category-level miss rates with CIs
- Coder × Category interaction analysis
- Difficulty × Category breakdown
- Contract-level risk scoring
- Visualizations for reporting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from itertools import combinations

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
np.random.seed(42)

# =============================================================================
# QUERY DEFINITIONS
# =============================================================================

QUERY_SCENARIOS = {
    # CONSTRUCTION (6 queries)
    'road_maintenance': ['237310', '237'],
    'highway_construction': ['237310'],
    'commercial_building': ['236220', '236'],
    'utility_line_construction': ['237110', '237130'],
    'specialty_trades': ['238210', '238220', '238350', '238320', '238990'],
    'infrastructure_general': ['237'],
    
    # PUBLIC ADMIN (9 queries)
    'police_services': ['922120'],
    'fire_protection': ['922160'],
    'corrections': ['922140'],
    'administrative_executive': ['921130', '921190', '921110'],
    'courts_legal': ['922110', '922130'],
    'public_safety_broad': ['922'],
    'environmental_programs': ['924120', '925120', '925110'],
    'justice_system': ['922110', '922140', '922150'],
    'regulatory_inspection': ['926150', '926120'],
    
    # SUPPORT SERVICES (7 queries)
    'facilities_support': ['561210', '561211'],
    'landscaping_services': ['561730', '567130'],
    'security_services': ['561612', '561710'],
    'waste_collection': ['562111', '562920'],
    'office_admin': ['561110'],
    'janitorial_custodial': ['561720'],
    'support_services_broad': ['561'],
    
    # UTILITIES (3 queries)
    'water_supply': ['221310'],
    'sewage_treatment': ['221320'],
    'utilities_broad': ['221'],
    
    # PROFESSIONAL (5 queries)
    'engineering_civil': ['541330', '541320'],
    'surveying_mapping': ['541370'],
    'computer_services': ['541512', '541513', '541519'],
    'building_inspection': ['541350'],
    'professional_broad': ['541'],
    
    # RECREATION (3 queries)
    'fitness_recreation': ['713940', '713910'],
    'nature_parks': ['712190'],
    'recreation_broad': ['71'],
    
    # REPAIR (3 queries)
    'auto_repair': ['811111', '811310'],
    'personal_services': ['812220', '812910'],
    'repair_broad': ['81'],
    
    # TRANSPORTATION (3 queries)
    'towing_services': ['488410'],
    'traffic_management': ['488490'],
    'transportation_broad': ['488'],
}

QUERY_CATEGORIES = {
    'Construction': ['road_maintenance', 'highway_construction', 'commercial_building',
                    'utility_line_construction', 'specialty_trades', 'infrastructure_general'],
    'Public Admin': ['police_services', 'fire_protection', 'corrections', 'administrative_executive',
                    'courts_legal', 'public_safety_broad', 'environmental_programs', 
                    'justice_system', 'regulatory_inspection'],
    'Support Services': ['facilities_support', 'landscaping_services', 'security_services',
                        'waste_collection', 'office_admin', 'janitorial_custodial', 'support_services_broad'],
    'Utilities': ['water_supply', 'sewage_treatment', 'utilities_broad'],
    'Professional': ['engineering_civil', 'surveying_mapping', 'computer_services',
                    'building_inspection', 'professional_broad'],
    'Recreation': ['fitness_recreation', 'nature_parks', 'recreation_broad'],
    'Repair': ['auto_repair', 'personal_services', 'repair_broad'],
    'Transportation': ['towing_services', 'traffic_management', 'transportation_broad'],
}

# Build reverse mapping
QUERY_TO_CATEGORY = {}
for cat, queries in QUERY_CATEGORIES.items():
    for q in queries:
        QUERY_TO_CATEGORY[q] = cat


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def get_codes_set(naics_str):
    """Parse NAICS codes from semicolon-delimited string."""
    if pd.isna(naics_str) or naics_str == '':
        return set()
    codes = set()
    for code in str(naics_str).split(';'):
        code = code.strip()
        if code and code != 'nan':
            codes.add(code)
    return codes


def query_matches(code_set, query_codes):
    """Check if code set satisfies query (exact or prefix match)."""
    for code in code_set:
        code_str = str(code).strip()
        for query in query_codes:
            query_str = str(query).strip()
            if code_str == query_str or code_str.startswith(query_str):
                return True
    return False


def bootstrap_ci(values, n_bootstrap=1000, ci=0.95):
    """Compute bootstrap confidence interval."""
    if len(values) == 0:
        return np.nan, np.nan, np.nan
    
    values = np.array(values)
    point = np.mean(values)
    
    boot_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(values, size=len(values), replace=True)
        boot_means.append(np.mean(sample))
    
    alpha = 1 - ci
    lower = np.percentile(boot_means, alpha/2 * 100)
    upper = np.percentile(boot_means, (1 - alpha/2) * 100)
    
    return point, lower, upper


# =============================================================================
# SIMULATION ENGINE
# =============================================================================

def run_simulation(df):
    """
    Run full query simulation.
    Returns detailed results DataFrame.
    """
    results = []
    
    for contract in df['Contract'].unique():
        df_contract = df[df['Contract'] == contract]
        difficulty = df_contract['Difficulty'].iloc[0]
        round_num = df_contract['Round'].iloc[0]
        
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
        for query_name, query_codes in QUERY_SCENARIOS.items():
            union_hit = query_matches(union_codes, query_codes)
            
            row = {
                'contract': contract,
                'difficulty': difficulty,
                'round': round_num,
                'query': query_name,
                'category': QUERY_TO_CATEGORY.get(query_name, 'Unknown'),
                'union_hit': int(union_hit),
            }
            
            for coder, codes in codes_by_coder.items():
                coder_hit = query_matches(codes, query_codes)
                row[f'{coder}_hit'] = int(coder_hit)
                row[f'{coder}_miss'] = int(union_hit and not coder_hit)
            
            results.append(row)
    
    return pd.DataFrame(results)


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_overall(sim_df, coder_cols):
    """Compute overall statistics."""
    union_hits = sim_df['union_hit'].sum()
    total_queries = len(sim_df)
    
    print("=" * 70)
    print("OVERALL SIMULATION STATISTICS")
    print("=" * 70)
    print(f"\nTotal queries tested: {len(QUERY_SCENARIOS)}")
    print(f"Total contracts: {sim_df['contract'].nunique()}")
    print(f"Query-contract combinations: {total_queries}")
    print(f"Union hits (queries findable by at least one coder): {union_hits}")
    print(f"Union hit rate: {union_hits/total_queries*100:.1f}%")
    
    print("\n" + "-" * 70)
    print("Per-Coder Performance:")
    print("-" * 70)
    
    coder_stats = []
    for col in sorted(coder_cols):
        coder = col.replace('_hit', '')
        hits = sim_df[col].sum()
        misses = sim_df[f'{coder}_miss'].sum()
        miss_rate = misses / union_hits * 100 if union_hits > 0 else 0
        
        # Bootstrap CI on miss rate
        miss_indicators = sim_df[sim_df['union_hit'] == 1][f'{coder}_miss'].values
        point, lower, upper = bootstrap_ci(miss_indicators)
        
        print(f"  {coder}: {hits} hits, {misses} misses, "
              f"miss rate = {miss_rate:.1f}% [{lower*100:.1f}%, {upper*100:.1f}%]")
        
        coder_stats.append({
            'coder': coder,
            'hits': hits,
            'misses': misses,
            'miss_rate': miss_rate,
            'ci_lower': lower * 100,
            'ci_upper': upper * 100
        })
    
    # Average miss rate
    avg_miss = np.mean([s['miss_rate'] for s in coder_stats])
    print(f"\n  Average single-coder miss rate: {avg_miss:.1f}%")
    
    return pd.DataFrame(coder_stats)


def analyze_by_category(sim_df, coder_cols):
    """Analyze miss rates by query category."""
    print("\n" + "=" * 70)
    print("MISS RATES BY QUERY CATEGORY")
    print("=" * 70)
    
    results = []
    
    for category in QUERY_CATEGORIES.keys():
        cat_df = sim_df[sim_df['category'] == category]
        cat_union = cat_df['union_hit'].sum()
        
        if cat_union == 0:
            continue
        
        cat_result = {
            'category': category,
            'n_queries': len(QUERY_CATEGORIES[category]),
            'union_hits': cat_union,
        }
        
        miss_rates = []
        for col in coder_cols:
            coder = col.replace('_hit', '')
            coder_misses = cat_df[f'{coder}_miss'].sum()
            miss_rate = coder_misses / cat_union * 100
            cat_result[f'{coder}_miss_rate'] = miss_rate
            miss_rates.append(miss_rate)
        
        cat_result['avg_miss_rate'] = np.mean(miss_rates)
        cat_result['max_miss_rate'] = np.max(miss_rates)
        cat_result['min_miss_rate'] = np.min(miss_rates)
        cat_result['miss_rate_range'] = np.max(miss_rates) - np.min(miss_rates)
        
        # Bootstrap CI on average miss rate
        miss_indicators = []
        for col in coder_cols:
            coder = col.replace('_hit', '')
            miss_indicators.extend(cat_df[cat_df['union_hit'] == 1][f'{coder}_miss'].values)
        
        if len(miss_indicators) > 0:
            point, lower, upper = bootstrap_ci(miss_indicators)
            cat_result['ci_lower'] = lower * 100
            cat_result['ci_upper'] = upper * 100
        
        results.append(cat_result)
    
    results_df = pd.DataFrame(results).sort_values('avg_miss_rate', ascending=False)
    
    print(f"\n{'Category':<18} {'Hits':>6} {'Avg Miss':>10} {'95% CI':>18} {'Range':>10}")
    print("-" * 65)
    for _, row in results_df.iterrows():
        ci_str = f"[{row.get('ci_lower', 0):.1f}%, {row.get('ci_upper', 0):.1f}%]"
        print(f"{row['category']:<18} {row['union_hits']:>6} {row['avg_miss_rate']:>9.1f}% "
              f"{ci_str:>18} {row['miss_rate_range']:>9.1f}pp")
    
    return results_df


def analyze_by_difficulty(sim_df, coder_cols):
    """Analyze miss rates by contract difficulty."""
    print("\n" + "=" * 70)
    print("MISS RATES BY DIFFICULTY")
    print("=" * 70)
    
    results = []
    
    for diff in ['Easy', 'Medium', 'Hard']:
        diff_df = sim_df[sim_df['difficulty'] == diff]
        diff_union = diff_df['union_hit'].sum()
        
        if diff_union == 0:
            continue
        
        diff_result = {
            'difficulty': diff,
            'n_contracts': diff_df['contract'].nunique(),
            'union_hits': diff_union,
        }
        
        miss_rates = []
        for col in coder_cols:
            coder = col.replace('_hit', '')
            coder_misses = diff_df[f'{coder}_miss'].sum()
            miss_rate = coder_misses / diff_union * 100
            diff_result[f'{coder}_miss_rate'] = miss_rate
            miss_rates.append(miss_rate)
        
        diff_result['avg_miss_rate'] = np.mean(miss_rates)
        
        # Bootstrap CI
        miss_indicators = []
        for col in coder_cols:
            coder = col.replace('_hit', '')
            miss_indicators.extend(diff_df[diff_df['union_hit'] == 1][f'{coder}_miss'].values)
        
        if len(miss_indicators) > 0:
            point, lower, upper = bootstrap_ci(miss_indicators)
            diff_result['ci_lower'] = lower * 100
            diff_result['ci_upper'] = upper * 100
        
        results.append(diff_result)
    
    results_df = pd.DataFrame(results)
    
    print(f"\n{'Difficulty':<10} {'Contracts':>10} {'Hits':>8} {'Avg Miss':>10} {'95% CI':>20}")
    print("-" * 60)
    for _, row in results_df.iterrows():
        ci_str = f"[{row.get('ci_lower', 0):.1f}%, {row.get('ci_upper', 0):.1f}%]"
        print(f"{row['difficulty']:<10} {row['n_contracts']:>10} {row['union_hits']:>8} "
              f"{row['avg_miss_rate']:>9.1f}% {ci_str:>20}")
    
    return results_df


def analyze_category_by_difficulty(sim_df, coder_cols):
    """Analyze miss rates by category × difficulty interaction."""
    print("\n" + "=" * 70)
    print("CATEGORY × DIFFICULTY INTERACTION")
    print("=" * 70)
    
    results = []
    
    for category in QUERY_CATEGORIES.keys():
        for diff in ['Easy', 'Medium', 'Hard']:
            subset = sim_df[(sim_df['category'] == category) & (sim_df['difficulty'] == diff)]
            union_hits = subset['union_hit'].sum()
            
            if union_hits == 0:
                continue
            
            miss_rates = []
            for col in coder_cols:
                coder = col.replace('_hit', '')
                misses = subset[f'{coder}_miss'].sum()
                miss_rates.append(misses / union_hits * 100)
            
            results.append({
                'category': category,
                'difficulty': diff,
                'union_hits': union_hits,
                'avg_miss_rate': np.mean(miss_rates)
            })
    
    results_df = pd.DataFrame(results)
    
    # Pivot for display
    pivot = results_df.pivot(index='category', columns='difficulty', values='avg_miss_rate')
    pivot = pivot.reindex(columns=['Easy', 'Medium', 'Hard'])
    
    print("\nAverage Miss Rate (%) by Category and Difficulty:")
    print("-" * 50)
    print(pivot.round(1).fillna('-').to_string())
    
    return results_df, pivot


def analyze_coder_by_category(sim_df, coder_cols):
    """Analyze each coder's performance by category."""
    print("\n" + "=" * 70)
    print("CODER × CATEGORY INTERACTION")
    print("=" * 70)
    
    results = []
    
    for category in QUERY_CATEGORIES.keys():
        cat_df = sim_df[sim_df['category'] == category]
        cat_union = cat_df['union_hit'].sum()
        
        if cat_union == 0:
            continue
        
        for col in coder_cols:
            coder = col.replace('_hit', '')
            misses = cat_df[f'{coder}_miss'].sum()
            miss_rate = misses / cat_union * 100
            
            results.append({
                'category': category,
                'coder': coder,
                'union_hits': cat_union,
                'misses': misses,
                'miss_rate': miss_rate
            })
    
    results_df = pd.DataFrame(results)
    
    # Pivot for display
    pivot = results_df.pivot(index='category', columns='coder', values='miss_rate')
    
    print("\nMiss Rate (%) by Category and Coder:")
    print("-" * 50)
    print(pivot.round(1).to_string())
    
    # Identify worst coder per category
    print("\nWorst Performer by Category:")
    for cat in QUERY_CATEGORIES.keys():
        cat_data = results_df[results_df['category'] == cat]
        if len(cat_data) > 0:
            worst = cat_data.loc[cat_data['miss_rate'].idxmax()]
            if worst['miss_rate'] > 0:
                print(f"  {cat}: {worst['coder']} ({worst['miss_rate']:.1f}% miss rate)")
    
    return results_df, pivot


def analyze_by_contract(sim_df, coder_cols):
    """Analyze miss rates by individual contract."""
    print("\n" + "=" * 70)
    print("CONTRACT-LEVEL ANALYSIS")
    print("=" * 70)
    
    results = []
    
    for contract in sim_df['contract'].unique():
        con_df = sim_df[sim_df['contract'] == contract]
        con_union = con_df['union_hit'].sum()
        difficulty = con_df['difficulty'].iloc[0]
        
        if con_union == 0:
            continue
        
        con_result = {
            'contract': contract,
            'difficulty': difficulty,
            'union_hits': con_union,
        }
        
        miss_rates = []
        for col in coder_cols:
            coder = col.replace('_hit', '')
            misses = con_df[f'{coder}_miss'].sum()
            miss_rate = misses / con_union * 100
            con_result[f'{coder}_miss'] = miss_rate
            miss_rates.append(miss_rate)
        
        con_result['avg_miss_rate'] = np.mean(miss_rates)
        con_result['max_miss_rate'] = np.max(miss_rates)
        con_result['coder_variance'] = np.std(miss_rates)
        
        results.append(con_result)
    
    results_df = pd.DataFrame(results).sort_values('avg_miss_rate', ascending=False)
    
    print(f"\n{'Contract':<18} {'Diff':<8} {'Hits':>6} {'Avg Miss':>10} {'Max Miss':>10} {'Variance':>10}")
    print("-" * 70)
    for _, row in results_df.iterrows():
        print(f"{row['contract']:<18} {row['difficulty']:<8} {row['union_hits']:>6} "
              f"{row['avg_miss_rate']:>9.1f}% {row['max_miss_rate']:>9.1f}% {row['coder_variance']:>9.1f}")
    
    return results_df


def analyze_query_level(sim_df, coder_cols):
    """Analyze miss rates by individual query."""
    print("\n" + "=" * 70)
    print("QUERY-LEVEL ANALYSIS (Top 15 by miss rate)")
    print("=" * 70)
    
    results = []
    
    for query in QUERY_SCENARIOS.keys():
        q_df = sim_df[sim_df['query'] == query]
        q_union = q_df['union_hit'].sum()
        
        if q_union == 0:
            continue
        
        miss_rates = []
        for col in coder_cols:
            coder = col.replace('_hit', '')
            misses = q_df[f'{coder}_miss'].sum()
            miss_rates.append(misses / q_union * 100)
        
        results.append({
            'query': query,
            'category': QUERY_TO_CATEGORY.get(query, 'Unknown'),
            'union_hits': q_union,
            'avg_miss_rate': np.mean(miss_rates),
            'max_miss_rate': np.max(miss_rates)
        })
    
    results_df = pd.DataFrame(results).sort_values('avg_miss_rate', ascending=False)
    
    print(f"\n{'Query':<30} {'Category':<18} {'Hits':>6} {'Avg Miss':>10}")
    print("-" * 70)
    for _, row in results_df.head(15).iterrows():
        print(f"{row['query']:<30} {row['category']:<18} {row['union_hits']:>6} "
              f"{row['avg_miss_rate']:>9.1f}%")
    
    return results_df


def compute_risk_scores(sim_df, coder_cols, category_df, difficulty_df):
    """Compute risk scores for prioritization."""
    print("\n" + "=" * 70)
    print("RISK PRIORITIZATION")
    print("=" * 70)
    
    # Category risk = miss rate × union hits (impact-weighted)
    category_df = category_df.copy()
    category_df['risk_score'] = category_df['avg_miss_rate'] * category_df['union_hits'] / 100
    category_df = category_df.sort_values('risk_score', ascending=False)
    
    print("\nCategory Risk Scores (miss rate × hit frequency):")
    print("-" * 50)
    for _, row in category_df.iterrows():
        print(f"  {row['category']:<18} Risk: {row['risk_score']:>6.1f} "
              f"(Miss: {row['avg_miss_rate']:.1f}%, Hits: {row['union_hits']})")
    
    # High-risk combinations (category × difficulty)
    print("\nHigh-Risk Category × Difficulty Combinations:")
    print("-" * 50)
    
    high_risk = []
    for category in QUERY_CATEGORIES.keys():
        for diff in ['Medium', 'Hard']:  # Skip Easy (usually 0%)
            subset = sim_df[(sim_df['category'] == category) & (sim_df['difficulty'] == diff)]
            union_hits = subset['union_hit'].sum()
            
            if union_hits == 0:
                continue
            
            miss_rates = []
            for col in coder_cols:
                coder = col.replace('_hit', '')
                misses = subset[f'{coder}_miss'].sum()
                miss_rates.append(misses / union_hits * 100)
            
            avg_miss = np.mean(miss_rates)
            if avg_miss > 20:  # Threshold for "high risk"
                high_risk.append({
                    'category': category,
                    'difficulty': diff,
                    'miss_rate': avg_miss,
                    'union_hits': union_hits
                })
    
    high_risk_df = pd.DataFrame(high_risk).sort_values('miss_rate', ascending=False)
    
    for _, row in high_risk_df.iterrows():
        print(f"  {row['category']:<18} + {row['difficulty']:<8} → {row['miss_rate']:.1f}% miss rate")
    
    return category_df, high_risk_df


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def plot_category_miss_rates(category_df, output_path=None):
    """Bar chart of miss rates by category with error bars."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    df = category_df.sort_values('avg_miss_rate', ascending=True)
    
    colors = plt.cm.RdYlGn_r(df['avg_miss_rate'] / df['avg_miss_rate'].max())
    
    bars = ax.barh(df['category'], df['avg_miss_rate'], color=colors, edgecolor='black', linewidth=0.5)
    
    # Error bars
    if 'ci_lower' in df.columns and 'ci_upper' in df.columns:
        xerr_lower = df['avg_miss_rate'] - df['ci_lower']
        xerr_upper = df['ci_upper'] - df['avg_miss_rate']
        ax.errorbar(df['avg_miss_rate'], df['category'], 
                   xerr=[xerr_lower, xerr_upper], fmt='none', color='black', capsize=3)
    
    # Add value labels
    for bar, val in zip(bars, df['avg_miss_rate']):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2, 
               f'{val:.1f}%', va='center', fontsize=10)
    
    ax.set_xlabel('Average Single-Coder Miss Rate (%)', fontsize=12)
    ax.set_title('Query Miss Rates by Category\n(Higher = More risk from single-coder production)', fontsize=14)
    ax.set_xlim(0, max(df['avg_miss_rate']) * 1.3)
    
    # Add vertical line at overall average
    overall_avg = df['avg_miss_rate'].mean()
    ax.axvline(overall_avg, color='red', linestyle='--', linewidth=2, label=f'Overall avg: {overall_avg:.1f}%')
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig


def plot_coder_category_heatmap(coder_category_pivot, output_path=None):
    """Heatmap of coder × category miss rates."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(coder_category_pivot, annot=True, fmt='.1f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Miss Rate (%)'}, ax=ax,
                vmin=0, vmax=coder_category_pivot.max().max() * 1.1,
                linewidths=0.5, linecolor='white')
    
    ax.set_title('Miss Rates by Coder and Query Category (%)\n(Red = Higher miss rate)', fontsize=14)
    ax.set_xlabel('Coder', fontsize=12)
    ax.set_ylabel('Query Category', fontsize=12)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig


def plot_difficulty_category_heatmap(cat_diff_pivot, output_path=None):
    """Heatmap of difficulty × category miss rates."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Reorder columns
    cat_diff_pivot = cat_diff_pivot.reindex(columns=['Easy', 'Medium', 'Hard'])
    
    sns.heatmap(cat_diff_pivot, annot=True, fmt='.1f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Avg Miss Rate (%)'}, ax=ax,
                vmin=0, linewidths=0.5, linecolor='white')
    
    ax.set_title('Miss Rates by Query Category and Contract Difficulty (%)', fontsize=14)
    ax.set_xlabel('Contract Difficulty', fontsize=12)
    ax.set_ylabel('Query Category', fontsize=12)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig


def plot_contract_heatmap(contract_df, coder_cols, output_path=None):
    """Heatmap of contract × coder miss rates."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Prepare data
    miss_cols = [c.replace('_hit', '_miss') for c in coder_cols]
    plot_data = contract_df.set_index('contract')[miss_cols].copy()
    plot_data.columns = [c.replace('_miss', '') for c in plot_data.columns]
    
    # Add difficulty annotation
    plot_data.index = [f"{idx} ({contract_df[contract_df['contract']==idx]['difficulty'].iloc[0]})" 
                       for idx in plot_data.index]
    
    sns.heatmap(plot_data, annot=True, fmt='.0f', cmap='RdYlGn_r',
                cbar_kws={'label': 'Miss Rate (%)'}, ax=ax,
                vmin=0, vmax=60, linewidths=0.5, linecolor='white')
    
    ax.set_title('Miss Rates by Contract and Coder (%)\n(Red = Higher miss rate)', fontsize=14)
    ax.set_xlabel('Coder', fontsize=12)
    ax.set_ylabel('Contract (Difficulty)', fontsize=12)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig


def plot_miss_rate_distribution(sim_df, coder_cols, output_path=None):
    """Distribution of miss rates across query-contract combinations."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: Histogram of miss indicators
    all_misses = []
    for col in coder_cols:
        coder = col.replace('_hit', '')
        # Only count where union hit = 1
        misses = sim_df[sim_df['union_hit'] == 1][f'{coder}_miss'].values
        all_misses.extend(misses)
    
    ax1 = axes[0]
    miss_rate = np.mean(all_misses) * 100
    ax1.bar(['Hit', 'Miss'], [1 - np.mean(all_misses), np.mean(all_misses)], 
           color=['forestgreen', 'firebrick'], edgecolor='black')
    ax1.set_ylabel('Proportion', fontsize=12)
    ax1.set_title(f'Single-Coder Query Outcomes\n(Miss rate: {miss_rate:.1f}%)', fontsize=14)
    ax1.set_ylim(0, 1)
    
    # Right: Miss rate by coder
    ax2 = axes[1]
    coder_miss_rates = []
    coder_names = []
    for col in sorted(coder_cols):
        coder = col.replace('_hit', '')
        misses = sim_df[sim_df['union_hit'] == 1][f'{coder}_miss'].values
        coder_miss_rates.append(np.mean(misses) * 100)
        coder_names.append(coder)
    
    colors = ['steelblue', 'darkorange', 'forestgreen']
    bars = ax2.bar(coder_names, coder_miss_rates, color=colors[:len(coder_names)], edgecolor='black')
    ax2.axhline(np.mean(coder_miss_rates), color='red', linestyle='--', label=f'Avg: {np.mean(coder_miss_rates):.1f}%')
    ax2.set_ylabel('Miss Rate (%)', fontsize=12)
    ax2.set_title('Miss Rate by Coder', fontsize=14)
    ax2.legend()
    
    # Add value labels
    for bar, val in zip(bars, coder_miss_rates):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', fontsize=11)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig


def plot_category_difficulty_grouped(cat_diff_df, output_path=None):
    """Grouped bar chart of miss rates by category and difficulty."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    categories = list(QUERY_CATEGORIES.keys())
    difficulties = ['Easy', 'Medium', 'Hard']
    x = np.arange(len(categories))
    width = 0.25
    
    colors = {'Easy': 'forestgreen', 'Medium': 'gold', 'Hard': 'firebrick'}
    
    for i, diff in enumerate(difficulties):
        values = []
        for cat in categories:
            row = cat_diff_df[(cat_diff_df['category'] == cat) & (cat_diff_df['difficulty'] == diff)]
            if len(row) > 0:
                values.append(row['avg_miss_rate'].iloc[0])
            else:
                values.append(0)
        
        bars = ax.bar(x + i*width, values, width, label=diff, color=colors[diff], edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Query Category', fontsize=12)
    ax.set_ylabel('Average Miss Rate (%)', fontsize=12)
    ax.set_title('Miss Rates by Query Category and Contract Difficulty', fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend(title='Difficulty')
    ax.set_ylim(0, max(cat_diff_df['avg_miss_rate']) * 1.2)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    
    return fig


# =============================================================================
# SUMMARY GENERATION
# =============================================================================

def generate_executive_summary(overall_df, category_df, difficulty_df, high_risk_df):
    """Generate executive summary statistics."""
    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY")
    print("=" * 70)
    
    avg_miss = overall_df['miss_rate'].mean()
    worst_coder = overall_df.loc[overall_df['miss_rate'].idxmax()]
    best_coder = overall_df.loc[overall_df['miss_rate'].idxmin()]
    
    worst_category = category_df.loc[category_df['avg_miss_rate'].idxmax()]
    best_category = category_df.loc[category_df['avg_miss_rate'].idxmin()]
    
    worst_difficulty = difficulty_df.loc[difficulty_df['avg_miss_rate'].idxmax()]
    
    print(f"""
KEY METRICS:
  • Overall single-coder miss rate: {avg_miss:.1f}%
  • Best coder: {best_coder['coder']} ({best_coder['miss_rate']:.1f}% miss rate)
  • Worst coder: {worst_coder['coder']} ({worst_coder['miss_rate']:.1f}% miss rate)

CATEGORY INSIGHTS:
  • Highest risk: {worst_category['category']} ({worst_category['avg_miss_rate']:.1f}% miss rate)
  • Lowest risk: {best_category['category']} ({best_category['avg_miss_rate']:.1f}% miss rate)

DIFFICULTY INSIGHTS:
  • Highest risk difficulty: {worst_difficulty['difficulty']} ({worst_difficulty['avg_miss_rate']:.1f}% miss rate)

HIGH-RISK COMBINATIONS (>20% miss rate):""")
    
    for _, row in high_risk_df.head(5).iterrows():
        print(f"  • {row['category']} + {row['difficulty']}: {row['miss_rate']:.1f}%")
    
    print(f"""
RECOMMENDATIONS:
  1. Prioritize handbook updates for: {worst_category['category']}
  2. Consider dual-coding for: {worst_difficulty['difficulty']} contracts
  3. Targeted training for: {worst_coder['coder']} (highest miss rate)
  4. Low-risk categories ({best_category['category']}) suitable for single-coder production
""")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_full_analysis(filepath, output_dir=None):
    """Run complete query simulation analysis."""
    
    # Load and prepare data
    df = pd.read_csv(filepath)
    df['Contract'] = df['Contract'].str.strip()
    
    # Run simulation
    print("Running query simulation...")
    sim_df = run_simulation(df)
    
    # Identify coder columns
    coder_cols = [c for c in sim_df.columns if c.endswith('_hit') and c != 'union_hit']
    
    # Run all analyses
    overall_df = analyze_overall(sim_df, coder_cols)
    category_df = analyze_by_category(sim_df, coder_cols)
    difficulty_df = analyze_by_difficulty(sim_df, coder_cols)
    cat_diff_df, cat_diff_pivot = analyze_category_by_difficulty(sim_df, coder_cols)
    coder_cat_df, coder_cat_pivot = analyze_coder_by_category(sim_df, coder_cols)
    contract_df = analyze_by_contract(sim_df, coder_cols)
    query_df = analyze_query_level(sim_df, coder_cols)
    category_risk_df, high_risk_df = compute_risk_scores(sim_df, coder_cols, category_df, difficulty_df)
    
    # Executive summary
    generate_executive_summary(overall_df, category_df, difficulty_df, high_risk_df)
    
    # Generate visualizations
    if output_dir:
        print("\n" + "=" * 70)
        print("GENERATING VISUALIZATIONS")
        print("=" * 70)
        
        plot_category_miss_rates(category_df, f"{output_dir}/fig_category_miss_rates.png")
        plot_coder_category_heatmap(coder_cat_pivot, f"{output_dir}/fig_coder_category_heatmap.png")
        plot_difficulty_category_heatmap(cat_diff_pivot, f"{output_dir}/fig_difficulty_category_heatmap.png")
        plot_contract_heatmap(contract_df, coder_cols, f"{output_dir}/fig_contract_heatmap.png")
        plot_miss_rate_distribution(sim_df, coder_cols, f"{output_dir}/fig_miss_rate_distribution.png")
        plot_category_difficulty_grouped(cat_diff_df, f"{output_dir}/fig_category_difficulty_grouped.png")
    
    return {
        'sim_df': sim_df,
        'overall_df': overall_df,
        'category_df': category_df,
        'difficulty_df': difficulty_df,
        'cat_diff_df': cat_diff_df,
        'cat_diff_pivot': cat_diff_pivot,
        'coder_cat_df': coder_cat_df,
        'coder_cat_pivot': coder_cat_pivot,
        'contract_df': contract_df,
        'query_df': query_df,
        'high_risk_df': high_risk_df,
    }


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import os
    
    INPUT_FILE = "data/consistency_analysis.csv"
    OUTPUT_DIR = "figures"
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    results = run_full_analysis(INPUT_FILE, OUTPUT_DIR)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)