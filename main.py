from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql

app = FastAPI()

# 允許 React 前端跨網域抓資料
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# 設定 MySQL 連線資訊 (請換成你的 Railway 實際資訊)
# 設定 MySQL 連線資訊 (已更新為你的 Railway 專屬資訊)
# 設定 MySQL 連線資訊 (已更新為你的 Railway 專屬資訊)
db_config = {
    'host': 'sakura.proxy.rlwy.net',  # 你提供的 Hostname
    'user': 'root',                   # Railway 的帳號通常預設是 root，若不同請更改
    'password': 'VkCFiGIDmtkeeyzrpNAScrScMrATHOBL', 
    'database': 'railway',            # 預設資料庫名稱
    'port': 58793,                    # 你提供的超重要 Port
    'cursorclass': pymysql.cursors.DictCursor
}

# 測試用：確認 API 有活
@app.get("/")
def read_root():
    return {"message": "急診系統 API 伺服器已啟動！"}

# 抓取病患清單的 API
@app.get("/api/patients")
def get_patients():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            sql = "SELECT * FROM patients"
            cursor.execute(sql)
            results = cursor.fetchall()
            connection.close()
        return results
    except Exception as e:
        return {"error": str(e)}