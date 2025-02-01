# 即時聊天室與消息管理系統

- **1. 需求分析與系統架構設計**
    
    **目標：確定系統功能與技術架構**
    
    ✅ **核心功能**
    
    - 即時聊天室（群聊 & 私聊）
    - 速率限制（每秒最大消息數量限制）
    - 消息存儲與查詢（Oracle歷史紀錄）
    - 訊息分發與通知機制
    - 用戶驗證（JWT 或 OAuth）
    - 後台數據分析
    
    ✅ **技術選擇**
    
    | 需求 | 技術 |
    | --- | --- |
    | Web 框架 | Django + Django REST Framework |
    | 微服務架構 | FastAPI (可用於非同步消息處理) |
    | 即時通訊 | WebSocket (Django Channels) |
    | 速率限制 | Upstash Rate Limit (`ratelimit-js`) |
    | 訊息分發 | Kafka |
    | 資料庫 | Oracle (儲存消息歷史) + Redis (快取) |
    | 負載均衡 & 安全 | Nginx + Cloudflare |
    | 部署 | Docker + Kubernetes |
    
    ✅ **架構設計**
    
    - Django API 負責用戶驗證、聊天室管理、速率限制
    - Kafka 作為訊息隊列，處理即時消息分發
    - WebSocket 伺服器負責即時訊息推送
    - Redis 儲存活躍用戶、快取聊天室數據
    - Nginx 反向代理，整合 Cloudflare 提供安全防護
- **2. 開發環境設置**
    
    ### **✅ 環境準備**
    
    1. **安裝依賴**
        
        ```
        pip install django djangorestframework channels cx_Oracle kafka-python redis
        ```
        
    2. **安裝 Kafka、Redis、Oracle Client**
        
        ```
        docker-compose up -d
        ```
        
    3. **設定專案目錄結構**
        
        ```
        /chat-app
        ├── backend/       # Django API 伺服器
        ├── websocket/     # WebSocket 伺服器
        ├── kafka/         # Kafka 消費者
        ├── redis/         # Redis 快取
        ├── nginx/         # Nginx 反向代理
        ├── cloudflare/    # Cloudflare 設定
        ├── docker/        # 容器化設定
        ├── docs/          # API 說明
        ```
        
- 3. Django API 伺服器
    
    ```
    django-admin startproject chat_backend 
    ```
    
    這會建立 Django 專案，目錄結構如下：
    
    ```bash
    backend/
    │── chat_backend/      # 專案主目錄
    │   ├── settings.py    # 設定檔
    │   ├── urls.py        # 路由
    │   ├── wsgi.py        # WSGI 入口
    │   ├── asgi.py        # ASGI 入口（支援 WebSocket）
    │── manage.py          # Django 管理指令
    ```
    
    ---
    
    ## **3️⃣ 創建 Django 應用**
    
    Django 內的「應用（app）」相當於模組，你可以為 API 服務建立一個 `api` 應用：
    
    ```
    python manage.py startapp api
    ```
    
    這會建立：
    
    ```bash
    backend/
    │── api/              # 應用程式
    │   ├── models.py     # 資料庫模型
    │   ├── views.py      # 處理邏輯
    │   ├── urls.py       # 路由
    │   ├── serializers.py # 序列化處理（若使用 DRF）
    │   ├── admin.py      # Django 管理介面
    │   ├── apps.py       # 設定檔
    ```
    
    ## **4️⃣ 設定 `settings.py`**
    
    打開 `backend/chat_backend/settings.py`，找到 `INSTALLED_APPS`，新增你的應用：
    
    ```python
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'api',             # 加入自訂應用
    ]
    
    ```
    
    ---
    
    ## **5️⃣ 設定資料庫（使用 Oracle）**
    
    去Oracle 找對應oracle db 對應docker image
    
    https://container-registry.oracle.com/ords/f?p=113:4:100164500337088:::4:P4_REPOSITORY,AI_REPOSITORY,AI_REPOSITORY_NAME,P4_REPOSITORY_NAME,P4_EULA_ID,P4_BUSINESS_AREA_ID:9,9,Oracle%20Database%20Enterprise%20Edition,Oracle%20Database%20Enterprise%20Edition,32,0&cs=3dq9JGZsJY2ni863y51KX4SNaSG2mx51N46E_7Z2677ETWUchw3L347Db_O3e3zGGX4aPPcSXsHe4rLSDI4uk9w
    
    ```sql
    建立container
    docker run -d --name CHAT -p 1521:1521 -e ORACLE_PWD=root123 -e ORACLE_CHARACTERSET=UTF-8 container-registry.oracle.com/database/express:21.3.0-xe
    
    ```
    
    如果你要用 Oracle，先安裝 `cx_Oracle`：
    
    ```
    pip install cx_Oracle
    ```
    
    然後在 `settings.py` 設定：
    
    ```python
    DATABASES = {
        # Oracle 資料庫
         'default': {
            'ENGINE': 'django.db.backends.oracle',
            'NAME': 'XE',  # 資料庫名稱
            'USER': 'SYSTEM',
            'PASSWORD': 'root123',
            'HOST': 'localhost',  # 主機地址
            'PORT': '1521',        # 端口號
        }
    }
    ```
    
    `settings.py` 設定： 系統抓不到 oracle_client.dll 路徑，需手動指定路徑
    
    ```sql
    # 系統抓不到 oracle_client.dll 路徑，需手動指定路徑
    # 參考 cx_Oracle 官方文件
    # https://cx-oracle.readthedocs.io/en/latest/user_guide/initialization.html#usinginitoracleclient
    try:
        if sys.platform.startswith("win32"):
            lib_dir = r"D:\oracle\instantclient-basic-windows.x64-23.6.0.24.10\instantclient_23_6"
            cx_Oracle.init_oracle_client(lib_dir=lib_dir)
    except Exception as err:
        print(err)
        sys.exit(1)
    ```
    
    ---
    
    ## **6️⃣ 執行遷移 & 啟動伺服器**
    
    ### **建立資料表**
    
    ```
    python manage.py migrate
    ```
    
    ### **建立管理員帳號**
    
    ```
    python manage.py createsuperuser
    daniel/daniel
    ```
    
    輸入帳號、信箱、密碼。
    
    ### **啟動 Django 伺服器**
    
    ```
    python manage.py runserver
    ```
    
    瀏覽 `http://127.0.0.1:8000/` 即可看到 Django 預設首頁。
    
    ---
    
    ## **7️⃣（可選）設定 Docker**
    
    在 `docker/` 目錄內新增 `Dockerfile`：
    
    ```
    # 使用 Python 官方映像
    FROM python:3.11
    
    # 設定工作目錄
    WORKDIR /app
    
    # 複製專案
    COPY . /app/
    
    # 安裝需求
    RUN pip install -r requirements.txt
    
    # 啟動 Django
    CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
    ```
    
    再新增 `docker-compose.yml`：
    
    ```yaml
    version: '3.8'
    services:
      backend:
        build: ../backend
        ports:
          - "8000:8000"
        depends_on:
          - db
      db:
        image: oracleinanutshell/oracle-xe-11g
        environment:
          ORACLE_ALLOW_REMOTE: "true"
    ```
    
    啟動：
    
    ```
    docker-compose up -d
    ```
    
- 4. API
    
    

### **✅ 設計 API**

| API | 方法 | 描述 |
| --- | --- | --- |
| `/api/auth/login` | `POST` | 用戶登入 |
| `/api/auth/register` | `POST` | 用戶註冊 |
| `/api/chat/rooms` | `GET` | 取得聊天室列表 |
| `/api/chat/rooms/{id}/messages` | `GET` | 取得聊天室歷史訊息 |
| `/api/chat/send` | `POST` | 發送訊息（受速率限制） |