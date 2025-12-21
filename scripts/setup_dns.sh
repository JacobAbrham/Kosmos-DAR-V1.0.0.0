#!/bin/bash
# Script to update Cloudflare DNS records for nuvanta-holding.com
# Usage: ./setup_dns.sh <CLOUDFLARE_API_TOKEN> <ZONE_ID>

API_TOKEN=$1
ZONE_ID=$2
IP_ADDRESS="47.91.123.78"

if [ -z "$API_TOKEN" ] || [ -z "$ZONE_ID" ]; then
    echo "Usage: $0 <CLOUDFLARE_API_TOKEN> <ZONE_ID>"
    exit 1
fi

echo "Creating A record for nuvanta-holding.com -> $IP_ADDRESS"
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"A","name":"nuvanta-holding.com","content":"'"$IP_ADDRESS"'","ttl":1,"proxied":true}'

echo -e "\nCreating CNAME record for www.nuvanta-holding.com -> nuvanta-holding.com"
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"CNAME","name":"www.nuvanta-holding.com","content":"nuvanta-holding.com","ttl":1,"proxied":true}'

echo -e "\nDNS Setup Complete!"
