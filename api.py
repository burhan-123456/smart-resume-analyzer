from flask import Flask, jsonify
from database import get_connection

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
if __name__ == "__main__":
    app.run(port=5000, debug=True)