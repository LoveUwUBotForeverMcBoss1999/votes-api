from flask import Flask, jsonify, send_file
from flask_cors import CORS  # Add this import
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db():
    return mysql.connector.connect(
        host="in.leoxstudios.com",
        user="u3_qmMpg6ebmu",
        password="ias=Veu^tr@zEfny@sliQpJa",
        database="s3_MNS-NETWORK"
    )

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not path or path == '/':
        return send_file('index.html')
    return app.send_static_file(path)

@app.route('/api/votes/<path:param>')
def get_votes(param):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            rank = int(param)
            cursor.execute("""
                SELECT *, ROW_NUMBER() OVER (ORDER BY votes DESC) as rank 
                FROM votes 
                ORDER BY votes DESC
                LIMIT 1 OFFSET %s
            """, (rank - 1,))
        except ValueError:
            cursor.execute("""
                WITH ranked_votes AS (
                    SELECT *, ROW_NUMBER() OVER (ORDER BY votes DESC) as rank 
                    FROM votes
                )
                SELECT * FROM ranked_votes WHERE last_name = %s
            """, (param,))
        
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                "username": result['last_name'],
                "rank": result['rank'],
                "votes": result['votes'],
                "lastVoted": result['last_vote'].strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({"error": "User not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals(): db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
