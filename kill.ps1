# 杀死前端进程（http.server 8080）
Get-Process | Where-Object { $_.Path -like "*python*" -and $_.CommandLine -like "*http.server 8080*" } | Stop-Process

# 杀死后端进程（uvicorn backend.main:app）
Get-Process | Where-Object { $_.Path -like "*python*" -and $_.CommandLine -like "*uvicorn backend.main:app*" } | Stop-Process