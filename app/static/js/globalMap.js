const globalMap = document.getElementById('global-map');

function toggleMap() {
    globalMap.classList.toggle('active');
}

function showSettlement(event, settlementId) {
    const settlement = document.getElementById(`id-${settlementId}`);

    settlement.classList.add("active");
}

function hideSettlement(settlementId) {
    const settlement = document.getElementById(`id-${settlementId}`);

    settlement.classList.remove("active");
}
