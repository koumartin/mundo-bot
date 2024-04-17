'use client'
import { SessionProvider } from 'next-auth/react'
import { PropsWithChildren } from 'react'

const ClientSessionProvider = (props: PropsWithChildren) => {
  return <SessionProvider>{props.children}</SessionProvider>
}

export default ClientSessionProvider
