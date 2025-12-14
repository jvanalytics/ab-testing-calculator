"""
Statistical functions for A/B testing calculations
All formulas are clearly documented with references
"""
import math
from scipy import stats
from scipy.stats import norm, t
import numpy as np


def two_proportion_z_test(control_visitors, control_conversions,
                          variant_visitors, variant_conversions, alpha=0.05):
    """
    Two-Proportion Z-Test for comparing conversion rates
    
    Formula:
    z = (p1 - p2) / sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    where p_pool = (x1 + x2) / (n1 + n2)
    
    Args:
        control_visitors: Number of visitors in control group
        control_conversions: Number of conversions in control group
        variant_visitors: Number of visitors in variant group
        variant_conversions: Number of conversions in variant group
        alpha: Significance level (default 0.05)
    
    Returns:
        dict with conversion rates, lift, z-score, p-value, significance, interpretation
    """
    if control_visitors == 0 or variant_visitors == 0:
        raise ValueError("Number of visitors must be greater than 0")
    
    # Calculate conversion rates
    p_control = control_conversions / control_visitors
    p_variant = variant_conversions / variant_visitors
    
    # Pooled proportion
    p_pool = (control_conversions + variant_conversions) / (control_visitors + variant_visitors)
    
    # Standard error
    se = math.sqrt(p_pool * (1 - p_pool) * (1/control_visitors + 1/variant_visitors))
    
    if se == 0:
        raise ValueError("Standard error is zero - cannot compute z-score")
    
    # Z-score
    z_score = (p_variant - p_control) / se
    
    # P-value (two-tailed)
    p_value = 2 * (1 - norm.cdf(abs(z_score)))
    
    # Calculate lift
    absolute_lift = p_variant - p_control
    if p_control > 0:
        relative_lift = (absolute_lift / p_control) * 100
    else:
        relative_lift = 0
    
    # Significance decision using custom alpha
    is_significant = p_value < alpha
    
    # Confidence intervals using custom alpha level
    z_critical = norm.ppf(1 - alpha / 2)  # For custom confidence level
    
    # CI for control proportion
    se_control = math.sqrt(p_control * (1 - p_control) / control_visitors)
    ci_control_lower = p_control - z_critical * se_control
    ci_control_upper = p_control + z_critical * se_control
    
    # CI for variant proportion
    se_variant = math.sqrt(p_variant * (1 - p_variant) / variant_visitors)
    ci_variant_lower = p_variant - z_critical * se_variant
    ci_variant_upper = p_variant + z_critical * se_variant
    
    # Confidence interval for the difference in proportions (using custom alpha)
    ci_lower = absolute_lift - z_critical * se
    ci_upper = absolute_lift + z_critical * se
    
    # Interpretation
    if is_significant:
        if p_variant > p_control:
            interpretation = "Variant is significantly better than control"
        else:
            interpretation = "Control is significantly better than variant"
    else:
        interpretation = "No significant difference between control and variant"
    
    return {
        'control_rate': p_control * 100,
        'variant_rate': p_variant * 100,
        'absolute_lift': absolute_lift * 100,
        'relative_lift': relative_lift,
        'z_score': z_score,
        'p_value': p_value,
        'is_significant': is_significant,
        'interpretation': interpretation,
        'ci_lower': ci_lower * 100,  # Convert to percentage (difference)
        'ci_upper': ci_upper * 100,   # Convert to percentage (difference)
        'ci_control_lower': max(0, ci_control_lower * 100),  # Convert to percentage, ensure >= 0
        'ci_control_upper': min(100, ci_control_upper * 100),  # Convert to percentage, ensure <= 100
        'ci_variant_lower': max(0, ci_variant_lower * 100),  # Convert to percentage, ensure >= 0
        'ci_variant_upper': min(100, ci_variant_upper * 100)   # Convert to percentage, ensure <= 100
    }


def two_sample_z_test(mean_a, pop_sd_a, n_a, mean_b, pop_sd_b, n_b):
    """
    Two-Sample Z-Test for comparing means when population standard deviation is known
    
    Formula:
    z = (mean_a - mean_b) / sqrt(pop_sd_a^2/n_a + pop_sd_b^2/n_b)
    
    Args:
        mean_a: Mean of group A
        pop_sd_a: Population standard deviation of group A
        n_a: Sample size of group A
        mean_b: Mean of group B
        pop_sd_b: Population standard deviation of group B
        n_b: Sample size of group B
    
    Returns:
        dict with mean difference, z-statistic, p-value, confidence interval, interpretation
    """
    if n_a < 1 or n_b < 1:
        raise ValueError("Sample size must be at least 1 for each group")
    
    if pop_sd_a <= 0 or pop_sd_b <= 0:
        raise ValueError("Population standard deviation must be greater than 0")
    
    # Mean difference
    mean_diff = mean_a - mean_b
    
    # Standard error (using population SD)
    se_a = pop_sd_a ** 2 / n_a
    se_b = pop_sd_b ** 2 / n_b
    se = math.sqrt(se_a + se_b)
    
    # Z-statistic
    z_stat = mean_diff / se if se > 0 else 0
    
    # P-value (two-tailed) using normal distribution
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    
    # 95% Confidence interval using normal distribution
    z_critical = norm.ppf(0.975)  # 1.96 for 95% CI
    ci_lower = mean_diff - z_critical * se
    ci_upper = mean_diff + z_critical * se
    
    # Significance decision
    is_significant = p_value < 0.05
    
    # Interpretation
    if is_significant:
        if mean_a > mean_b:
            interpretation = "Group A is significantly higher than Group B (z-test)"
        else:
            interpretation = "Group B is significantly higher than Group A (z-test)"
    else:
        interpretation = "No significant difference between groups (z-test)"
    
    return {
        'mean_diff': mean_diff,
        'z_statistic': z_stat,
        'test_type': 'z-test',
        'p_value': p_value,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'is_significant': is_significant,
        'interpretation': interpretation
    }


def welch_t_test(mean_a, sd_a, n_a, mean_b, sd_b, n_b):
    """
    Welch's t-test for comparing means with unequal variances
    
    Formula:
    t = (mean_a - mean_b) / sqrt(sd_a^2/n_a + sd_b^2/n_b)
    df = (sd_a^2/n_a + sd_b^2/n_b)^2 / ((sd_a^2/n_a)^2/(n_a-1) + (sd_b^2/n_b)^2/(n_b-1))
    
    Args:
        mean_a: Mean of group A
        sd_a: Standard deviation of group A
        n_a: Sample size of group A
        mean_b: Mean of group B
        sd_b: Standard deviation of group B
        n_b: Sample size of group B
    
    Returns:
        dict with mean difference, t-statistic, p-value, confidence interval, interpretation
    """
    if n_a < 2 or n_b < 2:
        raise ValueError("Sample size must be at least 2 for each group")
    
    if sd_a <= 0 or sd_b <= 0:
        raise ValueError("Standard deviation must be greater than 0")
    
    # Mean difference
    mean_diff = mean_a - mean_b
    
    # Standard error
    se_a = sd_a ** 2 / n_a
    se_b = sd_b ** 2 / n_b
    se = math.sqrt(se_a + se_b)
    
    # T-statistic
    t_stat = mean_diff / se if se > 0 else 0
    
    # Degrees of freedom (Welch's approximation)
    df = (se_a + se_b) ** 2 / (se_a ** 2 / (n_a - 1) + se_b ** 2 / (n_b - 1))
    df = max(1, int(df))
    
    # P-value (two-tailed)
    p_value = 2 * (1 - t.cdf(abs(t_stat), df))
    
    # 95% Confidence interval
    t_critical = t.ppf(0.975, df)
    ci_lower = mean_diff - t_critical * se
    ci_upper = mean_diff + t_critical * se
    
    # Significance decision
    is_significant = p_value < 0.05
    
    # Interpretation
    if is_significant:
        if mean_a > mean_b:
            interpretation = "Group A is significantly higher than Group B"
        else:
            interpretation = "Group B is significantly higher than Group A"
    else:
        interpretation = "No significant difference between groups"
    
    return {
        'mean_diff': mean_diff,
        't_statistic': t_stat,
        'test_type': 't-test',
        'degrees_of_freedom': df,
        'p_value': p_value,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'is_significant': is_significant,
        'interpretation': interpretation
    }


def mann_whitney_u_test(mean_a, sd_a, n_a, mean_b, sd_b, n_b):
    """
    Mann-Whitney U Test (non-parametric alternative to t-test)
    
    Note: This is a simplified approximation. For exact results, 
    you would need the actual data points, not just summary statistics.
    We use a normal approximation based on the ranks.
    
    Args:
        mean_a: Mean of group A
        sd_a: Standard deviation of group A
        n_a: Sample size of group A
        mean_b: Mean of group B
        sd_b: Standard deviation of group B
        n_b: Sample size of group B
    
    Returns:
        dict with U-statistic, z-score, p-value, interpretation
    """
    if n_a < 2 or n_b < 2:
        raise ValueError("Sample size must be at least 2 for each group")
    
    if sd_a <= 0 or sd_b <= 0:
        raise ValueError("Standard deviation must be greater than 0")
    
    # Approximate U statistic using normal approximation
    # This is a simplification - actual Mann-Whitney requires raw data
    # We approximate using the means and assuming normal distribution
    
    # Expected U under null hypothesis
    u_expected = n_a * n_b / 2
    
    # Variance of U
    n_total = n_a + n_b
    u_variance = n_a * n_b * (n_total + 1) / 12
    
    # Approximate U from mean difference
    # This is a heuristic approximation
    mean_diff = mean_a - mean_b
    pooled_sd = math.sqrt((sd_a ** 2 + sd_b ** 2) / 2)
    
    if pooled_sd == 0:
        u_stat = u_expected
    else:
        # Approximate effect size
        effect = mean_diff / pooled_sd
        u_stat = u_expected + (n_a * n_b * effect) / 2
    
    # Ensure u_stat is within valid range (0 to n_a * n_b)
    u_stat = max(0, min(u_stat, n_a * n_b))
    
    # Z-score
    if u_variance > 0:
        z_score = (u_stat - u_expected) / math.sqrt(u_variance)
    else:
        z_score = 0
    
    # P-value (two-tailed)
    # Ensure p_value is between 0 and 1
    p_value = 2 * (1 - norm.cdf(abs(z_score)))
    p_value = max(0.0, min(1.0, p_value))
    
    # Significance decision
    is_significant = p_value < 0.05
    
    # Interpretation
    if is_significant:
        if mean_a > mean_b:
            interpretation = "Group A is significantly higher than Group B (non-parametric)"
        else:
            interpretation = "Group B is significantly higher than Group A (non-parametric)"
    else:
        interpretation = "No significant difference between groups (non-parametric)"
    
    return {
        'u_statistic': u_stat,
        'z_score': z_score,
        'p_value': p_value,
        'is_significant': is_significant,
        'interpretation': interpretation,
        'note': 'This is an approximation. For exact results, use raw data.'
    }


def sample_size_proportion(baseline_rate, mde_type, mde_value, power=0.8, alpha=0.05):
    """
    Calculate required sample size for proportion test (two-proportion z-test)
    
    Formula for two-proportion test:
    n = (Z_alpha/2 + Z_power)^2 * (p1*(1-p1) + p2*(1-p2)) / (p1 - p2)^2
    
    Args:
        baseline_rate: Baseline conversion rate (as proportion, e.g., 0.05 for 5%)
        mde_type: 'absolute' or 'relative'
        mde_value: Minimum detectable effect (as percentage, e.g., 10 for 10%)
        power: Statistical power (default 0.8)
        alpha: Significance level (default 0.05)
    
    Returns:
        dict with sample_per_variant and total_sample
    """
    if baseline_rate <= 0 or baseline_rate >= 1:
        raise ValueError("Baseline rate must be between 0 and 1")
    
    if mde_type == 'relative':
        # Relative MDE: e.g., 10% relative means 5% -> 5.5%
        variant_rate = baseline_rate * (1 + mde_value / 100)
    else:
        # Absolute MDE: e.g., 1% absolute means 5% -> 6%
        variant_rate = baseline_rate + (mde_value / 100)
    
    if variant_rate <= 0 or variant_rate >= 1:
        raise ValueError("Resulting variant rate must be between 0 and 1")
    
    # Z-scores
    z_alpha = norm.ppf(1 - alpha / 2)  # Two-tailed
    z_power = norm.ppf(power)
    
    # Pooled proportion for standard error
    p_pool = (baseline_rate + variant_rate) / 2
    
    # Variance terms
    var_control = baseline_rate * (1 - baseline_rate)
    var_variant = variant_rate * (1 - variant_rate)
    
    # Effect size
    effect_size = abs(variant_rate - baseline_rate)
    
    if effect_size == 0:
        raise ValueError("Effect size cannot be zero")
    
    # Sample size per variant
    numerator = (z_alpha + z_power) ** 2 * (var_control + var_variant)
    denominator = effect_size ** 2
    n_per_variant = math.ceil(numerator / denominator)
    
    return {
        'sample_per_variant': n_per_variant,
        'total_sample': n_per_variant * 2,
        'baseline_rate': baseline_rate,
        'variant_rate': variant_rate,
        'effect_size': effect_size
    }


def sample_size_continuous(expected_mean, expected_sd, min_detectable_diff,
                           power=0.8, alpha=0.05):
    """
    Calculate required sample size for continuous variable (t-test)
    
    Formula:
    n = 2 * (Z_alpha/2 + Z_power)^2 * (SD / effect_size)^2
    
    Args:
        expected_mean: Expected mean value
        expected_sd: Expected standard deviation
        min_detectable_diff: Minimum detectable difference
        power: Statistical power (default 0.8)
        alpha: Significance level (default 0.05)
    
    Returns:
        dict with sample_per_group and total_sample
    """
    if expected_sd <= 0:
        raise ValueError("Standard deviation must be greater than 0")
    
    if min_detectable_diff <= 0:
        raise ValueError("Minimum detectable difference must be greater than 0")
    
    # Z-scores
    z_alpha = norm.ppf(1 - alpha / 2)  # Two-tailed
    z_power = norm.ppf(power)
    
    # Effect size (Cohen's d)
    cohens_d = min_detectable_diff / expected_sd
    
    # Sample size per group
    n_per_group = math.ceil(2 * ((z_alpha + z_power) / cohens_d) ** 2)
    
    return {
        'sample_per_group': n_per_group,
        'total_sample': n_per_group * 2,
        'cohens_d': cohens_d,
        'effect_size': min_detectable_diff
    }

