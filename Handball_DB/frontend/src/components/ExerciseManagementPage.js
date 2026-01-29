import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import axios from 'axios';
import './ExerciseManagementPage.css'; // Import the new CSS file

const ExerciseManagementPage = () => {
    const navigate = useNavigate();
    const { token, user } = useAuth();
    const [exercises, setExercises] = useState([]);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [expandedExerciseId, setExpandedExerciseId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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
            // Don't block loading exercises if categories fail, but log it
        }
    };

    const fetchExercises = async () => {
        try {
            const response = await axios.get(`${API_URL}/exercises`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            // Filter exercises to show only those owned by the current coach, or all if admin
            const filteredExercises = response.data.filter(ex => user.role === 'admin' || ex.owner_coach_id === user.id);
            setExercises(filteredExercises);
        } catch (err) {
            setError('Failed to fetch exercises.');
            console.error('Error fetching exercises:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!user || !token) {
            navigate('/login');
            return;
        }
        fetchCategories();
        fetchExercises();
    }, [user, token, navigate, API_URL]);

    const handleCreateExercise = () => {
        navigate('/exercises/create');
    };

    const handleEditExercise = (exerciseId, e) => {
        e.stopPropagation(); // Prevent toggling expansion
        navigate(`/exercises/${exerciseId}/edit`);
    };

    const handleArchiveExercise = async (exerciseId, e) => {
        e.stopPropagation(); // Prevent toggling expansion
        if (window.confirm('Are you sure you want to archive this exercise?')) {
            try {
                await axios.patch(`${API_URL}/exercises/${exerciseId}`, { is_active: false }, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                alert('Exercise archived successfully!');
                fetchExercises(); // Re-fetch exercises to update the list
            } catch (err) {
                setError('Failed to archive exercise.');
                console.error('Error archiving exercise:', err);
                if (err.response && err.response.data && err.response.data.detail) {
                    setError(`Error: ${err.response.data.detail}`);
                }
            }
        }
    };

    const toggleExpand = (exerciseId) => {
        setExpandedExerciseId(expandedExerciseId === exerciseId ? null : exerciseId);
    };

    // Filter Logic
    const displayedExercises = selectedCategory
        ? exercises.filter(ex => ex.categories && ex.categories.includes(selectedCategory))
        : []; // Show nothing if no category selected

    if (loading) {
        return <div className="exercise-management-container exercise-management-loading">Loading exercises...</div>;
    }

    if (error) {
        return <div className="exercise-management-container exercise-management-error">Error: {error}</div>;
    }

    return (
        <div className="exercise-management-container">
            <h1 className="exercise-management-title">Exercise Management</h1>

            <button onClick={handleCreateExercise} className="btn-primary exercise-management-create-button">Create New Exercise</button>

            <div className="card exercise-management-filter-card">
                <label className="exercise-management-filter-label">Filter by Category: </label>
                <select
                    value={selectedCategory}
                    onChange={(e) => {
                        setSelectedCategory(e.target.value);
                        setExpandedExerciseId(null);
                    }}
                    className="exercise-management-select"
                >
                    <option value="">-- Select a Category --</option>
                    {categories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                    ))}
                </select>
            </div>

            <h2 className="exercise-management-section-title">My Exercises</h2>
            {!selectedCategory ? (
                <p className="exercise-management-no-category-selected">Please select a category to view exercises.</p>
            ) : displayedExercises.length === 0 ? (
                <p className="exercise-management-no-exercises">No exercises found for this category.</p>
            ) : (
                <div className="exercise-management-list">
                    {displayedExercises.map(exercise => (
                        <div
                            key={exercise.id}
                            className={`card exercise-management-item ${expandedExerciseId === exercise.id ? 'expanded' : ''}`}
                            onClick={() => toggleExpand(exercise.id)}
                        >
                            <div className="exercise-management-item-header">
                                <h3 className="exercise-management-item-title">{exercise.name} {exercise.is_active ? '' : '(Archived)'}</h3>
                                <span className="exercise-management-expand-icon">{expandedExerciseId === exercise.id ? '▼' : '▶'}</span>
                            </div>

                            {expandedExerciseId === exercise.id && (
                                <div className="exercise-management-item-details">
                                    <p><strong>Description:</strong> {exercise.description}</p>
                                    <p><strong>Categories:</strong> {exercise.categories ? exercise.categories.join(', ') : 'None'}</p>
                                    <div className="exercise-management-item-actions">
                                        <button onClick={(e) => handleEditExercise(exercise.id, e)} className="btn-primary exercise-management-edit-button">Edit</button>
                                        {exercise.is_active && (
                                            <button onClick={(e) => handleArchiveExercise(exercise.id, e)} className="btn-danger exercise-management-archive-button">Archive</button>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ExerciseManagementPage;
