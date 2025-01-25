# 杀死前端进程（http.server 8080）
kill $(ps aux | grep "http.server 8080" | grep -v grep | awk '{print $2}')

# 杀死后端进程（uvicorn backend.main:app）
kill $(ps aux | grep "uvicorn backend.main:app" | grep -v grep | awk '{print $2}')
