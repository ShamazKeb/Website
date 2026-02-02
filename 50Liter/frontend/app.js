// Configuration
const API_URL = window.location.hostname === 'localhost'
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
const modalRemaining = document.getElementById('modal-remaining');
const pushupCountInput = document.getElementById('pushup-count');
const submitBtn = document.getElementById('submit-btn');
const modalClose = document.getElementById('modal-close');
const quickButtons = document.querySelectorAll('.quick-btn');
const tabButtons = document.querySelectorAll('.tab-btn');

// Stats elements
const totalDoneEl = document.getElementById('total-done');
const completedPlayersEl = document.getElementById('completed-players');
const daysLeftEl = document.getElementById('days-left');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPlayers();
    loadLeaderboard();
    updateCountdown();
    setInterval(updateCountdown, 60000);
    setupTabs();
});

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

            // Reload leaderboard when switching to it
            if (tab === 'leaderboard') {
                loadLeaderboard();
            }
        });
    });
}

// Event Listeners
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

// Functions
async function loadPlayers() {
    playersGrid.innerHTML = '<div class="loading">Lädt Spieler...</div>';

    try {
        const response = await fetch(`${API_URL}/players`);
        if (!response.ok) throw new Error('Failed to load players');

        players = await response.json();
        renderPlayers();
        loadStats();
    } catch (error) {
        console.error('Error loading players:', error);
        playersGrid.innerHTML = `
            <div class="loading">
                ❌ Fehler beim Laden.<br>
                <small>Backend erreichbar? (${API_URL})</small>
            </div>
        `;
    }
}

async function loadLeaderboard() {
    try {
        const response = await fetch(`${API_URL}/leaderboard`);
        if (!response.ok) throw new Error('Failed to load leaderboard');

        leaderboard = await response.json();
        renderLeaderboard();
    } catch (error) {
        console.error('Error loading leaderboard:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        if (!response.ok) throw new Error('Failed to load stats');

        const stats = await response.json();
        totalDoneEl.textContent = stats.total_done.toLocaleString('de-DE');
        completedPlayersEl.textContent = stats.completed_players;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function renderPlayers() {
    // Sort: players with remaining first, then completed
    const sortedPlayers = [...players].sort((a, b) => {
        if (a.total_remaining === 0 && b.total_remaining > 0) return 1;
        if (b.total_remaining === 0 && a.total_remaining > 0) return -1;
        return a.total_remaining - b.total_remaining;
    });

    playersGrid.innerHTML = sortedPlayers.map(player => {
        // Andilaus has 1000, others 500
        const target = player.name === 'Andilaus' ? 1000 : 500;
        const done = target - player.total_remaining;
        const progress = (done / target) * 100;
        const isCompleted = player.total_remaining === 0;

        return `
            <div class="player-card ${isCompleted ? 'completed' : ''}" 
                 onclick="openModal(${player.id})"
                 data-player-id="${player.id}">
                <div class="player-name">${player.name}</div>
                <div class="player-remaining">
                    ${player.total_remaining} <span>übrig</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
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
            <div class="leaderboard-percentage">${entry.percentage}%</div>
        </div>
    `).join('');
}

function openModal(playerId) {
    selectedPlayer = players.find(p => p.id === playerId);
    if (!selectedPlayer) return;

    modalPlayerName.textContent = selectedPlayer.name;
    modalRemaining.textContent = selectedPlayer.total_remaining;
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

        if (!response.ok) throw new Error('Failed to save');

        const updatedPlayer = await response.json();

        // Update local state
        const index = players.findIndex(p => p.id === selectedPlayer.id);
        if (index !== -1) {
            players[index] = updatedPlayer;
        }

        // Success feedback
        submitBtn.innerHTML = '<span>Gespeichert! ✓</span>';

        setTimeout(() => {
            closeModal();
            renderPlayers();
            loadStats();
            loadLeaderboard();
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>Eintragen</span><span class="submit-icon">💪</span>';
        }, 800);

    } catch (error) {
        console.error('Error saving pushups:', error);
        alert('Fehler beim Speichern! Bitte nochmal versuchen.');
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
