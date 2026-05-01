from dataclasses import dataclass


@dataclass
class UploadedWordDocument:
    filename: str
    content_type: str
    data: bytes


@dataclass
class ConvertLimits:
    max_file_size_mb: int = 20