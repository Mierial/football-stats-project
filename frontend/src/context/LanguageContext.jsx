import { createContext, useState } from "react";

import {UA, EN, RU, availableLanguages} from './dictionaries'

export const LanguageContext = createContext(null);

export const LanguageProvider = ({children}) => {
    const DICTIONARIES_CHOICES = {
        'UA': UA,
        'RU': RU,
        'EN': EN,
    }
    const [language, setLanguage] = useState('RU')

    const languageChangeHandler = (event) => {
        setLanguage(event.target.value)
    } 

    const choosedLanguage = DICTIONARIES_CHOICES[language]

    const value = {choosedLanguage, languageChangeHandler, availableLanguages, language }


    return (
        <LanguageContext.Provider value={value} >
            {children}
        </LanguageContext.Provider>
    )
}