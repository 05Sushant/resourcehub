from pydantic import BaseModel, Field


class ResizeParameters(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class CSVValidationParameters(BaseModel):
    columns: dict[str, str]

class ValidationError(BaseModel):
    column: str
    row: int | None = None
    message: str


class CSVValidationResult(BaseModel):
    valid: bool
    errors: list[ValidationError]

class ColumnProfile(BaseModel):
    name: str
    type: str
    missing: int = 0
    unknown: int = 0
    unique: int = 0

class CSVProfile(BaseModel):
    rows: int
    columns: int
    columns_info: list[ColumnProfile]


class NumericStatistics(BaseModel):
    min: float | None = None
    max: float | None = None
    mean: float | None = None


class ColumnAnalysis(BaseModel):
    name: str
    type: str
    missing: int
    unique: int
    unknown: int
    statistics: NumericStatistics | None = None


class CSVAnalysis(BaseModel):
    rows: int
    columns: int
    columns_info: list[ColumnAnalysis]
