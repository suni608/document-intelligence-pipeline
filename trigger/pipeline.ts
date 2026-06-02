import { task } from "@trigger.dev/sdk/v3";
import { exec } from "child_process";
import path from "path";

// Define schema interface for the incoming trigger payload
interface ProcessDocumentPayload {
  pdfUrl?: string;
}

/**
 * Trigger.dev Background Job.
 * Ingests a payload containing an optional custom pdfUrl, configures environment variables,
 * and executes the Python main pipeline module inside a platform-aware virtual environment subprocess.
 */
export const processDocumentPipeline = task({
  id: "process-document-pipeline",
  run: async (payload: ProcessDocumentPayload, { ctx }) => {
    console.log("Trigger.dev Job process-document-pipeline started.");
    
    return new Promise((resolve, reject) => {
      // Platform detection for executing virtual environments cross-platform (Windows vs Unix)
      const isWindows = process.platform === "win32";
      
      const pythonExe = isWindows ? "python.exe" : "python";
      const venvSubfolder = isWindows ? "Scripts" : "bin";
      const infisicalBin = isWindows ? "infisical.cmd" : "infisical";
      
      const pythonPath = path.resolve(process.cwd(), "venv", venvSubfolder, pythonExe);
      
      // Inherit execution context env and dynamically inject custom PDF target if provided in payload
      const executionEnv = {
        ...process.env,
        PDF_URL: payload.pdfUrl || "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"
      };

      console.log(`Invoking pipeline runner at path: ${pythonPath}`);
      console.log(`Processing URL target: ${executionEnv.PDF_URL}`);

      // Spawns the CLI execution under Infisical to securely retrieve API keys at runtime
      exec(`${infisicalBin} run -- "${pythonPath}" -m app.main`, { env: executionEnv }, (error, stdout, stderr) => {
        if (error) {
          console.error(`Subprocess execution failed with error: ${error.message}`);
          reject(new Error(`Pipeline subprocess crash: ${stderr || error.message}`));
          return;
        }
        
        console.log("Subprocess run completed successfully.");
        resolve({
          status: "success",
          stdout: stdout.trim(),
          stderr: stderr.trim()
        });
      });
    });
  },
});
