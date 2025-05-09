#!/bin/bash
while true
 do
  python3 /home/smd/tvdirbg/tvxml.py
  sleep 1h
  systemctl restart eit-stream
  sleep 24h
 done
exit 0
