# 使用輕量級 Python 映像檔
FROM python:3.11-slim

# 設定容器內的工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝相依套件
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY . .

# 啟動 FastAPI，從 backend.app:app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
