from datetime import datetime
import re

def create_final_result(dictionary):
    result = ""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            sub_result = create_final_result(value)
            if sub_result == 'consider':
                return 'consider'
            elif sub_result == 'clear':
                result = 'clear'
        elif value in ['clear', 'consider', ""]:
            if value == 'consider':
                return 'consider'
            elif result != 'clear':
                result = value
    return result

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

def data_comparison_check():
    ## sending default as clear - identified from current nym's table results
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

def data_consistency_check(data, front_id_text, back_id_text):
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

    doc_type1 = identify_document_type(front_id_text)
    doc_type2 = identify_document_type(back_id_text)
    if doc_type1 == 'EID' or doc_type2=='EID':
        data_consistency['breakdown']['document_type']['result'] = 'clear'
    else:
        data_consistency['breakdown']['document_type']['result'] = 'consider'
        data_consistency['result'] = 'consider'
    
    return data_consistency

def data_validation_check(data):
    data_validation = {
    "breakdown": {
        "date_of_birth": {
            "properties": {},
            "result": "clear"
        },
        ## pending
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

    doc_no = data.get('card_number')
    if len(doc_no)==9:
        data_validation["breakdown"]['document_numbers']["result"] = 'clear'
    else:
        data_validation["breakdown"]['document_numbers']["result"] = 'consider'

    try:
        doe = data.get('expiry_date')
        parsed_date = datetime.strptime(doe, "%d/%m/%Y")
        data_validation["breakdown"]['expiry_date']["result"] = 'clear'
    except ValueError:
        data_validation["breakdown"]['expiry_date']["result"] = 'consider'

    gender = data.get('gender')
    if gender.isalpha() and len(gender) == 1:
        data_validation["breakdown"]['gender']["result"] = 'clear'
    else:
        data_validation["breakdown"]['gender']["result"] = 'consider'
    
    mrz = data.get('mrz')
    mrz1 = data.get('mrz1')
    mrz2 = data.get('mrz2')
    mrz3 = data.get('mrz3')
    if len(mrz) == 1 and mrz1 and mrz2 and mrz3:
        data_validation["breakdown"]['mrz']["result"] = 'clear'
    else:
        data_validation["breakdown"]['mrz']["result"] = 'consider'
    
    result = create_final_result(data_validation)
    data_validation['result'] = result

    # if data_validation["breakdown"]['date_of_birth']["result"]=='clear' and data_validation["breakdown"]['expiry_date']["result"]=='clear' and data_validation["breakdown"]['gender']["result"]=='clear' and data_validation["breakdown"]['mrz']["result"]=='clear':
    #     data_validation['result'] = 'clear'

    return data_validation

## pending
def image_integrity_check(front_id_text, back_id_text, coloured, blurred, glare, missing_fields):
    image_integrity = {
      "breakdown": {
        "colour_picture": {
          "properties": {},
          "result": "clear"
        },
        "conclusive_document_quality": {
          "properties": {
              # done
              "missing_back": "clear",
              # pedning - part of fraud check/tampering detection - TBD next week
              "digital_document": "clear",
              "punctured_document": "clear",
              "corner_removed": "clear",
              "watermarks_digital_text_overlay": "clear",
              "abnormal_document_features": "clear",
              "obscured_security_features": "clear",
              "obscured_data_points": "clear"
            },
          "result": "clear"
        },
        "image_quality": {
          "properties": {
              "blurred_photo": blurred,
              "covered_photo": missing_fields,
              ## pending
              "cut_off_document": "clear",
              "glare_on_photo": glare,
              "other_photo_issue": missing_fields,
              ## pending
              "two_documents_uploaded": "clear"
          },
          "result": "clear"
        },
        ## pending - complete this by checking excel comments - identifiers for document type
        "supported_document": {
          "properties": {},
          "result": "clear"
        }
      },
      "result": "clear"
    }

    if coloured:
        image_integrity['breakdown']['colour_picture']['result'] = coloured

    if back_id_text and identify_back_id(back_id_text):
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'clear'
    else:
        image_integrity['breakdown']['conclusive_document_quality']['properties']['missing_back'] = 'consider'

    f_result = identify_front_id(front_id_text)
    b_result = identify_back_id(back_id_text)

    if f_result and b_result:
        image_integrity['breakdown']['supported_document']['result'] = 'clear'
    else:
        image_integrity['breakdown']['supported_document']['result'] = 'consider'

    # image_integrity['breakdown']['image_quality']['properties']['blurred_photo'] = blurred
    # image_integrity['breakdown']['image_quality']['properties']['glare_on_photo'] = glare

    image_quality_result = create_final_result(image_integrity['breakdown']['image_quality'])
    conclusive_document_quality_result = create_final_result(image_integrity['breakdown']['conclusive_document_quality'])
    colour_picture_result = image_integrity['breakdown']['colour_picture']['result']
    supported_documents_result = image_integrity['breakdown']['supported_document']['result']

    if image_quality_result == 'consider' or conclusive_document_quality_result == 'consider' or colour_picture_result == 'consider' or supported_documents_result == 'consider':
        image_integrity['result'] = 'consider'

    return image_integrity

def visual_authenticity_check(data, front_id_text, back_id_text, facial_similarity):
    visual_authenticity = {
      "breakdown": {
        ## pending - tamper detection
        "digital_tampering": {
          "properties": {},
          "result": "clear"
        },
        "face_detection": {
          "properties": {},
          "result": "clear"
        },
        ## pending - tamper detection
        "fonts": {
          "properties": {},
          "result": "clear"
        },
        "original_document_present": {
          "properties": {
                "scan": "clear",
                ## pending - all 3 - tamper detection
                "document_on_printed_paper": "clear",
                "screenshot": "clear",
                "photo_of_screen": "consider"
          },
          "result": "clear"
        },
        "other": {
          "properties":  {},
          "result": "clear"
        },
        # compare all 3 faces extracted for similarity
        "picture_face_integrity": {
          "properties": {},
          "result": "clear"
        },
        "security_features": {
          "properties": {},
          "result": "clear"
        },
        ## pending - tamper detection
        "template": {
          "properties": {},
          "result": "clear"
        }
      },
      "result": "clear"
    }

    if facial_similarity>=0.65:
        visual_authenticity['breakdown']['face_detection'] = 'clear'
        visual_authenticity['breakdown']['security_features'] = 'clear'
    else:
        visual_authenticity['breakdown']['face_detection'] = 'consider'
        visual_authenticity['breakdown']['security_features'] = 'consider'
    
    doc_type1 = identify_document_type(front_id_text)
    doc_type2 = identify_document_type(back_id_text)
    if doc_type1 == 'EID' or doc_type2=='EID':
        visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'clear'
    else:
        visual_authenticity['breakdown']['original_document_present']['properties']['scan'] = 'consider'

    final_result = create_final_result(visual_authenticity)
    visual_authenticity['result'] = final_result

    return visual_authenticity

def main_details(data):
    main_properties = {
        ## barcode is empty in all instance - TBD
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

def form_final_data_document_report(data, front_id, front_id_text, back_id, back_id_text, coloured, facial_similarity, blurred, glare, missing_fields):
    try:
        document_report = {
            ## pending - to be filled by dev
            "_id": "",
            "breakdown": {
                "age_validation": age_validation(data.get('dob')),
                "compromised_document": {
                    "result": "clear"
                    },
                "data_comparison": data_comparison_check(),
                "data_consistency": data_consistency_check(data, front_id_text, back_id_text),
                "data_validation": data_validation_check(data),
                "image_integrity": image_integrity_check(front_id_text, back_id_text, coloured, blurred, glare, missing_fields),
                "issuing_authority": {
                "breakdown": {
                    "nfc_active_authentication": {
                    "properties": {}
                    },
                    "nfc_passive_authentication": {
                    "properties": {}
                    }
                }
                },
                "police_record": {},
                "visual_authenticity": visual_authenticity_check(data, front_id_text, back_id_text, facial_similarity),
                ## pending - to be filled by dev
                "check_id": "", 
                "created_at": created_at(),
                "documents": [
                    {
                    ## pending - id value in table stored in db for front id - to be filled by dev
                    "id": ""
                    },
                    {
                    ## pending - id value in table stored in db for front id - to be filled by dev
                    "id": ""
                    }
                ],
                "name": "document",
                "properties": main_details(data),
                # include all results from above to find this
                "result": "",
                "status": "complete",
                "sub_result": ""
            }
        }
        
        final_result = create_final_result(document_report)
        document_report['breakdown']['result'] = final_result
        document_report['breakdown']['sub_result'] = final_result

        return document_report
    
    except Exception as e:
        return e

def form_final_facial_similarity_report(facial_similarity, liveness_result):
    facial_report = {
        "created_at": "",
        ## pending - to be filled by dev
        "href": "/v3.6/reports/<REPORT_ID>",
        ## pending - to be filled by dev
        "id": "<REPORT_ID>",
        "name": "facial_similarity_video",
        "properties": {},
        "breakdown": {
            "face_comparison": {
                "breakdown": {
                    "face_match": { 
                        "properties": {
                            "score": 0,
                            ## pending - to be filled by dev
                            "document_id": "<DOCUMENT_ID>"
                        },
                        "result": "clear", 
                    }
                },
                "result": "clear"
            },
            "image_integrity": {
                "breakdown": {
                    "face_detected": {
                        "result": "clear",
                        "properties": {}
                    },
                    ## pending
                    "source_integrity": {
                        "result": "clear",
                        "properties": {}
                    }
                },
                "result": "clear",
            },
            "visual_authenticity": {
                "breakdown": {
                    "liveness_detected": {
                        "properties": {},
                        "result": "clear",
                    },
                    "spoofing_detection": {
                        "properties": {
                            "score": 0.90
                        },
                        "result": "clear",
                    }
                },
                "result": "clear",
            }
        },
        "result": "clear",
        "status": "complete",
        "sub_result": "clear",
        ## pending - to be filled by dev
        "check_id": "<CHECK_ID>",
        "documents": []
        }
    
    facial_report['created_at'] = created_at()

    facial_report['breakdown']['face_comparison']['breakdown']['face_match']['properties']['score'] = facial_similarity

    if facial_similarity>=0.65:
        facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result'] = 'clear'
        facial_report['breakdown']['face_comparison']['result'] = 'clear'
        facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'clear'
    else:
        facial_report['breakdown']['face_comparison']['breakdown']['face_match']['result']  = 'consider'
        facial_report['breakdown']['face_comparison']['result'] = 'consider'
        facial_report['breakdown']['image_integrity']['breakdown']['face_detected']['result'] = 'consider'
    
    facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['properties']['score'] = liveness_result

    if liveness_result == 'consider':
        facial_report['breakdown']['visual_authenticity']['breakdown']['liveness_detected']['result'] = 'consider'
        facial_report['breakdown']['visual_authenticity']['breakdown']['spoofing_detection']['result'] = 'consider'

    visual_authenticity_final_result = create_final_result(facial_report['breakdown']['visual_authenticity'])
    facial_report['breakdown']['visual_authenticity']['result'] = visual_authenticity_final_result

    image_integrity_final_result = create_final_result(facial_report['breakdown']['image_integrity'])
    facial_report['breakdown']['image_integrity']['result'] = image_integrity_final_result

    complete_final_reult = create_final_result(facial_report['breakdown'])
    facial_report['result'] = complete_final_reult
    facial_report['sub_result'] = complete_final_reult

    return facial_report
