import json
import traceback

from layernext.datalake.constants import MetadataUploadType

from .keys import DEST_PROJECT_ID, SESSION_ID, TOTAL_IMAGE_COUNT, UPLOADED_IMAGE_COUNT, USERNAME, LABELS, META_UPDATES_ARRAY, IS_NORMALIZED
import requests


class DatalakeInterface:

    def __init__(self, auth_token: str, dalalake_url: str):
        self.auth_token = auth_token
        self.dalalake_url = dalalake_url

    def create_datalake_label_coco(self, label, username='Python SDK'):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        payload = {
            USERNAME: username,
            LABELS: label,
        }
        url = f'{self.dalalake_url}/api/client/cocojson/import/label/create'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            return response.json()
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
        

    def find_datalake_label_references(self, label_attribute_values_dict, username='Python SDK'):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        payload = {
            LABELS: label_attribute_values_dict,
            USERNAME: username
        }
        url = f'{self.dalalake_url}/api/client/system/label/references'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return_object = response.json()
                return return_object
            elif status_code == 204:
                return {"isSuccess": False, "message": "No references found"}
            else:
                return {"isSuccess": False, "message":response.json().get("error").get("message")}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        

    def upload_metadata_updates(self, meta_updates, operation_type, operation_mode, operation_id, is_normalized, 
                                session_id, total_images_count, uploaded_images_count, dest_project_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        payload = {
            META_UPDATES_ARRAY: json.dumps(meta_updates),
            SESSION_ID : session_id,
            TOTAL_IMAGE_COUNT : total_images_count,
            UPLOADED_IMAGE_COUNT : uploaded_images_count
        }

        params = {
            IS_NORMALIZED: is_normalized,
        }
        if dest_project_id != None:
            params[DEST_PROJECT_ID] = dest_project_id

        url = f'{self.dalalake_url}/api/metadata/operationdata/{operation_type}/{operation_mode}/{operation_id}/update'
        print(url)

        try:
            response = requests.post(url=url, params=params, json=payload, headers=hed)
            return response.json()
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    ''''
    Upload meta data collection
    '''

    def upload_metadata_collection(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/uploadMetadataInCollection'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return_object = response.json()
                return_object["isSuccess"] = True
                return return_object
            else:
                return {"isSuccess": False, "message": response.json().get("error").get("message")}

        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    ''''
    Get file id and key from s3 bucket
    '''

    def get_file_id_and_key(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/fileUpload/initializeMultipartUpload'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code != 204 and status_code != 200:
                return {"isSuccess": False}

            return_object = response.json()
            return_object["isSuccess"] = True
            return return_object
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    ''''
    Get pre-signed url
    '''

    def get_pre_signed_url(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/fileUpload/getMultipartPreSignedUrls'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code != 204 and status_code != 200:
                return {"isSuccess": False}

            return_object = response.json()
            return_object["isSuccess"] = True
            return return_object
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}


    ''''
    Finalize multipart upload
    '''

    def finalize_upload(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/fileUpload/finalizeMultipartUpload'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 204 or status_code == 200:
                return {"isSuccess": True}
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}


    def complete_collection_upload(self, upload_id, is_single_file_upload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/collectionUploadingStatus/{upload_id}/complete?isReturnedUniqueName={is_single_file_upload}'

        try:
            response = requests.get(url=url, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return_object = response.json()
                return_object["isSuccess"] = True
                return return_object
            elif status_code == 204:
                return {"isSuccess": True}
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    def get_upload_status(self, collection_name):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/collection/getuploadProgress?collectionName={collection_name}'

        try:
            response = requests.get(url=url, headers=hed)
            status_code = response.status_code
            if status_code == 204 or status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    def remove_modelrun_collection_annotation(self, collection_id, model_run_id, session_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/collection/deleteAnnotation?collectionId={collection_id}&operationId={model_run_id}'

        payload = {
            SESSION_ID : session_id
        }

        try:
            response = requests.get(url=url, headers=hed, json=payload)
            status_code = response.status_code
            if status_code == 204 or status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}



    ''''
    get selection id from query, filter and collectionId
    '''
    def get_selection_id(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/query/getSelectionId'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    ''''
    trash selected objects
    ''' 
    def trash_files(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/file/trash'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            # print(response.json())
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False, "message":response.json().get("error").get("message")}
            
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    

    def get_object_type_by_id(self, object_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/{object_id}/getObjectTypeById'

        try:
            response = requests.get(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}

    def get_all_label_list(self, group_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/labels/list'
        if group_id != None:
            url += '?groupId=' + group_id
        try:
            response = requests.get(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return []
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return []
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return []
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return []
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return []
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return []

    def get_all_group_list(self):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/label_groups/list'

        try:
            response = requests.get(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return []
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return []
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return []
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return []
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return []
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return []

    def create_system_label(self, label):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/system/labels/create'
        payload = {
            "label": label,
            "userName": "Python SDK"
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                print(response.text)
                return None
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return None
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return None
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return None
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return None
        
    def create_label_group(self, name, keys):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/label_groups/create'
        payload = {
            "groupName": name,
            "labelKeys": keys
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                print(response.text)
                return None
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return None
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return None
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return None
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return None

    def add_labels_to_group(self, group_id, label_keys):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/label_groups/{group_id}/addLabels'
        payload = {
            "labelKeys": label_keys
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                print(response.text)
                return {"is_success": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"is_success": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"is_success": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"is_success": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"is_success": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"is_success": False, "message": "Error in checking version compatibility"}

    def remove_labels_from_group(self, group_id, label_keys):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/label_groups/{group_id}/removeLabels'
        payload = {
            "labelKeys": label_keys
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                print(response.text)
                return {"is_success": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"is_success": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"is_success": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"is_success": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"is_success": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"is_success": False, "message": "Error in checking version compatibility"}

    def check_job_status(self, job_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/jobs/{job_id}/getStatus'
        try:
            response = requests.get(url=url, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                print(response.text)
                return None
            
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return None
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return None
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return None
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return None

    def check_sdk_version_compatibility(self, sdk_version):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/sdk/compatibility/{sdk_version}'
        try:
            response = requests.get(url=url, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            elif status_code == 401:
                return {
                    "isCompatible": False,
                    "message": "Authentication failed, please check your credentials"
                }
            else:
                print(response.text)
                return {
                    "isCompatible": False,
                    "message": "Failed to connect to Data Lake"
                }
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isCompatible": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isCompatible": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isCompatible": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isCompatible": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isCompatible": False, "message": "Error in checking version compatibility"}
        
    def get_file_download_url(self, file_key):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/downloadUrl?file_key={file_key}'

        try:
            response = requests.get(url=url, json={}, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
            
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        
    """
    Uploads metadata to Data Lake
    """    
    def upload_metadata(self, payload, metadata_upload_type: MetadataUploadType):
        hed = {'Authorization': 'Basic ' + self.auth_token}

        if metadata_upload_type == MetadataUploadType.BY_JSON:
            url = f'{self.dalalake_url}/api/client/metadata/uploadMetadataByJson'
        elif metadata_upload_type == MetadataUploadType.BY_META_OBJECT:
            url = f'{self.dalalake_url}/api/client/metadata/uploadMetadataByMetaObject'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            # print(response)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            elif status_code == 406:
                return {"isSuccess": False, "message":response.json().get("error").get("message")}
            else:
                return {"isSuccess": False, "message":response.json().get("error").get("message")}
        except requests.exceptions.RequestException as e:
            print(f"An request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in uploading metadata1"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)} ")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in uploading metadata"}
        
    """
    Validates metadata tags to Data Lake
    """
    def validate_tags(self, unique_tags):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/metadata/validateTags'
        payload = {
            "tags": unique_tags
        }
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return {"is_valid": True}
            elif status_code == 204:
                return {"is_valid": True}
            elif status_code == 406:
                return {"is_valid": False, "message":response.json().get("error").get("message")}
            else:
                print(response.text)
                return {"is_valid": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"is_valid": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"is_valid": False, "message": "Error in checking version compatibility"}

        
    """
    Gets metadata from Data Lake by using unique name  
    """
    def get_item_details(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/metadata/getItemDetails'
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"is_valid": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"is_valid": False, "message": "Error in checking version compatibility"}
    

    """
    get item list from collection in datalake
    
    """
    def get_item_list_from_collection(self, payload, collection_id):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/explorer/{collection_id}/objects/list'
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            elif status_code == 204:
                return {"isSuccess": False, "message":"No content found"}
            elif status_code == 406:
                return {"isSuccess": False, "message":response.json().get("error").get("message")}
            else:
                print(response.text)
                return {"isSuccess": False, "message":f"Error in getting item details: {response.text}"}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        
    """
    Gets metadata from Data Lake by using collection id  
    """
    def get_collection_details(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/metadata/getCollectionDetails'
        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                return {"isSuccess": False}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"is_valid": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"is_valid": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"is_valid": False, "message": "Error in checking version compatibility"}
        

    """
    get item list from datalake
    
    """    
    def get_item_list_from_datalake(self, payload):
        hed = {'Authorization': 'Basic ' + self.auth_token}
        url = f'{self.dalalake_url}/api/client/explorer/objects/list'

        try:
            response = requests.post(url=url, json=payload, headers=hed)
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            elif status_code == 204:
                return {"isSuccess": False, "message":"No content found"}
            elif status_code == 406:
                return {"isSuccess": False, "message":response.json().get("error").get("message")}
            else:
                print(response.text)
                return {"isSuccess": False, "message":f"Error in getting item details: {response.text}"}
        #Handle connection error
        except requests.exceptions.ConnectionError as e:
            print("Connection error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle timeout error
        except requests.exceptions.Timeout as e:
            print("Timeout error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"}
        #Handle HTTP errors
        except requests.exceptions.HTTPError as e:
            print("HTTP error from Data Lake connection")
            return {"isSuccess": False, "message": "Failed to connect to Data Lake"} 
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request exception occurred: {format(e)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        except Exception as e1:
            print(f"An unexpected exception occurred: {format(e1)}")
            traceback.print_exc()
            return {"isSuccess": False, "message": "Error in checking version compatibility"}
        
