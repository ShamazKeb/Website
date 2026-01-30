import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './LoginPage.css';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setError('');
        try {
            await login(email, password);
            navigate('/dashboard'); // Redirect to dashboard on successful login
        } catch (err) {
            setError('Anmeldung fehlgeschlagen. Bitte überprüfen Sie Ihre E-Mail und Ihr Passwort.');
        }
    };

    return (
        <div className="login-page">
            <div className="login-branding">
                <h1 className="branding-title">
                    <span>Handball</span>
                    Statistik
                </h1>
                <p className="branding-subtitle">
                    Verfolge die Leistung deines Teams. Analysiere Spieldaten. Erreiche neue Ziele.
                </p>
            </div>
            <div className="login-container">
                <form onSubmit={handleSubmit} className="login-form">
                    <h2 className="login-title">Login</h2>
                    <p className="login-subtitle">Willkommen zurück!</p>
                    <div className="login-form-group">
                        <label htmlFor="email" className="form-label">E-Mail</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="form-control"
                            placeholder="deine.email@beispiel.de"
                        />
                    </div>
                    <div className="login-form-group">
                        <label htmlFor="password" className="form-label">Passwort</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="form-control"
                            placeholder="Dein Passwort"
                        />
                    </div>
                    
                    <button type="submit" className="login-button">Anmelden</button>
                    {error && <p className="login-error">{error}</p>}
                </form>
            </div>
        </div>
    );
};

export default LoginPage;
