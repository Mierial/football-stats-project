import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import '@fontsource/inter';
import '@fontsource/inter/500.css'; 
import '@fontsource/inter/600.css'; 
import '@fontsource/inter/700.css';
import '@fontsource/russo-one'; 
import './index.css'
import {BrowserRouter} from 'react-router-dom';

createRoot(document.getElementById('root')).render(
    <BrowserRouter >
        <App />
    </BrowserRouter>
)
