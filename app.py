from flask import Flask, jsonify
import mysql.connector
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host="in.leoxstudios.com",
        user="u3_qmMpg6ebmu",
        password="ias=Veu^tr@zEfny@sliQpJa",
        database="s3_MNS-NETWORK"
    )

@app.route('/api/votes/<rank>', methods=['GET'])
def get_votes_by_rank(rank):
    try:
        rank = int(rank)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT last_name, votes, last_vote,
            RANK() OVER (ORDER BY votes DESC) as rank
            FROM votes
            ORDER BY votes DESC
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if 0 < rank <= len(results):
            user = results[rank-1]
            return jsonify({
                "username": user['last_name'],
                "rank": user['rank'],
                "votes": user['votes'],
                "lastVoted": user['last_vote'].strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({"error": "Invalid rank"}), 404
        
    except ValueError:
        # Handle username lookup
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT last_name, votes, last_vote,
            RANK() OVER (ORDER BY votes DESC) as rank
            FROM votes
            WHERE last_name = %s
        """, (rank,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return jsonify({
                "username": user['last_name'],
                "rank": user['rank'],
                "votes": user['votes'],
                "lastVoted": user['last_vote'].strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
