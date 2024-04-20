'use client'

import Image from 'next/image'
import React, { useRef } from 'react'
import { Session } from 'next-auth'
import { OverlayPanel } from 'primereact/overlaypanel'
import { Avatar } from 'primereact/avatar'
import { Button } from 'primereact/button'

export interface ProfileSelectorProps {
  session: Session | null
}

const ProfileSelector = (props: ProfileSelectorProps) => {
  const { session } = props
  const panelRef = useRef<OverlayPanel>(null)

  const renderPanel = () => (
    <div>
      {session?.user?.name}
      <Button>Log out</Button>
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
            width={35}
            height={35}
          />
        )}
      </Avatar>
    </>
  )
}

export default ProfileSelector
