import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles.css'
import { GoogleOAuthProvider } from '@react-oauth/google'
import { AuthProvider } from './AuthContext'
import { API_URL } from './api'

async function getGoogleClientId() {
	try {
		const response = await fetch(`${API_URL}/auth/google/login`)
		if (response.ok) return (await response.json()).client_id as string
	} catch {
		// Use the build-time value when the API is unavailable during local startup.
	}
	return import.meta.env.VITE_GOOGLE_CLIENT_ID ?? ''
}

getGoogleClientId().then(clientId => {
	ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><GoogleOAuthProvider clientId={clientId}><AuthProvider><App /></AuthProvider></GoogleOAuthProvider></React.StrictMode>)
})
