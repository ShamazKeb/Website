import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PerformanceHistoryPage.css'; // Import the new CSS file

const PerformanceHistoryPage = () => {
    const { user, token } = useAuth();
    const navigate = useNavigate();
    const [measurements, setMeasurements] = useState([]);
    const [exercises, setExercises] = useState([]);
    const [selectedExerciseId, setSelectedExerciseId] = useState('');
    const [selectedMeasurementType, setSelectedMeasurementType] = useState('');
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }

        const fetchInitialData = async () => {
            try {
                // Fetch exercises
                const exercisesResponse = await axios.get(`${API_URL}/exercises`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setExercises(exercisesResponse.data);

                // Fetch measurements
                const measurementsResponse = await axios.get(`${API_URL}/players/me/measurements`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setMeasurements(measurementsResponse.data);

            } catch (err) {
                setError('Fehler beim Laden der Daten.');
                console.error('Error fetching initial data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchInitialData();
    }, [user, token, navigate, API_URL]);

    const handleFilterChange = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = {};
            if (selectedExerciseId) params.exercise_id = selectedExerciseId;
            if (dateFrom) params.date_from = dateFrom;
            if (dateTo) params.date_to = dateTo;

            const measurementsResponse = await axios.get(`${API_URL}/players/me/measurements`, {
                headers: { Authorization: `Bearer ${token}` },
                params: params
            });
            setMeasurements(measurementsResponse.data);
        } catch (err) {
            setError('Fehler beim Filtern der Messungen.');
            console.error('Error fetching filtered measurements:', err);
        } finally {
            setLoading(false);
        }
    };

    const getChartData = () => {
        if (!selectedMeasurementType || !selectedExerciseId) return [];

        const filtered = measurements.filter(m =>
            m.exercise_id === parseInt(selectedExerciseId) && m.values && m.values[selectedMeasurementType] !== undefined
        );

        return filtered.map(m => ({
            date: new Date(m.recorded_at).toLocaleDateString('de-DE'),
            value: m.values[selectedMeasurementType]
        })).sort((a, b) => new Date(a.date) - new Date(b.date));
    };

    if (loading) {
        return <div className="performance-history-container performance-history-loading">Lädt Leistungsverlauf...</div>;
    }

    if (error) {
        return <div className="performance-history-container performance-history-error">Fehler: {error}</div>;
    }

    const currentExercise = exercises.find(ex => ex.id === parseInt(selectedExerciseId));
    const availableMeasurementTypes = currentExercise ? currentExercise.measurement_types.map(mt => mt.measurement_type) : [];

    return (
        <div className="performance-history-container">
            <h2 className="performance-history-title">Leistungsverlauf</h2>

            <div className="performance-history-filter-section card">
                <div className="performance-history-form-group">
                    <label htmlFor="exerciseFilter" className="performance-history-label">Übung:</label>
                    <select
                        id="exerciseFilter"
                        value={selectedExerciseId}
                        onChange={(e) => {
                            setSelectedExerciseId(e.target.value);
                            setSelectedMeasurementType(''); // Reset measurement type when exercise changes
                        }}
                        className="performance-history-select"
                    >
                        <option value="">Alle Übungen</option>
                        {exercises.map(ex => (
                            <option key={ex.id} value={ex.id}>{ex.name}</option>
                        ))}
                    </select>
                </div>

                {selectedExerciseId && (
                    <div className="performance-history-form-group">
                        <label htmlFor="measurementTypeFilter" className="performance-history-label">Messtyp:</label>
                        <select
                            id="measurementTypeFilter"
                            value={selectedMeasurementType}
                            onChange={(e) => setSelectedMeasurementType(e.target.value)}
                            className="performance-history-select"
                        >
                            <option value="">Bitte Messtyp wählen</option>
                            {availableMeasurementTypes.map(type => (
                                <option key={type} value={type}>{type}</option>
                            ))}
                        </select>
                    </div>
                )}
                
                <div className="performance-history-form-group">
                    <label htmlFor="dateFrom" className="performance-history-label">Von Datum:</label>
                    <input
                        type="date"
                        id="dateFrom"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                        className="performance-history-input"
                    />
                </div>
                <div className="performance-history-form-group">
                    <label htmlFor="dateTo" className="performance-history-label">Bis Datum:</label>
                    <input
                        type="date"
                        id="dateTo"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                        className="performance-history-input"
                    />
                </div>
                <button onClick={handleFilterChange} className="btn-primary performance-history-filter-button">Filtern</button>
            </div>

            {selectedExerciseId && selectedMeasurementType && getChartData().length > 0 && (
                <div className="performance-history-chart-container card">
                    <h3 className="performance-history-chart-title">Leistungstrend für {currentExercise?.name} ({selectedMeasurementType})</h3>
                    <ResponsiveContainer width="100%" height="80%"> {/* Adjusted height to fit title */}
                        <LineChart data={getChartData()} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                            <XAxis dataKey="date" stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)' }} />
                            <YAxis stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: 'var(--background-card)', border: '1px solid var(--border-color)', color: 'var(--text-main)' }}
                                labelStyle={{ color: 'var(--primary-color)' }}
                                itemStyle={{ color: 'var(--text-light)' }}
                            />
                            <Legend wrapperStyle={{ color: 'var(--text-main)' }} />
                            <Line type="monotone" dataKey="value" stroke="var(--primary-color)" activeDot={{ r: 8 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}
             {selectedExerciseId && selectedMeasurementType && getChartData().length === 0 && (
                <p className="performance-history-no-data-message">Keine Daten für die ausgewählte Übung und den Messtyp im gewählten Zeitraum.</p>
            )}

            <h3 className="performance-history-section-title">Alle Messungen</h3>
            {measurements.length === 0 ? (
                <p className="performance-history-no-data-message">Keine Messungen gefunden.</p>
            ) : (
                <ul className="performance-history-measurement-list">
                    {measurements.map((measurement) => (
                        <li key={measurement.id} className="performance-history-measurement-item card">
                            <strong>Übung:</strong> {exercises.find(ex => ex.id === measurement.exercise_id)?.name || 'Unbekannt'} <br />
                            <strong>Datum:</strong> {new Date(measurement.recorded_at).toLocaleDateString()} <br />
                            <strong>Werte:</strong> {JSON.stringify(measurement.values)} <br />
                            {measurement.notes && <span><strong>Notizen:</strong> {measurement.notes}</span>}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default PerformanceHistoryPage;
