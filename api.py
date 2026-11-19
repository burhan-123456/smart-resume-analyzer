from flask import Flask, jsonify
from database import get_connection
from database import get_connection, init_db
from flask import Flask, jsonify, request


app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "Smart Resume Analyzer API",
        "status": "running"
    })

@app.route("/database-status")
def database_status():
    connection = get_connection()
    connection.close()

    return jsonify({
        "database": "SQLite",
        "status": "connected"
    })


@app.route("/submit-resume", methods=["POST"])
def submit_resume():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    return jsonify({
        "message": "Resume received successfully",
        "candidate": data
    }), 201


    
if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)