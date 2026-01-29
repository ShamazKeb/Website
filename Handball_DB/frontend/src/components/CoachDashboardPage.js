import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import axios from 'axios';
import { Link } from 'react-router-dom'; // Import Link for navigation
import './CoachDashboardPage.css'; // Import the new CSS file

const CoachDashboardPage = () => {
    const { token } = useAuth();
    const [teams, setTeams] = useState([]);
    const [activityLogs, setActivityLogs] = useState({}); // New state for activity logs
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchData = async () => {
            if (!token) return;

            try {
                // Fetch teams
                const teamsResponse = await axios.get(`${API_URL}/teams`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setTeams(teamsResponse.data);

                // Fetch activity logs for each team
                const logsPromises = teamsResponse.data.map(async (team) => {
                    const logsResponse = await axios.get(`${API_URL}/activity-logs`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        },
                        params: {
                            team_id: team.id,
                            limit: 3 // Get latest 3 activities
                        }
                    });
                    return { teamId: team.id, logs: logsResponse.data };
                });

                const allLogs = await Promise.all(logsPromises);
                const logsByTeam = allLogs.reduce((acc, { teamId, logs }) => {
                    acc[teamId] = logs;
                    return acc;
                }, {});
                setActivityLogs(logsByTeam);

            } catch (err) {
                setError('Failed to fetch data.');
                console.error('Error fetching data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [token, API_URL]);

    if (loading) {
        return <div className="coach-loading">Loading data...</div>;
    }

    if (error) {
        return <div className="coach-error">Error: {error}</div>;
    }

    return (
        <div className="coach-dashboard-container">
            <h1 className="coach-dashboard-title">Coach Dashboard</h1>
            <p className="coach-dashboard-welcome-text">Welcome to the coach dashboard!</p>

            <div className="coach-dashboard-actions">
                <Link to="/exercises-management">
                    <button className="btn-primary">Manage Exercises</button>
                </Link>
                <Link to="/analytics">
                    <button className="btn-primary">Analytics</button>
                </Link>
                <Link to="/leaderboards">
                    <button className="btn-primary">Leaderboards</button>
                </Link>
            </div>

            <h2 className="coach-dashboard-section-title">My Teams</h2>
            {teams.length === 0 ? (
                <p className="coach-no-activity">No teams assigned yet.</p>
            ) : (
                <div className="coach-teams-list">
                    {teams.map(team => (
                        <div key={team.id} className="card coach-team-card">
                            <h3 className="coach-team-header">
                                <span className="coach-team-name">
                                    {team.name} <span className="coach-team-season">({team.season})</span>
                                </span>
                                <Link to={`/teams/${team.id}`} className="coach-team-details-link">
                                    View Details
                                </Link>
                            </h3>
                            <p className="coach-team-players-count">Players: {team.players ? team.players.length : 0}</p>

                            <h4 className="coach-activity-title">Recent Activity</h4>
                            {activityLogs[team.id] && activityLogs[team.id].length > 0 ? (
                                <ul className="coach-activity-list">
                                    {activityLogs[team.id].map(log => (
                                        <li key={log.id}>
                                            <span className="coach-activity-date">{new Date(log.created_at).toLocaleDateString()}</span>: {log.description}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="coach-no-activity">No recent activity.</p>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CoachDashboardPage;