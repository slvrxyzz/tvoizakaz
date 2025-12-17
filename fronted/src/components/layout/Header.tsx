'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import { CategoryDTO, SearchResultDTO, UserSearchResultDTO } from '@/dto'
import { useAuth } from '@/providers/AuthProvider'
import { apiClient } from '@/utils/apiClient'
import { isDevMode } from '@/utils/config'

import styles from './Header.module.css'

interface SearchResult {
  id: string
  name: string
  type: 'order' | 'user' | 'category'
}

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [showAccountDropdown, setShowAccountDropdown] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false)
  const dropdownTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  const { user, isAuthenticated, logout } = useAuth()

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false)
    setMobileSearchOpen(false)
  }, [router])

  // Focus search input when mobile search opens
  useEffect(() => {
    if (mobileSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [mobileSearchOpen])

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([])
      return
    }

    const abortController = new AbortController()

    const fetchSearch = async () => {
      try {
        const data = await apiClient.get<{
          orders: SearchResultDTO[]
          users: UserSearchResultDTO[]
          categories: CategoryDTO[]
        }>('/search/', { q: searchQuery, limit: 5 })

        const results: SearchResult[] = [
          ...data.orders.map((order) => ({ id: String(order.id), name: order.title, type: 'order' as const })),
          ...data.users.map((resultUser) => ({ id: String(resultUser.id), name: resultUser.name, type: 'user' as const })),
          ...data.categories.map((category) => ({ id: String(category.id), name: category.name, type: 'category' as const })),
        ].slice(0, 5)

        if (!abortController.signal.aborted) {
          setSearchResults(results)
        }
      } catch (error) {
        if (!abortController.signal.aborted) {
          console.warn('Search error:', error)
          setSearchResults([])
        }
      }
    }

    fetchSearch()

    return () => abortController.abort()
  }, [searchQuery])

  const handleLogout = async () => {
    try {
      await logout()
      setShowAccountDropdown(false)
      router.push('/')
    } catch (error) {
      console.warn('Logout error:', error)
    }
  }

  const handleAccountMouseEnter = () => {
    if (dropdownTimeoutRef.current) {
      clearTimeout(dropdownTimeoutRef.current)
    }
    setShowAccountDropdown(true)
  }

  const handleAccountMouseLeave = () => {
    dropdownTimeoutRef.current = setTimeout(() => {
      setShowAccountDropdown(false)
    }, 200)
  }

  const handleSearchResultClick = (result: SearchResult) => {
    if (result.type === 'order') {
      router.push(`/orders/${result.id}`)
    } else if (result.type === 'user') {
      router.push(`/users/${result.id}`)
    } else {
      router.push(`/orders?category=${result.id}`)
    }

    setSearchQuery('')
    setSearchResults([])
    setMobileSearchOpen(false)
  }

  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <>
      <header className={styles.header}>
        <nav className={styles.navbar}>
          {/* Logo */}
          <Link href="/" className={styles.logo}>
            <span className={styles.logoIcon}>ТЗ</span>
            <span className={styles.logoText}>ТвойЗаказ</span>
          </Link>

          {/* Desktop navigation */}
          <div className={styles.navCenter}>
            <ul className={styles.navLinks}>
              <li><Link href="/orders">Заказы</Link></li>
              <li><Link href="/portfolio">Портфолио</Link></li>
              <li><Link href="/community">Сообщество</Link></li>
              <li><Link href="/about">О нас</Link></li>
              <li><Link href="/contacts">Контакты</Link></li>
              {isAuthenticated && <li><Link href="/chats">Чаты</Link></li>}
            </ul>
          </div>

          {/* Right section */}
          <div className={styles.navRight}>
            {/* Desktop search */}
            <div className={styles.searchContainer}>
              <div className={styles.searchInputWrapper}>
                <svg className={styles.searchIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.3-4.3" />
                </svg>
                <input
                  type="text"
                  placeholder="Поиск..."
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  className={styles.searchInput}
                />
              </div>

              {searchResults.length > 0 && (
                <div className={styles.searchResults}>
                  {searchResults.map((result) => (
                    <button
                      key={result.id}
                      type="button"
                      className={styles.searchResultItem}
                      onClick={() => handleSearchResultClick(result)}
                    >
                      <span className={styles.searchResultType}>
                        {result.type === 'order' ? '📋' : result.type === 'user' ? '👤' : '📂'}
                      </span>
                      <span className={styles.searchResultName}>{result.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Mobile search button */}
            <button 
              className={styles.mobileSearchButton}
              onClick={() => setMobileSearchOpen(!mobileSearchOpen)}
              aria-label="Поиск"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </button>

            {/* Balances for authenticated users */}
            {isAuthenticated && user && (
              <div className={styles.balanceGroup}>
                <div className={styles.balanceBadge}>
                  <span className={styles.balanceValue}>
                    {Number(user.balance ?? 0).toLocaleString('ru-RU')}
                  </span>
                  <span className={styles.balanceCurrency}>₽</span>
                </div>
                <div className={styles.balanceBadge}>
                  <span className={styles.balanceValue}>
                    {Number(user.tf_balance ?? 0).toLocaleString('ru-RU')}
                  </span>
                  <span className={styles.balanceCurrency}>ТЗ</span>
                </div>
              </div>
            )}

            {/* Account button */}
            <div
              className={styles.account}
              onMouseEnter={handleAccountMouseEnter}
              onMouseLeave={handleAccountMouseLeave}
            >
              <button className={`${styles.accountButton} ${isAuthenticated ? styles.accountButtonAuth : ''}`}>
                {isAuthenticated && user ? (
                  <span className={styles.accountAvatar}>
                    {user.name?.charAt(0) || 'U'}
                  </span>
                ) : (
                  <span className={styles.accountIcon}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  </span>
                )}
              </button>

              {showAccountDropdown && (
                <div className={styles.dropdownMenu}>
                  {isAuthenticated && user ? (
                    <div className={styles.accountDetails}>
                      <div className={styles.accountHeader}>
                        <div className={styles.accountAvatarLarge}>
                          {user.name?.charAt(0) || 'U'}
                        </div>
                        <div className={styles.accountInfo}>
                          <div className={styles.accountName}>
                            {user.name || 'Пользователь'}
                            {user.admin_verified && <span className={styles.verifiedBadge}>✓</span>}
                          </div>
                          <div className={styles.accountNickname}>@{user.nickname || 'username'}</div>
                        </div>
                      </div>
                      <div className={styles.accountEmail}>{user.email || 'email@example.com'}</div>
                      <div className={styles.accountRatings}>
                        <div className={styles.ratingItem}>
                          <span className={styles.ratingLabel}>Заказчик</span>
                          <span className={styles.ratingValue}>★ {user.customer_rating || 0}</span>
                        </div>
                        <div className={styles.ratingItem}>
                          <span className={styles.ratingLabel}>Исполнитель</span>
                          <span className={styles.ratingValue}>★ {user.executor_rating || 0}</span>
                        </div>
                      </div>
                      <div className={styles.dropdownActions}>
                        <button className={styles.dropdownAction} onClick={() => router.push('/profile')}>
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                          </svg>
                          Профиль
                        </button>
                        <button className={styles.dropdownAction} onClick={() => router.push('/chats')}>
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                          </svg>
                          Чаты
                        </button>
                        <button className={styles.dropdownActionLogout} onClick={handleLogout}>
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                            <polyline points="16,17 21,12 16,7" />
                            <line x1="21" y1="12" x2="9" y2="12" />
                          </svg>
                          Выйти
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className={styles.accountGuestActions}>
                      <Link href="/login" className={styles.guestLogin}>
                        Войти
                      </Link>
                      <Link href="/register" className={styles.guestRegister}>
                        Регистрация
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Burger button for mobile */}
            <button 
              className={`${styles.burgerButton} ${mobileMenuOpen ? styles.burgerButtonOpen : ''}`}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Меню"
            >
              <span className={styles.burgerLine} />
              <span className={styles.burgerLine} />
              <span className={styles.burgerLine} />
            </button>
          </div>
        </nav>

        {/* Mobile search bar */}
        <div className={`${styles.mobileSearchBar} ${mobileSearchOpen ? styles.mobileSearchBarOpen : ''}`}>
          <div className={styles.mobileSearchWrapper}>
            <svg className={styles.mobileSearchIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Что ищете?"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              className={styles.mobileSearchInput}
            />
            <button 
              className={styles.mobileSearchClose}
              onClick={() => { setMobileSearchOpen(false); setSearchQuery(''); }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
          {searchResults.length > 0 && (
            <div className={styles.mobileSearchResults}>
              {searchResults.map((result) => (
                <button
                  key={result.id}
                  type="button"
                  className={styles.searchResultItem}
                  onClick={() => handleSearchResultClick(result)}
                >
                  <span className={styles.searchResultType}>
                    {result.type === 'order' ? '📋' : result.type === 'user' ? '👤' : '📂'}
                  </span>
                  <span className={styles.searchResultName}>{result.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </header>

      {/* Mobile menu overlay */}
      <div 
        className={`${styles.mobileOverlay} ${mobileMenuOpen ? styles.mobileOverlayOpen : ''}`} 
        onClick={closeMobileMenu} 
      />

      {/* Mobile menu */}
      <div className={`${styles.mobileMenu} ${mobileMenuOpen ? styles.mobileMenuOpen : ''}`}>
        <div className={styles.mobileMenuHeader}>
          <span className={styles.mobileMenuLogo}>ТЗ</span>
          <span>Меню</span>
        </div>
        
        <ul className={styles.mobileNavLinks}>
          <li><Link href="/orders" onClick={closeMobileMenu}>Заказы</Link></li>
          <li><Link href="/portfolio" onClick={closeMobileMenu}>Портфолио</Link></li>
          <li><Link href="/community" onClick={closeMobileMenu}>Сообщество</Link></li>
          <li><Link href="/about" onClick={closeMobileMenu}>О нас</Link></li>
          <li><Link href="/contacts" onClick={closeMobileMenu}>Контакты</Link></li>
          {isAuthenticated && <li><Link href="/chats" onClick={closeMobileMenu}>Чаты</Link></li>}
        </ul>
        
        {isAuthenticated && user ? (
          <div className={styles.mobileUserSection}>
            <div className={styles.mobileUserCard}>
              <div className={styles.mobileUserAvatar}>
                {user.name?.charAt(0) || 'U'}
              </div>
              <div className={styles.mobileUserInfo}>
                <strong>{user.name || 'Пользователь'}</strong>
                <span>@{user.nickname || 'username'}</span>
              </div>
            </div>
            <div className={styles.mobileBalances}>
              <div className={styles.mobileBalanceItem}>
                <span className={styles.mobileBalanceValue}>{Number(user.balance ?? 0).toLocaleString('ru-RU')}</span>
                <span className={styles.mobileBalanceLabel}>₽</span>
              </div>
              <div className={styles.mobileBalanceItem}>
                <span className={styles.mobileBalanceValue}>{Number(user.tf_balance ?? 0).toLocaleString('ru-RU')}</span>
                <span className={styles.mobileBalanceLabel}>ТЗ</span>
              </div>
            </div>
            <Link href="/profile" className={styles.mobileActionButton} onClick={closeMobileMenu}>
              Профиль
            </Link>
            <button className={styles.mobileLogoutButton} onClick={() => { handleLogout(); closeMobileMenu(); }}>
              Выйти
            </button>
          </div>
        ) : (
          <div className={styles.mobileGuestSection}>
            <Link href="/login" className={styles.mobileLoginButton} onClick={closeMobileMenu}>
              Войти
            </Link>
            <Link href="/register" className={styles.mobileRegisterButton} onClick={closeMobileMenu}>
              Регистрация
            </Link>
          </div>
        )}
      </div>
    </>
  )
}
