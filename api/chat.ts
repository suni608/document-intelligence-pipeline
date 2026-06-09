import type { IncomingMessage, ServerResponse } from "http";
import { parse } from "url";

// Helper utility to buffer and parse JSON body payload from incoming streams
async function readBody(req: IncomingMessage): Promise<any> {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        resolve(JSON.parse(body));
      } catch (e) {
        resolve({});
      }
    });
    req.on("error", reject);
  });
}

/**
 * Serverless API endpoint handler for Q&A chatbot.
 * Expects a POST request with { question: string, context: string }.
 * Uses native fetch to query the Anthropic API.
 */
export default async function handler(req: IncomingMessage, res: ServerResponse) {
  res.setHeader("Content-Type", "application/json");

  if (req.method !== "POST") {
    res.statusCode = 405;
    res.end(JSON.stringify({ message: "Method Not Allowed" }));
    return;
  }

  try {
    const body = await readBody(req);
    const { question, context } = body;

    if (!question || !context) {
      res.statusCode = 400;
      res.end(JSON.stringify({ message: "Both 'question' and 'context' parameters are required" }));
      return;
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      res.statusCode = 500;
      res.end(JSON.stringify({ message: "ANTHROPIC_API_KEY is not configured in the server environment" }));
      return;
    }

    console.log(`Processing chatbot query. Context size: ${context.length} characters.`);

    // Perform direct HTTP post fetch to Anthropic API to keep deployment package small
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 800,
        temperature: 0.2,
        system: "You are a precise, helpful assistant. Answer the user's question about the provided document. Rely ONLY on the text inside <DocumentContext> tags. If you cannot find the answer to the question in the document, say: 'I cannot find the answer to this question in the provided document.' Do not make up facts or extrapolate beyond the text.",
        messages: [
          {
            role: "user",
            content: `<DocumentContext>\n${context}\n</DocumentContext>\n\nQuestion: ${question}`
          }
        ]
      })
    });

    if (!response.ok) {
      const errDetails = await response.text();
      throw new Error(`Anthropic API returned status ${response.status}: ${errDetails}`);
    }

    const data: any = await response.json();
    const answer = data.content?.[0]?.text || "Sorry, I could not generate an answer.";

    res.statusCode = 200;
    res.end(JSON.stringify({ answer }));
  } catch (error: any) {
    console.error("Chatbot assistant failed with error:", error);
    res.statusCode = 500;
    res.end(JSON.stringify({ message: error.message || "Internal Server Error" }));
  }
}
