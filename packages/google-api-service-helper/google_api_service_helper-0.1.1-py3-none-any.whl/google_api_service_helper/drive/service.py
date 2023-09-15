import time
from dataclasses import asdict
from typing import Literal

from googleapiclient.errors import HttpError

from ..utils import GoogleKeys, GoogleService, get_google_service
from .schemas import FileResponse

DRIVE_SERVICE = GoogleService(
    version="v3", service_name="drive", scope="https://www.googleapis.com/auth/drive"
)


class GoogleDrive:
    FIELDS = "id,webViewLink,name,mimeType,kind,parents"

    def __init__(self, google_keys: GoogleKeys):
        self.service = get_google_service(
            google_keys=asdict(google_keys),
            scope=DRIVE_SERVICE.scope,
            service_name=DRIVE_SERVICE.service_name,
            version=DRIVE_SERVICE.version,
        )

    def make_new_folder(
        self,
        new_folder_title: str,
        parent_folder_id: str,
    ) -> FileResponse | None:
        data = {
            "name": new_folder_title,
            "parents": [parent_folder_id],
            "mimeType": "application/vnd.google-apps.folder",
        }
        try:
            result = (
                self.service.files().create(body=data, fields=self.FIELDS).execute()
            )
            return FileResponse(**result)
        except HttpError:
            return None

    def get_folder_by_id(self, folder_id: str) -> FileResponse | None:
        try:
            result = (
                self.service.files().get(fileId=folder_id, fields=self.FIELDS).execute()
            )
            return FileResponse(**result)
        except HttpError:
            return None

    def set_permissions_for_users_by_list(
        self,
        folder_id: str,
        user_email_list: list[str],
        permission: Literal["reader", "writer"] = "writer",
    ) -> None:
        """Выдает права на объект пользователям из списка"""
        batch = self.service.new_batch_http_request()
        for email in user_email_list:
            batch.add(
                self.service.permissions().create(
                    fileId=folder_id,
                    body={
                        "type": "user",
                        "role": permission,
                        "emailAddress": email,
                    },
                )
            )
        batch.execute()

    def set_permissions_for_anyone(
        self, folder_id: str, permission: Literal["reader", "writer"] = "reader"
    ) -> None:
        """Дать доступ к файлу любому в интернете"""
        batch = self.service.new_batch_http_request()
        batch.add(
            self.service.permissions().create(
                fileId=folder_id,
                body={
                    "type": "anyone",
                    "role": permission,
                },
            )
        )
        batch.execute()

    def get_files(self, folder_id: str) -> list[FileResponse]:
        files: list[FileResponse] = []
        page_token = None
        while True:
            response = (
                self.service.files()
                .list(
                    q=f"'{folder_id}' in parents",
                    spaces="drive",
                    fields="nextPageToken, "
                    "files(id,webViewLink,name,mimeType,kind,parents)",
                    pageSize=1000,
                    pageToken=page_token,
                )
                .execute()
            )
            files.extend([FileResponse(**f) for f in response.get("files", [])])
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
            time.sleep(0.1)
        return files

    def get_all_folder_files_recursively(self, folder_id: str) -> list[FileResponse]:
        files = self.get_files(folder_id=folder_id)
        for file in files:
            if ".folder" in file.mimeType:
                files.extend(self.get_all_folder_files_recursively(folder_id=file.id))
        return files
