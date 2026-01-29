import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './MeasurementEntryPage.css'; // Import the new CSS file

const MeasurementEntryPage = () => {
    const { user, token, isCoach, isAdmin } = useAuth();
    const navigate = useNavigate();
    const { player_id: routePlayerId } = useParams();
    const [exercises, setExercises] = useState([]);
    const [players, setPlayers] = useState([]);
    const [selectedPlayerId, setSelectedPlayerId] = useState(routePlayerId || (user ? user.id : ''));
    const [selectedExercise, setSelectedExercise] = useState(null);
    const [measurementValues, setMeasurementValues] = useState({});
    const [notes, setNotes] = useState('');
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }

        const fetchData = async () => {
            try {
                // Fetch exercises
                const exercisesResponse = await axios.get(`${API_URL}/exercises`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setExercises(exercisesResponse.data);

                // If coach/admin and no player_id in URL, fetch players
                if ((isCoach || isAdmin) && !routePlayerId) {
                    const playersResponse = await axios.get(`${API_URL}/players`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    setPlayers(playersResponse.data);
                } else if (routePlayerId && user.id === parseInt(routePlayerId)) {
                    // If route has player_id and it's the current user, ensure selectedPlayerId is set
                    setSelectedPlayerId(routePlayerId);
                }


            } catch (err) {
                setError('Fehler beim Laden der Daten.');
                console.error('Error fetching data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [user, token, navigate, API_URL, routePlayerId, isCoach, isAdmin]);

    const handleExerciseChange = (e) => {
        const exerciseId = e.target.value;
        const exercise = exercises.find(ex => ex.id === parseInt(exerciseId));
        setSelectedExercise(exercise);
        setMeasurementValues({}); // Reset values for new exercise
        setNotes('');
        setError(null);
        setSuccess(false);
    };

    const handlePlayerChange = (e) => {
        setSelectedPlayerId(e.target.value);
    };

    const handleValueChange = (type, value) => {
        setMeasurementValues(prev => ({ ...prev, [type]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);
        setSubmitting(true);

        if (!selectedExercise) {
            setError('Bitte wählen Sie eine Übung aus.');
            setSubmitting(false);
            return;
        }
        if (!selectedPlayerId) {
            setError('Bitte wählen Sie einen Spieler aus.');
            setSubmitting(false);
            return;
        }

        const payload = {
            player_id: parseInt(selectedPlayerId),
            exercise_id: selectedExercise.id,
            values: Object.entries(measurementValues).map(([type, val]) => ({
                measurement_type: type,
                value: String(val)
            })),
            notes: notes,
        };

        try {
            await axios.post(`${API_URL}/measurements`, payload, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setSuccess(true);
            setMeasurementValues({});
            setNotes('');
            setSelectedExercise(null);
            // Optionally navigate back to dashboard or history
            // navigate('/dashboard');
        } catch (err) {
            setError('Fehler beim Speichern der Messung. Bitte versuchen Sie es erneut.');
            console.error('Error submitting measurement:', err);
            if (err.response && err.response.data && err.response.data.detail) {
                setError(`Fehler: ${err.response.data.detail}`);
            }
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return <div className="measurement-entry-container coach-loading">Lädt Daten...</div>;
    }

    // Combine error and success messages for better UX
    const statusMessage = error ? (
        <p className="measurement-entry-error">{error}</p>
    ) : success ? (
        <p className="measurement-entry-success">Messung erfolgreich gespeichert!</p>
    ) : null;

    return (
        <div className="measurement-entry-container">
            <h2 className="measurement-entry-title">Messung eingeben</h2>
            <form onSubmit={handleSubmit} className="measurement-entry-form">
                {(isCoach || isAdmin) && !routePlayerId && (
                    <div className="measurement-entry-form-group">
                        <label htmlFor="playerSelect" className="measurement-entry-label">Spieler auswählen:</label>
                        <select
                            id="playerSelect"
                            onChange={handlePlayerChange}
                            value={selectedPlayerId}
                            className="measurement-entry-select"
                            required
                        >
                            <option value="">-- Bitte wählen --</option>
                            {players.map(player => (
                                <option key={player.id} value={player.id}>
                                    {player.first_name} {player.last_name}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
                {routePlayerId && (user.id !== parseInt(routePlayerId)) && (
                    <div className="measurement-entry-form-group">
                        <label className="measurement-entry-label">Spieler:</label>
                        <p className="measurement-entry-label">
                            {players.find(p => p.id === parseInt(routePlayerId))?.first_name} {players.find(p => p.id === parseInt(routePlayerId))?.last_name}
                        </p>
                    </div>
                )}


                <div className="measurement-entry-form-group">
                    <label htmlFor="exerciseSelect" className="measurement-entry-label">Übung auswählen:</label>
                    <select
                        id="exerciseSelect"
                        onChange={handleExerciseChange}
                        value={selectedExercise ? selectedExercise.id : ''}
                        className="measurement-entry-select"
                        required
                    >
                        <option value="">-- Bitte wählen --</option>
                        {exercises.map(ex => (
                            <option key={ex.id} value={ex.id}>{ex.name}</option>
                        ))}
                    </select>
                </div>

                {selectedExercise && (
                    <>
                        <p className="measurement-entry-description">Beschreibung: {selectedExercise.description}</p>
                        {selectedExercise.measurement_types && selectedExercise.measurement_types.map((mt, index) => (
                            <div key={index} className="measurement-entry-form-group">
                                <label htmlFor={`value-${mt.measurement_type}`} className="measurement-entry-label">
                                    {mt.measurement_type} {mt.is_required ? '(erforderlich)' : ''}:
                                </label>
                                <input
                                    type="number"
                                    id={`value-${mt.measurement_type}`}
                                    value={measurementValues[mt.measurement_type] || ''}
                                    onChange={(e) => handleValueChange(mt.measurement_type, parseFloat(e.target.value))}
                                    required={mt.is_required}
                                    className="measurement-entry-input"
                                    step="0.01"
                                />
                            </div>
                        ))}
                        <div className="measurement-entry-form-group">
                            <label htmlFor="notes" className="measurement-entry-label">Notizen (optional):</label>
                            <textarea
                                id="notes"
                                value={notes}
                                onChange={(e) => setNotes(e.target.value)}
                                className="measurement-entry-textarea"
                                rows="3"
                                required={false}
                            ></textarea>
                        </div>
                    </>
                )}

                {statusMessage}

                <button type="submit" className="measurement-entry-button btn-primary" disabled={submitting || !selectedExercise || !selectedPlayerId}>
                    {submitting ? 'Speichert...' : 'Messung speichern'}
                </button>
            </form>
        </div>
    );
};

export default MeasurementEntryPage;