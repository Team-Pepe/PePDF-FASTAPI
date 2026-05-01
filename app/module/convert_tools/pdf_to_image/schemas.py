from dataclasses import dataclass


@dataclass
class UploadedPDF:
    """Represents an uploaded PDF file with its metadata."""
    filename: str
    content_type: str
    data: bytes


@dataclass
class ConvertLimits:
    """Configuration for PDF to image conversion limits."""
    max_files: int = 5
    max_file_size_mb: int = 20
