'use client'

import { Dropdown, DropdownChangeEvent } from 'primereact/dropdown'
import { useEffect, useState } from 'react'
import { useApi } from '@/api/useApi'
import { GuildDto } from '@/api'
import { useCookies } from 'react-cookie'

export interface GuildCookie {
  guild: {
    id: number
    name: string
  }
}

export const GuildSelector = () => {
  const { guildsApi } = useApi()
  const [selectedGuild, setSelectedGuild] = useCookies<'guild', GuildCookie>([
    'guild',
  ])
  const [avalilableServers, setAvailableServers] = useState<GuildDto[]>([])

  useEffect(() => {
    guildsApi.availableGuilds().then(resp => setAvailableServers(resp.data))
  }, [guildsApi])

  const handleChange = (e: DropdownChangeEvent) => {
    setSelectedGuild('guild', { id: e.value, name: null }, { path: '/' })
  }

  return (
    <>
      <span>Selected server:</span>
      <Dropdown
        value={selectedGuild.guild.id}
        onChange={handleChange}
        options={avalilableServers}
        optionValue={'id'}
        optionLabel={'name'}
      />
    </>
  )
}
