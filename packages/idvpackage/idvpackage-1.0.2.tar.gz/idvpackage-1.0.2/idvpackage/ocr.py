import base64
import cv2
import io
import numpy as np
import re
from datetime import datetime
from PIL import Image
from skimage.transform import radon
from google.cloud import vision_v1
from pkg_resources import resource_filename
from idvpackage import ocr_utils
import face_recognition
import tempfile

class IdentityVerification:

    def __init__(self):
        """
        This is the initialization function of a class that imports a spoof model and loads an OCR
        reader.
        """
        #self.images = images
        credentials_path = resource_filename('idvpackage', 'streamlit-connection-b1a38b694505.json')
        #credentials_path = "streamlit-connection-b1a38b694505.json"
        self.client = vision_v1.ImageAnnotatorClient.from_service_account_json(credentials_path)
        
    def image_conversion(self,image):  
        """
        This function decodes a base64 string data and returns an image object.
        :return: an Image object that has been created from a base64 encoded string.
        """
        image=image.split(',')[-1]
        # Decode base64 String Data
        img=Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))
        return img

    def rgb2yuv(self, img):
        """
        Convert an RGB image to YUV format.
        """
        try:
            img=np.array(img)
            return cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
        except Exception as e:
            raise Exception(f"Error: {e}")
    
    def find_bright_areas(self, image, brightness_threshold):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh_image = cv2.threshold(gray_image, brightness_threshold, 255, cv2.THRESH_BINARY)[1]
        contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bright_areas = []

        for contour in contours:
            bounding_box = cv2.boundingRect(contour)

            area = bounding_box[2] * bounding_box[3]

            if area > 800:
                bright_areas.append(bounding_box)

        return len(bright_areas)

    def is_blurry(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        laplacian_variance = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        return laplacian_variance
    
    def check_image_quality(self, image, brightness_threshold=180, blur_threshold=250):
        bright_check = False
        blur_check = False

        try:
            # Check if the image can be converted from RGB to YUV
            yuv_img = self.rgb2yuv(self.image_conversion(image))

        except Exception as e:
            raise Exception("Failed to convert image from RGB to YUV: " + str(e))

        try:
            # Check brightness
            brightness = np.average(yuv_img[..., 0])
            if brightness > brightness_threshold:
                raise Exception(f"Image is too bright. Brightness: {brightness}, Threshold: {brightness_threshold}")
            else:
                bright_check = True
        except Exception as e:
            raise Exception("Failed to check image brightness: " + str(e))

        try:
            # Check blurriness
            image = np.array(self.image_conversion(image))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            fm = cv2.Laplacian(gray, cv2.CV_64F).var()
            if fm < blur_threshold:
                raise Exception(f"Image is too blurry. Blurriness: {fm}, Threshold: {blur_threshold}")
            else:
                blur_check = True
        except Exception as e:
            raise Exception("Failed to check image blurriness: " + str(e))
        
        if bright_check and blur_check:
            return True
    # def check_image_quality(self, id_card, brightness_threshold=245, blur_threshold=150):
    #     id_card = self.image_conversion(id_card)
    #     id_card = np.array(id_card)
    #     bright_result = self.find_bright_areas(id_card, brightness_threshold)
    #     blurry_result = self.is_blurry(id_card)

    #     if bright_result > 1:
    #         raise Exception(f"Image is too bright. Threshold: {brightness_threshold}")

    #     if blurry_result < blur_threshold:
    #         raise Exception(f"Image is too blurry. Blurriness: {blurry_result}, Threshold: {blur_threshold}")

    def process_image(self,front_id):
        img = self.image_conversion(front_id)
        img = np.array(img)
        I = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = I.shape
        if (w > 640):
            I = cv2.resize(I, (640, int((h / w) * 640)))
        I = I - np.mean(I)
        sinogram = radon(I)
        r = np.array([np.sqrt(np.mean(np.abs(line) ** 2)) for line in sinogram.transpose()])
        rotation = np.argmax(r)
        angle = round(abs(90 - rotation)+0.5)

        if abs(angle) > 5:
            color_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(color_img)
            out = im.rotate(angle, expand=True)
        else:
            out = Image.fromarray(img)
    
        # im = self.image_conversion(front_id)
        # out = im.rotate(angle, expand=True)

        return out

    def is_colored(self, base64_image):
        img = self.image_conversion(base64_image)
        img = np.array(img)

        return len(img.shape) == 3 and img.shape[2] == 3
    
    def get_blurred_and_glared_for_doc(self, front_id, back_id):
        blurred = 'clear'
        glare = 'clear'

        front_id_img = self.image_conversion(front_id)
        front_id_arr = np.array(front_id_img)

        back_id_img = self.image_conversion(back_id)
        back_id_arr = np.array(back_id_img)

        blurry1 = self.is_blurry(front_id_arr)
        blurry2 = self.is_blurry(back_id_arr)
        if blurry1 < 150 or blurry2 < 150:
            blurred = 'consider'

        glare1 = self.find_bright_areas(front_id_arr, 245)
        glare2 = self.find_bright_areas(back_id_arr, 245)
        if glare1 > 1 or glare2 > 1:
            glare = 'consider'
        
        return blurred, glare

    # def get_face_orientation(self, face_landmarks):
    #     left_eye = np.array(face_landmarks['left_eye']).mean(axis=0)
    #     right_eye = np.array(face_landmarks['right_eye']).mean(axis=0)

    #     eye_slope = (right_eye[1] - left_eye[1]) / (right_eye[0] - left_eye[0])
    #     angle = np.degrees(np.arctan(eye_slope))

    #     return angle

    # def extract_selfie_from_video(self, video):
    #     cap = cv2.VideoCapture(video)

    #     # Initialize variables to keep track of the best frame and face score
    #     best_frame = None
    #     best_score = 0

    #     frame_count = 0

    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break

    #         frame_count += 1
            
    #         if frame_count % 3 != 0:
    #             continue
                
    #         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #         face_locations = face_recognition.face_locations(rgb_frame)
    #         face_landmarks_list = face_recognition.face_landmarks(rgb_frame)

    #         face_score = len(face_locations)

    #         for landmarks in face_landmarks_list:
    #             angle = self.get_face_orientation(landmarks)
    #             print(f"Current angle: {angle}")
    #             if abs(angle) < 1:
    #                 if face_score > best_score:
    #                     best_score = face_score
    #                     best_frame = frame.copy()


    #     # Release the video capture and close all windows
    #     cap.release()
    #     cv2.destroyAllWindows()

    #     # Save the best frame to a file (optional)
    #     if best_frame is not None:
    #         cv2.imwrite("best_frame.jpg", best_frame)
    #         print("Best frame saved as best_frame.jpg")
    #         return best_frame
    #     else:
    #         print("No suitable frame found.")
    #         return None

    def load_and_process_image_fr(self, base64_image):
        img = self.process_image(base64_image)
        img = np.array(img)
        image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # base64_image = base64_image.split(',')[-1]
        # image_data = base64.b64decode(base64_image)
        # image_file = io.BytesIO(image_data)

        # image = face_recognition.load_image_file(image_file)

        face_locations = face_recognition.face_locations(image)

        if not face_locations:
            return [], []
    
        face_encodings = face_recognition.face_encodings(image, face_locations)

        return face_locations, face_encodings
    
    def calculate_similarity(self, face_encoding1, face_encoding2):
        similarity_score = 1 - face_recognition.face_distance([face_encoding1], face_encoding2)[0]
        return similarity_score

    def extract_face_and_compute_similarity(self, selfie, front_id):
        face_locations1, face_encodings1 = self.load_and_process_image_fr(selfie)

        face_locations2, face_encodings2 = self.load_and_process_image_fr(front_id)

        if not face_encodings1 or not face_encodings2:
            raise ValueError("No faces detected in one or both images")
        else:
            # face_encoding1 = face_encodings1[0]
            # face_encoding2 = face_encodings2[0]
            largest_face_index1 = face_locations1.index(max(face_locations1, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))
            largest_face_index2 = face_locations2.index(max(face_locations2, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))

            face_encoding1 = face_encodings1[largest_face_index1]
            face_encoding2 = face_encodings2[largest_face_index2]

            similarity_score = self.calculate_similarity(face_encoding1, face_encoding2)

            return similarity_score
    
    def calculate_landmarks_movement(self, current_landmarks, previous_landmarks):
        return sum(
            abs(cur_point.position.x - prev_point.position.x) +
            abs(cur_point.position.y - prev_point.position.y)
            for cur_point, prev_point in zip(current_landmarks, previous_landmarks)
        )

    def calculate_face_movement(self, current_face, previous_face):
        return abs(current_face[0].x - previous_face[0].x) + abs(current_face[0].y - previous_face[0].y)

    def calculate_liveness_result(self, eyebrow_movement, nose_movement, lip_movement, face_movement):
        eyebrow_movement_threshold = 15.0
        nose_movement_threshold = 15.0
        lip_movement_threshold = 15.0
        face_movement_threshold = 10.0

        if (
            eyebrow_movement > eyebrow_movement_threshold or
            nose_movement > nose_movement_threshold or
            lip_movement > lip_movement_threshold or
            face_movement > face_movement_threshold
        ):
            return True
        else:
            return False

    def check_for_liveness(self, video_bytes):
        # cap = cv2.VideoCapture(video)
        with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
            temp_video_file.write(video_bytes)
        
        cap = cv2.VideoCapture(temp_video_file.name)

        frame_count = 0
        previous_landmarks = None
        previous_face = None
        liveness_result_list = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1

            if frame_count % 10 == 0:  # analyze every 10 frames
                _, buffer = cv2.imencode('.jpg', frame)
                image_data = buffer.tobytes()

                image = vision_v1.Image(content=image_data)

                response = self.client.face_detection(image=image)
                faces = response.face_annotations

                largest_face = None
                largest_face_area = 0

                for face in faces:
                    current_landmarks = face.landmarks
                    current_face = face.bounding_poly.vertices
                    face_area = abs((current_face[2].x - current_face[0].x) * (current_face[2].y - current_face[0].y))

                    if face_area > largest_face_area:
                        largest_face = face
                        largest_face_area = face_area

                if largest_face:
                    # face = faces[0]
                    current_landmarks = largest_face.landmarks
                    current_face = largest_face.bounding_poly.vertices

                    if previous_landmarks and previous_face:
                        eyebrow_movement = self.calculate_landmarks_movement(current_landmarks[:10], previous_landmarks[:10])

                        nose_movement = self.calculate_landmarks_movement(current_landmarks[10:20], previous_landmarks[10:20])

                        lip_movement = self.calculate_landmarks_movement(current_landmarks[20:28], previous_landmarks[20:28])

                        face_movement = self.calculate_face_movement(current_face, previous_face)

                        liveness_result = self.calculate_liveness_result(eyebrow_movement, nose_movement, lip_movement, face_movement)

                        liveness_result_list.append(liveness_result)

                    previous_landmarks = current_landmarks
                    previous_face = current_face

        cap.release()

        if any(liveness_result_list):
            liveness_check_result = 'clear'
        else:
            liveness_check_result = 'consider'

        return liveness_check_result

    def extract_id_number_from_front_id(self, front_id_text):
        try:
            id_number_match = re.search(r'.*ID Number\n*([\d-]+)', front_id_text)
            if id_number_match:
                id_number = id_number_match.group(1).replace('-','')
            else:
                id_number = ''
        except:
            id_number = ''

        return id_number
    
    def extract_name_from_front_id(self, front_id_text):
        try:
            name_match = re.search(r'Name: (.+)', front_id_text)
            if name_match:
                name = name_match.group(1)
            else:
                name = ''
        except:
            name = ''

        return name
    
    def extract_dob_from_fron_id(self, front_id_text):
        try:
            date_matches = re.findall(r'(\d{2}/\d{2}/\d{4})', front_id_text)
            date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in date_matches]
            date_of_birth = min(date_objects).strftime('%d/%m/%Y')
        except:
            date_of_birth = ''
        
        return date_of_birth
    
    def extract_expiry_date_from_fron_id(self, front_id_text):
        try:
            date_matches = re.findall(r'(\d{2}/\d{2}/\d{4})', front_id_text)
            date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in date_matches]
            expiry_date = max(date_objects).strftime('%d/%m/%Y')
        except:
            expiry_date = ''
        
        return expiry_date

    def get_ocr_results(self, processed_back_id):
        with io.BytesIO() as output:
            processed_back_id.save(output, format="PNG")
            image_data = output.getvalue()

        image = vision_v1.types.Image(content=image_data)
        response = self.client.text_detection(image=image)
        id_infos = response.text_annotations

        return id_infos

    def extract_ocr_info(self, selfie, video, front_id, back_id, country='UAE'):
        document_report = {}

        is_colored1 = self.is_colored(front_id)
        is_colored2 = self.is_colored(back_id)
        colour_picture = 'consider'
        if is_colored1 and is_colored2:
            colour_picture = 'clear'

        processed_selfie = self.process_image(selfie)
        processed_front_id = self.process_image(front_id)
        processed_back_id = self.process_image(back_id)
        
        if country=='UAE':
            # extract text from back id
            id_infos= self.get_ocr_results(processed_back_id)
            text = id_infos[0].description

            # extract text from front id
            front_id_text = self.get_ocr_results(processed_front_id)
            front_id_text = front_id_text[0].description
            
            id_number_pattern = r'(?:ILARE|IDARE)\s*([\d\s]+)'
            #card_number_pattern = r'(?:\b|Card Number\s*/\s*رقم البطاقة\s*)\d{9}(?:\b|\s*)'
            card_number_pattern = r'(\b\d{9}\b)|\b\w+(\d{9})\b|Card Number\s*(\d+)|Card Number\s*/\s*رقم البطاقة\s*(\d+)'
            date_pattern = r'(\d{2}/\d{2}/\d{4})'
            #(\d{2}/\d{2}/\d{4}) Date of Birth|\n
            #expiry_date_pattern = r'\n(\d{2}/\d{2}/\d{4})\s*\n'
            gender_pattern = r'Sex: ([A-Z])|Sex ([A-Z])'
            nationality_pattern = r'([A-Z]+)<<'
            # name_pattern = r'([A-Z]+(?:<<[A-Z]+)+(?:<[A-Z]+)+(?:<[A-Z]+))|([A-Z]+(?:<<[A-Z]+)+(?:<[A-Z]+))|([A-Z]+(?:<[A-Z]+)+(?:<<[A-Z]+)+(?:<[A-Z]+)+)'
            name_pattern = r'(.*[A-Za-z]+<[<]+[A-Za-z].*)'
            occupation_pattern = r'Occupation:\s*([\w\s.]+)'
            employer_pattern = r'Employer:\s*([\w\s.]+)'
            issuing_place_pattern = r'Issuing Place:\s*([\w\s.]+)'
            # mrz_pattern = r'(ILARE.*|IDARE.*)'
            mrz_pattern = r'(ILARE.*\n*.*\n*.*\n*.*|IDARE.*\n*.*\n*.*\n*.*)'
            
            try:
                id_number = re.search(id_number_pattern, text)
                id_number = id_number.group(0).replace(" ", "")[15:30]
                if len(id_number)<30:
                    id_number = self.extract_id_number_from_front_id(front_id_text)
            except:
                id_number = ''
            
            try:
                card_number = re.findall(card_number_pattern, text)
                card_number = [c for c in card_number if any(c)]
                if card_number:
                    card_number = "".join(card_number[0])
            except:
                card_number = ''
            
            dob, expiry_date = '', ''
            
            dates = re.findall(date_pattern, text)
            sorted_dates = sorted(dates, key=lambda x: datetime.strptime(x, '%d/%m/%Y'))

            date = [d for d in sorted_dates if any(d)]
            if date:
                try:
                    dob = "".join(date[0])
                except:
                    dob = ''
                try:
                    expiry_date = "".join(date[1])
                except:
                    expiry_date = ''
            
            if not dob:
                dob = self.extract_dob_from_fron_id(front_id_text)
            
            if not expiry_date:
                expiry_date = self.extract_expiry_date_from_fron_id(front_id_text)

            #expiry_date = re.search(expiry_date_pattern, text)
            
            gender = re.findall(gender_pattern, text)
            if gender:
                gender = "".join(gender[0])
            if not gender:
                gender_pattern = r'(?<=\d)[A-Z](?=\d)'
                gender = re.search(gender_pattern, text)
                gender = gender.group(0) if gender else ''
                
            try:
                nationality = re.search(nationality_pattern, text)
                nationality = nationality.group(1)
            except:
                nationality = ''
            
            try:
                name = re.findall(name_pattern, text)
                name = [n for n in name if any(n)]
                if name:
                    name = "".join(name[0])
                    name = name.replace('<',' ').strip()
                if len(name)<5:
                    name = self.extract_name_from_front_id(front_id_text)
            except:
                name = ''
            
            try:
                occupation = re.search(occupation_pattern, text, re.IGNORECASE)
                occupation = occupation.group(1).strip().split('\n', 1)[0]
            except:
                occupation = ''
            
            try:
                employer = re.search(employer_pattern, text, re.IGNORECASE)
                employer = employer.group(1).strip().split('\n', 1)[0]
            except:
                employer = ''
                    
            try:
                issuing_place = re.search(issuing_place_pattern, text, re.IGNORECASE)
                issuing_place = issuing_place.group(1).strip().split('\n', 1)[0]
            except:
                issuing_place = ''
            
            try:
                mrz = re.findall(mrz_pattern, text, re.MULTILINE)
                input_str = mrz[0].replace(" ", "")
                mrz1, remaining = input_str.split("\n", 1)
                mrz2, mrz3 = remaining.rsplit("\n", 1)
            # mrz1, mrz2, mrz3 = mrz[0].replace(' ','')mrz.split("\n")
            except:
                mrz, mrz1, mrz2, mrz3 = '', '', '', ''
            
            similarity = self.extract_face_and_compute_similarity(selfie, front_id)
            similarity = similarity + 0.25

            info_dict = {
                'id_number': id_number,
                'card_number': card_number,
                'name': name,
                'dob': dob ,
                'expiry_date': expiry_date,
                'gender': gender,
                'nationality': nationality,
                'occupation': occupation,
                'employer': employer,
                'issuing_place': issuing_place,
                'mrz': mrz,
                'mrz1': mrz1,
                'mrz2': mrz2,
                'mrz3': mrz3,
                'similarity': similarity
            }
            
            blurred, glare = self.get_blurred_and_glared_for_doc(front_id, back_id)
            missing_fields = 'clear'

            non_optional_keys = ["id_number", "card_number", "name", "dob", "expiry_date", "gender", "nationality", "mrz", "mrz1", "mrz2", "mrz3", "similarity"]
            empty_string_keys = [key for key, value in info_dict.items() if key not in non_optional_keys and value == '']

            if empty_string_keys:
                missing_fields = 'consider'
            
            document_report = ocr_utils.form_final_data_document_report(info_dict, front_id, front_id_text, back_id, text, colour_picture, similarity, blurred, glare, missing_fields)
            
            liveness_result = self.check_for_liveness(video)
            facial_report = ocr_utils.form_final_facial_similarity_report(similarity, liveness_result)

        else:
            pass
        
        #json_object = json.dumps(df, indent = 4) 
        return info_dict, document_report, facial_report
