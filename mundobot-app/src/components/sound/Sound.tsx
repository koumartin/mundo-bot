'use client'

import { SyntheticEvent, useEffect, useRef, useState } from 'react'
import { useApi } from '@/api/useApi'

import styles from './sound.module.scss'
import { Button } from 'primereact/button'
import { saveAs } from 'file-saver'
import { Duration } from 'luxon'
import { SoundDto } from '@/api'
import SoundBar from '@/components/sound/SoundBar'

export interface SoundProps {
  sound: SoundDto
  onDelete: (name: string) => void
}

interface SoundState {
  src?: string | null
  showing: boolean
  playing?: boolean
  duration?: number
  currentTime?: number
}

const Sound = (props: SoundProps) => {
  const {
    sound: { name, default: def },
    onDelete,
  } = props
  const [audioState, setAudioState] = useState<SoundState>({ showing: false })
  const { soundsApi } = useApi()
  const audioRef = useRef<HTMLAudioElement>(null)

  const prepareUrl = async () => {
    try {
      const soundData = await soundsApi.getSound(name, {
        responseType: 'blob',
      })
      return URL.createObjectURL(soundData.data)
    } catch (e) {
      console.log(e)
    }
  }

  const handlePlay = async () => {
    // Already have all data and player is visible
    if (audioState.src && audioState.showing) {
      if (audioState.playing) audioRef.current?.pause()
      else await audioRef.current?.play()
      return
    }
    // Data was downloaded through download button, only show player
    if (audioState.src && !audioState.showing) {
      setAudioState(prev => ({ ...prev, showing: true }))
      return
    }

    // Download first
    const url = await prepareUrl()
    if (url) {
      setAudioState({ src: url, currentTime: 0, showing: true })
    }
  }

  const handleDownload = async () => {
    let url
    if (!audioState.src) {
      url = await prepareUrl()
      if (url) {
        setAudioState({ src: url, currentTime: 0, showing: false })
      } else {
        return
      }
    } else {
      url = audioState.src
    }

    saveAs(await fetch(url).then(r => r.blob()), `${name}.mp3`)
  }

  useEffect(() => {
    if (audioState.playing) {
      const interval = setInterval(
        () =>
          setAudioState(prevState => ({
            ...prevState,
            currentTime: audioRef.current?.currentTime,
          })),
        50
      )
      return () => clearInterval(interval)
    }
  })

  const renderDuration = () => {
    const currDuration = Duration.fromDurationLike({
      second: audioState.currentTime ?? 0,
    })

    const durationDuration = Duration.fromDurationLike({
      second: audioState.duration ?? 0,
    })

    return (
      <span
        className={styles.duration}
      >{`${currDuration.toFormat('mm:ss')} / ${durationDuration.toFormat('mm:ss')}`}</span>
    )
  }

  return (
    <div className={styles.sound}>
      <span className={styles.name}>{name}</span>
      <Button
        icon={audioState.playing ? 'pi pi-pause' : 'pi pi-play'}
        onClick={handlePlay}
        rounded
        text
      />
      {audioState.src && audioState.showing && (
        <>
          <audio
            src={audioState.src}
            ref={audioRef}
            onPlay={() =>
              setAudioState(prevState => ({ ...prevState, playing: true }))
            }
            onPause={() => {
              setAudioState(prevState => ({
                ...prevState,
                playing: false,
                currentTime: audioRef.current?.currentTime,
              }))
            }}
            onEnded={() => {
              setAudioState(prevState => ({
                ...prevState,
                playing: false,
                currentTime: prevState.duration,
              }))
            }}
            onLoadedMetadata={(e: SyntheticEvent<HTMLAudioElement>) => {
              const duration = e.currentTarget?.duration
              setAudioState(prev => ({
                ...prev,
                duration: duration,
              }))
            }}
          />
          <SoundBar
            duration={audioState.duration}
            currentTime={audioState.currentTime}
            onTimeChange={newTime => {
              if (!audioState.playing) {
                setAudioState(prev => ({ ...prev, currentTime: newTime }))
                if (audioRef.current) audioRef.current.currentTime = newTime
              }
            }}
          />
          {renderDuration()}
        </>
      )}
      {!audioState.showing && <div style={{ flexGrow: 1 }} />}
      {!def && (
        <Button
          icon={'pi pi-times'}
          onClick={() => onDelete(name)}
          rounded
          text
        />
      )}
      <Button icon={'pi pi-download'} onClick={handleDownload} rounded text />
    </div>
  )
}

export default Sound
