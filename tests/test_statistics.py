"""
Unit tests for statistical functions
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.statistics import (
    two_proportion_z_test,
    welch_t_test,
    mann_whitney_u_test,
    sample_size_proportion,
    sample_size_continuous
)


class TestTwoProportionZTest(unittest.TestCase):
    """Tests for two-proportion z-test"""
    
    def test_basic_calculation(self):
        """Test basic z-test calculation"""
        result = two_proportion_z_test(
            control_visitors=1000,
            control_conversions=50,
            variant_visitors=1000,
            variant_conversions=60
        )
        
        self.assertIn('control_rate', result)
        self.assertIn('variant_rate', result)
        self.assertIn('z_score', result)
        self.assertIn('p_value', result)
        self.assertIn('is_significant', result)
        
        # Control rate should be 5%
        self.assertAlmostEqual(result['control_rate'], 5.0, places=1)
        
        # Variant rate should be 6%
        self.assertAlmostEqual(result['variant_rate'], 6.0, places=1)
    
    def test_zero_visitors_error(self):
        """Test that zero visitors raises error"""
        with self.assertRaises(ValueError):
            two_proportion_z_test(0, 0, 100, 10)
    
    def test_no_difference(self):
        """Test with identical conversion rates"""
        result = two_proportion_z_test(
            control_visitors=1000,
            control_conversions=50,
            variant_visitors=1000,
            variant_conversions=50
        )
        
        # Should have zero lift
        self.assertAlmostEqual(result['absolute_lift'], 0.0, places=2)


class TestWelchTTest(unittest.TestCase):
    """Tests for Welch's t-test"""
    
    def test_basic_calculation(self):
        """Test basic t-test calculation"""
        result = welch_t_test(
            mean_a=100.0,
            sd_a=15.0,
            n_a=30,
            mean_b=105.0,
            sd_b=15.0,
            n_b=30
        )
        
        self.assertIn('mean_diff', result)
        self.assertIn('t_statistic', result)
        self.assertIn('p_value', result)
        self.assertIn('ci_lower', result)
        self.assertIn('ci_upper', result)
        
        # Mean difference should be -5
        self.assertAlmostEqual(result['mean_diff'], -5.0, places=1)
    
    def test_insufficient_sample_size(self):
        """Test that sample size < 2 raises error"""
        with self.assertRaises(ValueError):
            welch_t_test(100, 15, 1, 105, 15, 30)
    
    def test_zero_sd_error(self):
        """Test that zero standard deviation raises error"""
        with self.assertRaises(ValueError):
            welch_t_test(100, 0, 30, 105, 15, 30)


class TestMannWhitneyUTest(unittest.TestCase):
    """Tests for Mann-Whitney U test"""
    
    def test_basic_calculation(self):
        """Test basic Mann-Whitney U calculation"""
        result = mann_whitney_u_test(
            mean_a=100.0,
            sd_a=15.0,
            n_a=30,
            mean_b=105.0,
            sd_b=15.0,
            n_b=30
        )
        
        self.assertIn('u_statistic', result)
        self.assertIn('z_score', result)
        self.assertIn('p_value', result)
        self.assertIn('is_significant', result)
        
        # Validate p_value is between 0 and 1
        self.assertGreaterEqual(result['p_value'], 0.0)
        self.assertLessEqual(result['p_value'], 1.0)
        
        # Validate u_statistic is within valid range
        self.assertGreaterEqual(result['u_statistic'], 0)
        self.assertLessEqual(result['u_statistic'], 30 * 30)
    
    def test_zero_sd_error(self):
        """Test that zero standard deviation raises error"""
        with self.assertRaises(ValueError):
            mann_whitney_u_test(100, 0, 30, 105, 15, 30)
        
        with self.assertRaises(ValueError):
            mann_whitney_u_test(100, 15, 30, 105, 0, 30)
    
    def test_negative_sd_error(self):
        """Test that negative standard deviation raises error"""
        with self.assertRaises(ValueError):
            mann_whitney_u_test(100, -5, 30, 105, 15, 30)
    
    def test_insufficient_sample_size(self):
        """Test that sample size < 2 raises error"""
        with self.assertRaises(ValueError):
            mann_whitney_u_test(100, 15, 1, 105, 15, 30)


class TestSampleSizeProportion(unittest.TestCase):
    """Tests for proportion sample size calculation"""
    
    def test_absolute_mde(self):
        """Test sample size with absolute MDE"""
        result = sample_size_proportion(
            baseline_rate=0.05,
            mde_type='absolute',
            mde_value=1.0,  # 1% absolute
            power=0.8,
            alpha=0.05
        )
        
        self.assertIn('sample_per_variant', result)
        self.assertIn('total_sample', result)
        self.assertGreater(result['sample_per_variant'], 0)
        self.assertEqual(result['total_sample'], result['sample_per_variant'] * 2)
    
    def test_relative_mde(self):
        """Test sample size with relative MDE"""
        result = sample_size_proportion(
            baseline_rate=0.05,
            mde_type='relative',
            mde_value=20.0,  # 20% relative (5% -> 6%)
            power=0.8,
            alpha=0.05
        )
        
        self.assertIn('sample_per_variant', result)
        self.assertGreater(result['sample_per_variant'], 0)
    
    def test_invalid_baseline_rate(self):
        """Test that invalid baseline rate raises error"""
        with self.assertRaises(ValueError):
            sample_size_proportion(1.5, 'absolute', 1.0, 0.8, 0.05)


class TestSampleSizeContinuous(unittest.TestCase):
    """Tests for continuous sample size calculation"""
    
    def test_basic_calculation(self):
        """Test basic continuous sample size calculation"""
        result = sample_size_continuous(
            expected_mean=100.0,
            expected_sd=15.0,
            min_detectable_diff=5.0,
            power=0.8,
            alpha=0.05
        )
        
        self.assertIn('sample_per_group', result)
        self.assertIn('total_sample', result)
        self.assertIn('cohens_d', result)
        self.assertGreater(result['sample_per_group'], 0)
        self.assertEqual(result['total_sample'], result['sample_per_group'] * 2)
    
    def test_zero_sd_error(self):
        """Test that zero standard deviation raises error"""
        with self.assertRaises(ValueError):
            sample_size_continuous(100, 0, 5, 0.8, 0.05)
    
    def test_zero_effect_size_error(self):
        """Test that zero effect size raises error"""
        with self.assertRaises(ValueError):
            sample_size_continuous(100, 15, 0, 0.8, 0.05)


if __name__ == '__main__':
    unittest.main()

