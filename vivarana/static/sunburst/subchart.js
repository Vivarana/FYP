var subwidth =  width;
var subheight = height;
var subradius =  Math.min(subwidth, subheight-seq_height) / 2;

var subvis = d3.select("#chart2").append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .append("sub:g")
    .attr("id", "subcontainer")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")scale(" + 1 / 2 + ")")
    .on("mouseover", subchartmouseover)
    .on("mouseleave",mouseleave);
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
        return  Math.sqrt(d.y+40)*4;
    })
    .outerRadius(function (d) {
        return Math.sqrt(d.y + d.dy+40)*4;
    });


function createSubchart(node) {

    // Bounding circle underneath the sunburst, to make it easier to detect
    // when the mouse leaves the parent g.
    subvis.append("svg:circle")
        .attr("r", subradius)
        .style("opacity", 0);

    var subnodes = partition.nodes(node); // add depth
   // .filter(function(d) {
   //     return (d.depth < 20+node.depth); // 0.005 radians = 0.29 degrees
   // });
    //subnodes = partition.nodes(subnodes.data);

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
        .on("mouseover", mouseover);

};

function subchartmouseover() {

    //subvis.attr("transform", "translate(" + 850 + "," + height / 2 + ")");
    //vis.attr("transform", "scale(" + 1 / 2 + ")");
    //d3.select("#explanation").style("transform", "translate(675px)");
};
