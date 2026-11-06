import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; 
const UserProfilePage = () => {
    const [isLoading, setIsLoading] = useState(true)
    const [user, setUser] = useState(null)
    const navigate = useNavigate();
    useEffect(()=>{
        const access_token = localStorage.getItem('access')

        if (!access_token) {
            navigate('/auth/login')
            return;
        }

        const refreshToken = async() => {
            try{
                const response = await fetch('http://127.0.0.1:8000/auth/refresh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh: localStorage.getItem('refresh') }),
                })
                if (response.ok){
                    const data = await response.json()
                    localStorage.setItem('access', data.access)
                    return data.access
                }
                else{
                    localStorage.clear();
                    navigate('/auth/login');
                    return null;
                }
            } catch(error){
                console.log(error)
            }
            
        }

        const getUserProfile = async() => {
            try{
                let response = await fetch('http://127.0.0.1:8000/profile/me', {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${access_token}`
                        }})

                if(response.status===401){
                    const newToken = await refreshToken();
                    response = await fetch('http://127.0.0.1:8000/profile/me', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${newToken}`
                    },
                })
                }
                if (!response.ok) {
                    throw new Error(`Помилка сервера: ${response.status}`);
                }
                const data = await response.json()
                console.log(data)
                setUser(data)
            
            } catch(error){
                console.log(error)
            }finally{
                setIsLoading(false)
            }
        }
        getUserProfile()
    }, [navigate])

    if(isLoading) { return <div className="">downloading</div> }
    if(!user) {return <div>Error</div>}

    return (
        <div>
            <h1>Профіль: {user.username}</h1>
            <p>Email: {user.email}</p>
        </div>
    );
}
    
export default UserProfilePage;
