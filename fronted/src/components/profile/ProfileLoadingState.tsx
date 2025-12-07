import styles from './ProfilePage.module.css'

export function ProfileLoadingState({ message = 'Загрузка профиля...' }: { message?: string }) {
  return (
    <div className={styles.loadingWrapper}>
      <div className={styles.loadingSpinner}></div>
      <p>{message}</p>
    </div>
  )
}
