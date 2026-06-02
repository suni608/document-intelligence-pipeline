from pydantic import BaseModel, Field
from typing import List, Optional

class KeyPoint(BaseModel):
    """
    Represents a single atomic takeaway extracted from a document chunk,
    accompanied by verifiable quote evidence from the source text.
    """
    point: str = Field(
        description="A key takeaway or core claim extracted from the document text."
    )
    evidence: Optional[str] = Field(
        default=None,
        description="An exact, direct quote from the source text that supports this point."
    )

class ExtractedDocument(BaseModel):
    """
    The structured document schema that defines Stage 03 of the pipeline.
    Validates LLM extraction formats using Pydantic runtime enforcement.
    """
    title: str = Field(
        description="A concise and descriptive title of the document chunk or entire document."
    )
    summary: str = Field(
        description="A detailed, comprehensive summary of the main points. Must explicitly capture metadata, contact emails, and URLs if present."
    )
    key_points: List[KeyPoint] = Field(
        default=[],
        description="A collection of key points and their corresponding source text evidence."
    )
    important_dates: Optional[List[str]] = Field(
        default=[],
        description="Important dates (e.g. publication, updates) as they appear in the source text."
    )
    risks: Optional[List[str]] = Field(
        default=[],
        description="Any risks, challenges, regulatory vulnerability, or harms mentioned in the text."
    )
