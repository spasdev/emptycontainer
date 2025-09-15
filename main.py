import os
import subprocess
import socket
from flask import Flask, render_template_string, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Updated HTML template with the new reachability test button
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
        button.danger { background-color: #dc3545; }
        button.danger:hover { background-color: #c82333; }
        pre { background-color: #eee; text-align: left; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; max-width: 800px; margin: auto;}
        .message { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Network Diagnostic Tools 🛠️</h1>
        <p>Run network tools inside the container.</p>
        <div class="buttons">
            <form action="/reachability-test" method="post">
                <button type="submit">Test App Reachability to 192.168.1.66</button>
            </form>
            <form action="/netinfo" method="post">
                <button type="submit" class="secondary">Show Network Config</button>
            </form>
            <form action="/debug" method="post">
                <button type="submit" class="danger">Run Debug Evaluation</button>
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
            timeout=30
        )
        return result.stdout.strip() + "\n" + result.stderr.strip()
    except subprocess.TimeoutExpired:
        return f"⌛️ Command '{' '.join(command)}' timed out."
    except Exception as e:
        return f"An error occurred: {e}"

@app.route("/")
def index():
    """Renders the main page with the buttons."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/reachability-test", methods=["POST"])
def reachability_test():
    """Attempts a TCP connection from the app to a target host and port."""
    host = "192.168.1.66"
    port = 80  # We test a standard web server port. Change if the target service uses a different port.
    timeout = 5

    try:
        # Create a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            # Attempt to connect. This will be routed through the Tailscale proxy.
            s.connect((host, port))
        
        flash(f"✅ Success! A connection was established to {host} on port {port}.")

    except socket.timeout:
        flash(f"❌ Failed: Connection to {host} on port {port} timed out after {timeout} seconds.")
    except ConnectionRefusedError:
        flash(f"❌ Failed: Connection to {host} on port {port} was refused. The host is reachable, but the port is closed.")
    except Exception as e:
        flash(f"❌ Failed: An unexpected error occurred while connecting to {host} on port {port}.\nError: {e}")

    return redirect(url_for('index'))

@app.route("/netinfo", methods=["POST"])
def network_info():
    """Handles the network config button press."""
    ip_addr_output = run_command(["ip", "addr"])
    ip_route_output = run_command(["ip", "route"])
    
    full_output = (
        "===== IP Addresses =====\n"
        f"{ip_addr_output}\n\n"
        "===== Routing Table =====\n"
        f"{ip_route_output}"
    )
    flash(full_output)
    return redirect(url_for('index'))

@app.route("/debug", methods=["POST"])
def debug_evaluation():
    """Runs a series of checks to debug Tailscale routing."""
    report = ["### Tailscale Debug Evaluation ###\n"]

    # 1. Check for the ALL_PROXY environment variable
    proxy_var = os.getenv('ALL_PROXY', 'NOT SET')
    report.append(f"===== 1. Environment Variable Check =====\nALL_PROXY={proxy_var}\n")

    # 2. Check Tailscale status
    ts_status = run_command(["/app/tailscale", "status"])
    report.append(f"===== 2. Tailscale Status =====\n{ts_status}\n")

    # 3. Check for the SOCKS5 listener
    listener_check = run_command(["ss", "-lntp"])
    report.append(f"===== 3. SOCKS5 Listener (ss -lntp) =====\n{listener_check}\n")

    # 4. Get public IP through the Tailscale proxy
    proxied_ip = run_command(["curl", "--socks5", "localhost:1055", "ifconfig.me"])
    report.append(f"===== 4. Public IP (via Tailscale SOCKS5) =====\n{proxied_ip}\n")

    # 5. Get public IP without the proxy
    direct_ip = run_command(["curl", "ifconfig.me"])
    report.append(f"===== 5. Public IP (direct connection) =====\n{direct_ip}\n")
    
    # 6. Conclusion
    conclusion = "CONCLUSION: "
    if proxied_ip and direct_ip and proxied_ip != direct_ip:
        conclusion += "✅ Traffic appears to be routed correctly through Tailscale. The proxied and direct IPs are different."
    else:
        conclusion += "❌ Traffic is likely NOT routed through Tailscale. The proxied and direct IPs are the same or an error occurred."
    report.append(f"===== 6. Conclusion =====\n{conclusion}")

    flash("\n".join(report))
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)