# 设置 Conda 环境名称和项目路径
$envName = "trans" # 替换为您的 Conda 环境名称
$projectPath = "C:\Users\Robin\Desktop\trans-sbf" # 替换为您的项目路径

# 切换到项目目录
Set-Location -Path $projectPath

# 构建启动命令
$command = "conda activate $envName; python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --ws websockets"

# 后台运行服务
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command $command" -PassThru
