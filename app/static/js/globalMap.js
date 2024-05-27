const globalMap = document.getElementById('global-map');

function toggleMap(forceRemove=false) {
    cancelBuild();
    closeWorkPopup();
    closeMarket();

    if (forceRemove) {
        globalMap.classList.remove('active');

        return;
    }

    globalMap.classList.toggle('active');
}
