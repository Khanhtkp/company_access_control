from fastapi import FastAPI, UploadFile, File, Form, Query, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
from datetime import date
from backend.controllers.admin_controller import AdminController
from backend.services.access_control_service import MySQLAccessControlService
from backend.services.access_log_repo_memory import MySQLAccessLogRepository
from backend.services.user_repo_memory import MySQLUserRepository
from backend.services.face_recognition_insight import InsightFaceRecognitionService
from backend.services.llms_service import GeminiLLMService
from backend.services.kafka_logger import KafkaLogger
from backend.services.email_service import EmailService
from insightface.app import FaceAnalysis
from config.config import settings
app_face = FaceAnalysis(providers=['CPUExecutionProvider'])
app_face.prepare(ctx_id=0)
user_repo = MySQLUserRepository()
log_repo = MySQLAccessLogRepository()
access_service = MySQLAccessControlService()
known_embeddings, student_ids = user_repo.load_known_faces(app_face)
face_service = InsightFaceRecognitionService(app_face, known_embeddings, student_ids)
llm_service = GeminiLLMService(settings.llm_api_key)
controller = AdminController(user_repo, log_repo, access_service, face_service, llm_service)
kafka_logger = KafkaLogger()
email_service = EmailService(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_user=settings.email_user,
    smtp_password=settings.email_pass
)
email_sent_today = {}
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

@app.patch("/users/{user_id}")
async def modify_user(
    user_id: str,
    name: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    face_file: Optional[UploadFile] = File(None)
):
    try:
        face_data = await face_file.read() if face_file else None
        updates = {
            "name": name,
            "department": department,
            "role": role,
            "email": email,
            "phone": phone,
            "face_data": face_data
        }
        updated_user = controller.modify_user(user_id, updates)

        if face_data:
            global face_service
            known_embeddings, student_ids = user_repo.load_known_faces(app_face)
            face_service = InsightFaceRecognitionService(app_face, known_embeddings, student_ids)
            controller.face_service = face_service

        return {"message": "User updated successfully", "user": updated_user}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/verify_access")
async def verify_access(face_file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    face_bytes = await face_file.read()
    matched_id, status = controller.verify_and_log_access(face_bytes)
    kafka_logger.log_access(matched_id or "unknown", status)

    if status == "granted" and matched_id:
        today_str = date.today().isoformat()
        if email_sent_today.get(matched_id) != today_str:
            user = user_repo.get_user(matched_id)
            if user and user.email:
                subject = "Access Verified Today"
                body = f"Hello {user.name},\n\nYour access was verified today ({today_str}). Have a great day!\n\nRegards,\nAccess Control Team"

                background_tasks.add_task(email_service.send_email, user.email, subject, body)

                email_sent_today[matched_id] = today_str

    return {"status": status, "user_id": matched_id or ""}


@app.get("/logs")
def get_logs(user_id: Optional[str] = None):
    return controller.get_user_logs(user_id)
@app.get("/report")
def get_report(period_days: int = Query(30, ge=1, le=365)):
    try:
        report = controller.get_report(period_days)
        return {"report": report}
    except RuntimeError as e:
        return {"error": str(e)}
@app.get("/report/today")
def get_today_attendance_report():
    try:
        report = controller.get_today_attendance_report()
        return {"report": report}
    except RuntimeError as e:
        return {"error": str(e)}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
