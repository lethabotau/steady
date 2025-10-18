"""
Flask Backend Server for Steady App
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import forecast_engine as forecast
import insights_engine as insights
import steadiness_engine as steadiness
import recommendation_engine as recommendations
import feature_builder as features

app = Flask(__name__)
CORS(app)  # Allow all origins for development

# HOME TAB ROUTES
@app.route('/api/home/overview', methods=['GET'])
def get_home_overview():
    """Combined data for home dashboard"""
    driver_id = request.args.get('driver_id', 'driver1')
    return jsonify({
        "forecast": forecast.get_weekly_forecast(driver_id, "2026-10-20"),
        "steadiness": steadiness.get_steadiness_score(driver_id),
        "goal_progress": recommendations.get_goal_progress(driver_id)
    })

# FORECAST TAB ROUTES
@app.route('/api/forecast/weekly', methods=['GET'])
def get_weekly_forecast():
    driver_id = request.args.get('driver_id', 'driver1')
    week = request.args.get('week', '2026-10-20')
    return jsonify(forecast.get_weekly_forecast(driver_id, week))

@app.route('/api/forecast/chart', methods=['GET'])
def get_forecast_chart():
    driver_id = request.args.get('driver_id', 'driver1')
    weeks = int(request.args.get('weeks', 8))
    return jsonify(forecast.get_forecast_chart_data(driver_id, weeks))

@app.route('/api/forecast/daily', methods=['GET'])
def get_daily_forecast():
    driver_id = request.args.get('driver_id', 'driver1')
    date = request.args.get('date', '2026-10-20')
    return jsonify(forecast.get_daily_forecast(driver_id, date))

# INSIGHTS TAB ROUTES
@app.route('/api/insights/stability', methods=['GET'])
def get_stability_metrics():
    driver_id = request.args.get('driver_id', 'driver1')
    return jsonify(insights.get_income_stability_metrics(driver_id))

@app.route('/api/insights/peak-hours', methods=['GET'])
def get_peak_hours():
    driver_id = request.args.get('driver_id', 'driver1')
    return jsonify(insights.get_peak_hours_analysis(driver_id))

@app.route('/api/insights/weather', methods=['GET'])
def get_weather_impact():
    driver_id = request.args.get('driver_id', 'driver1')
    return jsonify(insights.get_weather_impact_analysis(driver_id))

@app.route('/api/insights/events', methods=['GET'])
def get_events():
    driver_id = request.args.get('driver_id', 'driver1')
    days = int(request.args.get('days', 14))
    return jsonify(insights.get_event_opportunities(driver_id, days))

# STEADINESS/TRADE TAB ROUTES
@app.route('/api/steadiness/score', methods=['GET'])
def get_steadiness():
    driver_id = request.args.get('driver_id', 'driver1')
    period = request.args.get('period', 'weekly')
    return jsonify(steadiness.get_steadiness_score(driver_id, period))

@app.route('/api/steadiness/breakdown', methods=['GET'])
def get_consistency():
    driver_id = request.args.get('driver_id', 'driver1')
    return jsonify(steadiness.get_consistency_breakdown(driver_id))

@app.route('/api/steadiness/volatility', methods=['GET'])
def get_volatility():
    driver_id = request.args.get('driver_id', 'driver1')
    weeks = int(request.args.get('weeks', 12))
    return jsonify(steadiness.get_volatility_trend(driver_id, weeks))

# RECOMMENDATIONS ROUTES
@app.route('/api/recommendations/weekly', methods=['GET'])
def get_weekly_recs():
    driver_id = request.args.get('driver_id', 'driver1')
    week = request.args.get('week', '2026-10-20')
    return jsonify(recommendations.get_weekly_recommendations(driver_id, week))

@app.route('/api/recommendations/daily', methods=['GET'])
def get_daily_recs():
    driver_id = request.args.get('driver_id', 'driver1')
    date = request.args.get('date', '2026-10-20')
    return jsonify(recommendations.get_daily_recommendations(driver_id, date))

@app.route('/api/recommendations/schedule', methods=['POST'])
def get_optimal_schedule():
    data = request.json
    driver_id = data.get('driver_id', 'driver1')
    target = data.get('target_income', 1000)
    hours = data.get('available_hours', 40)
    return jsonify(recommendations.get_optimal_schedule(driver_id, target, hours))

# PROFILE/USER ROUTES
@app.route('/api/profile/preferences', methods=['GET'])
def get_preferences():
    driver_id = request.args.get('driver_id', 'driver1')
    return jsonify(features.get_user_preferences(driver_id))

@app.route('/api/profile/preferences', methods=['POST'])
def update_preferences():
    data = request.json
    driver_id = data.get('driver_id', 'driver1')
    # In real implementation, would save to database
    return jsonify({"success": True, "message": "Preferences updated"})

@app.route('/api/profile/data', methods=['GET'])
def get_profile_data():
    driver_id = request.args.get('driver_id', 'driver1')
    return jsonify(features.load_driver_data(driver_id))

# HEALTH CHECK
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Steady API is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)