import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity


class FaceRecognizer:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.face_db = {}
        self.app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def build_database(self, base_dir="./face_base"):
        self.db_stats = {}  # Store statistics for each person
        for person_name in os.listdir(base_dir):
            person_dir = os.path.join(base_dir, person_name)
            if os.path.isdir(person_dir):
                embeddings = []
                img_count = 0
                for img_name in os.listdir(person_dir):
                    if img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                        img_path = os.path.join(person_dir, img_name)
                        img = cv2.imread(img_path)
                        faces = self.app.get(img)
                        if faces:
                            embeddings.append(faces[0].embedding)
                            img_count += 1
                if embeddings:
                    self.face_db[person_name] = np.mean(embeddings, axis=0)
                    self.db_stats[person_name] = img_count

    def display_database_info(self):
        print("Face Database Statistics:")
        print("-" * 40)
        print(f"Total persons: {len(self.face_db)}")
        for person, count in self.db_stats.items():
            print(f"{person}: {count} images")
        print("-" * 40)

    def search(self, img_array):
        faces = self.app.get(img_array)
        if not faces:
            return []

        output=[]
         
        for face in faces:
            query_embedding = face.embedding
            bb = face.bbox
            bb = [max(0, int(x)) for x in bb]

            max_similarity = -1
            best_match = -1

            for idx, (name, stored_embedding) in enumerate(self.face_db.items()):
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1), stored_embedding.reshape(1, -1)
                )[0][0]

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = idx if similarity >= self.threshold else -1

            output.append((best_match, bb,similarity))
        return output
    
    def get_name_by_index(self, index):
        if index == -1:
            return "Unknown"
        return list(self.face_db.keys())[index]
