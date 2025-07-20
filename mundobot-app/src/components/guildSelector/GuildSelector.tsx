'use client'

import { Dropdown, DropdownChangeEvent } from 'primereact/dropdown'
import { useEffect, useState } from 'react'
import { useApi } from '@/api/useApi'
import { GuildDto } from '@/api'
import { useCookies } from 'react-cookie'

import styles from './guildSelector.module.scss'

export interface GuildCookieValue {
  id: number
  name: string
}

export interface GuildCookie {
  guild: GuildCookieValue
}

const GuildSelector = () => {
  const { guildsApi } = useApi()
  const [selectedGuildCookie, setSelectedGuild] = useCookies<
    'guild',
    GuildCookie
  >(['guild'])
  const [avalilableServers, setAvailableServers] = useState<GuildDto[]>([])
  const [value, setValue] = useState<number | null>(null)

  useEffect(() => {
    guildsApi.availableGuilds().then(resp => setAvailableServers(resp.data))
  }, [guildsApi])

  useEffect(() => {
    setValue(selectedGuildCookie?.guild?.id)
  }, [selectedGuildCookie?.guild?.id])

  const handleChange = (e: DropdownChangeEvent) => {
    setSelectedGuild(
      'guild',
      {
        id: e.value,
        name: avalilableServers.find(x => x.id === e.value)?.name,
      },
      { path: '/', maxAge: 2147483647 }
    )
  }

  // TODO: Dropdown should show loading until it is hydrated - probably using next/dynamic
  return (
    <div className={styles.guildSelector}>
      <span>Selected server:</span>
      <Dropdown
        value={value}
        onChange={handleChange}
        options={avalilableServers}
        optionValue={'id'}
        optionLabel={'name'}
      />
    </div>
  )
}

export default GuildSelector
