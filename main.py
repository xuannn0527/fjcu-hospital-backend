from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import random # 引入 random 來模擬 AI 預測分數

app = FastAPI()

# 允許 React 前端跨網域抓資料
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定 MySQL 連線資訊
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

# 抓取病患清單的 API
@app.get("/api/patients")
def get_patients():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # ★ 升級版 SQL：使用 LEFT JOIN 將三張表完美合併
            sql = """
                SELECT 
                    p.patient_id, p.name, p.gender, p.drug_allergy, p.past_medical_history,
                    t.triage_id, t.created_at, t.final_level,
                    v.temperature, v.heart_rate, v.spo2, v.respiratory_rate,
                    v.blood_pressure_sys, v.blood_pressure_dia, 
                    v.sentiment, v.past_medical_history_y, v.allergy
                FROM patients p
                LEFT JOIN triage_record t ON p.patient_id = t.patient_id
                LEFT JOIN vital_signs v ON t.triage_id = v.triage_id
            """
            cursor.execute(sql)
            results = cursor.fetchall()
        connection.close()

        # ★ 模擬 Agent_1 (AI 引擎) 進行風險推算與資料整理
        for row in results:
            # 1. 預設狀態，讓前端左側面板可以篩選
            row['status'] = '未處理'
            
            # 2. 將 datetime 時間格式轉成字串，避免 FastAPI 轉 JSON 時報錯
            if row.get('created_at'):
                row['created_at'] = row['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                
            # 3. 模擬 AI 風險分數 (根據檢傷級別與血氧濃度推算)
            score = 0
            if row.get('final_level'):
                level = int(row['final_level'])
                if level == 1: score = random.randint(90, 99)
                elif level == 2: score = random.randint(75, 89)
                elif level == 3: score = random.randint(40, 74)
                else: score = random.randint(10, 39)
            
            # 如果血氧低於 95，加重惡化風險
            if row.get('spo2') and int(row['spo2']) < 95:
                score = min(99, score + 15) # 最高不超過 99%
                
            row['risk_score'] = score

        return results
    except Exception as e:
        print("資料庫連線錯誤:", str(e))
        return {"error": str(e)}