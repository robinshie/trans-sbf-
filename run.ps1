# PowerShell 脚本：启动 Conda 环境并运行 uvicorn 服务
# 请替换环境名称和项目路径为您的实际情况

# 设置 Conda 环境名称和项目路径
$envName = "trans" # 替换为您的 Conda 环境名称
$projectPath = "C:\Users\Robin\Desktop\trans-sbf" # 替换为您的项目路径

# 切换到项目目录
Set-Location -Path $projectPath

# 激活 Conda 环境并启动 uvicorn 服务
conda activate $envName
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --ws websockets
