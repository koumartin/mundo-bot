'use client'

import { useCookies } from 'react-cookie'
import { GuildCookie } from '@/components/GuildSelector'

const Sounds = () => {
  const [selectedGuild] = useCookies<'guild', GuildCookie>(['guild'])

  console.log(selectedGuild)
  if (!selectedGuild?.guild?.id) return <>Please select server</>
  console.log('AAAA')
  return (
    <>
      <p>SOUNDS</p>
    </>
  )
}

export default Sounds
