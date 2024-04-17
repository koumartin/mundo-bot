import { getServerSession } from 'next-auth'
import { config } from '@/app/api/auth/[...nextauth]/auth'
import { getSession } from 'next-auth/react'
import { getToken } from 'next-auth/jwt'

const Sounds = async () => {
  const session = await getServerSession(config)
  const s = await getSession()

  return (
    <>
      <p>SOUNDS</p>
      <p>{JSON.stringify(session, null, 2)}</p>
      <p>{JSON.stringify(s, null, 2)}</p>
    </>
  )
}

export default Sounds
