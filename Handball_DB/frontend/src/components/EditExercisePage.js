import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './EditExercisePage.css'; // Import the new CSS file

const EditExercisePage = () => {
    const { id } = useParams(); // Exercise ID from URL
    const navigate = useNavigate();
    const { token, user } = useAuth();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [categories, setCategories] = useState([]); // All available categories
    const [selectedCategories, setSelectedCategories] = useState([]); // Categories for this exercise
    const [measurementTypes, setMeasurementTypes] = useState([]); // Measurement types for this exercise
    const [allMeasurementTypes, setAllMeasurementTypes] = useState([]); // All possible measurement types (e.g., seconds, repetitions)
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (!user || !token) {
            navigate('/login');
            return;
        }

        const fetchExerciseData = async () => {
            try {
                // Fetch available categories
                const categoriesResponse = await axios.get(`${API_URL}/exercises/categories`, { headers: { Authorization: `Bearer ${token}` } });
                setCategories(categoriesResponse.data);

                // Fetch all possible measurement types (assuming an endpoint /measurement-types)
                // For simplicity, we'll hardcode them as in CreateExercisePage.js for now if no specific endpoint exists.
                // If a `/measurement-types` endpoint is implemented, use it.
                setAllMeasurementTypes(['seconds', 'repetitions', 'kilograms', 'meters', 'centimeters']);


                // Fetch exercise details
                const exerciseResponse = await axios.get(`${API_URL}/exercises/${id}`, { headers: { Authorization: `Bearer ${token}` } });
                const exerciseData = exerciseResponse.data;

                setName(exerciseData.name);
                setDescription(exerciseData.description);
                setSelectedCategories(exerciseData.categories || []);
                setMeasurementTypes(exerciseData.measurement_types.map(mt => ({
                    type: mt.measurement_type,
                    is_required: mt.is_required
                })));

            } catch (err) {
                setError('Failed to fetch exercise data.');
                console.error('Error fetching exercise data:', err);
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchExerciseData();
        }
    }, [id, user, token, navigate, API_URL]);

    const handleCategoryChange = (e) => {
        const { value, checked } = e.target;
        if (checked) {
            setSelectedCategories(prev => [...prev, value]);
        } else {
            setSelectedCategories(prev => prev.filter(cat => cat !== value));
        }
    };

    const handleMeasurementTypeChange = (index, field, value) => {
        const newMeasurementTypes = [...measurementTypes];
        newMeasurementTypes[index][field] = value;
        setMeasurementTypes(newMeasurementTypes);
    };

    const addMeasurementType = () => {
        setMeasurementTypes(prev => [...prev, { type: '', is_required: true }]);
    };

    const removeMeasurementType = (index) => {
        setMeasurementTypes(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(false);
        setLoading(true);

        // Basic validation
        if (!name || !description || selectedCategories.length === 0 || measurementTypes.length === 0) {
            setError('Please fill in all required fields and select at least one category and one measurement type.');
            setLoading(false);
            return;
        }
        if (measurementTypes.some(mt => !mt.type)) {
            setError('All measurement types must have a selected type.');
            setLoading(false);
            return;
        }

        try {
            const payload = {
                name,
                description,
                categories: selectedCategories,
                measurement_types: measurementTypes.map(mt => ({
                    measurement_type: mt.type,
                    is_required: mt.is_required
                }))
            };

            await axios.put(`${API_URL}/exercises/${id}`, payload, { // Use PUT for update
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            setSuccess(true);
            // Redirect or provide feedback
            navigate('/exercises-management');
        } catch (err) {
            setError('Failed to update exercise.');
            console.error('Error updating exercise:', err);
            if (err.response && err.response.data && err.response.data.detail) {
                setError(`Error: ${err.response.data.detail}`);
            }
        } finally {
            setLoading(false);
        }
    };

    // Combine error and success messages for better UX
    const statusMessage = error ? (
        <p className="edit-exercise-error">{error}</p>
    ) : success ? (
        <p className="edit-exercise-success">Exercise updated successfully!</p>
    ) : null;

    if (loading) {
        return <div className="edit-exercise-container edit-exercise-loading">Loading exercise data...</div>;
    }

    return (
        <div className="edit-exercise-container">
            <h1 className="edit-exercise-title">Edit Exercise</h1>
            <form onSubmit={handleSubmit} className="edit-exercise-form">
                <div className="edit-exercise-form-group">
                    <label htmlFor="name" className="edit-exercise-label">Name:</label>
                    <input
                        type="text"
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="edit-exercise-input"
                        required
                    />
                </div>
                <div className="edit-exercise-form-group">
                    <label htmlFor="description" className="edit-exercise-label">Description:</label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="edit-exercise-textarea"
                        rows="3"
                        required
                    ></textarea>
                </div>

                <div className="edit-exercise-form-group">
                    <label className="edit-exercise-label">Categories:</label>
                    <div className="edit-exercise-checkbox-group">
                        {categories.map(cat => (
                            <label key={cat} className="edit-exercise-checkbox-label">
                                <input
                                    type="checkbox"
                                    value={cat}
                                    checked={selectedCategories.includes(cat)}
                                    onChange={handleCategoryChange}
                                />
                                {cat}
                            </label>
                        ))}
                    </div>
                </div>

                <div className="edit-exercise-form-group">
                    <label className="edit-exercise-label">Measurement Types:</label>
                    {measurementTypes.map((mt, index) => (
                        <div key={index} className="edit-exercise-measurement-type-item">
                            <select
                                value={mt.type}
                                onChange={(e) => handleMeasurementTypeChange(index, 'type', e.target.value)}
                                className="edit-exercise-select"
                                required
                            >
                                <option value="">-- Select Type --</option>
                                {allMeasurementTypes.map(type => (
                                    <option key={type} value={type}>{type}</option>
                                ))}
                            </select>
                            <label className="edit-exercise-checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={mt.is_required}
                                    onChange={(e) => handleMeasurementTypeChange(index, 'is_required', e.target.checked)}
                                />
                                Required
                            </label>
                            {measurementTypes.length > 1 && (
                                <button type="button" onClick={() => removeMeasurementType(index)} className="btn-danger">Remove</button>
                            )}
                        </div>
                    ))}
                    <button type="button" onClick={addMeasurementType} className="edit-exercise-add-measurement-button">Add Measurement Type</button>
                </div>

                {statusMessage}

                <button type="submit" className="edit-exercise-submit-button btn-primary" disabled={loading}>
                    {loading ? 'Updating...' : 'Update Exercise'}
                </button>
            </form>
        </div>
    );
};

export default EditExercisePage;
