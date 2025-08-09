from abc import ABC, abstractmethod
class IFaceRecognitionService(ABC):
    @abstractmethod
    def train_model(self): pass

    @abstractmethod
    def verify_face(self, face_image: bytes) -> str: pass