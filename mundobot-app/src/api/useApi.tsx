import { useSession } from 'next-auth/react'
import { Configuration } from '@/api/configuration'
import { useMemo } from 'react'
import { DefaultApi, GuildsApi, SoundsApi } from '@/api/api'

export const useApi = () => {
  const { data } = useSession()

  return useMemo(() => {
    const configuration = new Configuration({
      accessToken: data?.accessToken,
      basePath: process.env.NEXT_PUBLIC_API_URL,
      baseOptions: {
        headers: { Authorization: `Bearer ${data?.accessToken}` },
      },
    })

    return {
      api: new DefaultApi(configuration),
      guildsApi: new GuildsApi(configuration),
      soundsApi: new SoundsApi(configuration),
    }
  }, [data?.accessToken])
}
