import type { IncomingMessage, ServerResponse } from "http";
import { tasks } from "@trigger.dev/sdk/v3";

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
 * Serverless API endpoint handler.
 * Listens for POST requests from the client UI containing the target pdfUrl,
 * and uses the Trigger.dev SDK to dispatch the background processing task.
 */
export default async function handler(req: IncomingMessage, res: ServerResponse) {
  // Enforce JSON responses
  res.setHeader("Content-Type", "application/json");

  if (req.method !== "POST") {
    res.statusCode = 405;
    res.end(JSON.stringify({ message: "Method Not Allowed" }));
    return;
  }

  try {
    const body = await readBody(req);
    const pdfUrl = body.pdfUrl;

    console.log(`Dispatched trigger payload target: ${pdfUrl}`);

    // Dispatches task execution to Trigger.dev Cloud using the tasks service client
    const run = await tasks.trigger("process-document-pipeline", {
      pdfUrl
    });

    res.statusCode = 200;
    res.end(
      JSON.stringify({
        runId: run.id,
        dashboardUrl: `https://cloud.trigger.dev/runs/${run.id}`
      })
    );
  } catch (error: any) {
    console.error("Trigger.dev dispatch failed with error:", error);
    res.statusCode = 500;
    res.end(JSON.stringify({ message: error.message || "Internal Server Error" }));
  }
}

