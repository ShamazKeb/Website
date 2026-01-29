import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './PlayerMeasurementHistoryPage.css'; // Import the new CSS file

const PlayerMeasurementHistoryPage = () => {
    const { id } = useParams(); // This 'id' will be the player_id
    const { token } = useAuth();
    const [measurements, setMeasurements] = useState([]);
    const [exercises, setExercises] = useState([]); // State to store exercises
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch exercises to map exercise_id to name
                const exercisesResponse = await axios.get(`${API_URL}/exercises`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setExercises(exercisesResponse.data);

                const response = await axios.get(`${API_URL}/measurements`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    params: {
                        player_id: id // Filter by player_id
                    }
                });
                setMeasurements(response.data);
            } catch (err) {
                setError('Failed to fetch data (measurements or exercises).');
                console.error('Error fetching data:', err);
            } finally {
                setLoading(false);
            }
        };

        if (token && id) {
            fetchData();
        }
    }, [token, id, API_URL]);

    const getExerciseName = (exerciseId) => {
        const exercise = exercises.find(ex => ex.id === exerciseId);
        return exercise ? exercise.name : 'Unknown Exercise';
    };


    if (loading) {
        return <div className="player-measurement-history-container player-measurement-history-loading">Loading measurements...</div>;
    }

    if (error) {
        return <div className="player-measurement-history-container player-measurement-history-error">Error: {error}</div>;
    }

    if (measurements.length === 0) {
        return <div className="player-measurement-history-container player-measurement-history-no-data">No measurements found for this player.</div>;
    }

    return (
        <div className="player-measurement-history-container">
            <h1 className="player-measurement-history-title">Measurement History for Player ID: {id}</h1>
            <ul className="player-measurement-history-list">
                {measurements.map(measurement => (
                    <li key={measurement.id} className="player-measurement-history-item card">
                        <span><strong>Exercise:</strong> {getExerciseName(measurement.exercise_id)}</span>
                        <span><strong>Recorded:</strong> {new Date(measurement.recorded_at).toLocaleString()}</span>
                        <span>
                            <strong>Values:</strong>
                            {Object.entries(measurement.values).map(([key, val]) => (
                                <span key={key} className="value-pair">
                                    {key}: <strong>{val}</strong>
                                </span>
                            ))}
                        </span>
                        {measurement.notes && <span><strong>Notes:</strong> {measurement.notes}</span>}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default PlayerMeasurementHistoryPage;
