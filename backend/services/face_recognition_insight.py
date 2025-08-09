import numpy as np
from ..interfaces.face_recognition import IFaceRecognitionService
from typing import List
from insightface.app import FaceAnalysis
import cv2
class InsightFaceRecognitionService(IFaceRecognitionService):
    def __init__(self, app_face: FaceAnalysis, known_embeddings: List[np.ndarray], student_ids: List[str]):
        self.app = app_face
        self.known_embeddings = known_embeddings
        self.student_ids = student_ids

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def train_model(self):
        print("InsightFace does not require training here.")

    def verify_face(self, face_image: bytes) -> str:
        frame = cv2.imdecode(np.frombuffer(face_image, np.uint8), cv2.IMREAD_COLOR)
        faces = self.app.get(frame)
        best_similarity = -1
        label = "Unknown"

        for face in faces:
            embedding = face.embedding
            for i in range(len(self.known_embeddings)):
                similarity = self.cosine_similarity(embedding, self.known_embeddings[i])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_name = self.student_ids[i]

            if best_similarity > 0.4:
                label = best_match_name

        return label if label != "Unknown" else ""