import os
import subprocess
from flask import Flask, render_template_string, redirect, url_for, flash

app = Flask(__name__)
# It's good practice to set a secret key for flashing messages
app.secret_key = os.urandom(24)

# Use an HTML template string for the user interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Run App</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; color: #333; text-align: center; margin-top: 50px; }
        .container { background: white; padding: 2rem; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        button { background-color: #007bff; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        pre { background-color: #eee; text-align: left; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
        .message { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello, Cloud Run! 🚀</h1>
        <p>Press the button to ping a device on your Tailnet.</p>
        <form action="/ping" method="post">
            <button type="submit">Ping 192.168.1.66</button>
        </form>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <div class="message">
              {% for category, message in messages %}
                <pre class="{{ category }}">{{ message }}</pre>
              {% endfor %}
            </div>
          {% endif %}
        {% endwith %}
    </div>
</body>
</html>
"""

@app.route("/")
def hello_world():
    """Renders the main page with the button."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/ping", methods=["POST"])
def ping_host():
    """Handles the button press, executes the ping, and shows the result."""
    ip_address = "192.168.1.66"
    
    # The command uses '-c 4' to send 4 packets, which is standard for Linux.
    command = ["ping", "-c", "4", ip_address]
    
    try:
        # Execute the ping command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10 # Add a timeout to prevent it from hanging
        )
        
        # Combine stdout and stderr for the full output
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            flash(f"✅ Ping successful to {ip_address}:\n\n{output}")
        else:
            flash(f"❌ Ping failed to {ip_address}:\n\n{output}")
            
    except subprocess.TimeoutExpired:
        flash(f"⌛️ Ping timed out. The host {ip_address} is unreachable.")
    except Exception as e:
        flash(f"An error occurred: {e}")

    return redirect(url_for('hello_world'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)