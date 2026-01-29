import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './LeaderboardsPage.css'; // Import the new CSS file

const LeaderboardsPage = () => {
    const { token } = useAuth();
    const [exercises, setExercises] = useState([]);
    const [teams, setTeams] = useState([]);
    const [allPlayers, setAllPlayers] = useState([]); // Needed to map player IDs to names

    const [selectedExercise, setSelectedExercise] = useState('');
    const [selectedTeam, setSelectedTeam] = useState('');
    const [selectedBirthYear, setSelectedBirthYear] = useState('');
    const [selectedSeason, setSelectedSeason] = useState('');

    const [leaderboardData, setLeaderboardData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    // Fetch initial data (exercises, teams, all players)
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [exercisesRes, teamsRes, playersRes] = await Promise.all([
                    axios.get(`${API_URL}/exercises`, { headers: { Authorization: `Bearer ${token}` } }),
                    axios.get(`${API_URL}/teams`, { headers: { Authorization: `Bearer ${token}` } }),
                    axios.get(`${API_URL}/players`, { headers: { Authorization: `Bearer ${token}` } }),
                ]);
                setExercises(exercisesRes.data);
                setTeams(teamsRes.data);
                setAllPlayers(playersRes.data);
            } catch (err) {
                setError('Failed to fetch initial data.');
                console.error('Error fetching initial data:', err);
            } finally {
                setLoading(false);
            }
        };

        if (token) {
            fetchInitialData();
        }
    }, [token, API_URL]);

    // Fetch leaderboard data based on filters
    useEffect(() => {
        const fetchLeaderboardData = async () => {
            if (!token || !selectedExercise) {
                setLeaderboardData([]);
                return;
            }

            setLoading(true);
            try {
                const params = {
                    exercise_id: selectedExercise,
                    team_id: selectedTeam || undefined,
                    birth_year: selectedBirthYear || undefined,
                    season: selectedSeason || undefined,
                    // Assuming an API endpoint that provides aggregated best performance per player
                };
                // Assuming an endpoint for leaderboards, e.g., /measurements/leaderboard
                const response = await axios.get(`${API_URL}/measurements/leaderboard`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    params: params
                });
                setLeaderboardData(response.data); // Expecting [{player_id, best_value, recorded_at, ...}]
            } catch (err) {
                setError('Failed to fetch leaderboard data.');
                console.error('Error fetching leaderboard data:', err);
                setLeaderboardData([]);
            } finally {
                setLoading(false);
            }
        };

        fetchLeaderboardData();
    }, [token, selectedExercise, selectedTeam, selectedBirthYear, selectedSeason, API_URL]);

    const getPlayerName = (playerId) => {
        const player = allPlayers.find(p => p.id === playerId);
        return player ? `${player.first_name} ${player.last_name}` : `Player ${playerId}`;
    };

    if (loading) {
        return <div className="leaderboards-container leaderboards-loading">Loading leaderboards...</div>;
    }

    if (error) {
        return <div className="leaderboards-container leaderboards-error">Error: {error}</div>;
    }

    // Extract unique seasons and birth years for filters
    const availableSeasons = Array.from(new Set(teams.map(team => team.season))).sort();
    const availableBirthYears = Array.from(new Set(allPlayers.map(player => player.birth_year))).sort((a, b) => b - a);


    return (
        <div className="leaderboards-container">
            <h1 className="leaderboards-title">Leaderboards</h1>

            <div className="card leaderboards-filter-card">
                <div className="leaderboards-filter-grid">
                    <div className="leaderboards-filter-group">
                        <label className="leaderboards-label">Exercise:</label>
                        <select value={selectedExercise} onChange={e => setSelectedExercise(e.target.value)} className="leaderboards-select">
                            <option value="">Select Exercise</option>
                            {exercises.map(exercise => (
                                <option key={exercise.id} value={exercise.id}>{exercise.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="leaderboards-filter-group">
                        <label className="leaderboards-label">Team:</label>
                        <select value={selectedTeam} onChange={e => setSelectedTeam(e.target.value)} className="leaderboards-select">
                            <option value="">All Teams</option>
                            {teams.map(team => (
                                <option key={team.id} value={team.id}>{team.name} ({team.season})</option>
                            ))}
                        </select>
                    </div>

                    <div className="leaderboards-filter-group">
                        <label className="leaderboards-label">Season:</label>
                        <select value={selectedSeason} onChange={e => setSelectedSeason(e.target.value)} className="leaderboards-select">
                            <option value="">All Seasons</option>
                            {availableSeasons.map(season => (
                                <option key={season} value={season}>{season}</option>
                            ))}
                        </select>
                    </div>

                    <div className="leaderboards-filter-group">
                        <label className="leaderboards-label">Birth Year:</label>
                        <select value={selectedBirthYear} onChange={e => setSelectedBirthYear(e.target.value)} className="leaderboards-select">
                            <option value="">All Birth Years</option>
                            {availableBirthYears.map(year => (
                                <option key={year} value={year}>{year}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {selectedExercise ? (
                leaderboardData.length > 0 ? (
                    <div className="card leaderboards-table-card">
                        <table className="leaderboards-table">
                            <thead>
                                <tr>
                                    <th className="leaderboards-th">Rank</th>
                                    <th className="leaderboards-th">Player</th>
                                    <th className="leaderboards-th">Best Value</th>
                                    <th className="leaderboards-th">Date Achieved</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leaderboardData.map((entry, index) => (
                                    <tr key={entry.player_id}>
                                        <td className="leaderboards-td" data-label="Rank">{index + 1}</td>
                                        <td className="leaderboards-td" data-label="Player">{getPlayerName(entry.player_id)}</td>
                                        <td className="leaderboards-td" data-label="Best Value">{entry.best_value}</td>
                                        <td className="leaderboards-td" data-label="Date Achieved">{new Date(entry.recorded_at).toLocaleDateString()}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="leaderboards-no-data-message">No leaderboard data available for the selected filters.</p>
                )
            ) : (
                <p className="leaderboards-no-data-message">Please select an exercise to view the leaderboard.</p>
            )}
        </div>
    );
};

export default LeaderboardsPage;