'use client'

import { useState } from 'react'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/contacts/ContactsPage.module.css'

const CONTACT_ITEMS = [
  { title: 'Адрес', text: 'г. Москва, ул. Примерная, д. 123' },
  { title: 'Телефон', text: '+7 (999) 123-45-67' },
  { title: 'Email', text: 'info@teenfreelance.ru' },
  { title: 'Режим работы', text: 'Пн-Пт: 9:00 – 18:00' },
]

export default function ContactsPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  })

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    console.log('Form submitted:', formData)
  }

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.heroSection}>
          <h1 className={styles.title}>Свяжитесь с нами</h1>
        </div>
        
        <section className={styles.section}>
          <div className={styles.layout}>
            <div className={styles.infoList}>
              {CONTACT_ITEMS.map((item) => (
                <article key={item.title} className={styles.infoCard}>
                  <h3 className={styles.infoTitle}>{item.title}</h3>
                  <p className={styles.infoText}>{item.text}</p>
                </article>
              ))}
            </div>

            <div className={styles.formCard}>
              <h3 className={styles.formTitle}>Форма обратной связи</h3>
              <form onSubmit={handleSubmit} className={styles.form}>
                <div className={styles.field}>
                  <input
                    className={styles.input}
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Ваше имя"
                    required
                  />
                </div>

                <div className={styles.field}>
                  <input
                    className={styles.input}
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="Ваш email"
                    required
                  />
                </div>

                <div className={styles.field}>
                  <textarea
                    className={styles.textarea}
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    placeholder="Ваше сообщение"
                    required
                  />
                </div>

                <button type="submit" className={styles.submit}>
                  Отправить сообщение
                </button>
              </form>
            </div>
          </div>
        </section>

        <section className={styles.mapSection}>
          <div className={styles.mapPlaceholder}>
            <p className={styles.mapText}>Карта будет отображаться здесь</p>
          </div>
        </section>
      </main>

      <Footer />
    </>
  )
}