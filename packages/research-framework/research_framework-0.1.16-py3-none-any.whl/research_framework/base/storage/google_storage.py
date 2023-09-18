from googleapiclient.http import MediaInMemoryUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from google.cloud.storage import Client
from requests.exceptions import ConnectionError
import io
import os
import json 
import pickle

class BucketStorage:
    def __init__(self, service='drive'):
        print("Se está instanciando el Bucket Storage")
        creds = service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=list(json.loads(os.environ["ACCOUNT_SCOPES"])))
        if os.environ['DELEGATE_TO'] is not None:
            creds = creds.with_subject(os.environ['DELEGATE_TO'])
        self.creds = creds
        self.session = Client(project='tfm-project', credentials=self.creds)
        self.bucket = self.session.bucket(os.environ['BUCKET_NAME'])
        
    def upload_file(self, file, file_name, direct_stream=False):
        try:
            blob = self.bucket.blob(file_name)
            if not direct_stream:            
                binary = pickle.dumps(file)
                stream = io.BytesIO(binary)
                
                blob.upload_from_file(stream, timeout=300)
            else:
                file.seek(0)
                blob.upload_from_file(file, timeout=300)            
            print("Upload Complete!")
            return file_name

        except HttpError | ConnectionError as error:
            print(F'An connection error has occurred: {error}')
        return None
    
            
    def list_stored_files(self):
        try:
            return self.session.list_blobs(os.environ['BUCKET_NAME'])

        except HttpError as error:
            print(F'An error occurred: {error}')

    def get_file_by_id(self, file_id):
        return self.bucket.blob(file_id)
    
    def check_if_exists(self, file_id):
        return self.bucket.blob(file_id).exists()
    
    def download_file(self, drive_ref=None):
        try:
            blob = self.bucket.blob(drive_ref)
            return pickle.loads(blob.download_as_bytes())

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None
        
    def delete_file(self, file_id):
        print("Delete response:")
        blob = self.bucket.blob(file_id)
        if blob.exists():
            blob.delete()
        else:
            raise FileExistsError("No existe en el bucket")
    

class DriveStrage():
    def __init__(self, delegate=False):
        creds = service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=list(json.loads(os.environ["ACCOUNT_SCOPES"])))
        if os.environ['DELEGATE_TO'] is not None and delegate:
            creds = creds.with_subject(os.environ['DELEGATE_TO'])
        self.creds = creds
        self.session = build('drive', 'v3', credentials=self.creds)
        
    def upload_file(self, file, file_name):
        try:
            media = MediaInMemoryUpload(file, mimetype='application/octet-stream', resumable=True)
            request = self.session.files().create(media_body=media, body={"name":file_name}).execute()
            print("Upload Complete!")
            return request.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')

        return None
    
    def print_about(self):
        try:
            about = self.session.about().get(fields="*").execute()

            print(about)
        except HttpError as error:
            print ('An error occurred: %s' % error)
            
    def list_stored_files(self):
        try:
            return self.session.files().list(fields="files(id, name)").execute()

        except HttpError as error:
            print(F'An error occurred: {error}')

    def get_file_by_id(self, file_id):
        return self.session.files().get(fileId=file_id).execute()
    
    def download_file(self, drive_ref=None):
        try:
            request = self.session.files().get_media(fileId=drive_ref)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()

            return file.getvalue()

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None
        
        
    def delete_file(self, file_id):
        print("Delete response:")
        print(self.session.files().delete(fileId=file_id).execute())
        print("Empty trash:")
        print(self.session.files().emptyTrash().execute())