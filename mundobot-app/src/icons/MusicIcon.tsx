const MusicIcon = (props: {
  width: string
  height: string
  className?: string
}) => {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      className={props.className}
      fill={'currentColor'}
      viewBox={'0 0 100 100'}
      preserveAspectRatio={'xMidYMid'}
    >
      <ellipse cx={'20%'} cy={'80%'} rx={20} ry={12} />
      <ellipse cx={'80%'} cy={'72%'} rx={20} ry={12} />
      <rect
        x={'30%'}
        y={'5%'}
        rx={2}
        width={10}
        height={70}
        strokeLinecap={'round'}
      />
      <rect
        x={'90%'}
        y={'5%'}
        rx={2}
        width={10}
        height={62}
        strokeLinecap={'round'}
      />
      <rect x={'40%'} y={'5%'} width={'50%'} height={20} />
    </svg>
  )
}

export default MusicIcon
