// Configuration
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'
    : '/api';

const DEADLINE = new Date('2026-02-15T23:59:59');

// State
let players = [];
let leaderboard = [];
let selectedPlayer = null;

// DOM Elements
const playersGrid = document.getElementById('players-grid');
const leaderboardEl = document.getElementById('leaderboard');
const modalOverlay = document.getElementById('modal-overlay');
const modalPlayerName = document.getElementById('modal-player-name');
const modalRemainingEl = document.getElementById('modal-remaining');
const pushupCountInput = document.getElementById('pushup-count');
const submitBtn = document.getElementById('submit-btn');
const modalClose = document.getElementById('modal-close');
const quickButtons = document.querySelectorAll('.quick-btn');
const tabButtons = document.querySelectorAll('.tab-btn');
const searchInput = document.getElementById('search-input');

// Stats elements
const totalDoneEl = document.getElementById('total-done');
const completedPlayersEl = document.getElementById('completed-players');
const daysLeftEl = document.getElementById('days-left');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    updateCountdown();
    setInterval(updateCountdown, 60000);
    setupTabs();
    setupEventListeners();
});

function setupEventListeners() {
    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    submitBtn.addEventListener('click', submitPushups);

    quickButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const value = parseInt(btn.dataset.value);
            pushupCountInput.value = (parseInt(pushupCountInput.value) || 0) + value;
        });
    });

    pushupCountInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitPushups();
    });
    
    searchInput.addEventListener('input', (e) => renderPlayers(e.target.value));
}

// Tab functionality
function setupTabs() {
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;

            // Update buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update content
            document.getElementById('players-tab').classList.toggle('hidden', tab !== 'players');
            document.getElementById('leaderboard-tab').classList.toggle('hidden', tab !== 'leaderboard');
            
            // Show/hide search based on tab
            searchInput.parentElement.style.display = tab === 'players' ? 'block' : 'none';

            if (tab === 'leaderboard') {
                renderLeaderboard();
            } else {
                renderPlayers();
            }
        });
    });
}

// Data loading
async function loadData() {
    playersGrid.innerHTML = '<div class="loading">Lädt Spieler...</div>';
    try {
        const [playersRes, statsRes, leaderboardRes] = await Promise.all([
            fetch(`${API_URL}/players`),
            fetch(`${API_URL}/stats`),
            fetch(`${API_URL}/leaderboard`)
        ]);

        if (!playersRes.ok) throw new Error(`Failed to load players (${playersRes.status})`);
        if (!statsRes.ok) throw new Error(`Failed to load stats (${statsRes.status})`);
        if (!leaderboardRes.ok) throw new Error(`Failed to load leaderboard (${leaderboardRes.status})`);

        players = await playersRes.json();
        const stats = await statsRes.json();
        leaderboard = await leaderboardRes.json();
        
        updateStats(stats);
        renderPlayers();
        renderLeaderboard();

    } catch (error) {
        console.error('Error loading data:', error);
        playersGrid.innerHTML = `
            <div class="loading">
                ❌ Fehler beim Laden.<br>
                <small>${error.message}</small>
            </div>
        `;
    }
}

function updateStats(stats) {
    totalDoneEl.textContent = stats.total_done.toLocaleString('de-DE');
    completedPlayersEl.textContent = stats.completed_players;
}

function renderPlayers(filter = '') {
    const sortedPlayers = [...players].sort((a, b) => {
        const aCompleted = a.total_remaining === 0;
        const bCompleted = b.total_remaining === 0;
        if (aCompleted && !bCompleted) return 1;
        if (!aCompleted && bCompleted) return -1;
        return a.name.localeCompare(b.name);
    });
    
    const filteredPlayers = sortedPlayers.filter(p => p.name.toLowerCase().includes(filter.toLowerCase()));

    if (filteredPlayers.length === 0) {
        playersGrid.innerHTML = `<div class="loading">Keine Spieler gefunden.</div>`;
        return;
    }

    playersGrid.innerHTML = filteredPlayers.map(player => {
        const target = player.target_goal;
        const progress = (player.total_remaining / target) * 100;
        const isCompleted = player.total_remaining === 0;

        return `
            <div class="player-card ${isCompleted ? 'completed' : ''}" 
                 onclick="openModal(${player.id})"
                 data-player-id="${player.id}">
                <div class="player-name">${player.name}</div>
                <div class="player-remaining">
                    ${isCompleted ? 'Fertig!' : player.total_remaining}
                    ${!isCompleted ? `<span>übrig von ${target}</span>` : ''}
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${100 - progress}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

function renderLeaderboard() {
    leaderboardEl.innerHTML = leaderboard.map(entry => `
        <div class="leaderboard-entry ${entry.completed ? 'completed' : ''}">
            <div class="leaderboard-rank">#${entry.rank}</div>
            <div class="leaderboard-name">${entry.name}</div>
            <div class="leaderboard-progress">
                <div class="leaderboard-progress-bar">
                    <div class="leaderboard-progress-fill" style="width: ${entry.percentage}%"></div>
                </div>
                <div class="leaderboard-progress-text">${entry.done}/${entry.target}</div>
            </div>
            <div class="leaderboard-percentage">${entry.percentage.toFixed(1)}%</div>
        </div>
    `).join('');
}

function openModal(playerId) {
    selectedPlayer = players.find(p => p.id === playerId);
    if (!selectedPlayer || selectedPlayer.total_remaining === 0) return;

    modalPlayerName.textContent = selectedPlayer.name;
    modalRemainingEl.innerHTML = `Noch <span>${selectedPlayer.total_remaining}</span> übrig`;
    pushupCountInput.value = '';
    pushupCountInput.max = selectedPlayer.total_remaining;
    
    modalOverlay.classList.add('active');
    setTimeout(() => pushupCountInput.focus(), 100);
}

function closeModal() {
    modalOverlay.classList.remove('active');
    selectedPlayer = null;
}

async function submitPushups() {
    const count = parseInt(pushupCountInput.value);

    if (!count || count <= 0) {
        alert('Bitte eine gültige Zahl eingeben!');
        return;
    }

    if (!selectedPlayer) return;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Speichern...</span>';

    try {
        const response = await fetch(`${API_URL}/players/${selectedPlayer.id}/pushups`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to save');
        }
        
        // Success feedback
        submitBtn.innerHTML = '<span>Gespeichert! ✓</span>';

        setTimeout(() => {
            closeModal();
            loadData(); // Reload all data
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>Eintragen</span><span class="submit-icon">💪</span>';
        }, 800);

    } catch (error) {
        console.error('Error saving pushups:', error);
        alert(`Fehler beim Speichern: ${error.message}`);
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>Eintragen</span><span class="submit-icon">💪</span>';
    }
}

function updateCountdown() {
    const now = new Date();
    const diff = DEADLINE - now;

    if (diff <= 0) {
        daysLeftEl.textContent = '0';
        return;
    }

    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    daysLeftEl.textContent = days;
}
