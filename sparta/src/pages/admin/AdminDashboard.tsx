export default function AdminDashboard() {
    return (
        <div className="animate-fade-in">
            <h1>Dashboard</h1>
            <p style={{ color: 'var(--color-text-muted)', marginTop: 'var(--space-sm)' }}>
                Team-Übersicht und Verwaltung – wird in Schritt 8 implementiert.
            </p>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: 'var(--space-lg)',
                marginTop: 'var(--space-xl)',
            }}>
                <div className="card">
                    <h3>👥 Kader</h3>
                    <p style={{ color: 'var(--color-text-muted)', marginTop: 'var(--space-sm)' }}>
                        0 / 16 Spieler angelegt
                    </p>
                </div>
                <div className="card">
                    <h3>🎵 Sounds</h3>
                    <p style={{ color: 'var(--color-text-muted)', marginTop: 'var(--space-sm)' }}>
                        0 Tracks hochgeladen
                    </p>
                </div>
                <div className="card">
                    <h3>🎮 Spieltag</h3>
                    <p style={{ color: 'var(--color-text-muted)', marginTop: 'var(--space-sm)' }}>
                        Kein aktiver Operator-Code
                    </p>
                </div>
            </div>
        </div>
    );
}
