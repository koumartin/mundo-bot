import { useSession } from 'next-auth/react'
import { Configuration } from '@/api/configuration'
import { useMemo } from 'react'
import { DefaultApi, GuildsApi, SoundsApi } from '@/api/api'
import { useCookies } from 'react-cookie'
import { GuildCookie } from '@/components/guildSelector/GuildSelector'

export const useApi = () => {
  const { data } = useSession()
  const [selectedGuild] = useCookies<'guild', GuildCookie>(['guild'])

  return useMemo(() => {
    const configuration = new Configuration({
      accessToken: data?.accessToken,
      basePath: process.env.NEXT_PUBLIC_API_URL,
      baseOptions: {
        headers: {
          Authorization: `Bearer ${data?.accessToken}`,
          'Guild-Id': selectedGuild?.guild?.id,
        },
      },
    })

    return {
      api: new DefaultApi(configuration),
      guildsApi: new GuildsApi(configuration),
      soundsApi: new SoundsApi(configuration),
    }
  }, [data?.accessToken, selectedGuild?.guild?.id])
}
