/**
 * Created by Developer on 11/15/2014.
 */
var subwidth = 450;
var subheight = 600;
var subradius = Math.min(subwidth, subheight) / 2;

var subvis = d3.select("svg")
    .append("sub:g")
    .attr("id", "subcontainer")
    .attr("transform", "translate(" + 850 + "," + subheight / 2 + ")scale(" + 1 / 2 + ")")
    .on("mouseover", subchartmouseover);


var subpartition = d3.layout.partition()
    .size([2 * Math.PI, subradius * subradius])
    .value(function (d) {
        return d.size;
    });
//.sort(function comparator(a,b){return a.value - b.value });
//.children(function children(d){return d.children});

var subarc = d3.svg.arc()
    .startAngle(function (d) {
        return d.x;
    })
    .endAngle(function (d) {
        return d.x + d.dx;
    })
    .innerRadius(function (d) {
        return Math.sqrt(d.y);
    })
    .outerRadius(function (d) {
        return Math.sqrt(d.y + d.dy);
    });


function createSubchart(node) {

    // Bounding circle underneath the sunburst, to make it easier to detect
    // when the mouse leaves the parent g.
    subvis.append("svg:circle")
        .attr("r", subradius)
        .style("opacity", 0);

    var subnodes = partition.nodes(node);
    //.filter(function(d) {
    //    return (d.dx > 0.005); // 0.005 radians = 0.29 degrees
    //});

    var subpath = subvis.datum(node).selectAll("path")
        .data(subnodes)
        .enter().append("svg:path")
        .attr("display", function (d) {
            return d.depth ? null : "none";
        })
        .attr("d", arc)
        .attr("fill-rule", "evenodd")
        .style("fill", function (d) {
            return colors[d.name];
        })
        .style("opacity", 1)
        .on("mouseover", mouseover);

    // Add the mouseleave handler to the bounding circle.
    d3.select("#container").on("mouseleave", mouseleave);
    d3.select("#subcontainer").on("mouseleave", subchartmouseleave);

    // Get total size of the tree = value of root node from partition.
    //totalSize = subpath.node().__data__.value;

};

function subchartmouseover() {

    subvis.attr("transform", "translate(" + 850 + "," + height / 2 + ")");
    vis.attr("transform", "translate(" + 375 + "," + 300 + ")scale(" + 1 / 2 + ")");
    d3.select("#explanation").style("transform", "translate(475px)");
};
function subchartmouseleave() {
    d3.selectAll("path")
        .transition()
        .duration(1000)
        .style("opacity", 1)
        .each("end", function () {
            d3.select(this).on("mouseover", mouseover);
        });
     d3.select("#explanation")
        .style("visibility", "hidden");
};