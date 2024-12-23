from flask import Flask, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host="in.leoxstudios.com",
        user="u3_qmMpg6ebmu",
        password="ias=Veu^tr@zEfny@sliQpJa",
        database="s3_MNS-NETWORK"
    )

@app.route('/api/votes/<path:param>')
def get_votes(param):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Check if param is a number (rank) or string (username)
        try:
            rank = int(param)
            # Get by rank
            cursor.execute("""
                SELECT *, ROW_NUMBER() OVER (ORDER BY votes DESC) as rank 
                FROM votes 
                ORDER BY votes DESC
                LIMIT 1 OFFSET %s
            """, (rank - 1,))
        except ValueError:
            # Get by username
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
