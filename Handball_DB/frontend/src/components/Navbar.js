import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

const Navbar = () => {
    const { user, logout, isCoach } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!user) return null; // Don't show navbar if not logged in

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <Link to={isCoach ? "/coach-dashboard" : "/dashboard"}>Handball DB</Link>
            </div>
            <div className="navbar-links">
                {isCoach ? (
                    <>
                        <Link to="/coach-dashboard" className={location.pathname === '/coach-dashboard' ? 'active' : ''}>Dashboard</Link>
                        <Link to="/exercises-management" className={location.pathname === '/exercises-management' ? 'active' : ''}>Exercises</Link>
                        <Link to="/analytics" className={location.pathname === '/analytics' ? 'active' : ''}>Analytics</Link>
                        <Link to="/leaderboards" className={location.pathname === '/leaderboards' ? 'active' : ''}>Leaderboards</Link>
                    </>
                ) : (
                    <>
                        <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>Dashboard</Link>
                        <Link to="/performance-history" className={location.pathname === '/performance-history' ? 'active' : ''}>My Performance</Link>
                        <Link to="/leaderboards" className={location.pathname === '/leaderboards' ? 'active' : ''}>Leaderboards</Link>
                    </>
                )}
            </div>
            <div className="navbar-user">
                <span className="user-email">{user.email}</span>
                <button onClick={handleLogout} className="btn-logout">Logout</button>
            </div>
        </nav>
    );
};

export default Navbar;
