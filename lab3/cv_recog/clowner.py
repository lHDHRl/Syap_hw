import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

class LandmarkUtils:
    def __init__(self, img_w, img_h):
        self.img_w = img_w
        self.img_h = img_h

    def l2p(self, landmark):
        """
        Converts a normalized landmark to pixel coordinates (x, y).
        Args:
            landmark: mediapipe NormalizedLandmark object
        Returns:
            (x, y): tuple of pixel coordinates
        """
        x = int(landmark.x * self.img_w)
        y = int(landmark.y * self.img_h)
        return (x, y)

    def l2dist(self, land_a, land_b):
        """
        Calculates the Euclidean distance between two landmarks in pixel space.
        Args:
            land_a, land_b: mediapipe NormalizedLandmark objects
        Returns:
            distance: float, Euclidean distance in pixels
        """
        dx = (land_a.x - land_b.x) * self.img_w
        dy = (land_a.y - land_b.y) * self.img_h
        dz = (land_a.z - land_b.z) * max(self.img_w, self.img_h)
        return np.sqrt(dx**2 + dy**2 + dz**2)

    def l2angl(self, land_a, land_b):
        """
        Computes the angle between two landmarks in the image plane.
        Args:
            land_a, land_b: mediapipe NormalizedLandmark objects
        Returns:
            angle: float, angle in radians
        """
        x1, y1 = self.l2p(land_a)
        x2, y2 = self.l2p(land_b)
        dy = y2 - y1
        dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if dist == 0:
            return 0.0
        angle = np.arcsin(dy / dist) * np.sign(x2 - x1)
        return angle


class Clowner:
    
    def __init__(self):
        #preload data
        self.nose_orig_img=cv2.imread("./resources/nose.png", cv2.IMREAD_UNCHANGED)# 4 channels RGBA
        # self.nose_orig_img = cv2.cvtColor(self.nose_orig_img, cv2.COLOR_BGRA2RGBA)

        self.rainbow_img=cv2.imread("./resources/rainbow-v.png")
        # self.rainbow=cv2.rotate(self.rainbow,cv2.ROTATE_90_COUNTERCLOCKWISE)
        # Resize rainbow to a square shape before further processing
        self.r_h,self.r_w,_=self.rainbow_img.shape
        # side_len = max(self.r_h, self.r_w)
        # self.rainbow = cv2.resize(self.rainbow, (side_len, side_len), interpolation=cv2.INTER_LANCZOS4)
        
        #preload hair segmenter
        base_options = python.BaseOptions(model_asset_path="./resources/hair_segmenter.tflite")
        self.hair_segmenter_options = vision.ImageSegmenterOptions(
            base_options=base_options, output_category_mask=True
        )
        
    def _add_nose(self,img,landmarks):
        image_height, image_width, _ = img.shape
        lu=LandmarkUtils(image_width,image_height)
        nose_down=landmarks.landmark[94]
        nose_up=landmarks.landmark[6]
        
        nose_size = lu.l2dist(nose_up, nose_down)
        clown_nose_point=lu.l2p(landmarks.landmark[4])
        clown_nose_angle=lu.l2angl(landmarks.landmark[26],landmarks.landmark[266])
        
    
        nose_resized = cv2.resize(self.nose_orig_img, (int(nose_size), int(nose_size)), interpolation=cv2.INTER_LANCZOS4)
        
        # Get rotation matrix and rotate using cv2
        nose_img_center = (nose_resized.shape[1] // 2, nose_resized.shape[0] // 2)
        rot_mat = cv2.getRotationMatrix2D(nose_img_center, np.degrees(-clown_nose_angle), 1.0)
    
        nose_img = cv2.warpAffine(nose_resized, rot_mat, (nose_resized.shape[1], nose_resized.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
        # Convert to numpy array and overlay on annotated_image
        
        nose_arr = np.array(nose_img)
        h, w = nose_arr.shape[:2]
        cx, cy = clown_nose_point

        # Calculate top-left corner for overlay
        x1 = int(cx - w // 2)
        y1 = int(cy - h // 2)

        # Overlay RGBA nose onto annotated_image
        for c in range(3):  # For each color channel
            img[y1:y1+h, x1:x1+w, c] = np.where(
                nose_arr[..., 3] > 0,
                nose_arr[..., c],
                img[y1:y1+h, x1:x1+w, c]
            )
        return img
    
    def _color_hair(self,img,landmarks):
        image_height, image_width, _ = img.shape
        lu=LandmarkUtils(image_width,image_height)
        face_angle=lu.l2angl(landmarks.landmark[33],landmarks.landmark[263])

        with vision.ImageSegmenter.create_from_options(self.hair_segmenter_options) as segmenter:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
            segmentation_result = segmenter.segment(mp_image)
            hair_mask = segmentation_result.confidence_masks[1].numpy_view()

        ys, xs = np.where(hair_mask > 0.8)
        if len(xs) > 0 and len(ys) > 0:
            x_min, x_max = xs.min(), xs.max()
            y_min, y_max = ys.min(), ys.max()
            bb = (x_min, y_min, x_max, y_max)
        else:
            bb = [0, 0, self.r_h, self.r_w]

        rot_mat = cv2.getRotationMatrix2D((self.r_w // 2, self.r_h // 2), np.degrees(face_angle), 2.0)
        rainbow_new = cv2.warpAffine(
            self.rainbow_img,
            rot_mat,
            (self.r_w * 2, self.r_h * 2),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )
        

        #cut center part with aspect ratio of bb out of rainbo image
        rn_h, rn_w, _ = rainbow_new.shape
        aspect_ratio_diff = (rn_h / rn_w) / ((bb[3] - bb[1]) / (max(bb[2] - bb[0], 1)))
        cut_part_w = rn_w
        cut_part_h = rn_h

        if aspect_ratio_diff < 1:
            cut_part_w = int(cut_part_w * aspect_ratio_diff)
        else:
            cut_part_h = int(cut_part_h / aspect_ratio_diff)
        rainbow_new = rainbow_new[
            int((rn_h - cut_part_h) // 2) : rn_h - int((rn_h - cut_part_h) // 2),
            int((rn_w - cut_part_w) // 2) : rn_w - int((rn_w - cut_part_w) // 2),
            :,
        ]
        rainbow_new = cv2.resize(rainbow_new, (bb[2] - bb[0], bb[3] - bb[1]))
        
        rainbow_hair_image = img

        for c in range(3):  # For each color channel
            rainbow_hair_image[bb[1] : bb[3], bb[0] : bb[2], c] = np.where(
                hair_mask[bb[1] : bb[3], bb[0] : bb[2]] > 0.5,
                rainbow_new[..., c] * hair_mask[bb[1] : bb[3], bb[0] : bb[2]] * 0.6
                + rainbow_hair_image[bb[1] : bb[3], bb[0] : bb[2], c]
                * (1 - (hair_mask[bb[1] : bb[3], bb[0] : bb[2]] * 0.6)),
                rainbow_hair_image[bb[1] : bb[3], bb[0] : bb[2], c],
            )
            
        return rainbow_hair_image

# now rotate
    
    def process(self,img:np.ndarray):
        '''accepts a frame with ONE face'''
        
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        
        #detect mesh on face
        with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        ) as face_mesh:
            results = face_mesh.process(image)
            if len(results.multi_face_landmarks)==0:
                return None
            if len(results.multi_face_landmarks)!=1:
                print("WARNING, MORE THAN ONE FACE at clowning funtion")
        

        landmarks=results.multi_face_landmarks[0]

        # drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        # mp_drawing.draw_landmarks(
        #     image=annotated_image,
        #     landmark_list=landmarks,
        #     connections=mp_face_mesh.FACEMESH_TESSELATION,
        #     landmark_drawing_spec=None,
        #     connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
        # )

        img=self._color_hair(img,landmarks)
        
        img=self._add_nose(img,landmarks)
        
        # Convert BGR to RGB before returning
        return img
        
        
       
        

    