from app.extraction.schema import ExtractedDocument

def generate_markdown(document: ExtractedDocument) -> str:
    """
    Renders an ExtractedDocument object into a beautifully structured Markdown document.
    Suitable for local knowledge storage or for publishing to Confluence via Markdown import.
    
    Args:
        document (ExtractedDocument): The validated schema object.
        
    Returns:
        str: The rendered Markdown content as a single string.
    """
    markdown = f"# {document.title}\n\n"
    
    markdown += f"## Summary\n{document.summary}\n\n"
    
    markdown += "## Key Points & Evidence\n"
    if document.key_points:
        for item in document.key_points:
            markdown += f"- **Point**: {item.point}\n"
            if item.evidence:
                markdown += f"  - *Evidence*: \"{item.evidence.strip()}\"\n"
    else:
        markdown += "*No key points extracted.*\n"
        
    markdown += "\n## Identified Risks & Vulnerabilities\n"
    if document.risks:
        for risk in document.risks:
            markdown += f"- {risk}\n"
    else:
        markdown += "*No risks identified.*\n"
        
    markdown += "\n## Important Timeline & Dates\n"
    if document.important_dates:
        for date in document.important_dates:
            markdown += f"- {date}\n"
    else:
        markdown += "*No dates extracted.*\n"
        
    return markdown
