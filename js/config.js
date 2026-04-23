// Defines all global variables used throughout the web app

let datasets = {};
let centres = new Map();
let countryNames = new Map();
let container = document.getElementById("main-map-container");
let svg = d3.select("#main-map-frame");
let tooltip = document.getElementById("tooltip");
let timeline = document.getElementById("timeline");
let yearDisplay = document.getElementById("year-display");
let playBtn = document.getElementById("play-btn");
let playRange = null;
const HEIGHT_RATIO = 0.5;
const SCALE = 6.5;
let projection, path, colourMap;
let currentIndicator = "gdp";
const theRadiusScale = d3.scaleSqrt().domain([1, 200]).range([9, 2]);

const INDICATORS = {
    gdp: {
        label: "GDP per capita",
        scheme: ["#feebe2", "#fbb4b9", "#f768a1", "#c51b8a", "#7a0177"],
        scale: "threshold",
        bins: [1135, 4465, 13845, 50000],
        format: d => "$" + d3.format(",.2f")(d),
        scaleFormat: d => "$" + d3.format(",.0f")(d)
    },
    gni: {
        label: "GNI per capita",
        scheme: ["#f1eef6", "#d7b5d8", "#df65b0", "#dd1c77", "#980043"],
        scale: "threshold",
        bins: [1135, 4465, 13845, 50000],
        format: d => "$" + d3.format(",.2f")(d),
        scaleFormat: d => "$" + d3.format(",.0f")(d)
    },
    gov_spend: {
        label: "Government Expenditure on Education (% of GDP)",
        scheme: ["#edf8fb", "#b3cde3", "#8c96c6", "#8856a7", "#810f7c"],
        scale: "threshold",
        bins: [2, 4, 6, 8],
        format: d => d3.format(".2f")(d) + "%"
    },
    lit_rate: {
        label: "Literacy Rate (Adult)",
        scheme: ["#ffffcc", "#c2e699", "#78c679", "#31a354", "#006837"],
        scale: "threshold",
        bins: [30, 50, 65, 85],
        format: d => d3.format(".2f")(d) + "%"
    },
    pri_comp:{
        label: "Completion Rate (Primary)",
        scheme: ["#f6eff7", "#bdc9e1", "#67a9cf", "#1c9099", "#016c59"],
        scale: "threshold",
        bins: [50, 75, 95, 100],
        format: d => d3.format(".2f")(d) + "%"
    },
    pri_pupil_teacher: {
        label: "Pupil: Teacher (Primary)",
        scheme: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
        scale: "threshold",
        bins: [20, 35, 50, 70],
        format: d3.format(".0f")
    },
    sec_pupil_teacher: {
        label: "Pupil: Teacher (Secondary)",
        scheme: ["#fef0d9", "#fdcc8a", "#fc8d59", "#e34a33", "#b30000"],
        scale: "threshold",
        bins: [20, 35, 50, 70],
        format: d3.format(".0f")
    },
    pri_enrol: {
        label: "Enrolment Rate (Primary)",
        scheme: ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"],
        scale: "threshold",
        bins: [75, 90, 100, 110],
        format: d => d3.format(".2f")(d) + "%"
    },
    sec_enrol: {
        label: "Enrolment Rate (Secondary)",
        scheme: ["#f0f9e8", "#bae4bc", "#7bccc4", "#43a2ca", "#0868ac"],
        scale: "threshold",
        bins: [40, 65, 85, 100],
        format: d => d3.format(".2f")(d) + "%"
    },
    ter_enrol: {
        label: "Enrolment Rate (Tertiary)",
        scheme: ["#f1eef6", "#bdc9e1", "#74a9cf", "#2b8cbe", "#045a8d"],
        scale: "threshold",
        bins: [10, 25, 50, 75],
        format: d => d3.format(".2f")(d) + "%"
    },
};