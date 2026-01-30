import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import axios from 'axios';
import { Line, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import './AnalyticsPage.css'; // Import the new CSS file

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const AnalyticsPage = () => {
    const { token } = useAuth();
    const [teams, setTeams] = useState([]);
    const [players, setPlayers] = useState([]); // Players of the selected team
    const [allPlayers, setAllPlayers] = useState([]); // All players for multi-select
    const [exercises, setExercises] = useState([]);
    const [categories, setCategories] = useState([]);

    const [selectedTeam, setSelectedTeam] = useState('');
    const [selectedPlayers, setSelectedPlayers] = useState([]);
    const [selectedExercise, setSelectedExercise] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedBirthYear, setSelectedBirthYear] = useState('');
    const [selectedSeason, setSelectedSeason] = useState('');
    const [dateRange, setDateRange] = useState({ from: '', to: '' });
    const [chartType, setChartType] = useState('line');

    const [measurementData, setMeasurementData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    // Fetch initial data (teams, all players, exercises, categories)
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [teamsRes, allPlayersRes, exercisesRes, categoriesRes] = await Promise.all([
                    axios.get(`${API_URL}/teams`, { headers: { Authorization: `Bearer ${token}` } }),
                    axios.get(`${API_URL}/players`, { headers: { Authorization: `Bearer ${token}` } }),
                    axios.get(`${API_URL}/exercises`, { headers: { Authorization: `Bearer ${token}` } }),
                    axios.get(`${API_URL}/exercises/categories`, { headers: { Authorization: `Bearer ${token}` } }),
                ]);
                setTeams(teamsRes.data);
                setAllPlayers(allPlayersRes.data);
                setExercises(exercisesRes.data);
                setCategories(categoriesRes.data);
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

    // Fetch players for selected team
    useEffect(() => {
        if (selectedTeam) {
            const teamPlayers = allPlayers.filter(player =>
                teams.find(t => t.id === parseInt(selectedTeam))?.players.some(p => p.id === player.id)
            );
            setPlayers(teamPlayers);
        } else {
            setPlayers(allPlayers);
        }
        setSelectedPlayers([]);
    }, [selectedTeam, allPlayers, teams]);

    // Fetch measurement data based on filters
    useEffect(() => {
        const fetchMeasurementData = async () => {
            if (!token || !selectedExercise || selectedPlayers.length === 0) {
                setMeasurementData([]);
                return;
            }

            setLoading(true);
            try {
                const params = {
                    exercise_id: selectedExercise,
                    player_ids: selectedPlayers.join(','),
                };
                if (dateRange.from) params.date_from = dateRange.from;
                if (dateRange.to) params.date_to = dateRange.to;
                const response = await axios.get(`${API_URL}/measurements/stats`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    params: params
                });
                setMeasurementData(response.data);
            } catch (err) {
                setError('Failed to fetch measurement data.');
                console.error('Error fetching measurement data:', err);
                setMeasurementData([]);
            } finally {
                setLoading(false);
            }
        };

        fetchMeasurementData();
    }, [token, selectedPlayers, selectedExercise, dateRange, API_URL]);

    const getFilteredExercises = () => {
        if (!selectedCategory) return exercises;
        return exercises.filter(ex => ex.categories && ex.categories.includes(selectedCategory));
    };

    const calculatePerformanceValue = (measurement, exercise) => {
        if (!measurement || !measurement.values) return null;

        const isStrength = exercise.categories.includes('maximalkraft');

        const getValue = (type) => {
            const valObj = measurement.values.find(v => v.measurement_type === type);
            return valObj ? parseFloat(valObj.value) : null;
        };

        const weight = getValue('kilograms');
        const reps = getValue('repetitions');

        if (isStrength && weight !== null) {
            if (reps !== null && reps > 0) {
                return weight * (1 + reps / 30);
            }
            return weight;
        }

        const primaryType = exercise.measurement_types.length > 0 ? exercise.measurement_types[0].measurement_type : null;
        if (primaryType) {
            return getValue(primaryType);
        }
        return null;
    };


    const chartColors = [
        '#B00000', // Primary Red
        '#FF5733', // Orange
        '#FFC300', // Yellow
        '#DAF7A6', // Light Green
        '#00AEEF', // Cyan
        '#E6E6FA', // Lavender
    ];

    const getColor = (index) => {
        return chartColors[index % chartColors.length];
    };


    const getChartData = () => {
        const datasets = [];
        const exercise = exercises.find(ex => ex.id === parseInt(selectedExercise));

        if (!exercise) return { labels: [], datasets: [] };

        if (chartType === 'line') {
            const uniqueTimestamps = Array.from(new Set(measurementData.map(m => new Date(m.recorded_at).setHours(0, 0, 0, 0))))
                .sort((a, b) => a - b);

            const labels = uniqueTimestamps.map(ts => new Date(ts).toLocaleDateString());

            selectedPlayers.forEach((playerId, index) => {
                const playerMeasurements = measurementData.filter(m => m.player_id === parseInt(playerId));
                const playerData = uniqueTimestamps.map(ts => {
                    const measurement = playerMeasurements.find(m => new Date(m.recorded_at).setHours(0, 0, 0, 0) === ts);
                    return calculatePerformanceValue(measurement, exercise);
                });

                const validCount = playerData.filter(v => v !== null).length;
                const showPoints = validCount === 1;

                const player = allPlayers.find(p => p.id === parseInt(playerId));
                datasets.push({
                    label: player ? `${player.first_name} ${player.last_name}` : `Player ${playerId}`,
                    data: playerData,
                    borderColor: getColor(index),
                    backgroundColor: getColor(index) + '33', // Add transparency for area fill if used
                    tension: 0.1,
                    fill: false,
                    spanGaps: true,
                    pointRadius: showPoints ? 5 : 0,
                    pointHoverRadius: 6,
                    borderWidth: 2,
                });
            });
            return { labels, datasets };
        } else if (chartType === 'bar') {
            const labels = selectedPlayers.map(playerId => {
                const player = allPlayers.find(p => p.id === parseInt(playerId));
                return player ? `${player.first_name} ${player.last_name}` : `Player ${playerId}`;
            });

            const data = selectedPlayers.map(playerId => {
                const playerMeasurements = measurementData.filter(m => m.player_id === parseInt(playerId));
                if (playerMeasurements.length > 0) {
                    playerMeasurements.sort((a, b) => new Date(b.recorded_at) - new Date(a.recorded_at));
                    return calculatePerformanceValue(playerMeasurements[0], exercise);
                }
                return 0;
            });

            datasets.push({
                label: `Performance Index (e.g. 1RM or Value)`,
                data: data,
                backgroundColor: selectedPlayers.map((_, index) => getColor(index)),
            });
            return { labels, datasets };
        }
        return { labels: [], datasets: [] };
    };

    const getRandomColor = () => {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    };


    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    color: 'var(--text-main)',
                }
            },
            title: {
                display: true,
                text: chartType === 'line' ? 'Player Performance Over Time' : 'Latest Player Performance Comparison',
                padding: { top: 10, bottom: 30 },
                color: 'var(--text-main)',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'var(--background-card)',
                titleColor: 'var(--text-main)',
                bodyColor: 'var(--text-light)',
            }
        },
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 45,
                    autoSkip: true,
                    maxTicksLimit: 10,
                    color: 'var(--text-main)', // Use brighter color for ticks
                },
                grid: {
                    color: 'var(--border-color)', // Use theme color for grid lines
                }
            },
            y: {
                ticks: {
                    color: 'var(--text-main)', // Use brighter color for ticks
                },
                grid: {
                    color: 'var(--border-color)', // Use theme color for grid lines
                }
            }
        }
    };

    if (loading) {
        return <div className="analytics-container"><p className="analytics-no-data-message">Loading analytics data...</p></div>;
    }

    if (error) {
        return <div className="analytics-container"><p className="analytics-no-data-message">Error: {error}</p></div>;
    }

    return (
        <div className="analytics-container">
            <h1 className="analytics-title">Analytics & Charts</h1>

            <div className="card analytics-filters-card">
                <div className="analytics-filter-group">
                    <label className="analytics-label">Team:</label>
                    <select value={selectedTeam} onChange={e => setSelectedTeam(e.target.value)} className="analytics-select">
                        <option value="">All Teams</option>
                        {teams.map(team => (
                            <option key={team.id} value={team.id}>{team.name} ({team.season})</option>
                        ))}
                    </select>
                </div>

                <div className="analytics-filter-group">
                    <label className="analytics-label">Players:</label>
                    <div className="analytics-checkbox-container">
                        <div className="analytics-checkbox-option">
                            <input
                                type="checkbox"
                                checked={players.length > 0 && selectedPlayers.length === players.length}
                                onChange={(e) => {
                                    if (e.target.checked) {
                                        setSelectedPlayers(players.map(p => p.id.toString()));
                                    } else {
                                        setSelectedPlayers([]);
                                    }
                                }}
                            />
                            <label className="select-all analytics-checkbox-option-label checkbox-label">Select All</label>
                        </div>
                        {players.map(player => (
                            <div key={player.id} className="analytics-checkbox-option">
                                <input
                                    type="checkbox"
                                    value={player.id}
                                    checked={selectedPlayers.includes(player.id.toString())}
                                    onChange={(e) => {
                                        const id = player.id.toString();
                                        if (e.target.checked) {
                                            setSelectedPlayers(prev => [...prev, id]);
                                        } else {
                                            setSelectedPlayers(prev => prev.filter(pId => pId !== id));
                                        }
                                    }}
                                />
                                <label className="analytics-checkbox-option-label checkbox-label">
                                    {player.first_name} {player.last_name}
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="analytics-filter-group">
                    <label className="analytics-label">Exercise:</label>
                    <select value={selectedExercise} onChange={e => setSelectedExercise(e.target.value)} className="analytics-select">
                        <option value="">Select Exercise</option>
                        {getFilteredExercises().map(exercise => (
                            <option key={exercise.id} value={exercise.id}>{exercise.name}</option>
                        ))}
                    </select>
                </div>

                <div className="analytics-filter-group">
                    <label className="analytics-label">Category:</label>
                    <select value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} className="analytics-select">
                        <option value="">All Categories</option>
                        {categories.map(category => (
                            <option key={category} value={category}>{category}</option>
                        ))}
                    </select>
                </div>

                <div className="analytics-date-range-group">
                    <div className="analytics-filter-group">
                        <label className="analytics-label">Date From:</label>
                        <input type="date" value={dateRange.from} onChange={e => setDateRange(prev => ({ ...prev, from: e.target.value }))} className="analytics-input" />
                    </div>

                    <div className="analytics-filter-group">
                        <label className="analytics-label">Date To:</label>
                        <input type="date" value={dateRange.to} onChange={e => setDateRange(prev => ({ ...prev, to: e.target.value }))} className="analytics-input" />
                    </div>
                </div>

                <div className="analytics-filter-group">
                    <label className="analytics-label">Chart Type:</label>
                    <select value={chartType} onChange={e => setChartType(e.target.value)} className="analytics-select">
                        <option value="line">Line Chart (Progress Over Time)</option>
                        <option value="bar">Bar Chart (Comparison)</option>
                    </select>
                </div>
            </div>


            {selectedPlayers.length > 0 && selectedExercise && measurementData.length > 0 ? (
                <div className="analytics-chart-container">
                    {chartType === 'line' ? (
                        <Line data={getChartData()} options={chartOptions} />
                    ) : (
                        <Bar data={getChartData()} options={chartOptions} />
                    )}
                </div>
            ) : (
                <p className="analytics-no-data-message">Select players and an exercise to view performance data.</p>
            )}
        </div>
    );
};

export default AnalyticsPage;
