'use client'
import { SessionProvider } from 'next-auth/react'
import React, { PropsWithChildren, useEffect, useRef } from 'react'
import { Session } from 'next-auth'
import { CookiesProvider } from 'react-cookie'
import { Toast } from 'primereact/toast'
import globalAxios, { isCancel } from 'axios'
import LayoutProvider from '@/contexts/LayoutProvider'

export interface ClientSessionProviderProps extends PropsWithChildren {
  session: Session
}

export const ClientSessionProvider = (props: ClientSessionProviderProps) => {
  const toastRef = useRef<Toast>(null)

  useEffect(() => {
    globalAxios.interceptors.response.use(
      response => response,
      error => {
        // To prevent showing message for cancellation - that leads to showing both offline and error message
        if (isCancel(error)) throw error

        const summary = error.response
          ? error.response.status
          : 'Something went wrong'
        toastRef.current?.show({
          summary: summary,
          severity: 'error',
        })
        throw new Error(summary)
      }
    )

    globalAxios.interceptors.request.use(async config => {
      if (navigator.onLine) return config

      const controller = new AbortController()
      controller.abort()
      toastRef.current?.show({
        summary: 'You are offline',
        severity: 'error',
      })
      return { ...config, signal: controller.signal }
    })

    return () => {
      globalAxios.interceptors.request.clear()
      globalAxios.interceptors.response.clear()
    }
  }, [])

  return (
    <SessionProvider session={props.session}>
      <CookiesProvider>
        <LayoutProvider>
          <Toast ref={toastRef} position={'top-right'} />
          {props.session ? props.children : <div>LOADING SESSION</div>}
        </LayoutProvider>
      </CookiesProvider>
    </SessionProvider>
  )
}
