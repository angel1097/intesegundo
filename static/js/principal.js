document.addEventListener('DOMContentLoaded', function() {
    const background = document.querySelector('.background');
    const numDots = 100;

    for (let i = 0; i < numDots; i++) {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        dot.style.left = `${Math.random() * 100}vw`;
        dot.style.animationDuration = `${Math.random() * 3 + 2}s`;
        dot.style.animationDelay = `${Math.random() * 5}s`;
        background.appendChild(dot);
    }
});
