from pydantic import BaseModel


class FileResponse(BaseModel):
    id: str
    kind: str
    name: str
    mimeType: str
    webViewLink: str
    parents: list[str]
