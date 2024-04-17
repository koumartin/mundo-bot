'use client'

import Image from 'next/image'
import React, { useRef } from 'react'
import { Session } from 'next-auth'
import { OverlayPanel } from 'primereact/overlaypanel'
import { Avatar } from 'primereact/avatar'
import { auth } from '@/app/api/auth/[...nextauth]/auth'
import { useSession } from 'next-auth/react'

export interface ProfileSelectorProps {
  session: Session | null
}

const ProfileSelector = (props: ProfileSelectorProps) => {
  const { session } = props
  const panelRef = useRef<OverlayPanel>(null)
  const { data } = useSession()
  console.log('PS', data)

  return (
    <>
      <OverlayPanel ref={panelRef}>{session?.user?.name}</OverlayPanel>
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
