import { useSession } from 'next-auth/react'
import { Configuration } from '@/api/configuration'
import { useMemo } from 'react'
import { DefaultApi } from '@/api/api'

export const useApi = () => {
  const { data } = useSession()

  return useMemo(() => {
    const configuration = new Configuration({ accessToken: data?.accessToken })

    return {
      api: new DefaultApi(configuration),
    }
  }, [data?.accessToken])
}
