import styles from './CommunityPage.module.css'

const steps = [
  {
    title: 'Профориентационный тест',
    description: 'Пройдите комплексный тест для определения ваших склонностей',
  },
  {
    title: 'Анализ результатов',
    description: 'Получите детальный разбор ваших сильных сторон',
  },
  {
    title: 'Рекомендации',
    description: 'Подберем подходящие направления и курсы для развития',
  },
]

export function CareerGuide() {
  return (
    <section className={styles.careerGuide}>
      <header className={styles.careerHero}>
        <h2>Найди свой путь в фрилансе</h2>
        <p>Поможем определить ваши сильные стороны и выбрать подходящее направление</p>
      </header>

      <div className={styles.careerSteps}>
        {steps.map((step, index) => (
          <article key={step.title} className={styles.careerStep}>
            <div className={styles.stepNumber}>{index + 1}</div>
            <h3 className={styles.careerStepTitle}>{step.title}</h3>
            <p className={styles.careerStepText}>{step.description}</p>
          </article>
        ))}
      </div>

      <div className={styles.careerCTA}>
        <button
          type="button"
          className={styles.ctaButton}
          onClick={() => alert('Эта функция ещё в процессе разработки')}
        >
          Начать профориентацию
        </button>
        <p className={styles.ctaNote}>Бесплатно • 20–25 минут</p>
      </div>
    </section>
  )
}
