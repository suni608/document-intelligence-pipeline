import { task, metadata } from "@trigger.dev/sdk/v3";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";

// Define schema interface for the incoming trigger payload
interface ProcessDocumentPayload {
  pdfUrl?: string;
  pdfBase64?: string;
  filename?: string;
}

/**
 * Trigger.dev Background Job.
 * Ingests a payload containing either a custom pdfUrl or pdfBase64, configures env,
 * and executes the Python main pipeline module inside a virtual environment subprocess.
 */
export const processDocumentPipeline = task({
  id: "process-document-pipeline",
  run: async (payload: ProcessDocumentPayload, { ctx }) => {
    console.log("Trigger.dev Job process-document-pipeline started.");
    
    // Set initial progress metadata state
    metadata.set("progress", { stage: 0, message: "Pipeline initialized. Starting job..." });

    return new Promise((resolve, reject) => {
      // Platform detection for executing virtual environments cross-platform (Windows vs Unix)
      const isWindows = process.platform === "win32";
      
      const pythonExe = isWindows ? "python.exe" : "python";
      const venvSubfolder = isWindows ? "Scripts" : "bin";
      const infisicalBin = isWindows ? "infisical.cmd" : "infisical";
      
      const pythonPath = path.resolve(process.cwd(), "venv", venvSubfolder, pythonExe);
      
      let localPath = "";
      if (payload.pdfBase64) {
        const tempDir = path.resolve(process.cwd(), "sample_data");
        if (!fs.existsSync(tempDir)) {
          fs.mkdirSync(tempDir, { recursive: true });
        }
        localPath = path.resolve(tempDir, "uploaded.pdf");
        fs.writeFileSync(localPath, Buffer.from(payload.pdfBase64, "base64"));
        console.log(`Saved uploaded PDF base64 payload to local path: ${localPath}`);
      }

      // Inherit execution context env and dynamically inject custom PDF target if provided in payload
      const executionEnv = {
        ...process.env,
        PDF_URL: payload.pdfUrl || "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf",
        PDF_LOCAL_PATH: localPath || ""
      };

      console.log(`Invoking pipeline runner at path: ${pythonPath}`);
      if (localPath) {
        console.log(`Processing uploaded PDF file: ${payload.filename || "uploaded.pdf"}`);
      } else {
        console.log(`Processing URL target: ${executionEnv.PDF_URL}`);
      }

      // Determine if we should bypass Infisical (e.g. if ANTHROPIC_API_KEY is already present in execution environment)
      const hasApiKey = !!executionEnv.ANTHROPIC_API_KEY || !!executionEnv.ANTHROPIC_API_KEY; // checks both cases

      console.log(hasApiKey 
        ? "ANTHROPIC_API_KEY detected in environment. Running python script directly (bypassing Infisical)..."
        : "No ANTHROPIC_API_KEY in environment. Spawning under Infisical to retrieve keys..."
      );

      const child = hasApiKey
        ? spawn(pythonPath, ["-m", "app.main"], { env: executionEnv, shell: true })
        : spawn(infisicalBin, ["run", "--", pythonPath, "-m", "app.main"], { env: executionEnv, shell: true });

      let stdoutData = "";
      let stderrData = "";

      child.stdout.on("data", (chunk) => {
        const text = chunk.toString();
        stdoutData += text;
        console.log(text.trim());

        // Parse stage updates from stdout stream
        const lines = text.split("\n");
        for (const line of lines) {
          if (line.includes("[STAGE 01]")) {
            metadata.set("progress", { stage: 1, message: "Fetching/preparing target source PDF document..." });
          } else if (line.includes("[STAGE 02]")) {
            metadata.set("progress", { stage: 2, message: "Extracting plaintext stream from PDF..." });
          } else if (line.includes("[STAGE 03]")) {
            metadata.set("progress", { stage: 3, message: "Structuring extraction & running Pydantic validation..." });
          } else if (line.includes("[STAGE 04]")) {
            metadata.set("progress", { stage: 4, message: "Translating structure to publication Markdown..." });
          } else if (line.includes("[STAGE 05]")) {
            metadata.set("progress", { stage: 5, message: "Initiating self-verification rubric auditor..." });
          }
        }
      });

      child.stderr.on("data", (chunk) => {
        const text = chunk.toString();
        stderrData += text;
        console.error(text.trim());
      });

      child.on("close", (code) => {
        // Cleanup local uploaded file if it exists
        if (localPath && fs.existsSync(localPath)) {
          try {
            fs.unlinkSync(localPath);
            console.log(`Cleaned up temporary file: ${localPath}`);
          } catch (cleanupError) {
            console.error(`Failed to delete temp file ${localPath}:`, cleanupError);
          }
        }

        if (code !== 0) {
          console.error(`Subprocess execution failed with code: ${code}`);
          reject(new Error(`Pipeline subprocess crash: ${stderrData || `Exit code ${code}`}`));
          return;
        }

        console.log("Subprocess run completed successfully. Loading generated output JSON files...");
        
        // Define paths to output files
        const extractedPath = path.resolve(process.cwd(), "outputs", "extracted.json");
        const verificationPath = path.resolve(process.cwd(), "outputs", "verification.json");
        const markdownPath = path.resolve(process.cwd(), "outputs", "result.md");
        
        let extractedData = null;
        let verificationData = null;
        let markdownData = "";

        // Read output files to return them in Trigger.dev dashboard and API
        try {
          if (fs.existsSync(extractedPath)) {
            extractedData = JSON.parse(fs.readFileSync(extractedPath, "utf-8"));
          }
          if (fs.existsSync(verificationPath)) {
            verificationData = JSON.parse(fs.readFileSync(verificationPath, "utf-8"));
          }
          if (fs.existsSync(markdownPath)) {
            markdownData = fs.readFileSync(markdownPath, "utf-8");
          }
        } catch (readError) {
          console.error("Failed to parse output JSON/Markdown files:", readError);
        }

        resolve({
          status: "success",
          extractedData: extractedData,
          verificationData: verificationData,
          markdownData: markdownData
        });
      });
    });
  },
});
