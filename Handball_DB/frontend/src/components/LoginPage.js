import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext'; // Corrected import path
import './LoginPage.css'; // Import the new CSS file

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
        <div className="login-container">
            <h2 className="login-title">Anmelden</h2>
            <form onSubmit={handleSubmit} className="login-form">
                <div className="login-form-group">
                    <label htmlFor="email" className="login-label">E-Mail:</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="login-input"
                    />
                </div>
                <div className="login-form-group">
                    <label htmlFor="password" className="login-label">Passwort:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        className="login-input"
                    />
                </div>
                {error && <p className="login-error">{error}</p>}
                <button type="submit" className="login-button">Anmelden</button>
            </form>
        </div>
    );
};

export default LoginPage;