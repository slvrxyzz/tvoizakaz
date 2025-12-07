'use client'

import Link from 'next/link'

import styles from './Footer.module.css'

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.content}>
        <div className={styles.section}>
          <h3 className={styles.heading}>Сделано при поддержке</h3>
          <p className={styles.text}>ГБУДО ЦРТ Калининского района</p>
        </div>

        <div className={styles.section}>
          <h3 className={styles.heading}>Контакты</h3>
          <p className={styles.text}>Email: info@teenfreelance.ru</p>
        </div>

        <div className={styles.section}>
          <h3 className={styles.heading}>Соцсети</h3>
          <div className={styles.socials}>
            <Link href="#" className={styles.socialLink}>
              VK
            </Link>
            <Link href="#" className={styles.socialLink}>
              TG
            </Link>
          </div>
        </div>
      </div>

      <div className={styles.bottom}>
        <p className={styles.copyright}>&copy; 2025 TeenFreelance.</p>
      </div>
    </footer>
  )
}