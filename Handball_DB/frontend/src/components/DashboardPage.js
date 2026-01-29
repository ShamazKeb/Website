import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './DashboardPage.css'; // Import the new CSS file

const DashboardPage = () => {
    const { user, token, logout } = useAuth();
    const navigate = useNavigate();
    const [recentMeasurements, setRecentMeasurements] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }

        const fetchRecentMeasurements = async () => {
            try {
                const response = await axios.get(`${API_URL}/players/me/measurements?limit=10`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setRecentMeasurements(response.data);
            } catch (err) {
                setError('Fehler beim Laden der letzten Messungen.');
                console.error('Error fetching recent measurements:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchRecentMeasurements();
    }, [user, token, navigate, API_URL]);

    if (loading) {
        return <div className="dashboard-container">Lädt Dashboard...</div>;
    }

    if (error) {
        return <div className="dashboard-container"><p className="dashboard-error">{error}</p></div>;
    }

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h1 className="dashboard-title">Willkommen, {user?.email}!</h1>
            </div>
            <p className="dashboard-role-text">Rolle: {user?.role}</p>

            <div className="dashboard-button-group">
                <button onClick={() => navigate('/record-measurement')} className="btn-primary">
                    Neue Messung aufzeichnen
                </button>
                <button onClick={() => navigate('/performance-history')} className="btn-primary">
                    Leistungsverlauf ansehen
                </button>
            </div>


            <h2 className="dashboard-section-title">Letzte Messungen</h2>
            {recentMeasurements.length === 0 ? (
                <p>Keine Messungen gefunden.</p>
            ) : (
                <div className="dashboard-measurement-list">
                    {recentMeasurements.map((measurement) => (
                        <div key={measurement.id} className="card dashboard-measurement-card">
                            <div className="dashboard-measurement-header">
                                <strong className="dashboard-measurement-exercise">{measurement.exercise_name || 'Unbekannt'}</strong>
                                <span className="dashboard-measurement-date">{new Date(measurement.recorded_at).toLocaleDateString()}</span>
                            </div>
                            <div className="dashboard-measurement-values">
                                {Object.entries(measurement.values).map(([key, val]) => (
                                    <span key={key} className="dashboard-measurement-value-item">
                                        {key}: <strong>{val}</strong>
                                    </span>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default DashboardPage;