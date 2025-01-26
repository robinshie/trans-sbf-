# 激活 conda 环境
& "$env:USERPROFILE\anaconda3\Scripts\activate" trans

# 启动前端和后端应用

# 启动前端（后台运行并记录日志）
Start-Process -FilePath "python" -ArgumentList "-m http.server 8080" -WorkingDirectory ".\frontend" -RedirectStandardOutput ".\frontend.log" -RedirectStandardError ".\frontend.log" -NoNewWindow

# 启动后端（后台运行并记录日志）
Start-Process -FilePath "python" -ArgumentList "-m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --ws websockets" -WorkingDirectory ".\backend" -RedirectStandardOutput ".\backend.log" -RedirectStandardError ".\backend.log" -NoNewWindow

# 输出运行状态
Write-Host "前端和后端已启动，日志文件分别为 frontend.log 和 backend.log"