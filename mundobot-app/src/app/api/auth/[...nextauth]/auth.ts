import type {
  GetServerSidePropsContext,
  NextApiRequest,
  NextApiResponse,
} from 'next'
import type { NextAuthOptions } from 'next-auth'
import { getServerSession } from 'next-auth'
import DiscordProvider from 'next-auth/providers/discord'
import { Configuration, LoginApi } from '@/api'

// You'll need to import and pass this
// to `NextAuth` in `app/api/auth/[...nextauth]/route.ts`
export const config = {
  providers: [
    DiscordProvider({
      clientId: process.env.APP_DISCORD_ID as string,
      clientSecret: process.env.APP_DISCORD_SECRET as string,
    }),
  ],
  session: { strategy: 'jwt' },
  callbacks: {
    signIn: async params => {
      console.log('Signin', params)
      return true
    },
    jwt: async ({ account, token }) => {
      if (account && account.access_token) {
        // set access_token to the token payload
        token.accessToken = account.access_token
      }
      return token
    },
    session: async ({ session, token }) => {
      if (!token.accessToken) return session

      const api = new LoginApi(
        new Configuration({ basePath: process.env.NEXT_PUBLIC_API_URL })
      )
      const resp = await api.login(token.accessToken)

      return { ...session, accessToken: resp.data.access_token }
    },
  },
  // rest of your config
} satisfies NextAuthOptions

// Use it in server contexts
export function auth(
  ...args:
    | [GetServerSidePropsContext['req'], GetServerSidePropsContext['res']]
    | [NextApiRequest, NextApiResponse]
    | []
) {
  return getServerSession(...args, config)
}
