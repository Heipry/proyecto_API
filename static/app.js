
// Estado de la aplicación
let selectedGogItem = null;
let selectedSteamItem = null;

// Referencias DOM
const searchInput = document.getElementById('searchInput');
const resultsArea = document.getElementById('resultsArea');
const actionArea = document.getElementById('actionArea');
const btnCompare = document.getElementById('btnCompare');
const gogList = document.getElementById('gogList');
const steamList = document.getElementById('steamList');
const verdictArea = document.getElementById('verdictArea');

// Permitir buscar con Enter
searchInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') buscarJuegos();
});

async function buscarJuegos() {
    const query = searchInput.value.trim();
    if (!query) return;

    // Reset UI
    resultsArea.classList.add('d-none');
    actionArea.classList.add('d-none');
    verdictArea.classList.add('d-none');
    selectedGogItem = null;
    selectedSteamItem = null;
    updateCompareButton();

    // Mostrar Loading (opcional, simple cambio de texto)
    const btn = document.getElementById('btnSearch');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Buscando...';
    btn.disabled = true;

    try {
        const response = await fetch(`/search/${encodeURIComponent(query)}`);
        const data = await response.json();

        renderLists(data.gog, data.steam);
        resultsArea.classList.remove('d-none');
        actionArea.classList.remove('d-none');

    } catch (error) {
        alert("Error conectando con la API. ¿Está el backend encendido?");
        console.error(error);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function renderLists(gogData, steamData) {
    gogList.innerHTML = '';
    steamList.innerHTML = '';

    // Render GOG
    if(gogData.length === 0) gogList.innerHTML = '<div class="p-3 text-muted">Sin resultados</div>';
    gogData.forEach(game => {
        const item = document.createElement('button');
        item.className = 'list-group-item list-group-item-action cursor-pointer';
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <strong>${game.title}</strong>
                <small class="badge bg-secondary rounded-pill">ID: ${game.id}</small>
            </div>
        `;
        item.onclick = () => selectItem('gog', game, item);
        gogList.appendChild(item);
    });

    // Render Steam
    if(steamData.length === 0) steamList.innerHTML = '<div class="p-3 text-muted">Sin resultados</div>';
    steamData.forEach(game => {
        const item = document.createElement('button');
        item.className = 'list-group-item list-group-item-action cursor-pointer';
        item.innerHTML = `
             <div class="d-flex justify-content-between align-items-center">
                <strong>${game.title}</strong>
                <small class="badge bg-dark rounded-pill">ID: ${game.id}</small>
            </div>
        `;
        item.onclick = () => selectItem('steam', game, item);
        steamList.appendChild(item);
    });
}

function selectItem(platform, game, domElement) {
    if (platform === 'gog') {
        selectedGogItem = game;
        // Limpiar clases previas
        document.querySelectorAll('#gogList .list-group-item').forEach(el => el.classList.remove('active-gog'));
        domElement.classList.add('active-gog');
    } else {
        selectedSteamItem = game;
        document.querySelectorAll('#steamList .list-group-item').forEach(el => el.classList.remove('active-steam'));
        domElement.classList.add('active-steam');
    }
    updateCompareButton();
}

function updateCompareButton() {
    const summary = document.getElementById('selectionSummary');
    
    if (selectedGogItem && selectedSteamItem) {
        btnCompare.classList.remove('disabled');
        summary.innerHTML = `A comparar: <strong>${selectedGogItem.title}</strong> (GOG) vs <strong>${selectedSteamItem.title}</strong> (Steam)`;
        summary.className = "alert alert-success d-inline-block";
    } else {
        btnCompare.classList.add('disabled');
        summary.innerHTML = "Selecciona un juego de cada lista para continuar";
        summary.className = "alert alert-info d-inline-block";
    }
}

async function compararVersiones() {
    if (!selectedGogItem || !selectedSteamItem) return;

    // Loading en el botón comparar
    btnCompare.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analizando...';
    
    // IMPORTANTE: Enviar el title del juego de GOG (o Steam) como referencia
    const payload = {
        gog_id: selectedGogItem.id,
        steam_id: selectedSteamItem.id,
        game_title: selectedGogItem.title, 
        gog_os: "windows"
    };

    try {
        const response = await fetch(`/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        mostrarVeredicto(result);

    } catch (error) {
        console.error(error);
        alert("Error al comparar versiones.");
    } finally {
        btnCompare.innerHTML = '<i class="bi bi-arrow-left-right"></i> COMPARAR VERSIONES';
    }
}

function mostrarVeredicto(data) {
    verdictArea.classList.remove('d-none');
    
    // Elementos DOM
    const header = document.getElementById('verdictHeader');
    const msgAlert = document.getElementById('verdictMessageAlert');

    document.getElementById('gameTitleDisplay').innerText = data.game_title;
    
    // Fechas
    document.getElementById('gogDateDisplay').innerText = data.gog_date || 'N/A';
    document.getElementById('steamDateDisplay').innerText = data.steam_date || 'N/A';
    
    // Versiones / Detalles extra
    document.getElementById('gogVersionDisplay').innerText = "Fecha GOG Release";
    document.getElementById('steamVersionDisplay').innerText = data.steam_version || 'Sin info';

    // Lógica visual de colores según status
    msgAlert.innerText = data.message;
    
    // Clases CSS según el status del backend
    header.className = 'card-header text-center text-white';
    msgAlert.className = 'alert fw-bold';

    if (data.status === 'AL DÍA') {
        header.classList.add('bg-success'); // Verde
        msgAlert.classList.add('alert-success');
    } else if (data.status === 'DESACTUALIZADO') {
        header.classList.add('bg-danger'); // Rojo
        msgAlert.classList.add('alert-danger');
    } else if (data.status === 'GOG ADELANTADO') {
        header.classList.add('bg-warning'); // Amarillo/Naranja
        header.classList.add('text-dark');
        msgAlert.classList.add('alert-warning');
    } else {
        header.classList.add('bg-secondary'); // Gris
        msgAlert.classList.add('alert-secondary');
    }

    // Scroll suave hacia el resultado
    verdictArea.scrollIntoView({ behavior: 'smooth' });
}