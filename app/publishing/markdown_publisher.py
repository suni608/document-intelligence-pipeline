def generate_markdown(document):

    markdown = f"# {document.title}\n\n"

    markdown += f"## Summary\n{document.summary}\n\n"

    markdown += "## Key Points\n"

    for item in document.key_points:
        markdown += f"- {item.point}\n"
        markdown += f"  - Evidence: {item.evidence}\n"

    markdown += "\n## Risks\n"

    for risk in document.risks:
        markdown += f"- {risk}\n"

    markdown += "\n## Important Dates\n"

    for date in document.important_dates:
        markdown += f"- {date}\n"

    return markdown