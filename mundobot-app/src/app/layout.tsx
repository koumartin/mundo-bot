import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import React from 'react'
import { getServerSession } from 'next-auth'
import { config } from '@/app/api/auth/[...nextauth]/auth'
import { redirect } from 'next/navigation'
import { ClientSessionProvider } from '@/contexts'
import { GuildSelector, ProfileSelector } from '@/components'

import { Menubar } from 'primereact/menubar'

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
  // TODO: Axios interceptors
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientSessionProvider session={session}>
          <nav>
            <span
              style={{
                background: 'var(--secondary)',
                width: '200px',
                height: '100%',
              }}
            >
              LOGO
            </span>
            <Menubar className={'menu-bar'} />
            <GuildSelector />
            <ProfileSelector session={session} />
          </nav>
          <main>{children}</main>
        </ClientSessionProvider>
      </body>
    </html>
  )
}
