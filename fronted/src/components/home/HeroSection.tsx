import Link from 'next/link'

import styles from './HomeSections.module.css'

interface HeroSectionProps {
  title: string
  subtitle: string
  ctaLabel: string
  ctaHref: string
}

export function HeroSection({ title, subtitle, ctaLabel, ctaHref }: HeroSectionProps) {
  return (
    <section className={styles.heroSection}>
      <div className={styles.heroContent}>
        <h1 className={styles.heroTitle}>{title}</h1>
        <p className={styles.heroSubtitle}>{subtitle}</p>
        <Link href={ctaHref} className={styles.heroCta}>
          {ctaLabel}
        </Link>
      </div>
    </section>
  )
}

