#!/bin/bash
HOST="$1"
DOMAIN="$2"
PASSWORD="$3"
IP="$4"

curl -s "https://dynamicdns.park-your-domain.com/update?host=$HOST&domain=$DOMAIN&password=$PASSWORD&ip=$IP"
