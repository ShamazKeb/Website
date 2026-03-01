import { NavLink, Outlet } from 'react-router-dom';

export default function AdminLayout() {
    return (
        <div className="admin-layout">
            <nav className="admin-nav">
                <NavLink to="/admin" className="admin-nav-brand" end>
                    🏐 Tormusik Admin
                </NavLink>
                <div className="admin-nav-links">
                    <NavLink to="/admin/roster" className={({ isActive }) => `admin-nav-link ${isActive ? 'active' : ''}`}>
                        Kader
                    </NavLink>
                    <NavLink to="/admin/sounds" className={({ isActive }) => `admin-nav-link ${isActive ? 'active' : ''}`}>
                        Sounds
                    </NavLink>
                    <NavLink to="/admin/game" className={({ isActive }) => `admin-nav-link ${isActive ? 'active' : ''}`}>
                        Spieltag
                    </NavLink>
                </div>
            </nav>
            <main className="admin-content">
                <Outlet />
            </main>
        </div>
    );
}
