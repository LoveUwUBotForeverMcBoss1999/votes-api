from flask import Flask, jsonify, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__, template_folder='.')

def get_db():
    return mysql.connector.connect(
        host="in.leoxstudios.com",
        user="u3_qmMpg6ebmu",
        password="ias=Veu^tr@zEfny@sliQpJa",
        database="s3_MNS-NETWORK"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/votes/<path:param>')
def get_votes(param):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
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
        
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run()
