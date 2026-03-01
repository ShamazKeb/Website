// import { useSearchParams } from 'react-router-dom';

// Placeholder data – will be loaded from Supabase/IndexedDB in Schritt 6
const PLAYERS = [
    { number: 2, name: 'Zarti', isGk: false },
    { number: 4, name: 'Frodo', isGk: false },
    { number: 5, name: 'Nike', isGk: false },
    { number: 6, name: 'Konrad', isGk: false },
    { number: 8, name: 'Doro', isGk: false },
    { number: 9, name: 'Mickie', isGk: false },
    { number: 10, name: 'Ross', isGk: false },
    { number: 11, name: 'Brutus', isGk: false },
    { number: 13, name: 'Simson', isGk: false },
    { number: 15, name: 'Pömpel', isGk: false },
    { number: 17, name: 'Ulf', isGk: false },
    { number: 19, name: 'Tobi', isGk: false },
    { number: 16, name: 'Lars', isGk: true },
    { number: 21, name: 'Johann', isGk: true },
];

export default function BoardPage() {
    // TODO: get code from URL and load team data (Schritt 3)
    const fieldPlayers = PLAYERS.filter(p => !p.isGk);
    const goalkeepers = PLAYERS.filter(p => p.isGk);

    return (
        <div className="board">
            {/* Geometric background pattern */}
            <div className="board-bg-pattern" />

            {/* ── Player Jerseys ──────────────────────────────── */}
            <section className="board-players">
                <div className="jersey-grid">
                    {fieldPlayers.map((p) => (
                        <button
                            key={p.number}
                            id={`player-btn-${p.number}`}
                            className="jersey-btn"
                        >
                            <div className="jersey-shape">
                                <span className="jersey-number">{p.number}</span>
                            </div>
                            <span className="jersey-name">{p.name}</span>
                        </button>
                    ))}
                    {goalkeepers.map((p) => (
                        <button
                            key={p.number}
                            id={`player-btn-${p.number}`}
                            className="jersey-btn jersey-btn--gk"
                        >
                            <div className="jersey-shape jersey-shape--gk">
                                <span className="jersey-number">{p.number}</span>
                            </div>
                            <span className="jersey-name">{p.name}</span>
                        </button>
                    ))}
                </div>
            </section>

            {/* ── Heim Row ────────────────────────────────────── */}
            <section className="board-row">
                <button id="btn-7m-heim" className="cat-btn cat-btn--heim">
                    <span className="cat-btn-big">7M</span>
                    <span className="cat-btn-label">Heim</span>
                </button>
                <button id="btn-tor-heim" className="cat-btn cat-btn--heim">
                    <span className="cat-btn-icon">✌️</span>
                    <span className="cat-btn-label">Heim</span>
                </button>
                <button id="btn-t1-heim" className="cat-btn cat-btn--heim">
                    <span className="cat-btn-big">T<sub>1</sub></span>
                    <span className="cat-btn-label">Heim</span>
                </button>
                <button id="btn-t2-heim" className="cat-btn cat-btn--heim">
                    <span className="cat-btn-big">T<sub>2</sub></span>
                    <span className="cat-btn-label">Heim</span>
                </button>
                <button id="btn-t3-heim" className="cat-btn cat-btn--heim">
                    <span className="cat-btn-big">T<sub>3</sub></span>
                    <span className="cat-btn-label">Heim</span>
                </button>
                <button id="btn-pause-1" className="cat-btn cat-btn--neutral">
                    <span className="cat-btn-small">Unter-<br />brechung</span>
                </button>
                <button id="btn-pause-2" className="cat-btn cat-btn--neutral">
                    <span className="cat-btn-small">Unter-<br />brechung</span>
                </button>
                <button id="btn-pause-3" className="cat-btn cat-btn--neutral">
                    <span className="cat-btn-small">Unter-<br />brechung</span>
                </button>
                <button id="btn-pause-4" className="cat-btn cat-btn--neutral">
                    <span className="cat-btn-small">Unter-<br />brechung</span>
                </button>
                {/* Spotify + Halbzeit on right side */}
                <button id="btn-halbzeit" className="cat-btn cat-btn--special">
                    <span className="cat-btn-small">Halbzeit</span>
                </button>
            </section>

            {/* ── Gast Row ────────────────────────────────────── */}
            <section className="board-row">
                <button id="btn-7m-gast" className="cat-btn cat-btn--gast">
                    <span className="cat-btn-big">7M</span>
                    <span className="cat-btn-label">Gast</span>
                </button>
                <button id="btn-tor-gast" className="cat-btn cat-btn--gast">
                    <span className="cat-btn-icon">✌️</span>
                    <span className="cat-btn-label">Gast</span>
                </button>
                <button id="btn-t1-gast" className="cat-btn cat-btn--gast">
                    <span className="cat-btn-big">T<sub>1</sub></span>
                    <span className="cat-btn-label">Gast</span>
                </button>
                <button id="btn-t2-gast" className="cat-btn cat-btn--gast">
                    <span className="cat-btn-big">T<sub>2</sub></span>
                    <span className="cat-btn-label">Gast</span>
                </button>
                <button id="btn-t3-gast" className="cat-btn cat-btn--gast">
                    <span className="cat-btn-big">T<sub>3</sub></span>
                    <span className="cat-btn-label">Gast</span>
                </button>
                <button id="btn-rote-karte" className="cat-btn cat-btn--danger">
                    <span className="cat-btn-small">Rote<br />Karte</span>
                </button>
                <button id="btn-wischer-1" className="cat-btn cat-btn--neutral">
                    <span className="cat-btn-icon">🧹</span>
                    <span className="cat-btn-small">Wischer</span>
                </button>
                <button id="btn-wischer-2" className="cat-btn cat-btn--neutral">
                    <span className="cat-btn-icon">🧹</span>
                    <span className="cat-btn-small">Wischer</span>
                </button>
                {/* Spacer */}
                <div className="cat-btn-spacer" />
                {/* STOP */}
                <button id="stop-btn" className="stop-btn">
                    <span className="stop-label">STOP</span>
                </button>
            </section>

            {/* ── Bottom Bar ──────────────────────────────────── */}
            <footer className="board-bottom">
                <button id="btn-nach-dem-spiel" className="bottom-bar-btn">
                    Nach dem Spiel →
                </button>
            </footer>
        </div>
    );
}
