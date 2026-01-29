import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './CreateExercisePage.css'; // Import the new CSS file

const CreateExercisePage = () => {
    const navigate = useNavigate();
    const { token, user } = useAuth();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [categories, setCategories] = useState([]);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [measurementTypes, setMeasurementTypes] = useState([{ type: '', is_required: true }]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    useEffect(() => {
        // Fetch available categories from backend
        const fetchCategories = async () => {
            try {
                const response = await axios.get(`${API_URL}/exercises/categories`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setCategories(response.data);
            } catch (err) {
                console.error('Error fetching categories:', err);
                setError('Failed to load categories.');
            }
        };
        if (token) {
            fetchCategories();
        }
    }, [token, API_URL]);

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

            await axios.post(`${API_URL}/exercises`, payload, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            setSuccess(true);
            setName('');
            setDescription('');
            setSelectedCategories([]);
            setMeasurementTypes([{ type: '', is_required: true }]);
            // Redirect or provide feedback
            navigate('/exercises-management');
        } catch (err) {
            setError('Failed to create exercise.');
            console.error('Error creating exercise:', err);
            if (err.response && err.response.data && err.response.data.detail) {
                setError(`Error: ${err.response.data.detail}`);
            }
        } finally {
            setLoading(false);
        }
    };

    // Combine error and success messages for better UX
    const statusMessage = error ? (
        <p className="create-exercise-error">{error}</p>
    ) : success ? (
        <p className="create-exercise-success">Exercise created successfully!</p>
    ) : null;

    return (
        <div className="create-exercise-container">
            <h1 className="create-exercise-title">Create New Exercise</h1>
            <form onSubmit={handleSubmit} className="create-exercise-form">
                <div className="create-exercise-form-group">
                    <label htmlFor="name" className="create-exercise-label">Name:</label>
                    <input
                        type="text"
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="create-exercise-input"
                        required
                    />
                </div>
                <div className="create-exercise-form-group">
                    <label htmlFor="description" className="create-exercise-label">Description:</label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="create-exercise-textarea"
                        rows="3"
                        required
                    ></textarea>
                </div>

                <div className="create-exercise-form-group">
                    <label className="create-exercise-label">Categories:</label>
                    <div className="create-exercise-checkbox-group">
                        {categories.map(cat => (
                            <label key={cat} className="create-exercise-checkbox-label">
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

                <div className="create-exercise-form-group">
                    <label className="create-exercise-label">Measurement Types:</label>
                    {measurementTypes.map((mt, index) => (
                        <div key={index} className="create-exercise-measurement-type-item">
                            <select
                                value={mt.type}
                                onChange={(e) => handleMeasurementTypeChange(index, 'type', e.target.value)}
                                className="create-exercise-select"
                                required
                            >
                                <option value="">-- Select Type --</option>
                                <option value="seconds">seconds</option>
                                <option value="repetitions">repetitions</option>
                                <option value="kilograms">kilograms</option>
                                <option value="meters">meters</option>
                                <option value="centimeters">centimeters</option>
                            </select>
                            <label className="create-exercise-checkbox-label">
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
                    <button type="button" onClick={addMeasurementType} className="create-exercise-add-measurement-button">Add Measurement Type</button>
                </div>

                {statusMessage}

                <button type="submit" className="create-exercise-submit-button btn-primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Exercise'}
                </button>
            </form>
        </div>
    );
};

export default CreateExercisePage;
