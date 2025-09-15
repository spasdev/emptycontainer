# 1. Start with a lightweight Python image based on Alpine Linux
FROM python:3.11-alpine

# 2. Set the working directory
WORKDIR /app

# 3. Install system dependencies (traceroute is no longer needed)
RUN apk update && apk add --no-cache ca-certificates iproute2 curl

# 4. Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your application code and the updated start.sh script
COPY main.py .
COPY start.sh .

# 6. Copy Tailscale binaries from the official image
COPY --from=docker.io/tailscale/tailscale:stable /usr/local/bin/tailscaled /app/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable /usr/local/bin/tailscale /app/tailscale

# 7. Create directories needed for Tailscale state
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

# 8. Make the startup script executable
RUN chmod +x /app/start.sh

# 9. Set the container's startup command
CMD ["/app/start.sh"]