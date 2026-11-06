import { useState } from "react";
import { useNavigate } from "react-router-dom";
import './AuthPage.css'
const AuthPage = ({setIsAuthenticated, onSuccess}) => {
    const [isLogin, setIsLogin] = useState(true)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [email, setEmail] = useState('')
    const navigate = useNavigate()
    
    const handleSubmit = async (e) => {
        e.preventDefault()
        const endpoint = isLogin ? 'login' : 'register'

        const payload = {
            username: username,
            password: password,  
        }

        if(!isLogin) {
            payload.email = email
        }

        try{
            const response = await fetch(`http://127.0.0.1:8000/auth/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            })
            const data = await response.json()
            if (response.ok && data){
                localStorage.setItem('access', data.access);
                localStorage.setItem('refresh', data.refresh);
                setIsAuthenticated(true)
                if (onSuccess) onSuccess();
                navigate('/profile/me')
            }
            else{
                console.error('Server problem', data)
            }
        }
        catch(error){
            console.log(error)
        }   
    }
   

    return (
        <form onSubmit={handleSubmit}>
        <div className="auth-page">
                <div className="auth-page__label-cont">
                <label className="auth-page__label" htmlFor="user-username">Username</label>
                <input 
                id='user-username'
                type='text'
                name='username'
                value={username}
                onChange={(e)=>setUsername(e.target.value)}
                />
            </div>
            <div className="auth-page__label-cont">
                <label className="auth-page__label" htmlFor="user-password">Password</label>
                <input 
                id='user-password'
                type='password'
                name='password'
                value={password}
                onChange={(e)=>setPassword(e.target.value)}
                />
            </div>
            {!isLogin && (<div className="auth-page__label-cont">
                <label className="auth-page__label" htmlFor="user-email">Email</label>
                <input 
                id='user-email'
                type='email'
                name='email'
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
                />
            </div>)}
        </div>
        
        <button className="auth-page__submit" type="submit">{isLogin ? 'Login' : 'Register'}</button>
        <button 
        type="button" 
        className="auth-page__change-mode" 
        onClick={()=>{setIsLogin(!isLogin)}}
        >
            Switch to {isLogin ? 'register' : 'login'}
        </button>
        
        </form>
    )
}
export default AuthPage;