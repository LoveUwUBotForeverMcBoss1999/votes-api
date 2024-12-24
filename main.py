from flask import Flask, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)

def get_db():
    try:
        conn = mysql.connector.connect(
            host="in.leoxstudios.com",
            user="u3_qmMpg6ebmu",
            password="ias=Veu^tr@zEfny@sliQpJa",
            database="s3_MNS-NETWORK",
            connection_timeout=10  # Added timeout
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")  # Debug print
        raise

@app.route('/api/votes/<path:param>')
def get_votes(param):
    try:
        # Debug print
        print(f"Received request for param: {param}")
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            rank = int(param)
            # Debug print
            print(f"Executing query for rank: {rank}")
            
            cursor.execute("""
                SELECT *, ROW_NUMBER() OVER (ORDER BY votes DESC) as rank 
                FROM votes 
                ORDER BY votes DESC
                LIMIT 1 OFFSET %s
            """, (rank - 1,))
        except ValueError:
            # Debug print
            print(f"Executing query for username: {param}")
            
            cursor.execute("""
                WITH ranked_votes AS (
                    SELECT *, ROW_NUMBER() OVER (ORDER BY votes DESC) as rank 
                    FROM votes
                )
                SELECT * FROM ranked_votes WHERE last_name = %s
            """, (param,))
        
        result = cursor.fetchone()
        
        # Debug print
        print(f"Query result: {result}")
        
        if result:
            response = {
                "username": result['last_name'],
                "rank": result['rank'],
                "votes": result['votes'],
                "lastVoted": result['last_vote'].strftime('%Y-%m-%d %H:%M:%S') if result['last_vote'] else None
            }
            return jsonify(response)
        return jsonify({"error": "User not found"}), 404
        
    except mysql.connector.Error as e:
        # Detailed error for debugging
        error_details = str(e)
        traceback.print_exc()  # Print stack trace
        return jsonify({
            "error": "Database error occurred",
            "details": error_details
        }), 500
    except Exception as e:
        # Detailed error for debugging
        error_details = str(e)
        traceback.print_exc()  # Print stack trace
        return jsonify({
            "error": "An unexpected error occurred",
            "details": error_details
        }), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals(): db.close()

# Add a test endpoint
@app.route('/test')
def test():
    return jsonify({"status": "API is running"})

# Add a database test endpoint
@app.route('/test/db')
def test_db():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({"status": "Database connection successful"})
    except Exception as e:
        return jsonify({
            "status": "Database connection failed",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
