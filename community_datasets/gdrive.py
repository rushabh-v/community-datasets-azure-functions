import io
import os.path
import zipfile

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class MyDrive:
    def __init__(self):
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_authorized_user_file("./token.json", SCOPES)
        self.service = build("drive", "v3", credentials=creds)

    def update_file(self, filename, path):
        media = MediaFileUpload(f"{path}/{filename}")
        response = (
            self.service.files()
            .list(
                q=f"name='{filename}'",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=None,
            )
            .execute()
        )
        if len(response["files"]) > 0:
            for file in response.get("files", []):
                update_file = (
                    self.service.files()
                    .update(fileId=file.get("id"), media_body=media,)
                    .execute()
                )
        else:
            raise Exception("File not found on drive.")

    def download_file(self, filename):
        response = (
            self.service.files()
            .list(
                q=f"name='{filename}'",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=None,
            )
            .execute()
        )

        if len(response["files"]) == 1:
            file = response.get("files")[0]
            file_id = file.get("id")
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            return fh

        elif len(response["files"]) > 1:
            raise Exception("More files found with same name.")
        else:
            raise Exception("File not found on drive.")
