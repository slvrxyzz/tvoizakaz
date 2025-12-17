'use client'

import { useState } from 'react'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/contacts/ContactsPage.module.css'

const CONTACT_ITEMS = [
  { title: 'Адрес', text: '195267, г. Санкт-Петербург, ул. Ушинского, д. 6, литера А' },
  { title: 'Телефон 1', text: '+7 952 214-88-77' },
  { title: 'Телефон 2', text: '+7 931 343-42-03' },
  { title: 'Email 1', text: 'yaroslav@yanilov.ru' },
  { title: 'Email 2', text: 'lavrinenko.roman.217@mail.ru' },
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

      </main>

      <Footer />
    </>
  )
}