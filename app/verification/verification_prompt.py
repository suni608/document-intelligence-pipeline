VERIFICATION_PROMPT = """
You are an objective auditor. Compare the source document text with the extracted structured JSON output and calculate a mathematical score out of 100 based on the following rubric:

- **Accuracy (50 points maximum)**: Start with 50. Subtract 10 points for every factual error or mismatch. If there are no factual errors, award the full 50 points.
- **Completeness (30 points maximum)**: Start with 30. Subtract 5 points for each key fact, date, or risk that was omitted. If there are no omissions, award the full 30 points. (Note: Do not penalize for omitting index listings, page numbers, or Table of Contents formatting that doesn't fit the schema fields).
- **No Hallucinations (20 points maximum)**: Start with 20. Subtract 5 points for every hallucinated detail that is not in the source text. If there are no hallucinations, award the full 20 points.

Calculation Rule:
The final `accuracy_score` MUST be the exact sum of the points from the three categories: Accuracy + Completeness + No Hallucinations. For example, if there are no errors, no omissions, and no hallucinations, the score is 50 + 30 + 20 = 100.

Return the result in STRICT JSON format:
{
  "accuracy_score": 0,
  "explanation": "State the score for each category (e.g., Accuracy: X/50, Completeness: Y/30, No Hallucinations: Z/20) and calculate the final sum.",
  "hallucinations": [],
  "missing_information": [],
  "confidence": ""
}
"""