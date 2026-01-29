import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import DashboardPage from './components/DashboardPage';
import MeasurementEntryPage from './components/MeasurementEntryPage';
import PerformanceHistoryPage from './components/PerformanceHistoryPage'; // Import the new PerformanceHistoryPage
import CoachDashboardPage from './components/CoachDashboardPage'; // Import the new CoachDashboardPage
import TeamDetailsPage from './components/TeamDetailsPage'; // Import the new TeamDetailsPage
import PlayerMeasurementHistoryPage from './components/PlayerMeasurementHistoryPage'; // Import the new PlayerMeasurementHistoryPage
import CreatePlayerPage from './components/CreatePlayerPage'; // Import the new CreatePlayerPage
import ExerciseManagementPage from './components/ExerciseManagementPage'; // Import the new ExerciseManagementPage
import CreateExercisePage from './components/CreateExercisePage'; // Import the new CreateExercisePage
import EditExercisePage from './components/EditExercisePage'; // Import the new EditExercisePage
import AnalyticsPage from './components/AnalyticsPage'; // Import the new AnalyticsPage
import LeaderboardsPage from './components/LeaderboardsPage'; // Import the new LeaderboardsPage
import { useAuth } from './components/AuthContext';

import Navbar from './components/Navbar'; // Import Navbar

function App() {
    const { token, isCoach } = useAuth(); // Destructure isCoach from useAuth()

    return (
        <div className="App">
            <Navbar /> {/* Render Navbar */}
            <div className="main-content">
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route
                        path="/dashboard"
                        element={token ? (isCoach ? <Navigate to="/coach-dashboard" replace /> : <DashboardPage />) : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/record-measurement/:player_id?" // Make player_id optional
                        element={token ? <MeasurementEntryPage /> : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/performance-history"
                        element={token ? <PerformanceHistoryPage /> : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/coach-dashboard"
                        element={token ? (isCoach ? <CoachDashboardPage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/teams/:id"
                        element={token ? (isCoach ? <TeamDetailsPage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/players/:id/measurements"
                        element={token ? (isCoach ? <PlayerMeasurementHistoryPage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/teams/:id/players/create"
                        element={token ? (isCoach ? <CreatePlayerPage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/exercises-management"
                        element={token ? (isCoach ? <ExerciseManagementPage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/exercises/create"
                        element={token ? (isCoach ? <CreateExercisePage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />}
                    />
                    <Route
                        path="/exercises/:id/edit"
                        element={token ? (isCoach ? <EditExercisePage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />} />
                    <Route
                        path="/analytics"
                        element={token ? (isCoach ? <AnalyticsPage /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />} />
                    <Route
                        path="/leaderboards"
                        element={token ? <LeaderboardsPage /> : <Navigate to="/login" replace />} />
                    <Route path="*" element={token ? (isCoach ? <Navigate to="/coach-dashboard" replace /> : <Navigate to="/dashboard" replace />) : <Navigate to="/login" replace />} />
                </Routes>
            </div>
        </div>
    );
}

export default App;