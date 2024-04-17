import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import React from 'react'
import { getServerSession } from 'next-auth'
import { config } from '@/app/api/auth/[...nextauth]/auth'
import { redirect } from 'next/navigation'
import ProfileSelector from '@/components/ProfileSelector'

import './app.scss'
import 'primereact/resources/themes/md-dark-indigo/theme.css'
import ClientSessionProvider from '@/contexts/ClientSessionProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MundoBot',
  description: 'Mundo Bot control panel',
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const session = await getServerSession(config)
  if (!session) {
    redirect('/api/auth/signin')
  }

  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientSessionProvider>
          <nav>
            <span>TODO: MUNDOBOT LOGO</span>
            <div style={{ flexGrow: 1 }} />
            <ProfileSelector session={session} />
          </nav>
          <main>{children}</main>
        </ClientSessionProvider>
      </body>
    </html>
  )
}
