#!/bin/bash
# 激活 conda 环境
source ~/anaconda3/bin/activate trans

# 启动前端和后端应用

# 启动前端（后台运行并记录日志）
cd /home/robin/桌面/trans/frontend
python -m http.server 8080 > frontend.log 2>&1 &

# 启动后端（后台运行并记录日志）
cd /home/robin/桌面/trans/backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --ws websockets > backend.log 2>&1 &

# 输出运行状态
echo "前端和后端已启动，日志文件分别为 frontend.log 和 backend.log"
