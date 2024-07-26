#!/bin/bash

cd /root/wpi
git fetch origin              # 获取远程分支的最新更新
git reset --hard origin/main  # 将本地分支重置到远程分支的最新提交

sudo systemctl stop start.service

echo "Starting WPI"
Python3 /root/wpi/main.py
