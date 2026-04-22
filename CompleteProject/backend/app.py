import sqlite3
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

import data_updater

app = Flask(__name__)
CORS(app)

DB_PATH = data_updater.DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/cron_update', methods=['GET'])
def cron_update():
    """Vercel Cron Job endpoint 呼叫此 API 以自動更新"""
    try:
        data_updater.fetch_and_save_weather_data()
        return jsonify({"status": "success", "message": "Weather data updated successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/options', methods=['GET'])
def get_options():
    try:
        data_updater.init_db_if_needed() # 確保在 Vercel cold start 狀態下，必定先抓資料
        conn = get_db_connection()
        regions = conn.execute('SELECT DISTINCT regionName FROM TemperatureForecasts ORDER BY regionName').fetchall()
        dates = conn.execute('SELECT DISTINCT dataDate FROM TemperatureForecasts ORDER BY dataDate').fetchall()
        conn.close()

        return jsonify({
            "regions": [row['regionName'] for row in regions],
            "dates": [row['dataDate'] for row in dates]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    region = request.args.get('region')
    date = request.args.get('date')
    
    if not region or not date:
        return jsonify({"error": "請提供 region 與 date 參數"}), 400

    try:
        data_updater.init_db_if_needed()
        conn = get_db_connection()
        row = conn.execute('''
            SELECT mint, maxt FROM TemperatureForecasts 
            WHERE regionName = ? AND dataDate = ?
        ''', (region, date)).fetchone()
        conn.close()

        if row:
            return jsonify({"mint": row['mint'], "maxt": row['maxt']})
        else:
            return jsonify({"error": "找不到資料"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast_all', methods=['GET'])
def get_forecast_all():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "請提供 date 參數"}), 400

    try:
        data_updater.init_db_if_needed()
        conn = get_db_connection()
        rows = conn.execute('''
            SELECT regionName, mint, maxt FROM TemperatureForecasts 
            WHERE dataDate = ?
        ''', (date,)).fetchall()
        conn.close()

        result = [{"region": row['regionName'], "mint": row['mint'], "maxt": row['maxt']} for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast_week', methods=['GET'])
def get_forecast_week():
    region = request.args.get('region')
    if not region:
        return jsonify({"error": "請提供 region 參數"}), 400

    try:
        data_updater.init_db_if_needed()
        conn = get_db_connection()
        rows = conn.execute('''
            SELECT dataDate, mint, maxt FROM TemperatureForecasts 
            WHERE regionName = ?
            ORDER BY dataDate ASC
            LIMIT 7
        ''', (region,)).fetchall()
        conn.close()

        result = [{"date": row['dataDate'], "mint": row['mint'], "maxt": row['maxt']} for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 啟動背景更新排程 (非 Vercel 環境下)
    data_updater.start_scheduler()
    app.run(host='0.0.0.0', debug=True, port=5000)
