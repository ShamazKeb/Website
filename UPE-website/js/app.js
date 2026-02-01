document.addEventListener('DOMContentLoaded', async () => {

    // --- DOM ELEMENTS ---
    const beverageForm = document.getElementById('beverage-form');
    const leaderboardContainer = document.getElementById('leaderboard-container');
    const filterType = document.getElementById('filter-type');
    const filterStore = document.getElementById('filter-store');
    const formMessage = document.getElementById('form-message');

    // --- API SETUP ---
    const API_URL = '';

    // --- DATA ---
    let masterBeverageList = [];

    // --- CORE LOGIC ---
    const calculateUPE = (volume, price, alcohol) => {
        if (price <= 0 || volume <= 0 || alcohol <= 0) return 0;
        const totalAlcoholVolume = volume * (alcohol / 100);
        return totalAlcoholVolume / price;
    };

    const renderLeaderboard = (data) => {
        leaderboardContainer.innerHTML = '';
        if (data.length === 0) {
            leaderboardContainer.innerHTML = `<div class="text-center text-gray-300 p-8">Keine Ergebnisse gefunden.</div>`;
            return;
        }

        data.forEach(bev => {
            bev.upe = calculateUPE(bev.volume, bev.price, bev.alcohol_content);
        });

        data.sort((a, b) => b.upe - a.upe);

        data.forEach((beverage, index) => {
            const isTopDeal = index === 0;
            const item = document.createElement('div');
            item.className = `p-4 rounded-md leaderboard-item type-${beverage.type}`;
            item.style.animationDelay = `${index * 0.05}s`;
            item.innerHTML = `
                <div class="flex items-center">
                    ${isTopDeal ? '<span class="top-deal-badge text-xs px-2 py-1 rounded-full mr-4">TOP DEAL</span>' : ''}
                    <div>
                        <h3 class="font-chakra-petch text-lg text-white">${beverage.name}</h3>
                        <p class="text-sm text-gray-400">${beverage.store} | ${beverage.volume}L | ${beverage.price.toFixed(2)}€ | ${beverage.alcohol_content}% Alc.</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="font-chakra-petch text-xl text-emerald-400">${beverage.upe.toFixed(3)}</span>
                    <p class="text-xs text-gray-400">UPE-Score</p>
                </div>
            `;
            leaderboardContainer.appendChild(item);
        });
    };

    const applyFilters = () => {
        const typeFilter = filterType.value;
        const storeFilter = filterStore.value;

        const filteredBeverages = masterBeverageList.filter(bev => {
            const typeMatch = typeFilter === 'all' || bev.type === typeFilter;
            const storeMatch = storeFilter === 'all' || !storeFilter || bev.store === storeFilter;
            return typeMatch && storeMatch;
        });
        renderLeaderboard(filteredBeverages);
    };

    // --- API FUNCTIONS ---

    const getBeverages = async () => {
        leaderboardContainer.innerHTML = `<div class="text-center text-gray-300 p-8">Lade Leaderboard...</div>`;
        try {
            const response = await fetch(`${API_URL}/beverages/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            masterBeverageList = await response.json();
            applyFilters();
        } catch (error) {
            console.error('Error fetching beverages:', error);
            leaderboardContainer.innerHTML = `<div class="text-center text-red-400 p-8">Fehler: Backend-Server scheint nicht zu laufen.</div>`;
        }
    };

    const addBeverage = async (beverageData) => {
        try {
            const response = await fetch(`${API_URL}/beverages/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(beverageData),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return true;
        } catch (error) {
            console.error('Error adding beverage:', error);
            formMessage.textContent = 'Fehler beim Speichern!';
            formMessage.style.color = 'red';
            return false;
        }
    };

    // --- EVENT LISTENERS ---

    beverageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitButton = e.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Speichere...';

        const formData = new FormData(beverageForm);
        const newBeverage = {
            name: formData.get('name'),
            type: formData.get('type'),
            volume: parseFloat(formData.get('container_volume')),
            price: parseFloat(formData.get('price')),
            store: formData.get('store'),
            alcohol_content: parseFloat(formData.get('alcohol-content')),
        };

        const newUpe = calculateUPE(newBeverage.volume, newBeverage.price, newBeverage.alcohol_content);
        const isNewTopDeal = masterBeverageList.every(bev => newUpe > calculateUPE(bev.volume, bev.price, bev.alcohol_content));

        const success = await addBeverage(newBeverage);

        if (success) {
            await getBeverages(); // Refresh the whole list from the API
            formMessage.textContent = 'Getränk erfolgreich hinzugefügt!';
            formMessage.style.color = '#34d399';
            beverageForm.reset();

            if (isNewTopDeal && confetti) {
                confetti({ particleCount: 150, spread: 180, origin: { y: 0.6 } });
            }
        }

        setTimeout(() => formMessage.textContent = '', 3000);
        submitButton.disabled = false;
        submitButton.textContent = 'Berechnen & Einreichen';
    });

    filterType.addEventListener('change', applyFilters);
    filterStore.addEventListener('change', applyFilters);

    // --- INITIALIZATION ---
    await getBeverages();
});

