'use client'

import { useCookies } from 'react-cookie'
import {
  GuildCookie,
  GuildCookieValue,
} from '@/components/guildSelector/GuildSelector'
import { useCallback, useEffect, useState } from 'react'
import { useApi } from '@/api/useApi'
import { Sound } from '@/components'

import styles from './sounds.module.scss'
import { Button } from 'primereact/button'
import { SoundUploadDialog } from '@/components/dialogs'
import { SoundDto } from '@/api'
import Loading from '@/components/loading/Loading'

const Sounds = () => {
  const [selectedGuild] = useCookies<'guild', GuildCookie>(['guild'])
  const [selectedGuildValue, setSelectedGuildValue] =
    useState<GuildCookieValue | null>(null)
  const [sounds, setSounds] = useState<SoundDto[]>([])
  const [dialogVisible, setDialogVisible] = useState<boolean>(false)

  const { soundsApi } = useApi()

  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    // This has to be done to allow for hydration of this component (can't depend on browser features during initial render)
    setSelectedGuildValue(selectedGuild?.guild)
  }, [selectedGuild?.guild])

  useEffect(() => {
    soundsApi.listSounds().then(res => setSounds(res.data))
  }, [soundsApi])

  const handleDelete = useCallback(
    async (name: string) => {
      await soundsApi.deleteSound(name)
      setSounds(prev => prev.filter(s => s.name != name))
    },
    [soundsApi]
  )

  if (!mounted) return <Loading />

  if (!selectedGuildValue)
    return <p className={styles.aaaa}>Please select server</p>

  return (
    <div>
      <SoundUploadDialog
        onHide={() => setDialogVisible(false)}
        visible={dialogVisible}
        onUpload={newSound => setSounds(prev => [...prev, newSound])}
      />
      <div className={styles.header}>
        <span>
          Sounds for the server <strong>{selectedGuildValue.name}</strong> are:
        </span>
        <Button
          icon={'pi pi-plus'}
          label={'Add'}
          onClick={() => setDialogVisible(true)}
        />
      </div>
      <div className={styles.soundsList}>
        {sounds.map(s => (
          <Sound sound={s} key={s.name} onDelete={handleDelete} />
        ))}
      </div>
    </div>
  )
}

export default Sounds
