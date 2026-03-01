import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import BoardPage from './pages/BoardPage';
import AdminLayout from './pages/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import RosterPage from './pages/admin/RosterPage';
import SoundsPage from './pages/admin/SoundsPage';
import GamePage from './pages/admin/GamePage';

export default function App() {
    return (
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/board" element={<BoardPage />} />
            <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<AdminDashboard />} />
                <Route path="roster" element={<RosterPage />} />
                <Route path="sounds" element={<SoundsPage />} />
                <Route path="game" element={<GamePage />} />
            </Route>
        </Routes>
    );
}
