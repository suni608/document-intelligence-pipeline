import type { IncomingMessage, ServerResponse } from "http";
import { runs } from "@trigger.dev/sdk/v3";
import { parse } from "url";

/**
 * Serverless API endpoint handler.
 * Listens for GET requests from the client UI containing the target runId query parameter,
 * and calls the Trigger.dev SDK to retrieve current run execution details.
 */
export default async function handler(req: IncomingMessage, res: ServerResponse) {
  // Enforce JSON responses
  res.setHeader("Content-Type", "application/json");

  if (req.method !== "GET") {
    res.statusCode = 405;
    res.end(JSON.stringify({ message: "Method Not Allowed" }));
    return;
  }

  try {
    const { query } = parse(req.url || "", true);
    const runId = query.runId as string;

    if (!runId) {
      res.statusCode = 400;
      res.end(JSON.stringify({ message: "runId parameter is required" }));
      return;
    }

    console.log(`Polling status for run ID: ${runId}`);
    
    // Retrieve run information from Trigger.dev Cloud
    const run = await runs.retrieve(runId);

    // Prepare safe output response payload
    res.statusCode = 200;
    res.end(
      JSON.stringify({
        status: run.status,
        metadata: run.metadata || {},
        output: run.output || null,
        error: run.error || null,
      })
    );
  } catch (error: any) {
    console.error("Trigger.dev status retrieval failed with error:", error);
    res.statusCode = 500;
    res.end(JSON.stringify({ message: error.message || "Internal Server Error" }));
  }
}
