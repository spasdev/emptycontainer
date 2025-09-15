import os
import subprocess
from flask import Flask, render_template_string, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Updated HTML template with two buttons for the new functions
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Tools</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; color: #333; text-align: center; margin-top: 50px; }
        .container { background: white; padding: 2rem; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .buttons form { display: inline-block; margin: 0 10px; }
        button { background-color: #007bff; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        button.secondary { background-color: #6c757d; }
        button.secondary:hover { background-color: #5a6268; }
        pre { background-color: #eee; text-align: left; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; max-width: 800px; margin: auto;}
        .message { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Network Diagnostic Tools 🛠️</h1>
        <p>Run network tools inside the container.</p>
        <div class="buttons">
            <form action="/traceroute" method="post">
                <button type="submit">Traceroute to 192.168.1.66</button>
            </form>
            <form action="/netinfo" method="post">
                <button type="submit" class="secondary">Show Network Config</button>
            </form>
        </div>
        
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

def run_command(command):
    """Helper function to run a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30  # Increased timeout for potentially long commands
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return f"⌛️ Command '{' '.join(command)}' timed out."
    except Exception as e:
        return f"An error occurred: {e}"

@app.route("/")
def index():
    """Renders the main page with the buttons."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/traceroute", methods=["POST"])
def traceroute_host():
    """Handles the traceroute button press."""
    ip_address = "192.168.1.66"
    output = run_command(["traceroute", ip_address])
    flash(f"🔍 Traceroute results for {ip_address}:\n\n{output}")
    return redirect(url_for('index'))

@app.route("/netinfo", methods=["POST"])
def network_info():
    """Handles the network config button press."""
    ip_addr_output = run_command(["ip", "addr"])
    ip_route_output = run_command(["ip", "route"])
    
    full_output = (
        "===== IP Addresses =====\n"
        f"{ip_addr_output}\n"
        "===== Routing Table =====\n"
        f"{ip_route_output}"
    )
    flash(full_output)
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)