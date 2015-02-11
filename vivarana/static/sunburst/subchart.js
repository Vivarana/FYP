var subwidth = width;
var subheight = height;
var subradius = Math.min(subwidth, subheight - seq_height) / 2;

var subInnerRad = 50;
var subRadiusIncrement = 20;

var subvis = d3.select("#chart2").append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .append("sub:g")
    .attr("id", "subcontainer")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")scale(" + 1 / 2 + ")")
    .on("mouseleave", mouseleave);
var subpartition = d3.layout.partition()
    .size([2 * Math.PI, subradius * subradius])
    .value(function (d) {
        return d.size;
    });

subarc = d3.svg.arc()
    .startAngle(function (d) {
        return d.x;
    })
    .endAngle(function (d) {
        return d.x + d.dx;
    })
    .innerRadius(function (d) {
        return  Math.min(1, d.depth) * subInnerRad + Math.max(0, d.depth - 1) * subRadiusIncrement;
    })
    .outerRadius(function (d) {
        return subInnerRad + d.depth * subRadiusIncrement;
    });

function createSubchart(node) {

    // Bounding circle underneath the sunburst, to make it easier to detect
    // when the mouse leaves the parent g.
    subvis.append("svg:circle")
        .attr("r", subradius)
        .style("opacity", 0);

    var subnodes = partition.nodes(node); // add depth

    var subpath = subvis.datum(node).selectAll("path")
        .data(subnodes)
        .enter().append("svg:path")
        .attr("display", function (d) {
            return d.depth ? null : "none";
        })
        .attr("d", subarc)
        .attr("fill-rule", "evenodd")
        .style("fill", function (d) {
            return colors[d.name];
        })
        .style("opacity", 1)
        .on("mouseover", mouseover)
        .on("click", mouseclick);

};
