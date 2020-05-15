#!/bin/bash
cmd_path=$(dirname $0)
cd $cmd_path

systemctl disable webchat
rm /lib/systemd/system/webchat.service
systemctl daemon-reload
echo "disable & remove webchat systemd service"
