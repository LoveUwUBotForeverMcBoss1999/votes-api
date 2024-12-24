from flask import Flask, jsonify, send_from_directory, redirect
from flask_cors import CORS
import mysql.connector
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configure static file serving
app.static_folder = 'static'
app.static_url_path = ''

def get_db():
    return mysql.connector.connect(
        host="in.leoxstudios.com",
        user="u3_qmMpg6ebmu",
        password="ias=Veu^tr@zEfny@sliQpJa",
        database="s3_MNS-NETWORK"
    )

# Serve index.html for the root route
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Serve leaderboard.html for the /leaderboard route
@app.route('/leaderboard')
def serve_leaderboard():
    return send_from_directory('.', 'leaderboard.html')

# Redirect /404 to the root route
@app.route('/404')
def handle_404():
    return redirect('/')

# API route for votes
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

# API route to get the latest vote
@app.route('/api/votes')
def get_latest_vote():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT *, ROW_NUMBER() OVER (ORDER BY votes DESC) as rank
            FROM votes
            ORDER BY last_vote DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            playername = result['last_name']
            return jsonify({
                "Voter Avatar": f"https://mc-heads.net/avatar/{playername}",
                "Voter Name": playername,
                "Total Votes": result['votes'],
                "Last Voted Time": result['last_vote'].strftime('%Y-%m-%d %H:%M:%S'),
                "Vote Rank": result['rank']
            })
        return jsonify({"error": "No votes found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals(): db.close()

# Catch-all route to serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
