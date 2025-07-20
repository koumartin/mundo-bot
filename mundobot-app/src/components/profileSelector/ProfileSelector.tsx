'use client'

import Image from 'next/image'
import React, { useRef } from 'react'
import { Session } from 'next-auth'
import { OverlayPanel } from 'primereact/overlaypanel'
import { Avatar } from 'primereact/avatar'
import { Button } from 'primereact/button'
import { signOut } from 'next-auth/react'

export interface ProfileSelectorProps {
  session: Session | null
}

const ProfileSelector = (props: ProfileSelectorProps) => {
  const { session } = props
  const panelRef = useRef<OverlayPanel>(null)

  const handleLogout = async () => {
    await signOut()
  }

  const renderPanel = () => (
    <div style={{ display: 'flex', flexFlow: 'column' }}>
      <span>{session?.user?.name}</span>
      <Button onClick={handleLogout}>Log out</Button>
    </div>
  )

  return (
    <>
      <OverlayPanel ref={panelRef}>{renderPanel()}</OverlayPanel>
      <Avatar onClick={e => panelRef.current?.toggle(e)}>
        {session?.user?.image && (
          <Image
            src={session.user.image}
            alt={'profile-picture'}
            width={40}
            height={40}
            priority={true}
          />
        )}
      </Avatar>
    </>
  )
}

export default ProfileSelector
