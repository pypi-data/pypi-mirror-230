from dataclasses import asdict
from typing import Any, Literal

from ..utils import GoogleKeys, GoogleService, get_google_service
from .schemas import (
    ColoredDataResponse,
    CreateSheetReply,
    SheetRangeResponse,
    Spreadsheet,
    UpdatedResponse,
)

SPREADSHEET_SERVICE = GoogleService(
    version="v4",
    service_name="sheets",
    scope="https://www.googleapis.com/auth/spreadsheets",
)


class GoogleSheets:
    def __init__(self, google_keys: GoogleKeys) -> None:
        self.service = get_google_service(
            google_keys=asdict(google_keys),
            scope=SPREADSHEET_SERVICE.scope,
            service_name=SPREADSHEET_SERVICE.service_name,
            version=SPREADSHEET_SERVICE.version,
        )

    def get_spreadsheet(self, spreadsheet_id: str) -> Spreadsheet:
        result = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return Spreadsheet(**result)

    def create_sheet(
        self,
        spreadsheet_id: str,
        title: str,
        index: int = 0,
        row_count: int = 200,
        col_count: int = 200,
        red: float = 1,
        green: float = 1,
        blue: float = 0,
    ) -> CreateSheetReply:
        request_body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": title,
                            "tabColor": {"red": red, "green": green, "blue": blue},
                            "index": index,
                            "gridProperties": {
                                "rowCount": row_count,
                                "columnCount": col_count,
                            },
                        }
                    }
                }
            ]
        }
        result = (
            self.service.spreadsheets()
            .batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body,
            )
            .execute()
        )
        return CreateSheetReply(**result)

    def get_sheet(self, spreadsheet_id: str, sheet: str) -> SheetRangeResponse:
        result = (
            self.service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=sheet,
                valueRenderOption="FORMATTED_VALUE",
                dateTimeRenderOption="FORMATTED_STRING",
            )
            .execute()
        )
        return SheetRangeResponse(**result)

    def set_data(
        self,
        spreadsheet_id: str,
        range_sheet: int,
        values: list[list[Any]],
        major_dimension: Literal["COLUMNS", "ROWS"] = "ROWS",
    ) -> UpdatedResponse:
        request_body = {
            "valueInputOption": "USER_ENTERED",
            "data": [
                {
                    "range": range_sheet,
                    "majorDimension": major_dimension,
                    "values": values,
                }
            ],
        }
        result = (
            self.service.spreadsheets()
            .values()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
            .execute()
        )
        return UpdatedResponse(**result)

    def get_sheet_with_colors(
        self, ss_id: str, range_sheet: str
    ) -> ColoredDataResponse:
        params = {
            "spreadsheetId": ss_id,
            "ranges": range_sheet,
            "fields": "sheets(data(rowData(values(effectiveFormat/"
            "backgroundColor,formattedValue)),startColumn,"
            "startRow))",
        }
        result = self.service.spreadsheets().get(**params).execute()
        return ColoredDataResponse(**result)

    def get_data(self, spreadsheet_id: str, sheet: str) -> list[list[str]]:
        result = self.get_sheet(spreadsheet_id=spreadsheet_id, sheet=sheet)
        return result.valueRanges[0].values

    def clear_sheet_data(self, spreadsheet_id: str, sheet: str) -> None:
        self.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=sheet,
            body={},
        ).execute()
