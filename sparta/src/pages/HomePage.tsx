import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (code.length < 4) {
            setError('Code zu kurz');
            return;
        }

        setLoading(true);
        setError('');

        // TODO: Validate operator code against Supabase (Schritt 3)
        try {
            navigate(`/board?code=${code.toUpperCase()}`);
        } catch {
            setError('Ungültiger Code');
            setLoading(false);
        }
    };

    return (
        <div className="page-center">
            <div className="landing animate-fade-in">
                <div className="landing-logo">🏐</div>
                <h1 className="landing-title">Tormusik</h1>
                <p className="landing-subtitle">Operator-Code eingeben</p>

                <form onSubmit={handleSubmit} className="landing-form">
                    <input
                        id="operator-code-input"
                        type="text"
                        className={`input code-input ${error ? 'animate-shake' : ''}`}
                        placeholder="CODE"
                        value={code}
                        onChange={(e) => {
                            setCode(e.target.value.toUpperCase());
                            setError('');
                        }}
                        maxLength={8}
                        autoComplete="off"
                        autoFocus
                    />

                    {error && <p className="landing-error">{error}</p>}

                    <button
                        id="operator-code-submit"
                        type="submit"
                        className="btn btn-primary btn-lg landing-btn"
                        disabled={loading || code.length < 4}
                    >
                        {loading ? 'Verbinden…' : 'Starten'}
                    </button>
                </form>

                <a href="/admin" className="landing-admin-link">
                    Team-Verwaltung →
                </a>
            </div>
        </div>
    );
}
