import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    """Example endpoint that returns a simple string."""
    return "Hello, Cloud Run! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
