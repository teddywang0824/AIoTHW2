import sqlite3
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

import data_updater

app = Flask(__name__)
CORS(app)

DB_PATH = data_updater.DB_PATH

def execute_query(query, params=(), fetch_all=True):
    is_postgres = data_updater.POSTGRES_URL and data_updater.psycopg2 is not None
    
    if is_postgres:
        conn = data_updater.psycopg2.connect(data_updater.POSTGRES_URL)
        cursor = conn.cursor(cursor_factory=data_updater.psycopg2.extras.RealDictCursor)
        # 轉換 SQLite 參數綁定 ? 為 Postgres 的 %s
        query = query.replace('?', '%s')
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
    cursor.execute(query, params)
    
    if fetch_all:
        result = [dict(row) for row in cursor.fetchall()]
    else:
        row = cursor.fetchone()
        result = dict(row) if row else None
        
    conn.close()
    return result



@app.route('/api/options', methods=['GET'])
@app.route('/options', methods=['GET'])
def get_options():
    try:
        data_updater.init_db_if_needed() # 確保在 Vercel cold start 狀態下，必定先抓資料
        
        regions = execute_query('SELECT DISTINCT regionName FROM TemperatureForecasts ORDER BY regionName')
        dates = execute_query('SELECT DISTINCT dataDate FROM TemperatureForecasts ORDER BY dataDate')

        return jsonify({
            "regions": [row.get('regionname', row.get('regionName')) for row in regions],
            "dates": [row.get('datadate', row.get('dataDate')) for row in dates]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast', methods=['GET'])
@app.route('/forecast', methods=['GET'])
def get_forecast():
    region = request.args.get('region')
    date = request.args.get('date')
    
    if not region or not date:
        return jsonify({"error": "請提供 region 與 date 參數"}), 400

    try:
        data_updater.init_db_if_needed()
        row = execute_query('''
            SELECT mint, maxt FROM TemperatureForecasts 
            WHERE regionName = ? AND dataDate = ?
        ''', (region, date), fetch_all=False)

        if row:
            return jsonify({"mint": row['mint'], "maxt": row['maxt']})
        else:
            return jsonify({"error": "找不到資料"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast_all', methods=['GET'])
@app.route('/forecast_all', methods=['GET'])
def get_forecast_all():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "請提供 date 參數"}), 400

    try:
        data_updater.init_db_if_needed()
        rows = execute_query('''
            SELECT regionName, mint, maxt FROM TemperatureForecasts 
            WHERE dataDate = ?
        ''', (date,))

        result = [{"region": row.get('regionname', row.get('regionName')), 
                   "mint": row['mint'], 
                   "maxt": row['maxt']} for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast_week', methods=['GET'])
@app.route('/forecast_week', methods=['GET'])
def get_forecast_week():
    region = request.args.get('region')
    if not region:
        return jsonify({"error": "請提供 region 參數"}), 400

    try:
        data_updater.init_db_if_needed()
        rows = execute_query('''
            SELECT dataDate, mint, maxt FROM TemperatureForecasts 
            WHERE regionName = ?
            ORDER BY dataDate ASC
            LIMIT 7
        ''', (region,))

        result = [{"date": row.get('datadate', row.get('dataDate')), 
                   "mint": row['mint'], 
                   "maxt": row['maxt']} for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 啟動背景更新排程 (非 Vercel 環境下)
    data_updater.start_scheduler()
    app.run(host='0.0.0.0', debug=True, port=5000)
