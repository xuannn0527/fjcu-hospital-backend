from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_config = {
    'host': 'sakura.proxy.rlwy.net',  
    'user': 'root',                   
    'password': 'VkCFiGIDmtkeeyzrpNAScrScMrATHOBL', 
    'database': 'railway',            
    'port': 58793,                    
    'cursorclass': pymysql.cursors.DictCursor
}

@app.get("/")
def read_root():
    return {"message": "急診系統 API 伺服器已啟動！"}

@app.get("/api/patients")
def get_patients():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # 使用同學寫的完整三表聯查 (JOIN)
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

        # AI 風險邏輯計算
        for row in results:
            row['status'] = row.get('status') or '未處理'
            if row.get('created_at'):
                row['created_at'] = row['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                
            score = 0
            if row.get('final_level'):
                level = int(row['final_level'])
                if level == 1: score = random.randint(90, 99)
                elif level == 2: score = random.randint(75, 89)
                elif level == 3: score = random.randint(40, 74)
                else: score = random.randint(10, 39)
            
            if row.get('spo2') and int(row['spo2']) < 95:
                score = min(99, score + 15)
                
            row['risk_score'] = score

        return results
    except Exception as e:
        print("資料庫連線錯誤:", str(e))
        return {"error": str(e)}