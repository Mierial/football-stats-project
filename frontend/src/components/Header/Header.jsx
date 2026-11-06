import { useEffect, useRef, useState, memo } from 'react';
import './Header.css'
import { Sun, Moon, User, LogInIcon } from 'lucide-react';
import { useContext } from 'react';
import { LanguageContext } from '../../context/LanguageContext';
import { Modal } from '../Auth/Modal'
import AuthPage from '../../pages/AuthPage';
import UserProfilePage from '../../pages/UserProfilePage';
import { Link } from 'react-router-dom';

const Header = (props) => {
    const [isAuthOpen, setIsAuthOpen] = useState(false);
    const [search, setSearch] = useState('');
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const onInput = (value) => {
      setSearch(value);
    };

    const {
        toggleTheme,
        isDarkTheme,
    } = props


    const{
        choosedLanguage,
        languageChangeHandler,
        availableLanguages,
        language
    } = useContext(LanguageContext)

    return (
        <header>
            <div className="header__container">
                <label htmlFor="search" className="header__label">
                    <input 
                    type="text" 
                    id="search" 
                    placeholder={choosedLanguage.searchPlaceholder} 
                    className='header__input'
                    value={search}
                    onChange={(e)=>{onInput(e.target.value)}}
                    />
                </label>
                <div className="header__group--items">

                    <label htmlFor="choosedLanguage"></label>
                    <select name="choosedLanguage" id="choosedLanguage" onChange={languageChangeHandler} value={language}>
                        {availableLanguages.map((currLanguage)=>{
                            return <option key={currLanguage.key} value={currLanguage.key}>{currLanguage.value}</option>
                        })}
                        
                    </select>
                        <div className="header__group--actions">
                            {!isAuthenticated ? (<button className="header__button--login" onClick={()=>{setIsAuthOpen(true)}}>
                                <User className="button-icon" size="18"></User>
                                <span>{isAuthenticated ? 'profile' : 'login'}</span>
                            </button>
                        ) : (
                        <Link to="profile/me" className="header__button--login">
                            <span>profile</span>
                        </Link>)
                        }
                            <Modal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)}>
                                <AuthPage 
                                    setIsAuthenticated={setIsAuthenticated} 
                                    onSuccess={() => setIsAuthOpen(false)} 
                                />
                            </Modal>
                        </div>

                <div className="header__group--actions">
                    <button className="header__theme-toggle" onClick={toggleTheme}>
                        {isDarkTheme ? <Sun color="grey"size="18"/>: <Moon color="grey" size="18"/> }
                    </button>
                    
                    <a href="https://github.com/mierial" className="header__github" target="_blank" rel="noreferrer" >
                        <svg 
                            xmlns="http://www.w3.org/2000/svg" 
                            width="18" 
                            height="18" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="2" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                        >
                            <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.02c3.18-.35 6.5-1.59 6.5-7a4.6 4.6 0 0 0-1.39-3.23 4 4 0 0 0-.14-3.19s-1.14-.36-3.75 1.4A12 12 0 0 0 12 3c-1.2.05-2.4.2-3.5.55-2.6-1.76-3.75-1.4-3.75-1.4a4 4 0 0 0-.14 3.19 4.6 4.6 0 0 0-1.39 3.23c0 5.4 3.32 6.65 6.5 7A4.8 4.8 0 0 0 8 18v4"></path>
                            <path d="M5 20c-1.5 0-3-1-3-3"></path>
                        </svg>
                    </a>
                    </div>
                </div>
            </div>
        </header>
    )
}

export default memo(Header)