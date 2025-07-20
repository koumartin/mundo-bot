'use client'
import { createContext, PropsWithChildren, useEffect, useState } from 'react'

export type LayoutContextValue = 'desktop' | 'mobile'

export const LayoutContext = createContext<LayoutContextValue>('desktop')
const LayoutProvider = (props: PropsWithChildren) => {
  const [layout, setLayout] = useState<LayoutContextValue>('desktop')

  // Initial setup - can't be direct due to static optimization
  useEffect(() => {
    setLayout(window?.innerWidth >= 960 ? 'desktop' : 'mobile')
  }, [])

  useEffect(() => {
    const handleResize = () => {
      if (layout === 'desktop' && window.innerWidth < 960) {
        setLayout('mobile')
      }
      if (layout === 'mobile' && window.innerWidth >= 960) {
        setLayout('desktop')
      }
    }
    window.addEventListener('resize', handleResize)

    return () => window.removeEventListener('resize', handleResize)
  }, [layout])

  return (
    <LayoutContext.Provider value={layout}>
      {props.children}
    </LayoutContext.Provider>
  )
}

export default LayoutProvider
