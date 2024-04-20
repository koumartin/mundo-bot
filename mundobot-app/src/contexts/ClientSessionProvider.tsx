'use client'
import { SessionProvider } from 'next-auth/react'
import { PropsWithChildren } from 'react'
import { Session } from 'next-auth'
import { CookiesProvider } from 'react-cookie'

export interface ClientSessionProviderProps extends PropsWithChildren {
  session: Session
}

export const ClientSessionProvider = (props: ClientSessionProviderProps) => {
  console.log(props.session)
  return (
    <SessionProvider session={props.session}>
      <CookiesProvider>
        {props.session ? props.children : <div>LOADING SESSION</div>}
      </CookiesProvider>
    </SessionProvider>
  )
}
