from flask import Flask, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://votes.mnsnetwork.xyz", "http://localhost:3000"],
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'in.leoxstudios.com'),
        user=os.getenv('DB_USER', 'u3_qmMpg6ebmu'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 's3_MNS-NETWORK'),
        connection_timeout=5
    )

@app.route('/api/votes/<path:param>')
def get_votes(param):
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            rank = int(param)
            if rank < 1:
                return jsonify({"error": "Invalid rank"}), 400
                
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
                "lastVoted": result['last_vote'].strftime('%Y-%m-%d %H:%M:%S') if result['last_vote'] else None
            })
        return jsonify({"error": "User not found"}), 404
        
    except mysql.connector.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
        if cursor: cursor.close()
        if db: db.close()

@app.route('/health')
def health_check():
    try:
        db = get_db()
        db.close()
        return jsonify({"status": "healthy"}), 200
    except:
        return jsonify({"status": "unhealthy"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
