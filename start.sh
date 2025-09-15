#!/bin/sh
# Start the Tailscale daemon in the background
/app/tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &
sleep 3

# Bring the Tailscale interface up
/app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=cloudrun-app --accept-routes=true
echo "Tailscale started"
sleep 3

# Start the Gunicorn server, routing its traffic through the Tailscale SOCKS5 proxy
# Use the PORT env var, defaulting to 8080
ALL_PROXY=socks5://localhost:1055/ gunicorn --bind 0.0.0.0:${PORT:-8080} main:app