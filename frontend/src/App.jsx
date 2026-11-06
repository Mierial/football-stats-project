import { useState} from 'react'
import Header from './components/Header/Header'
import SidePanel from './components/SidePanel/SidePanel'
import { LanguageProvider } from './context/LanguageContext'

import TournamentPage from './pages/TournamentPage'
import TeamPage from './pages/TeamPage'
import HomePage from './pages/HomePage'

import { Route, Routes } from 'react-router-dom'
import UserProfilePage from './pages/UserProfilePage'

function App() {
  console.log('app')
    const [isDarkTheme, setDarkTheme] = useState(true)
    
    const toggleTheme = () => {
      setDarkTheme(!isDarkTheme);
    };

  return (
    <LanguageProvider >
      <div className="app-grid" data-theme={isDarkTheme ? 'dark' : 'light'}>
        <Header  toggleTheme={toggleTheme} isDarkTheme={isDarkTheme} />
        <SidePanel />
        <div className="main-content">
          <Routes>
            <Route path='/tournament/:leagueCode' element={<TournamentPage/>}></Route>
            <Route path='team/:teamId' element={<TeamPage />}></Route>
            <Route path='/home' element={<HomePage />}></Route>
            <Route path='/profile/me' element={<UserProfilePage/>}></Route>
          </Routes>
        </div>
      </div>
    </LanguageProvider>
  )
}

export default App
