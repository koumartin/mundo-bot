'use client'

import React, { useCallback, useMemo, useState } from 'react'
import { Menubar } from 'primereact/menubar'
import { MenuItem, MenuItemCommandEvent } from 'primereact/menuitem'
import { useRouter } from 'next/navigation'
import MusicIcon from '@/icons/MusicIcon'
import useLayout from '@/hooks/useLayout'
import { BurgerIcon } from '@/icons/BurgerIcon'
import { Button } from 'primereact/button'
import { Sidebar } from 'primereact/sidebar'
import { Menu } from 'primereact/menu'
import Image from 'next/image'
import Link from 'next/link'

interface NavBarProps {
  className: string
}

const NavBar = (props: NavBarProps) => {
  const { className } = props
  const router = useRouter()
  const layout = useLayout()

  const [sidebarOpened, setSidebarOpened] = useState(false)

  const onClick = useCallback(
    (e: MenuItemCommandEvent) => {
      setSidebarOpened(false)
      router.push('/' + e.item.id)
    },
    [router]
  )

  const items = useMemo((): MenuItem[] => {
    return [
      {
        id: 'sounds',
        label: 'Sounds',
        icon: (props?: { iconProps?: { className: string } }) => (
          <MusicIcon
            width={'1.2rem'}
            height={'1.2rem'}
            className={props?.iconProps?.className}
          />
        ),
        items: [{ id: 'sounds/manage', label: 'Manage', command: onClick }],
      },
    ]
  }, [onClick])

  return (
    <>
      <Link href={'/'} style={{ marginTop: '3px' }}>
        <Image
          src={layout === 'desktop' ? '/logo.png' : '/logo-small.png'}
          alt={'LOGO'}
          width={layout === 'desktop' ? 200 : 120}
          height={50}
        />
      </Link>
      {layout === 'desktop' ? (
        <Menubar model={items} className={className} />
      ) : (
        <div style={{ flexGrow: 1 }}>
          <Button text onClick={() => setSidebarOpened(true)}>
            <BurgerIcon />
          </Button>
          <Sidebar
            onHide={() => setSidebarOpened(false)}
            visible={sidebarOpened}
            position={'left'}
            style={{ width: '60vw' }}
          >
            <Menu model={items} className={className} />
          </Sidebar>
        </div>
      )}
    </>
  )
}

export default NavBar
