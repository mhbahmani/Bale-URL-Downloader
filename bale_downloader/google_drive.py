import os
import logging
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from bale_downloader.config import GOOGLE_DRIVE_FOLDER_ID

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'credentials.json'


class GoogleDrive:
    def __init__(self):
        self.creds = GoogleDrive.authenticate_google_drive()
        self.service = build('drive', 'v3', credentials=self.creds)

    @staticmethod
    def authenticate_google_drive() -> Optional[Credentials]:
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_PATH):
                    logging.error("credentials.json not found. Please download it from Google Cloud Console.")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

        return creds

    def upload_file_to_drive(self, file_path: str) -> str:
        file_id = self._upload_file(file_path)
        return self.generate_file_url_by_id(file_id)[0]

    def _upload_file(self, file_path: str, folder_id: Optional[str] = GOOGLE_DRIVE_FOLDER_ID) -> List[str]:
        """
        Upload the file paths to Google Drive.

        Args:
            file_path (str): A local file path to upload.
            folder_id (str, optional): The ID of the Google Drive folder to upload to.

        Returns:
            str: A Google Drive File ID for the uploaded file.
        """
        if not self.creds:
            raise ValueError("Google Drive credentials not found")

        uploaded_file_ids = []

        try:
            service = build('drive', 'v3', credentials=self.creds)

            if not os.path.isfile(file_path):
                logging.warning(f"File not found: {file_path}. Skipping.")
                return

            file_name = os.path.basename(file_path)
            file_metadata = {'name': file_name}

            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(file_path, resumable=True)

            logging.info(f"Uploading {file_name}...")
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
            uploaded_file_ids.append(file_id)
            logging.info(f"Successfully uploaded: {file_name} (ID: {file_id})")

        except HttpError as error:
            logging.error(f"An error occurred with the Google Drive API: {error}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

        return uploaded_file_ids

    def generate_file_url_by_id(self, file_ids: str) -> List[str]:
        """
        Makes files publicly accessible and returns their shareable URLs.

        Args:
            file_ids (List[str]): A list of Google Drive File IDs.

        Returns:
            List[str]: A list of publicly accessible file URLs.
        """
        urls = []
        for file_id in file_ids:
            try:
                self.service.permissions().create(
                    fileId=file_id,
                    body={'type': 'anyone', 'role': 'reader'},
                ).execute()
                urls.append(f"https://drive.google.com/file/d/{file_id}/view?usp=sharing")
            except HttpError as error:
                logging.error(f"Failed to share file {file_id}: {error}")
        return urls
