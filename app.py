"""
Flask A/B Testing Calculator Application
Main application entry point
"""
from flask import Flask, render_template, request, jsonify, session
import os

from utils.statistics import (
    two_proportion_z_test,
    two_sample_z_test,
    welch_t_test,
    sample_size_proportion,
    sample_size_continuous
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')


@app.context_processor
def inject_gtm_id():
    """Make GTM ID available in all templates"""
    return dict(gtm_id=os.environ.get('GTM_ID', ''))


@app.route('/')
def index():
    """Home page with navigation to all calculators"""
    return render_template('index.html')


@app.route('/conversion-rate', methods=['GET', 'POST'])
def conversion_rate():
    """Conversion Rate Significance Calculator (Two-Proportion Z Test)"""
    if request.method == 'POST':
        try:
            control_visitors = int(request.form.get('control_visitors', 0))
            control_conversions = int(request.form.get('control_conversions', 0))
            variant_visitors = int(request.form.get('variant_visitors', 0))
            variant_conversions = int(request.form.get('variant_conversions', 0))
            alpha = float(request.form.get('alpha', 0.05))
            
            # Validate alpha range
            if alpha < 0.01 or alpha > 0.1:
                raise ValueError("Alpha deve estar entre 0.01 e 0.1")
            
            result = two_proportion_z_test(
                control_visitors, control_conversions,
                variant_visitors, variant_conversions, alpha
            )
            
            return render_template('conversion_rate.html', result=result, 
                                 control_visitors=control_visitors,
                                 control_conversions=control_conversions,
                                 variant_visitors=variant_visitors,
                                 variant_conversions=variant_conversions,
                                 alpha=alpha)
        except (ValueError, ZeroDivisionError) as e:
            error = str(e)
            # Preserve form values on error
            # Safely parse alpha - if invalid, use default
            try:
                alpha = float(request.form.get('alpha', 0.05))
                # Validate alpha range
                if alpha < 0.01 or alpha > 0.1:
                    alpha = 0.05
            except (ValueError, TypeError):
                alpha = 0.05
            return render_template('conversion_rate.html', error=error,
                                 control_visitors=request.form.get('control_visitors', ''),
                                 control_conversions=request.form.get('control_conversions', ''),
                                 variant_visitors=request.form.get('variant_visitors', ''),
                                 variant_conversions=request.form.get('variant_conversions', ''),
                                 alpha=alpha)
    
    return render_template('conversion_rate.html')


@app.route('/average-value', methods=['GET', 'POST'])
def average_value():
    """Average Value Significance Calculator (Z-test or t-test)"""
    if request.method == 'POST':
        try:
            mean_a = float(request.form.get('mean_a', 0))
            n_a = int(request.form.get('n_a', 0))
            mean_b = float(request.form.get('mean_b', 0))
            n_b = int(request.form.get('n_b', 0))
            
            # Check if population SD is known (checkbox)
            known_pop_sd = request.form.get('known_pop_sd') == 'on'
            
            if known_pop_sd:
                # Use z-test with population standard deviation
                pop_sd_a = float(request.form.get('pop_sd_a', 0))
                pop_sd_b = float(request.form.get('pop_sd_b', 0))
                result = two_sample_z_test(mean_a, pop_sd_a, n_a, mean_b, pop_sd_b, n_b)
                return render_template('average_value.html', result=result,
                                     mean_a=mean_a, n_a=n_a,
                                     mean_b=mean_b, n_b=n_b,
                                     known_pop_sd=True,
                                     pop_sd_a=pop_sd_a, pop_sd_b=pop_sd_b)
            else:
                # Use t-test with sample standard deviation
                sd_a = float(request.form.get('sd_a', 0))
                sd_b = float(request.form.get('sd_b', 0))
                result = welch_t_test(mean_a, sd_a, n_a, mean_b, sd_b, n_b)
                return render_template('average_value.html', result=result,
                                     mean_a=mean_a, sd_a=sd_a, n_a=n_a,
                                     mean_b=mean_b, sd_b=sd_b, n_b=n_b,
                                     known_pop_sd=False)
        except (ValueError, ZeroDivisionError) as e:
            error = str(e)
            # Preserve form state on error
            known_pop_sd = request.form.get('known_pop_sd') == 'on'
            return render_template('average_value.html', error=error, known_pop_sd=known_pop_sd,
                                 mean_a=request.form.get('mean_a', ''),
                                 n_a=request.form.get('n_a', ''),
                                 mean_b=request.form.get('mean_b', ''),
                                 n_b=request.form.get('n_b', ''),
                                 sd_a=request.form.get('sd_a', ''),
                                 sd_b=request.form.get('sd_b', ''),
                                 pop_sd_a=request.form.get('pop_sd_a', ''),
                                 pop_sd_b=request.form.get('pop_sd_b', ''))
    
    return render_template('average_value.html', known_pop_sd=False)


@app.route('/planner-proportion', methods=['GET', 'POST'])
def planner_proportion():
    """A/B Test Planner - Proportion Test (Frequentist)"""
    if request.method == 'POST':
        try:
            baseline_rate = float(request.form.get('baseline_rate', 0)) / 100
            mde_type = request.form.get('mde_type', 'absolute')
            mde_value = float(request.form.get('mde_value', 0))
            power = float(request.form.get('power', 0.8))
            alpha = float(request.form.get('alpha', 0.05))
            daily_traffic = int(request.form.get('daily_traffic', 0))
            traffic_type = request.form.get('traffic_type', 'per_variant')
            
            result = sample_size_proportion(
                baseline_rate, mde_type, mde_value, power, alpha
            )
            
            # Calculate duration
            if traffic_type == 'per_variant':
                days = result['sample_per_variant'] / daily_traffic if daily_traffic > 0 else 0
            else:
                days = (result['total_sample'] / 2) / daily_traffic if daily_traffic > 0 else 0
            
            result['days'] = max(1, int(days))
            result['weeks'] = round(days / 7, 1)
            result['daily_traffic'] = daily_traffic
            result['traffic_type'] = traffic_type
            
            return render_template('planner_proportion.html', result=result,
                                 baseline_rate=baseline_rate * 100,
                                 mde_type=mde_type, mde_value=mde_value,
                                 power=power, alpha=alpha,
                                 daily_traffic=daily_traffic, traffic_type=traffic_type)
        except (ValueError, ZeroDivisionError) as e:
            error = str(e)
            return render_template('planner_proportion.html', error=error)
    
    return render_template('planner_proportion.html')


@app.route('/planner-average', methods=['GET', 'POST'])
def planner_average():
    """A/B Test Planner - Average Value (t-test)"""
    if request.method == 'POST':
        try:
            expected_mean = float(request.form.get('expected_mean', 0))
            expected_sd = float(request.form.get('expected_sd', 0))
            min_detectable_diff = float(request.form.get('min_detectable_diff', 0))
            power = float(request.form.get('power', 0.8))
            alpha = float(request.form.get('alpha', 0.05))
            daily_sample = int(request.form.get('daily_sample', 0))
            
            result = sample_size_continuous(
                expected_mean, expected_sd, min_detectable_diff, power, alpha
            )
            
            # Calculate duration
            days = result['sample_per_group'] / daily_sample if daily_sample > 0 else 0
            result['days'] = max(1, int(days))
            result['weeks'] = round(days / 7, 1)
            result['daily_sample'] = daily_sample
            
            return render_template('planner_average.html', result=result,
                                 expected_mean=expected_mean,
                                 expected_sd=expected_sd,
                                 min_detectable_diff=min_detectable_diff,
                                 power=power, alpha=alpha,
                                 daily_sample=daily_sample)
        except (ValueError, ZeroDivisionError) as e:
            error = str(e)
            return render_template('planner_average.html', error=error)
    
    return render_template('planner_average.html')




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')

