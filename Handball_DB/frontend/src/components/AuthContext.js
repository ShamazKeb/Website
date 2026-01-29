import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [role, setRole] = useState(null); // Add role state
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'; // FastAPI backend URL

    useEffect(() => {
        const fetchUser = async () => {
            if (token) {
                try {
                    const response = await axios.get(`${API_URL}/auth/me`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    setUser(response.data);
                    setRole(response.data.role); // Set role here
                } catch (error) {
                    console.error('Failed to fetch user:', error);
                    localStorage.removeItem('token');
                    setToken(null);
                    setUser(null);
                    setRole(null);
                }
            }
        };
        fetchUser();
    }, [token, API_URL]);

    const login = async (email, password) => {
        try {
            const response = await axios.post(`${API_URL}/auth/login`, { email, password });
            const newToken = response.data.access_token;
            localStorage.setItem('token', newToken);
            setToken(newToken);
            // Fetch user details immediately after setting token
            const userResponse = await axios.get(`${API_URL}/auth/me`, {
                headers: {
                    Authorization: `Bearer ${newToken}`
                }
            });
            setUser(userResponse.data);
            setRole(userResponse.data.role); // Set role here
            return true;
        } catch (error) {
            console.error('Login failed:', error);
            throw error; // Re-throw to be handled by the login component
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        setRole(null); // Clear role on logout
    };

    const isCoach = role === 'coach' || role === 'admin';
    const isAdmin = role === 'admin';

    return (
        <AuthContext.Provider value={{ user, token, login, logout, role, isCoach, isAdmin }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);