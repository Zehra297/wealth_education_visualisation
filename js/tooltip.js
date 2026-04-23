// Returns country name and corresponding value for tooltip
function showCountryTooltip(d) {
    const iso    = String(d.id).padStart(3, "0");
    const val   = datasets[currentIndicator].get(iso)?.get(+timeline.value);
    const name  = countryNames.get(iso) ?? "Unknown";
    const indicator = INDICATORS[currentIndicator];

    tooltip.querySelector(".tt-country").textContent = name;
    tooltip.querySelector(".tt-value").innerHTML = val != null
        ? `<strong>${indicator.label}:</strong> ${indicator.format(val)}`
        : `<span class="tt-null">No data collected</span>`;

    moveTooltip();
    tooltip.classList.add("visible");
}

// Returns university name and corresponding ranking for tool tip
function showTHETooltip(d) {
    tooltip.querySelector(".tt-country").textContent = d.name;
    tooltip.querySelector(".tt-value").innerHTML = `<strong>THE Rank:</strong> #${d.rank}`;
    moveTooltip();
    tooltip.classList.add("visible");
}

// Returns country name and research ranking for tool tip
function showScimagoTooltip(d) {
    tooltip.querySelector(".tt-country").textContent = countryNames.get(d.iso) ?? "Unknown";
    tooltip.querySelector(".tt-value").innerHTML = `<strong>SCImago Rank:</strong> #${d.rank}`;
    moveTooltip();
    tooltip.classList.add("visible");
}

// Used to move tool tip with mouse
function moveTooltip() {
    const pad = 12;
    let x = d3.event.clientX + pad;
    let y = d3.event.clientY + pad;
    // Prevent overflow off the right/bottom edge
    if (x + 230 > window.innerWidth)  x = d3.event.clientX - 230;
    if (y + 80  > window.innerHeight) y = d3.event.clientY - 80;
    tooltip.style.left = x + "px";
    tooltip.style.top  = y + "px";
}

// Removes/ hides tooltip once mouse is off the element
function hideTooltip() {tooltip.classList.remove("visible");}