//All functions to create the Choropleth Map and Markers

// Creates the colour map
function createColourMap(indicator){
    const selectedIndicator = INDICATORS[indicator];
    const dataset = datasets[indicator];
    const data = [];
    dataset.forEach(yearMap => {yearMap.forEach(d => {data.push(d)})});
    return d3.scaleThreshold().domain(selectedIndicator.bins).range(selectedIndicator.scheme)
}

// Draws Winkel Triple Choropleth Map
async function drawMap() {
    let width  = container.clientWidth;
    let height = width * HEIGHT_RATIO;
    svg.attr("height", height);

    projection = d3.geoWinkel3()
        .scale(width / SCALE)
        .translate([width / 2, height / 2]);

    path = d3.geoPath().projection(projection);

    const [countriesTopo] = await Promise.all([
        d3.json("data/countries-50m.json"),
        loadData()
    ]);
    const countries = topojson.feature(countriesTopo, countriesTopo.objects.countries);

    // Calculate centre point of each country for SCImago
    countries.features.forEach(d => {
        const id = String(d.id).padStart(3, "0");
        countryNames.set(id, d.properties.name);
        const centre = d3.geoCentroid(d);
        if (!isNaN(centre[0])) centres.set(id, centre);
    })
    colourMap = createColourMap(currentIndicator);

    // Defines the dashed pattern for null data
    svg.append("defs").append("pattern")
        .attr("id", "null-pattern")
        .attr("patternUnits", "userSpaceOnUse")
        .attr("width", 10)
        .attr("height", 10)
        .append("line")
        .attr("x1", 0).attr("y1", 0)
        .attr("x2", 10).attr("y2", 10)
        .attr("stroke", "#aaa")
        .attr("stroke-width", 1)

    d3.select("#main-map-frame").selectAll("path")
        .data(countries.features)
        .join("path")
        .attr("d", path)
        .attr("fill", d => {
            const id  = String(d.id).padStart(3, "0");
            const val = datasets[currentIndicator].get(id)?.get(+timeline.value);
            return val == null ? "url(#null-pattern)" : colourMap(val);
        })
        .on("mouseover", d => showCountryTooltip(d))
        .on("mousemove", () => moveTooltip())
        .on("mouseleave", () => hideTooltip());
    updateMarkers();
    createScale();
}

//Called to update map colours and marker positions on year/ indicator change
function update(){
    updateMap();
    updateMarkers();
}

// Updates map colours depending on year and indicator
function updateMap() {
    const year    = +timeline.value;
    const lookup  = datasets[currentIndicator];

    svg.selectAll("path")
        .transition()
        .duration(200)
        .attr("fill", d => {
            // get numeric code from world-atlas TopoJSON
            const id  = String(d.id).padStart(3, "0");
            const val = lookup.get(id)?.get(year);
            return val == null ? "url(#null-pattern)" : colourMap(val);
        });
}

// Updates ranking marker position depending on year and ranking indicator
function updateMarkers() {
    const year   = +timeline.value;
    const markerType = document.querySelector("input[name='rank-selector']:checked").value;

    svg.selectAll("circle.marker").remove();

    if (markerType === "the") {
        let uniRank = datasets.the.get(year) ?? [];
        svg.selectAll("circle.marker")
            .data(uniRank)
            .join("circle")
            .attr("class", "marker")
            .attr("cx", d => projection([d.lon, d.lat])[0])
            .attr("cy", d => projection([d.lon, d.lat])[1])
            .attr("r",  d => theRadiusScale(d.rank))
            .on("mouseover", showTHETooltip)
            .on("mousemove", moveTooltip)
            .on("mouseleave", hideTooltip);
    } else {
        const countries = datasets.scimago.get(year) ?? [];
        numRanks = d3.max(countries, d => d.rank)
        const scimagoRadiusScale = d3.scaleSqrt().domain([1, numRanks]).range([11, 3]);
        svg.selectAll("circle.marker")
            .data(countries.filter(d => centres.has(d.iso)))
            .join("circle")
            .attr("class", "marker")
            .attr("cx", d => projection(centres.get(d.iso))[0])
            .attr("cy", d => projection(centres.get(d.iso))[1])
            .attr("r",  d => scimagoRadiusScale(d.rank))
            .on("mouseover", showScimagoTooltip)
            .on("mousemove", moveTooltip)
            .on("mouseleave", hideTooltip);
    }
}

// Resizes map on screen resize
function resizeMap() {
    let width  = container.clientWidth;
    let height = width * HEIGHT_RATIO;
    svg.attr("height", height);

    projection
        .scale(width / SCALE)
        .translate([width / 2, height / 2]);

    svg.selectAll("path").attr("d", path);
    updateMarkers();
}