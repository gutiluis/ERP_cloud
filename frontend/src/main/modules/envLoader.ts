import { config } from 'dotenv' // Dotenv is a zero-dependency module that loads environment variables from a .env file into process.env.
import { resolve } from 'path' // make relative path into an absolute path
import { existsSync } from 'fs'

export function loadEnv() {
  // Determine cuurent envrironment mode: production, development, or fallback. allowing different .env files for dev, staging or prod
  const mode = process.env.NODE_ENV || 'development'

  // Build env file with absolute path
  const envFile = resolve(process.cwd(), `.env.${mode}`)

  // Optional: fallback to default .env if specific file doesn't exist
  const fileToLoad = existsSync(envFile)
    ? envFile
    : resolve(process.cwd(), '.env')

  // not the configuration. load attempt result
  // official dotenv docs use result to load environment variables from the selected file
  const result = config({ path: fileToLoad })

  // login behaviour
  if (result.error) {
    console.warn(`Failed to load env file at ${fileToLoad}. Proceed to use default system environment variables.`
    );
  } else {
    console.log(`Loaded environment variables from ${fileToLoad}`
    );
  }

  const requiredVars = ['VITE_AUTH_URL'];

  for (const key of requiredVars) {
    if (!process.env[key]) {
      throw new Error(`Startup failed: Missing required environment variable: ${key}`);
    }
  }
  // freeze config into a typed object to stop using process.env from dotenv
  return {
    AUTH_URL: process.env.VITE_AUTH_URL as string,
  }
}
