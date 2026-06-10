import { defineConfig } from "@trigger.dev/sdk/v3";
import { pythonExtension } from "@trigger.dev/python/extension";

export default defineConfig({
  // Your actual Trigger.dev project ID from the dashboard
  project: "proj_hrdjzjfczpetcjmdbbxf",
  runtime: "node",
  logLevel: "log",
  // Tells Trigger.dev to look for files defining background jobs under the /trigger directory
  dirs: ["trigger"],
  // Max duration (in seconds) that any run is allowed to execute for
  maxDuration: 300,
  build: {
    extensions: [
      pythonExtension({
        requirementsFile: "./requirements.txt",
        scripts: ["app/**/*.py"],
      }),
    ],
  },
});


