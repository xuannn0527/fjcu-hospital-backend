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

# 設定 MySQL 連線資訊 (使用你的 Railway 專屬資訊)
db_config = {
    'host': 'sakura.proxy.rlwy.net', 
    'user': 'root', 
    'password': 'VkCFiGIDmtkeeyzrpNAScrScMrATHOBL', 
    'database': 'railway', 
    'port': 58793, 
    'cursorclass': pymysql.cursors.DictCursor
}

# 測試用：確認 API 有活
@app.get("/")
def read_root():
    return {"message": "急診系統 API 伺服器已啟動！"}

# 抓取病患清單的 API（已加入 LEFT JOIN 串接 triage_record 檢傷紀錄表）
@app.get("/api/patients")
def get_patients():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    p.patient_id, 
                    p.name, 
                    p.id_number,
                    p.birth_date,
                    p.medical_number,
                    p.gender,
                    p.drug_allergy,
                    p.past_medical_history,
                    t.triage_id, 
                    t.nurse_id,
                    t.created_at, 
                    t.final_level,
                    t.status,
                    t.alert_message
                FROM patients p
                LEFT JOIN triage_record t ON p.patient_id = t.patient_id
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            connection.close()
        return results
    except Exception as e:
        return {"error": str(e)}