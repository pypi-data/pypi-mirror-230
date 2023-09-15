from pydantic import BaseModel


class SpreadsheetProperties(BaseModel):
    title: str
    locale: str
    autoRecalc: str
    timeZone: str


class SheetProperties(BaseModel):
    sheetId: int
    title: str
    index: int
    sheetType: str
    hidden: bool = False
    gridProperties: dict | None = None
    tabColor: dict | None = None
    tabColorStyle: dict | None = None


class Sheet(BaseModel):
    properties: SheetProperties


class Spreadsheet(BaseModel):
    spreadsheetId: str
    spreadsheetUrl: str
    properties: SpreadsheetProperties
    sheets: list[Sheet]


class Action(BaseModel):
    addSheet: Sheet


class CreateSheetReply(BaseModel):
    spreadsheetId: str
    replies: list[Action]


class UpdatedResponseRange(BaseModel):
    spreadsheetId: str
    updatedRange: str
    updatedRows: int
    updatedColumns: int
    updatedCells: int


class UpdatedResponse(BaseModel):
    spreadsheetId: str
    totalUpdatedRows: int
    totalUpdatedColumns: int
    totalUpdatedCells: int
    totalUpdatedSheets: int
    responses: list[UpdatedResponseRange]


class RangeResponse(BaseModel):
    range: str
    majorDimension: str
    values: list[list[str]]


class SheetRangeResponse(BaseModel):
    spreadsheetId: str
    valueRanges: list[RangeResponse]


class Colors(BaseModel):
    red: float
    green: float
    blue: float


class ColorParams(BaseModel):
    backgroundColor: Colors


class ColoredData(BaseModel):
    formattedValue: str
    effectiveFormat: ColorParams


class ColoredRow(BaseModel):
    values: list[ColoredData | dict]


class ColoredRowData(BaseModel):
    rowData: list[ColoredRow]


class ColoredSheetResponse(BaseModel):
    data: list[ColoredRowData]


class ColoredDataResponse(BaseModel):
    sheets: list[ColoredSheetResponse]
