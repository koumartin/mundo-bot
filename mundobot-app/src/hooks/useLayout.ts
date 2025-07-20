import { useContext } from 'react'
import { LayoutContext } from '@/contexts'

const useLayout = () => {
  return useContext(LayoutContext)
}

export default useLayout
