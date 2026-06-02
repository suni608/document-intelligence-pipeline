from pydantic import BaseModel
from typing import List, Optional


class KeyPoint(BaseModel):
    point: str
    evidence: Optional[str] = None


class ExtractedDocument(BaseModel):
    title: str
    summary: str

    key_points: List[KeyPoint]

    important_dates: Optional[List[str]] = []

    risks: Optional[List[str]] = []