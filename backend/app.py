from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import datetime
import uvicorn
from kafka import KafkaProducer
import json
from controllers.admin_controller import AdminController
from services.access_control_service import MySQLAccessControlService
from services.access_log_repo_memory import MySQLAccessLogRepository
from services.user_repo_memory import MySQLUserRepository
from services.face_recognition_insight import InsightFaceRecognitionService
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from services.user_repo_memory import MySQLUserRepository

class KafkaLogger:
    def __init__(self, topic='access_logs'):
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic

    def log_access(self, user_id: str, status: str):
        log = {
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.producer.send(self.topic, log)
        self.producer.flush()
app_face = FaceAnalysis(providers=['CPUExecutionProvider'])
app_face.prepare(ctx_id=0)
user_repo = MySQLUserRepository()
log_repo = MySQLAccessLogRepository()
access_service = MySQLAccessControlService()
known_embeddings, student_ids = user_repo.load_known_faces(app_face)
face_service = InsightFaceRecognitionService(app_face, known_embeddings, student_ids)

controller = AdminController(user_repo, log_repo, access_service, face_service)
kafka_logger = KafkaLogger()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users")
async def add_user(
    user_id: str = Form(...),
    name: str = Form(...),
    department: str = Form(...),
    role: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    face_file: Optional[UploadFile] = File(None)
):
    face_data = await face_file.read() if face_file else None
    controller.add_user({
        "user_id": user_id,
        "name": name,
        "department": department,
        "role": role,
        "email": email,
        "phone": phone,
        "face_data": face_data
    })

    global face_service
    known_embeddings, student_ids = user_repo.load_known_faces(app_face)
    face_service = InsightFaceRecognitionService(app_face, known_embeddings, student_ids)
    controller.face_service = face_service

    return {"message": "User added successfully."}


@app.get("/users")
def list_users():
    return controller.list_users()


@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    controller.delete_user(user_id)
    return {"message": "User deleted."}


@app.post("/verify_access")
async def verify_access(face_file: UploadFile = File(...)):
    face_bytes = await face_file.read()
    matched_id, status = controller.verify_and_log_access(face_bytes)
    kafka_logger.log_access(matched_id or "unknown", status)
    return {"status": status, "user_id": matched_id or ""}


@app.get("/logs")
def get_logs(user_id: Optional[str] = None):
    return controller.get_user_logs(user_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
