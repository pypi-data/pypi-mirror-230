from datetime import datetime
import re

def age_validation(dob, age_threshold=18):
    age_val = {
        "breakdown": {
            "minimum_accepted_age": {
            "properties": {},
            "result": ""
            }
        },
        "result": ""
        }
    
    dob_date = datetime.strptime(dob, "%d/%m/%Y")

    current_date = datetime.now()

    age = current_date.year - dob_date.year - ((current_date.month, current_date.day) < (dob_date.month, dob_date.day))

    if age>=age_threshold:
        age_val["breakdown"]["minimum_accepted_age"]["result"] = "clear"
        age_val["result"] = "clear"
    else:
        age_val["breakdown"]["minimum_accepted_age"]["result"] = "consider"
        age_val["result"] = "consider"

    return age_val
    
def created_at():
    current_datetime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    return current_datetime

def identify_document_type(text):
    text = text.upper()
    emirates_id_pattern = r'\b(ILARE\w*|IDARE\w*|RESIDENT IDENTITY)\b'
    passport_pattern = r'\b(PASSPORT|PPT)\b'
    driver_license_pattern = r'\b(DRIVER|LICENSE|DL)\b'

    if re.search(emirates_id_pattern, text):
        return "EID"

    if re.search(passport_pattern, text):
        return "PASSPORT"

    if re.search(driver_license_pattern, text):
        return "DL"

    return "Unknown"

def identify_front_id(text):
    front_id_keywords = ['Resident Identity', 'ID Number']
    pattern = '|'.join(map(re.escape, front_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def identify_back_id(text):
    back_id_keywords = ['ILARE', 'IDARE', 'Signature']
    pattern = '|'.join(map(re.escape, back_id_keywords))
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False

def is_valid_country(country):
    valid_countries = [country.name for country in pycountry.countries]

    if country in valid_countries:
        return True
    else:
        return False

def data_comparison_check():
    data_comparison = {
      "breakdown": {
        "date_of_birth": {
          "properties": {}
        },
        "date_of_expiry": {
          "properties": {}
        },
        "document_numbers": {
          "properties": {}
        },
        "document_type": {
          "properties": {}
        },
        "first_name": {
          "properties": {}
        },
        "gender": {
          "properties": {}
        },
        "issuing_country": {
          "properties": {}
        },
        "last_name": {
          "properties": {}
        }
      }
    }

    return data_comparison

def data_consistency_check(data):
    data_consistency = {
      "breakdown": {
        "date_of_birth": {
          "properties": {},
          "result": "clear"
        },
        "date_of_expiry": {
          "properties": {},
          "result": "clear"
        },
        "document_numbers": {
          "properties": {},
          "result": "clear"
        },
        "document_type": {
          "properties": {},
          "result": "clear"
        },
        "first_name": {
          "properties": {},
          "result": "clear"
        },
        "gender": {
          "properties": {},
          "result": "clear"
        },
        "issuing_country": {
          "properties": {},
          "result": "clear"
        },
        "last_name": {
          "properties": {},
          "result": "clear"
        },
        "multiple_data_sources_present": {
          "properties": {},
          "result": "clear"
        },
        "nationality": {
          "properties": {},
          "result": "clear"
        }
      },
      "result": "clear"
    }

    #### For data consistency compare data from different sources, like id and passport. 
    #### so the dob from id should match with dob extracted from passport

    doc_type = identify_document_type(data)
    if doc_type == 'EID' or doc_type=='PASSPORT':
        data_consistency['breakdown']['document_type']['result'] = 'clear'
    else:
        data_consistency['breakdown']['document_type']['result'] = 'consider'
    
    return data_consistency

def data_validation_check(data):
    data_validation = {
    "breakdown": {
        "date_of_birth": {
            "properties": {},
            "result": "clear"
        },
        "document_expiration": {
            "properties": {},
            "result": "clear"
        },
        "document_numbers": {
            "properties": {},
            "result": "clear"
        },
        "expiry_date": {
            "properties": {},
            "result": "clear"
        },
        "gender": {
            "properties": {},
            "result": "clear"
        },
        "mrz": {
            "properties": {},
            "result": "clear"
        },
        "barcode": {
            "properties": {},
            "result": "clear"
        }
    },
    "result": "clear"
}

    try:
        dob = data.get('dob')
        parsed_date = datetime.strptime(dob, "%d/%m/%Y")
        data_validation["breakdown"]['date_of_birth']["result"] = 'clear'
    except ValueError:
        data_validation["breakdown"]['date_of_birth']["result"] = 'consider'

    try:
        doe = data.get('expiry_date')
        parsed_date = datetime.strptime(doe, "%d/%m/%Y")
        data_validation["breakdown"]['expiry_date']["result"] = 'clear'
    except ValueError:
        data_validation["breakdown"]['expiry_date']["result"] = 'consider'

    gender = data.get('gender')
    if gender.isaplha() and len(gender) == 1:
        data_validation["breakdown"]['gender']["result"] = 'clear'
    else:
        data_validation["breakdown"]['gender']["result"] = 'consider'
    
    mrz = data.get('mrz')
    if len(mrz) == 30:
        data_validation["breakdown"]['mrz']["result"] = 'clear'
    else:
        data_validation["breakdown"]['mrz']["result"] = 'consider'
    
    doc_no = data.get('card_number')
    if len(doc_no)==9:
        data_validation["breakdown"]['document_numbers']["result"] = 'clear'
    else:
        data_validation["breakdown"]['document_numbers']["result"] = 'consider'

    if data_validation["breakdown"]['date_of_birth']["result"]=='clear' and data_validation["breakdown"]['expiry_date']["result"]=='clear' and data_validation["breakdown"]['gender']["result"]=='clear' and data_validation["breakdown"]['mrz']["result"]=='clear':
        data_validation['result'] = 'clear'

    return data_validation

## pending
def image_integrity_check(front_text, back_text):
    image_integrity = {
      "breakdown": {
        "colour_picture": {
          "properties": {},
          "result": "clear"
        },
        "conclusive_document_quality": {
          "properties": {
              #done
              "missing_back": "",
              #
              "digital_document": "",
              "punctured_document": "",
              "corner_removed": "",
              "watermarks_digital_text_overlay": "",
              "abnormal_document_features": "",
              "obscured_security_features": "",
              "obscured_data_points": ""
            },
          "result": "clear"
        },
        "image_quality": {
          "properties": {},
          "result": "clear"
        },
        "supported_document": {
          "properties": {},
          "result": "clear"
        }
      },
      "result": "clear"
    }

    if front_text and identify_back_id(front_text):
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
    else:
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'

    return image_integrity

## pending
def visual_authenticity_check():
    visual_authenticity = {
      "breakdown": {
        "digital_tampering": {
          "properties": {},
          "result": "clear"
        },
        "face_detection": {
          "properties": {},
          "result": "clear"
        },
        "fonts": {
          "properties": {},
          "result": "clear"
        },
        "original_document_present": {
          "properties": {},
          "result": "clear"
        },
        "other": {
          "properties": {},
          "result": "clear"
        },
        "picture_face_integrity": {
          "properties": {},
          "result": "clear"
        },
        "security_features": {
          "properties": {},
          "result": "clear"
        },
        "template": {
          "properties": {},
          "result": "clear"
        }
      },
      "result": "clear"
    }

    return visual_authenticity

def main_details(data):
    main_properties = {
        'barcode': [],
        "date_of_birth": "",
        "date_of_expiry": "",
        "document_numbers": [],
        "document_type": "",
        "first_name": "",
        "gender": "",
        "issuing_country": "",
        "last_name": "",
        "mrz_line1": "",
        "mrz_line2": "",
        "mrz_line3": "",
        "nationality": ""
    }

    try:
        main_properties['date_of_birth'] = data.get('dob')
        main_properties['date_of_expiry'] = data.get('expiry_date')

        if data.get('card_number'):
            card_data_t = {
            "type": "type",
            "value": "document_number"
            }

            card_data_v = {
                "type": "value",
                "value": data['card_number']
            }

            main_properties['document_numbers'].append(card_data_t)
            main_properties['document_numbers'].append(card_data_v)

        if data.get('id_number'):
            id_data_t = {
                        "type": "type",
                        "value": "personal_number"
                    }
            id_data_v = {
                        "type": "value",
                        "value": data['id_number']
                    }
                
            main_properties['document_numbers'].append(id_data_t) 
            main_properties['document_numbers'].append(id_data_v) 
        
        main_properties['document_type'] = 'national_identity_card'
        main_properties['first_name'] = data.get('name')
        main_properties['gender'] = data.get('gender')
        main_properties['issuing_country'] = data.get('issuing_place')
        main_properties['last_name'] = data.get('name')
        main_properties['mrz_line1'] = data.get('mrz1')
        main_properties['mrz_line2'] = data.get('mrz2')
        main_properties['mrz_line3'] = data.get('mrz3')
        main_properties['nationality'] = data.get('nationality')

    except:
        main_properties

    return main_properties    

def form_final_data(data, front_id, back_id, coloured, similarity):
    pass
