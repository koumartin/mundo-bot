async function Loading() {
  return (
    <div style={{ display: 'flex', flexFlow: 'row', alignItems: 'center' }}>
      <p style={{ fontSize: '2rem', marginLeft: '1rem' }}>LOADING</p>
      <div
        className={'pi pi-spinner pi-spin'}
        style={{ marginLeft: '1rem', scale: 1.5 }}
      />
    </div>
  )
}
export default Loading
