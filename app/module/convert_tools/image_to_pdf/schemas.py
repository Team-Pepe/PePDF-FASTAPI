from pydantic import BaseModel, Field


class ConvertLimits(BaseModel):
    max_files: int = Field(default=10, ge=1)
    max_file_size_mb: int = Field(default=15, ge=1)
