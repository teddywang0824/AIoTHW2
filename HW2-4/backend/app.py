from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'HW2-3', 'data.db'))

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/options', methods=['GET'])
def get_options():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        # 查詢所有地區
        c.execute('SELECT DISTINCT regionName FROM TemperatureForecasts ORDER BY regionName')
        regions = [row['regionName'] for row in c.fetchall()]
        # 查詢所有時間 (排序)
        c.execute('SELECT DISTINCT dataDate FROM TemperatureForecasts ORDER BY dataDate')
        dates = [row['dataDate'] for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            "regions": regions,
            "dates": dates
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast', methods=['GET'])
def get_forecast():
    region = request.args.get('region')
    date = request.args.get('date')
    
    if not region or not date:
        return jsonify({"error": "Missing region or date parameter"}), 400
        
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT mint, maxt 
            FROM TemperatureForecasts 
            WHERE regionName = ? AND dataDate = ?
        ''', (region, date))
        row = c.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                "mint": row['mint'],
                "maxt": row['maxt']
            })
        else:
            return jsonify({"error": "Data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast_all', methods=['GET'])
def get_forecast_all():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Missing date parameter"}), 400
        
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT regionName, mint, maxt 
            FROM TemperatureForecasts 
            WHERE dataDate = ?
        ''', (date,))
        rows = c.fetchall()
        conn.close()
        
        result = {}
        for row in rows:
            result[row['regionName']] = {
                "mint": row['mint'],
                "maxt": row['maxt']
            }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast_week', methods=['GET'])
def get_forecast_week():
    region = request.args.get('region')
    if not region:
        return jsonify({"error": "Missing region parameter"}), 400
        
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT dataDate, mint, maxt 
            FROM TemperatureForecasts 
            WHERE regionName = ?
            ORDER BY dataDate ASC
        ''', (region,))
        rows = c.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                "date": row['dataDate'],
                "mint": row['mint'],
                "maxt": row['maxt']
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

