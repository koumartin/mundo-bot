import { Dialog, DialogProps } from 'primereact/dialog'
import { InputText } from 'primereact/inputtext'
import {
  FileUpload,
  FileUploadHandlerEvent,
  FileUploadHeaderTemplateOptions,
} from 'primereact/fileupload'

import styles from './soundUploadDialog.module.scss'
import { useApi } from '@/api/useApi'
import { ChangeEvent, useCallback, useRef, useState } from 'react'
import { SoundDto } from '@/api'
import { Button } from 'primereact/button'
import SoundUploadAnimation from './SoundUploadAnimation'
import { Message } from 'primereact/message'

interface SoundUploadDialogProps extends DialogProps {
  onUpload: (newSound: SoundDto) => void
  existingNames: string[]
}

const DEFAULT_NAME_INPUT_VALUE = { value: '', valid: true }

const SoundUploadDialog = (props: SoundUploadDialogProps) => {
  const { visible, onHide, onUpload, existingNames } = props
  const { soundsApi } = useApi()
  const [nameInput, setNameInput] = useState<{ value: string; valid: boolean }>(
    DEFAULT_NAME_INPUT_VALUE
  )
  const [uploaded, setUploaded] = useState(false)
  const [errorText, setErrorText] = useState('')

  const uploadRef = useRef<FileUpload>(null)

  const emptyTemplate = () => {
    return (
      <div className={styles.emptyContent}>
        <i className="pi pi-image"></i>
        <span
          style={{ fontSize: '1.2em', color: 'var(--text-color-secondary)' }}
        >
          Drag and Drop Image Here
        </span>
      </div>
    )
  }

  const headerTemplate = (options: FileUploadHeaderTemplateOptions) => {
    const differentProps = { ...options.chooseButton.props, disabled: true }
    const filePresent = !options.uploadButton.props.disabled
    return (
      // Stupidity to turn off choose button when one element is already present
      <div className={options.className}>
        {filePresent ? <Button {...differentProps} /> : options.chooseButton}
        {options.uploadButton}
        {options.cancelButton}
      </div>
    )
  }

  const isNameValid = (value?: string) => {
    value ??= nameInput.value
    if (value.length === 0) {
      setErrorText('Name is required')
      return false
    } else if (value.length > 30) {
      setErrorText('Name is too long')
      return false
    } else if (existingNames.some(x => x === value)) {
      setErrorText('Name used already')
      return false
    }
    setErrorText('')
    return true
  }

  const handleUpload = async (e: FileUploadHandlerEvent) => {
    // Handle case of not adding name at all
    if (!isNameValid()) {
      setNameInput(prev => ({ ...prev, valid: false }))
      return
    }

    const newSound = await soundsApi.createSound(nameInput.value, e.files[0])
    setNameInput(DEFAULT_NAME_INPUT_VALUE)
    onUpload(newSound.data)
    setUploaded(true)
  }

  const handleNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    setNameInput({
      value: e.currentTarget.value,
      valid: isNameValid(e.currentTarget.value),
    })
  }

  const handlePlayingFinished = useCallback(() => {
    setUploaded(false)
    uploadRef.current?.clear()
    onHide()
  }, [onHide])

  const itemTemplate = (file: object) => {
    return (
      <SoundUploadAnimation
        file={file as File}
        playing={uploaded}
        onPlayingFinished={handlePlayingFinished}
      />
    )
  }

  const renderPanel = () => {
    return (
      <div className={styles.panel}>
        <span className={styles.nameSelect}>
          <label htmlFor={'name'} style={{ marginLeft: '3px' }}>
            Choose sound name:{' '}
          </label>
          <InputText
            id={'name'}
            placeholder={'Name'}
            value={nameInput.value}
            onChange={handleNameChange}
            autoFocus
            invalid={!nameInput.valid}
          />
          {errorText && (
            <Message
              className={styles.errorMessage}
              severity={'error'}
              text={errorText}
            />
          )}
        </span>
        <FileUpload
          ref={uploadRef}
          className={styles.uploadComponent}
          accept={'audio/*'}
          emptyTemplate={emptyTemplate}
          itemTemplate={itemTemplate}
          customUpload
          uploadHandler={handleUpload}
          onBeforeSelect={e => e.files.length <= 0}
          headerTemplate={headerTemplate}
        />
      </div>
    )
  }

  return (
    <Dialog
      visible={visible}
      onHide={() => {
        setNameInput(DEFAULT_NAME_INPUT_VALUE)
        setErrorText('')
        uploadRef.current?.clear()
        onHide()
      }}
      className={styles.dialog}
      header={'Upload new sound'}
    >
      {renderPanel()}
    </Dialog>
  )
}

export default SoundUploadDialog
