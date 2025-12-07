import styles from './CommunityPage.module.css'

export function CommunityHero() {
  return (
    <section className={styles.hero}>
      <div className={styles.container}>
        <h1 className={styles.heroTitle}>Сообщество TeenFreelance</h1>
        <p className={styles.heroSubtitle}>
          Место для общения, обучения и развития вместе с другими фрилансерами
        </p>
      </div>
    </section>
  )
}
