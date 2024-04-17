import { auth } from '@/app/api/auth/[...nextauth]/auth'

async function MundoAppRoot() {
  const session = await auth()

  return (
    <div style={{ height: '100%' }}>
      <p>{JSON.stringify(session, null, 2)}</p>
      <p>{process.env.APP_DISCORD_SECRET ?? 'EMPTY'}</p>
    </div>
  )
}

export default MundoAppRoot
