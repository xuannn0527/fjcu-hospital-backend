from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # ★ 新增：用來定義前端傳來的 JSON 格式
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

# ★ 新增：定義轉入觀察時，前端傳來的資料格式
class UpdateStatusRequest(BaseModel):
    status: str
    alert_message: str

@app.get("/")
def read_root():
    return {"message": "急診系統 API 伺服器已啟動！"}

@app.get("/api/patients")
def get_patients():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # 完整三表聯查 (JOIN)
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
                    p.do_not_treat,
                    
                    t.triage_id,
                    t.created_at,
                    t.final_level,
                    t.status,          -- ★ 新增：把狀態撈出來
                    t.alert_message,   -- ★ 新增：把處置紀錄撈出來
                    
                    v.temperature, 
                    v.heart_rate,
                    v.spo2,
                    v.respiratory_rate,
                    v.weight,
                    v.blood_pressure_sys, 
                    v.blood_pressure_dia, 
                    v.blood_sugar,
                    v.gcs_eye, 
                    v.gcs_verbal, 
                    v.gcs_motor,
                    v.past_medical_history_y,
                    v.do_not_treat,
                    v.allergy,
                    v.pain_score,
                    v.sentiment  
                FROM patients p
                LEFT JOIN triage_record t ON p.patient_id = t.patient_id
                LEFT JOIN vital_signs v ON t.triage_id = v.triage_id
            """
            cursor.execute(sql)
            results = cursor.fetchall()
        connection.close()

        # AI 風險邏輯計算
        for row in results:
            # 如果資料庫裡還沒有 status，預設給 '未處理'
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

# ★ 新增：負責處理「轉入觀察」的 PUT API
@app.put("/api/triage/{triage_id}/status")
def update_triage_status(triage_id: str, req: UpdateStatusRequest):
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # 根據 triage_id 更新 status 和 alert_message
            sql = """
                UPDATE triage_record 
                SET status = %s, alert_message = %s 
                WHERE triage_id = %s
            """
            cursor.execute(sql, (req.status, req.alert_message, triage_id))
            connection.commit()  # UPDATE 語法一定要 commit 才會真正寫入！
            
        connection.close()
        return {"message": f"成功將 {triage_id} 更新為 {req.status}"}
        
    except Exception as e:
        print("資料庫更新錯誤:", str(e))
        return {"error": str(e)}, 500