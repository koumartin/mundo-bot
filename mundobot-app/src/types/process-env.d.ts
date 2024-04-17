/* eslint-disable no-unused-vars */
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      API_URL: string
      APP_DISCORD_ID: string
      APP_DISCORD_SECRET: string
      [key: string]: string | undefined
    }
  }
}
