//Creates the colour map scale
function createScale() {
    const indicator = INDICATORS[currentIndicator];
    document.getElementById("scale-title").textContent = indicator.label;
    const tbody = document.querySelector("#scale-bins tbody");
    tbody.innerHTML = "";

    const fmt = indicator.scaleFormat ?? indicator.format;

    const boundaries = [0, ...indicator.bins, Infinity];
    indicator.scheme.forEach((colour, i) => {
        const low = boundaries[i];
        const high = boundaries[i + 1];
        const label = high === Infinity
            ? `> ${fmt(low)}`
            : low === 0
                ? `< ${fmt(high)}`
                : `${fmt(low)} – ${fmt(high)}`;
        tbody.appendChild(makeRow(colour, label));
    });
    // Null data swatch
    tbody.appendChild(makeRow("url(null-pattern)", "No data"));
}

function makeRow(colour, label) {
    const tr = document.createElement("tr");
    const fill = colour.startsWith("url")
        ? `<svg width="18" height="28"><defs><pattern id="null-swatch" patternUnits="userSpaceOnUse" width="10" height="10">
                <line x1="0" y1="0" x2="10" y2="10" stroke="#aaa" stroke-width="1"/>
                    </pattern></defs><rect width="18" height="28" fill="url(#null-swatch)" stroke="#ccc" stroke-width="1"/></svg>`
        : `<svg width="18" height="28"><rect width="18" height="28" fill="${colour}" stroke="#ccc" stroke-width="1"/></svg>`;
    tr.innerHTML = `<td class="scale-swatch">${fill}</td><td class="scale-label">${label}</td>`;
    return tr;
}