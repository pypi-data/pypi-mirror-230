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
        img=np.array(img)
        return cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    
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
        
    def check_image_quality(self, id_card, brightness_threshold=245, blur_threshold=150):
        id_card = self.image_conversion(id_card)
        id_card = np.array(id_card)
        bright_result = self.find_bright_areas(id_card, brightness_threshold)
        blurry_result = self.is_blurry(id_card)

        if bright_result >= 1:
            raise Exception(f"Image is too bright. Threshold: {brightness_threshold}")

        if blurry_result < blur_threshold:
            raise Exception(f"Image is too blurry. Blurriness: {blurry_result}, Threshold: {blur_threshold}")

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
        im = self.image_conversion(front_id)
        angle = round(abs(90 - rotation)+0.5)
        out = im.rotate(angle, expand=True)
        return out

    def get_ocr_results(self, processed_back_id):
        with io.BytesIO() as output:
            processed_back_id.save(output, format="PNG")
            image_data = output.getvalue()

        image = vision_v1.types.Image(content=image_data)
        response = self.client.text_detection(image=image)
        id_infos = response.text_annotations

        return id_infos

    def extract_ocr_info(self, selfie, video, front_id, back_id, country='UAE'):
        processed_front_id = self.process_image(front_id)
        processed_back_id = self.process_image(back_id)
        
        if country=='UAE':
            id_infos= self.get_ocr_results(processed_back_id)
            text = id_infos[0].description
            id_number_pattern = r'(?:ILARE|IDARE)\s*([\d\s]+)'
            #card_number_pattern = r'(?:\b|Card Number\s*/\s*رقم البطاقة\s*)\d{9}(?:\b|\s*)'
            card_number_pattern = r'(\b\d{9}\b)|\b\w+(\d{9})\b|Card Number\s*(\d+)|Card Number\s*/\s*رقم البطاقة\s*(\d+)'
            date_pattern = r'(\d{2}/\d{2}/\d{4})'
            #(\d{2}/\d{2}/\d{4}) Date of Birth|\n
            #expiry_date_pattern = r'\n(\d{2}/\d{2}/\d{4})\s*\n'
            gender_pattern = r'Sex: ([A-Z])|Sex ([A-Z])'
            nationality_pattern = r'([A-Z]+)<<'
            name_pattern = r'([A-Z]+(?:<<[A-Z]+)+(?:<[A-Z]+)+(?:<[A-Z]+))|([A-Z]+(?:<<[A-Z]+)+(?:<[A-Z]+))|([A-Z]+(?:<[A-Z]+)+(?:<<[A-Z]+)+(?:<[A-Z]+)+)'
            occupation_pattern = r'Occupation:\s*([\w\s.]+)'
            employer_pattern = r'Employer:\s*([\w\s.]+)'
            issuing_place_pattern = r'Issuing Place:\s*([\w\s.]+)'
            
            try:
                id_number = re.search(id_number_pattern, text)
                id_number = id_number.group(0).replace(" ", "")[15:30]
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
                    name = name.replace('<',' ')
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
                'similarity': 1
            }

        else:
            pass
        
        #json_object = json.dumps(df, indent = 4) 
        return info_dict
