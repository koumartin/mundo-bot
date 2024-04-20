import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import React from 'react'
import { getServerSession } from 'next-auth'
import { config } from '@/app/api/auth/[...nextauth]/auth'
import { redirect } from 'next/navigation'
import ProfileSelector from '@/components/ProfileSelector'
import { ClientSessionProvider, SelectedGuildProvider } from '@/contexts'

import './app.scss'
import 'primereact/resources/themes/md-dark-indigo/theme.css'
import { GuildSelector } from '@/components/GuildSelector'

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
        <ClientSessionProvider session={session}>
          <nav>
            <span>TODO: MUNDOBOT LOGO</span>
            <div style={{ flexGrow: 1 }} />
            <GuildSelector />
            <ProfileSelector session={session} />
          </nav>
          <main>{children}</main>
        </ClientSessionProvider>
      </body>
    </html>
  )
}
