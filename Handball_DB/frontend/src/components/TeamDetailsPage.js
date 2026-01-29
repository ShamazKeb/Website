import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './TeamDetailsPage.css'; // Import the new CSS file

const TeamDetailsPage = () => {
    const { id } = useParams();
    const { token } = useAuth();
    const [team, setTeam] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const fetchTeamDetails = async () => {
        try {
            const response = await axios.get(`${API_URL}/teams/${id}`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setTeam(response.data);
        } catch (err) {
            setError('Failed to fetch team details.');
            console.error('Error fetching team details:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token && id) {
            fetchTeamDetails();
        }
    }, [token, id, API_URL]);

    const handleDeactivatePlayer = async (playerId) => {
        if (window.confirm('Are you sure you want to deactivate this player?')) {
            try {
                await axios.patch(`${API_URL}/players/${playerId}`, { is_active: false }, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                alert('Player deactivated successfully!');
                fetchTeamDetails(); // Re-fetch team details to update the player list
            } catch (err) {
                setError('Failed to deactivate player.');
                console.error('Error deactivating player:', err);
                if (err.response && err.response.data && err.response.data.detail) {
                    setError(`Error: ${err.response.data.detail}`);
                }
            }
        }
    };

    if (loading) {
        return <div className="team-details-container"><p className="coach-loading">Loading team details...</p></div>;
    }

    if (error) {
        return <div className="team-details-container"><p className="coach-error">Error: {error}</p></div>;
    }

    if (!team) {
        return <div className="team-details-container"><p className="team-details-no-players">Team not found.</p></div>;
    }

    return (
        <div className="team-details-container">
            <h1 className="team-details-title">Team Details: {team.name} ({team.season})</h1>
            <p className="team-details-description">This page will display detailed information about the team.</p>

            <h2 className="team-details-players-section-title">Players</h2>
            {team.players && team.players.length > 0 ? (
                <ul className="team-details-player-list">
                    {team.players.map(player => (
                        <li key={player.id} className="team-details-player-item card">
                            <span className="team-details-player-info">
                                {player.first_name} {player.last_name} (Birth Year: {player.birth_year}, Active: {player.is_active ? 'Yes' : 'No'})
                            </span>
                            <div className="team-details-player-actions">
                                <Link to={`/players/${player.id}/measurements`} className="team-details-link-button btn-primary">
                                    View History
                                </Link>
                                <Link to={`/record-measurement/${player.id}`} className="team-details-link-button btn-primary">
                                    Add Measurement
                                </Link>
                                {player.is_active && (
                                    <button onClick={() => handleDeactivatePlayer(player.id)} className="btn-deactivate-player">
                                        Deactivate
                                    </button>
                                )}
                            </div>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="team-details-no-players">No players in this team.</p>
            )}

            <Link to={`/teams/${id}/players/create`} className="team-details-create-player-link">
                <button className="btn-primary">Create New Player</button>
            </Link>

            {/* TODO: Add coaches, full activity logs, add/edit measurements, create new player, deactivate player */}
        </div>
    );
};

export default TeamDetailsPage;