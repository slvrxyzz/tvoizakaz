import { ChangeEvent } from 'react'

import { UserProfileResponseDTO } from '@/dto'

import styles from './ProfilePage.module.css'

interface ProfileInfoTabProps {
  user: UserProfileResponseDTO
  editForm: Partial<UserProfileResponseDTO>
  isEditing: boolean
  onEditToggle: (value: boolean) => void
  onChange: (field: keyof UserProfileResponseDTO, value: string) => void
  onSave: () => void
  onCancel: () => void
}

export function ProfileInfoTab({
  user,
  editForm,
  isEditing,
  onEditToggle,
  onChange,
  onSave,
  onCancel,
}: ProfileInfoTabProps) {
  const handleInputChange = (field: keyof UserProfileResponseDTO) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onChange(field, event.target.value)
  }

  return (
    <section>
      <div className={styles.tabHeader}>
        <h2 className={styles.tabTitle}>Основная информация</h2>
        <div className={styles.tabActions}>
          {isEditing ? (
            <>
              <button type="button" className={styles.primaryAction} onClick={onSave}>
                Сохранить
              </button>
              <button type="button" className={styles.secondaryAction} onClick={onCancel}>
                Отмена
              </button>
            </>
          ) : (
            <button type="button" className={styles.primaryAction} onClick={() => onEditToggle(true)}>
              Редактировать
            </button>
          )}
        </div>
      </div>

      <div className={styles.infoGrid}>
        <div className={styles.infoField}>
          <label className={styles.infoLabel}>Имя</label>
          {isEditing ? (
            <input
              className={styles.infoInput}
              type="text"
              value={editForm.name ?? ''}
              onChange={handleInputChange('name')}
            />
          ) : (
            <div className={styles.infoValue}>{user.name}</div>
          )}
        </div>

        <div className={styles.infoField}>
          <label className={styles.infoLabel}>Имя пользователя</label>
          {isEditing ? (
            <input
              className={styles.infoInput}
              type="text"
              value={editForm.nickname ?? ''}
              onChange={handleInputChange('nickname')}
              disabled
            />
          ) : (
            <div className={styles.infoValue}>@{user.nickname}</div>
          )}
        </div>

        <div className={styles.infoField}>
          <label className={styles.infoLabel}>Email</label>
          {isEditing ? (
            <input
              className={styles.infoInput}
              type="email"
              value={editForm.email ?? ''}
              onChange={handleInputChange('email')}
              disabled
            />
          ) : (
            <div className={styles.infoValue}>{user.email}</div>
          )}
        </div>

        <div className={styles.infoField}>
          <label className={styles.infoLabel}>Телефон</label>
          {isEditing ? (
            <input
              className={styles.infoInput}
              type="tel"
              value={editForm.phone_number ?? ''}
              onChange={handleInputChange('phone_number')}
            />
          ) : (
            <div className={styles.infoValue}>{user.phone_number || 'Не указан'}</div>
          )}
        </div>

        <div className={`${styles.infoField} ${styles.infoFieldFull}`}>
          <label className={styles.infoLabel}>О себе</label>
          {isEditing ? (
            <textarea
              className={styles.infoTextarea}
              value={editForm.description ?? ''}
              onChange={handleInputChange('description')}
            />
          ) : (
            <div className={styles.infoValue}>{user.description || 'Информация о себе не добавлена'}</div>
          )}
        </div>
      </div>
    </section>
  )
}
