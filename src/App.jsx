import React, { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import MoodTrackerPage from './pages/MoodTrackerPage'
import BreathingExercisePage from './pages/BreathingExercisePage'
import ReflectionPage from './pages/ReflectionPage'
import LandingPage from './pages/LandingPage'
import SignInPage from './pages/SignInPage'

function App() {
  // We'll use 'landing' as the absolute default so the user sees it first
  const [activePage, setActivePage] = useState('landing')
  const [isDarkMode, setIsDarkMode] = useState(false)

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDarkMode])

  const renderPage = () => {
    switch (activePage) {
      case 'landing':
        return <LandingPage onNavigate={setActivePage} />
      case 'signin':
        return <SignInPage onNavigate={setActivePage} onSignIn={() => setActivePage('chat')} />
      case 'chat':
        return <ChatPage />
      case 'mood':
        return <MoodTrackerPage />
      case 'breathing':
        return <BreathingExercisePage />
      case 'reflection':
        return <ReflectionPage />
      default:
        return <LandingPage onNavigate={setActivePage} />
    }
  }

  return (
    <div className={isDarkMode ? 'dark' : ''}>
      {(activePage === 'landing' || activePage === 'signin') ? (
        renderPage()
      ) : (
        <div className="flex h-screen bg-wellness-gray dark:bg-gray-900 transition-colors duration-300 overflow-hidden font-sans text-wellness-text dark:text-gray-100">
          <Sidebar activePage={activePage} setActivePage={setActivePage} isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />

          <main className="flex-1 overflow-y-auto p-8 lg:p-12 relative">
            <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-wellness-blue to-transparent dark:from-blue-900/20 dark:to-transparent opacity-50 pointer-events-none -z-10 transition-colors duration-300" />
            {renderPage()}
          </main>
        </div>
      )}
    </div>
  )
}

export default App
