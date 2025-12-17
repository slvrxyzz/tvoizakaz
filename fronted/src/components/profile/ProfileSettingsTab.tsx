import styles from './ProfilePage.module.css'

export function ProfileSettingsTab() {
  return (
    <section className={styles.settingsSection}>
      <div className={styles.tabHeader}>
        <h2 className={styles.tabTitle}>Настройки аккаунта</h2>
      </div>

      <div className={styles.settingsGroup}>
        <h3>Безопасность</h3>
        <div className={styles.settingsList}>
          <button
            type="button"
            className={styles.settingsButton}
            onClick={() => alert('Эта функция ещё в процессе разработки')}
          >
            <span>Сменить пароль</span>
            <span>→</span>
          </button>
          <button type="button" className={styles.settingsButton}>
            <span>Двухфакторная аутентификация</span>
            <span>Не активно</span>
          </button>
        </div>
      </div>

      <div className={styles.settingsGroup}>
        <h3>Уведомления</h3>
        <div className={styles.settingsList}>
          <div className={styles.toggleRow}>
            <span>Email уведомления</span>
            <label className={styles.toggleSwitch}>
              <input type="checkbox" defaultChecked />
              <span className={styles.toggleSlider}></span>
            </label>
          </div>
          <div className={styles.toggleRow}>
            <span>Уведомления о новых заказах</span>
            <label className={styles.toggleSwitch}>
              <input type="checkbox" defaultChecked />
              <span className={styles.toggleSlider}></span>
            </label>
          </div>
        </div>
      </div>

      <div className={styles.settingsGroup}>
        <h3>Аккаунт</h3>
        <div className={styles.settingsList}>
          <button
            type="button"
            className={`${styles.settingsButton} ${styles.settingsButtonDanger}`}
            onClick={() => alert('Эта функция ещё в процессе разработки')}
          >
            <span>Удалить аккаунт</span>
            <span>→</span>
          </button>
        </div>
      </div>
    </section>
  )
}
