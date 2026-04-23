// Load all required data once on start up

async function loadData() {
    const [gdp, gni, education, the, scimago] = await Promise.all([
        d3.csv("data/gdp-per-capita-worldbank.csv"),
        d3.csv("data/gross-national-income-per-capita-worldbank.csv"),
        d3.csv("data/world-education-data.csv"),
        d3.csv("data/the_combined.csv"),
        d3.csv("data/scimago_combined.csv")
    ]);
    datasets.the = formatTHEData(the)
    datasets.scimago = formatScimagoData(scimago)
    datasets.gdp = formatData(gdp, "numeric_code", "Year", "GDP per capita")
    datasets.gni = formatData(gni, "numeric_code", "Year", "GNI per capita")
    datasets.gov_spend = formatData(education, "numeric_code", "year", "gov_exp_pct_gdp")
    datasets.lit_rate = formatData(education, "numeric_code", "year", "lit_rate_adult_pct");
    datasets.pri_comp = formatData(education, "numeric_code", "year", "pri_comp_rate_pct");
    datasets.pri_pupil_teacher = formatData(education, "numeric_code", "year", "pupil_teacher_primary");
    datasets.sec_pupil_teacher = formatData(education, "numeric_code", "year", "pupil_teacher_secondary");
    datasets.pri_enrol = formatData(education, "numeric_code", "year", "school_enrol_primary_pct");
    datasets.sec_enrol = formatData(education, "numeric_code", "year", "school_enrol_secondary_pct");
    datasets.ter_enrol = formatData(education, "numeric_code", "year", "school_enrol_tertiary_pct");
}

// Data formatting for indicators: Map(#ISO -> (year -> val))
function formatData(data, isoCol, yearCol, valCol){
    const dataMap = new Map();
    data.forEach(d => {
        let iso = d[isoCol];
        let year = +d[yearCol];
        let val = d[valCol] === "" ? null : +d[valCol];
        if (!iso || isNaN(year) || val === null) return;
        if (!dataMap.has(iso)) dataMap.set(iso, new Map());
        dataMap.get(iso).set(year, val);
    });
    return dataMap;
}

// Data formatting for THE: Map(year -> [ISO, uniName, rank, latitude, longitude])
function formatTHEData(data){
    const dataMap = new Map();
    data.forEach(d => {
        let year = +d.year;
        let lat = +d.lat;
        let lon = +d.lon;
        if (isNaN(year) || isNaN(lat) || isNaN(lon)) return;
        if (!dataMap.has(year)) dataMap.set(year, []);
        dataMap.get(year).push({
            name: d.name,
            iso: d.numeric_code,
            rank: +d.rank,
            lat: lat,
            lon: lon,
        })
    })
    return dataMap;
}

// Data formatting for SCImago: Map(year -> [ISO, rank])
function formatScimagoData(data){
    const dataMap = new Map();
    data.forEach(d => {
        let year = +d.year;
        if (isNaN(year)) return;
        if (!dataMap.has(year)) dataMap.set(year, []);
        dataMap.get(year).push({
            iso: d.numeric_code,
            rank: +d.rank,
        })
    })
    return dataMap;
}