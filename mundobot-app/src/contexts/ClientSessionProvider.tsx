'use client'
import { SessionProvider } from 'next-auth/react'
import React, { PropsWithChildren, useEffect, useRef } from 'react'
import { Session } from 'next-auth'
import { CookiesProvider } from 'react-cookie'
import { Toast } from 'primereact/toast'
import globalAxios from 'axios'

export interface ClientSessionProviderProps extends PropsWithChildren {
  session: Session
}

export const ClientSessionProvider = (props: ClientSessionProviderProps) => {
  const toastRef = useRef<Toast>(null)

  useEffect(() => {
    globalAxios.interceptors.response.use(
      response => response,
      error => {
        toastRef.current?.show({
          summary: error.response?.status,
          severity: 'error',
        })
      }
    )
  }, [])

  return (
    <SessionProvider session={props.session}>
      <CookiesProvider>
        <Toast ref={toastRef} position={'top-right'} />
        {props.session ? props.children : <div>LOADING SESSION</div>}
      </CookiesProvider>
    </SessionProvider>
  )
}
