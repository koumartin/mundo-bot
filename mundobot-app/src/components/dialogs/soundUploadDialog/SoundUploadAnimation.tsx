import { useCallback, useEffect, useState } from 'react'
import MusicIcon from '@/icons/MusicIcon'

import styles from './soundUploadDialog.module.scss'
import Image from 'next/image'

interface SoundUploadedAnimationProps {
  file: File
  playing: boolean
  onPlayingFinished: () => void
}

const SoundUploadAnimation = (props: SoundUploadedAnimationProps) => {
  const { file, playing, onPlayingFinished } = props

  const [audio, setAudio] = useState<HTMLAudioElement | null>(null)
  const [started, setStarted] = useState(false)

  const humanFileSize = (size: number) => {
    const i = size == 0 ? 0 : Math.floor(Math.log(size) / Math.log(1024))
    return (
      +(size / Math.pow(1024, i)).toFixed(2) +
      ' ' +
      ['B', 'kB', 'MB', 'GB', 'TB'][i]
    )
  }

  const onMusicFinished = useCallback(() => {
    setStarted(false)
    onPlayingFinished()
  }, [onPlayingFinished])

  useEffect(() => {
    if (started) return

    const audioUrl = URL.createObjectURL(file)
    const audio = new Audio(audioUrl)
    audio.onended = onMusicFinished
    audio.onprogress = () => {
      if (audio.currentTime > 5) {
        audio.pause()
        onMusicFinished()
      }
    }
    setAudio(audio)
  }, [file, onMusicFinished, onPlayingFinished, started])

  useEffect(() => {
    if (started || !playing) return
    else setStarted(true)

    setTimeout(() => {
      console.log(audio)
      audio?.play().then()
    }, 5000)
  }, [audio, playing, started])

  return (
    <div
      className={`${styles.animationSpace} ${started ? styles.animating : ''}`}
    >
      <div className={styles.face}>
        <Image
          src={'/mundo-face-upper.jpg'}
          width={333 * 0.75}
          height={215 * 0.75}
          alt={''}
          className={styles.faceUpper}
        />
        <Image
          src={'/mundo-face-lower.jpg'}
          width={333 * 0.75}
          height={118 * 0.75}
          alt={''}
          className={styles.faceLower}
        />
      </div>
      <div className={styles.faceInside} />
      <div className={styles.music}>
        <span className={styles.fileInfo}>
          <b>{file.name}</b>
          <br />
          {humanFileSize(file.size)}
        </span>
        <MusicIcon width={'80'} height={'80'} className={styles.musicIcon} />
      </div>
    </div>
  )
}

export default SoundUploadAnimation
