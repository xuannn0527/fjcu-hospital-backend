from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import pymysql
import random
import os
from dotenv import load_dotenv

load_dotenv() # 讓程式啟動時去讀取 .env 檔案

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_password = os.getenv("DB_PASSWORD", "")

db_config = {
<<<<<<< HEAD
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'fjcu_hospital'),
    'port': int(os.getenv('DB_PORT', 3306)),
=======
    'host': '127.0.0.1',  
    'user': 'root',                  
    'password': db_password,     
    'database': 'fjcu_hospital', 
    'port': 3306,                    
>>>>>>> 93a43b514f9de1a9ba49c6697f8119468ad0ab99
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
            # 配合剛才提供的 .sql 結構，將表名改為 triage_records
            sql = """
                SELECT 
<<<<<<< HEAD
                    p.patient_id, p.name, p.gender,
                    t.triage_id, t.triage_level, t.chief_complaint,
                    v.measured_at, v.temperature, v.heart_rate, v.spo2, v.respiratory_rate,
                    v.systolic_bp AS blood_pressure_sys, 
                    v.diastolic_bp AS blood_pressure_dia
=======
                    p.patient_id, 
                    p.name, 
                    p.gender,
                    p.age,
                    p.birth_date,
                    
                    t.triage_id,
                    t.triage_level AS final_level,
                    t.chief_complaint,
                    
                    v.measured_at,
                    v.temperature, 
                    v.heart_rate,
                    v.respiratory_rate,
                    v.systolic_bp AS blood_pressure_sys, 
                    v.diastolic_bp AS blood_pressure_dia, 
                    v.spo2
>>>>>>> 93a43b514f9de1a9ba49c6697f8119468ad0ab99
                FROM patients p
                LEFT JOIN triage_records t ON p.patient_id = t.patient_id
                LEFT JOIN vital_signs v ON p.patient_id = v.patient_id
            """
            cursor.execute(sql)
            results = cursor.fetchall()
        connection.close()

        # AI 風險評分邏輯
        for row in results:
            if row.get('measured_at'):
                row['measured_at'] = row['measured_at'].strftime("%Y-%m-%d %H:%M:%S")
                
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