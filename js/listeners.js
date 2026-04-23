//Listeners for other UI elements

// Updates the map (colours) on indicator change
document.getElementById("indicator-selectors").addEventListener("change", function() {
    currentIndicator = this.value;
    colourMap = createColourMap(currentIndicator);
    update();
    createScale();
});

// Writes year + changes data subset corresponding to timeline selection
timeline.addEventListener("input", () => {
    stopPlaying()
    yearDisplay.textContent = timeline.value;
    update();
});

// Changes range of timeline depending on the ranking metric selected
document.querySelectorAll("input[name='rank-selector']").forEach(radio => {
    radio.addEventListener("change", (e) => {
        stopPlaying()
        if (e.target.value === "scimago") {
            timeline.min = 1996;
        } else {
            timeline.min = 2011;
            if (+timeline.value < 2011) timeline.value = 2011;
        }
        yearDisplay.textContent = timeline.value;
        update();
    });
});

// Listener for play button for timeline animation
playBtn.addEventListener("click", () => {
    if (playRange){
        stopPlaying()
    }
    else{
        playBtn.innerHTML = "&#9646;&#9646;"
        playRange = setInterval(() => {
            let year = +timeline.value;
            if (year >= +timeline.max) {
                stopPlaying()
                year = +timeline.min;
            }
            else {
                year += 1;
            }
            timeline.value = year;
            yearDisplay.textContent = year;
            update();
        }, 750)
    }
});

// Reusable function to stop timeline animation
function stopPlaying(){
    clearInterval(playRange);
    playRange = null;
    playBtn.innerHTML = "&#9654;";
}

// Listener for window resizing
const observer = new ResizeObserver(() => resizeMap());
observer.observe(container);

drawMap();