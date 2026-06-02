import { defineConfig } from "@trigger.dev/sdk/v3";

export default defineConfig({
  // Replace this with your actual Trigger.dev project ID / reference from the dashboard
  project: "document-intelligence-pipeline",
  runtime: "node",
  logLevel: "log",
  // Tells Trigger.dev to look for files defining background jobs under the /trigger directory
  dirs: ["trigger"],
});
