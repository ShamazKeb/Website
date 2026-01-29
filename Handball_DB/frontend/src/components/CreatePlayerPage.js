import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './CreatePlayerPage.css'; // Import the new CSS file

const CreatePlayerPage = () => {
    const { id: teamId } = useParams(); // Get teamId from URL
    const navigate = useNavigate();
    const { token } = useAuth();
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [birthYear, setBirthYear] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);
        setLoading(true);

        if (!firstName || !lastName || !birthYear) {
            setError('Please fill in all fields.');
            setLoading(false);
            return;
        }

        try {
            // Create player (assuming a /players endpoint for creating player first)
            const playerResponse = await axios.post(`${API_URL}/players`, {
                first_name: firstName,
                last_name: lastName,
                birth_year: parseInt(birthYear),
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            const newPlayerId = playerResponse.data.id;

            // Link player to team (assuming /teams/{id}/players endpoint for linking)
            await axios.post(`${API_URL}/teams/${teamId}/players`, {
                player_id: newPlayerId,
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            setSuccess(true);
            setFirstName('');
            setLastName('');
            setBirthYear('');
            navigate(`/teams/${teamId}`); // Redirect back to team details page
        } catch (err) {
            setError('Failed to create player or link to team.');
            console.error('Error creating player:', err);
            if (err.response && err.response.data && err.response.data.detail) {
                setError(`Error: ${err.response.data.detail}`);
            }
        } finally {
            setLoading(false);
        }
    };

    // Combine error and success messages for better UX
    const statusMessage = error ? (
        <p className="create-player-error">{error}</p>
    ) : success ? (
        <p className="create-player-success">Player created and linked successfully!</p>
    ) : null;

    return (
        <div className="create-player-container">
            <h2 className="create-player-title">Create New Player for Team {teamId}</h2>
            <form onSubmit={handleSubmit} className="create-player-form">
                <div className="create-player-form-group">
                    <label htmlFor="firstName" className="create-player-label">First Name:</label>
                    <input
                        type="text"
                        id="firstName"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="create-player-input"
                        required
                    />
                </div>
                <div className="create-player-form-group">
                    <label htmlFor="lastName" className="create-player-label">Last Name:</label>
                    <input
                        type="text"
                        id="lastName"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="create-player-input"
                        required
                    />
                </div>
                <div className="create-player-form-group">
                    <label htmlFor="birthYear" className="create-player-label">Birth Year:</label>
                    <input
                        type="number"
                        id="birthYear"
                        value={birthYear}
                        onChange={(e) => setBirthYear(e.target.value)}
                        className="create-player-input"
                        required
                    />
                </div>

                {statusMessage}

                <button type="submit" className="create-player-button btn-primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Player'}
                </button>
            </form>
        </div>
    );
};

export default CreatePlayerPage;
