'use client'
import { MouseEvent } from 'react'
import styles from './sound.module.scss'

interface SoundBarProps {
  currentTime?: number
  duration?: number
  onTimeChange?: (newTime: number) => void
}

const SoundBar = (props: SoundBarProps) => {
  const { duration, currentTime = 0, onTimeChange } = props

  const handleClick = (e: MouseEvent<HTMLDivElement>) => {
    if (!onTimeChange) return
    const { left, right } = e.currentTarget.getBoundingClientRect()
    const fractionClick = (e.clientX - left) / (right - left)

    onTimeChange((duration ?? 0) * fractionClick)
  }

  const percentage = duration ? (currentTime / duration) * 100 : 0
  return (
    <div className={styles.soundBar} onClick={handleClick}>
      <div className={styles.active} style={{ width: `${percentage}%` }} />
    </div>
  )
}

export default SoundBar
