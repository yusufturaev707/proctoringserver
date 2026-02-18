import numpy as np
import base64
import re
import cv2
from django.conf import settings

class Base64ImageConverter:
    def __init__(self, base64_string: str):
        self.base64_string = base64_string
        self.image_data = None
        self.image_format = None
        self.app = settings.FACE_ANALYSIS_MODEL

    def validate_base64(self):
        base64_pattern = r"^data:image\/(jpeg|jpg|png|gif|bmp);base64,"
        match = re.match(base64_pattern, self.base64_string)
        if not match:
            raise ValueError("Base64 string is a empty or invalid!")
        self.image_format = match.group(1)

    def decode_base64(self):
        try:
            image_base64_data = self.base64_string.split(",")[1]
            img_data = base64.b64decode(image_base64_data)
            np_arr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.image_data = img_rgb
        except Exception:
            raise ValueError("Base64 string is incorrect!!")

    def get_embedding_more_face(self):
        try:
            detected_faces = self.app.get(self.image_data)
            if len(detected_faces) == 0:
                return [], False
            else:
                list_faces = [detected_face.embedding for detected_face in detected_faces]
                return list_faces, True
        except Exception as e:
            raise ValueError(f"{e}")

    def convert(self):
        self.validate_base64()
        self.decode_base64()
        embeddings_list, t = self.get_embedding_more_face()
        is_success = True
        if not t:
            is_success = False
        return embeddings_list, is_success


def cosine_similarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


def get_percentage(cosine_score, threshold=0.5):
    normalized = (cosine_score + 1) / 2
    similarity_score = round(normalized * 100)
    return round(similarity_score)

