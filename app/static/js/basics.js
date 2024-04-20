function getCookie(name) {
    const cookieString = document.cookie;
    const cookies = cookieString.split(';');

    for (const cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) {
            return cookieValue;
        }
    }

    return null;
}

const shuffle = (array) => { 
    for (let i = array.length - 1; i > 0; i--) { 
      const j = Math.floor(Math.random() * (i + 1)); 
      [array[i], array[j]] = [array[j], array[i]]; 
    } 
    
    return array; 
}; 

function orderedShuffle(array) {
    const oddIndexes = shuffle(array.filter((_, index) => index % 2 !== 0));
    const evenIndexes = shuffle(array.filter((_, index) => index % 2 === 0));

    const shuffledArray = [];

    for (let i = 0; i < array.length; i++) {
        shuffledArray[i] = i % 2 !== 0 ? oddIndexes.shift() : evenIndexes.shift();
    }

    return shuffledArray;
}

let alertActive = false;

function sendAlert(type, text) {
    const wordsPerMinute = text.split(/\s+/).length;
    const delay = Math.max((wordsPerMinute / 125) * 60 * 1000, 1500);
    
    if (alertActive) {
        setTimeout(() => {
            sendAlert(type, text);
        }, delay + 500);

        return
    }

    alertElement.innerHTML = `
        <div class="icon alert-icon"></div>
        <div class="alert-${type}">
            ${text}
        </div>
    `;

    alertElement.classList.add('show');

    alertActive = true;

    setTimeout(() => {
        alertElement.classList.remove('show');
        alertActive = false;
    }, delay);
}

window.onload = function() {
    alertElement = document.getElementById('alert');
}