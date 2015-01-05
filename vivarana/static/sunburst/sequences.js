var json;
var uniqueValues;
// Dimensions of sunburst.
var width = $(window).width();
var height = $(window).height();
//window.alert(width+","+height);
var seq_height = 70;
var radius = Math.min(width, height-seq_height) / 2;
// Breadcrumb dimensions: width, height, spacing, width of tip/tail.
var b = {
    w: 130, h: 30, s: 3, t: 10
};

// Mapping of step names to colors.
var colors ={ null :"#000000"};
var colorList = ["#000080","#00008B","#0000CD","#0000FF","#006400","#008000","#008080","#008B8B","#00BFFF","#00CED1",
                "#00FA9A","#00FF00","#00FF7F","#00FFFF","#191970","#1E90FF","#20B2AA","#228B22","#2E8B57","#2F4F4F",
                "#32CD32","#3CB371","#40E0D0","#4169E1","#4682B4","#483D8B","#48D1CC","#4B0082","#556B2F","#5F9EA0",
                "#6495ED","#66CDAA","#696969","#6A5ACD","#6B8E23","#708090","#778899","#7B68EE","#7CFC00","#7FFF00",
                "#7FFFD4","#800000","#800080","#808000","#808080","#87CEEB","#87CEFA","#8A2BE2","#8B0000","#8B008B",
                "#8B4513","#8FBC8F","#90EE90","#9370DB","#9400D3","#98FB98","#9932CC","#9ACD32","#A0522D","#A52A2A",
                "#A9A9A9","#ADD8E6","#ADFF2F","#AFEEEE","#B0C4DE","#B0E0E6","#B22222","#B8860B","#BA55D3","#BC8F8F",
                "#BDB76B","#C0C0C0","#C71585","#CD5C5C","#CD853F","#D2691E","#D2B48C","#D3D3D3","#D8BFD8","#DA70D6",
                "#DAA520","#DB7093","#DC143C","#DCDCDC","#DDA0DD","#DEB887","#E6E6FA","#E9967A","#EE82EE","#EEE8AA",
                "#F08080","#F0E68C","#F4A460","#F5DEB3","#FA8072","#FAEBD7","#FAF0E6","#FAFAD2","#FDF5E6","#FF0000",
                "#FF00FF","#FF00FF","#FF1493","#FF4500","#FF6347","#FF69B4","#FF7F50","#FF8C00","#FFA07A","#FFA500",
                "#FFB6C1","#FFC0CB","#FFD700","#FFDAB9","#FFDEAD","#FFE4B5","#FFE4C4","#FFE4E1","#FFEBCD","#FFEFD5",
                "#FFFF00"];

var redColorList = ["#000000","#000080","#0000FF","#008000","#008080","#00FF00","#00FFFF","#800000","#800080","#808000",
                "#808080","#C0C0C0","#FF0000","#FF00FF","#FFA500","#FFFF00"];

// Total size of all segments; we set this later, after loading the data.
var totalSize = 0;

var vis = d3.select("#chart").append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .append("svg:g")
    .attr("id", "container")
    .attr("transform", "translate(" + 375 + "," + 300 + ")");


var partition = d3.layout.partition()
    .size([2 * Math.PI, radius * radius])
    .value(function (d) {
        return d.size;
    })
//  .children(function children(d){return d.children});
//.sort(function comparator(a,b){return a.value - b.value });


var arc = d3.svg.arc()
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

var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([-10, 0])
  .html(function(d) {
    return "<span style='color:black'>" + d + "</span>";
  })

vis.call(tip);

function showSunburst(){
    var colorsSet = false;
    initializeBreadcrumbTrail();
    drawLegend();
    $.get('/uniqueurls/', function (data) {
        uniqueValues = data;
        colorsSet = initialzeColors(data);
    });

    $.get('/treedata/', function (data) {
            json = JSON.parse(data);
        if(colorsSet){
         createVisualization(json);
        }
        else{
            showSunburst();
        }
     });

}
function createVisualization(json) {

    // Basic setup of page elements.
    d3.select("#togglelegend").on("click", toggleLegend);

    // Bounding circle underneath the sunburst, to make it easier to detect
   vis.append("svg:circle")
        .attr("r", radius)
        .style("opacity", 0)
        .on("mouseenter",function(){
            vis.attr("transform", "translate(" + 375 + "," + 300 + ")");
            subvis.attr("transform", "translate(" + 850 + "," + height / 2 + ")scale(" + 1 / 2 + ")");
        d3.select("#explanation").style("transform", "None");})
        .on("mouseleave",mouseleave());

    // For efficiency, filter nodes to keep only those large enough to see.
    var nodes = partition.nodes(json)
        .filter(function (d) {
            return (d.dx > 0.005); // 0.005 radians = 0.29 degrees
        });

    //   alert(nodes[7].children);

    var path = vis.data([json]).selectAll("path")
        .data(nodes)
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
        .attr("data-toggle","tooltip")
        .attr("data-placement","top")
        .attr("title",function(d){return d.name})
        .on("mouseover", mouseover)
        .on("click", mouseclick);

    // Add the mouseleave handler to the bounding circle.
    d3.select("#container").on("mouseleave", mouseleave);


    // Get total size of the tree = value of root node from partition.
    totalSize = path.node().__data__.value;
};

// on click generate subchart

function mouseclick(d) {
    d3.select("#subcontainer").selectAll("*").remove();
    createSubchart(d);
}

// Fade all but the current sequence, and show it in the breadcrumb trail.
function mouseover(d) {
    var html = d.name;

        tip.html(html);
        tip.show();
    var percentage = (100 * d.value / totalSize).toPrecision(3);
    var percentageString = percentage + "%";
    if (percentage < 0.1) {
        percentageString = "< 0.1%";
    }

    d3.select("#percentage")
        .text(percentageString);

    d3.select("#explanation")
        .style("visibility", "");

    var sequenceArray = getAncestors(d);
    updateBreadcrumbs(sequenceArray, percentageString);

    // Fade all the segments.
    d3.selectAll("path")
        .style("opacity", 0.3);

    // Then highlight only those that are an ancestor of the current segment.
    vis.selectAll("path")
        .filter(function (node) {
            return (sequenceArray.indexOf(node) >= 0);
        })
        .style("opacity", 1);
    subvis.selectAll("path")
        .filter(function (node) {
            return (sequenceArray.indexOf(node) >= 0);
        })
        .style("opacity", 1);
}

// Restore everything to full opacity when moving off the visualization.
function mouseleave(d) {

    tip.hide();
    // Hide the breadcrumb trail
    d3.select("#trail")
        .style("visibility", "hidden");

    // Deactivate all segments during transition.
    d3.selectAll("path").on("mouseover", null);

    // Transition each segment to full opacity and then reactivate it.
    d3.selectAll("path")
        .transition()
        .duration(1000)
        .style("opacity", 1)
        .each("end", function () {
            d3.select(this).on("mouseover", mouseover);
        });

    d3.select("#explanation")
        .style("visibility", "hidden");
}

// Given a node in a partition layout, return an array of all of its ancestor
// nodes, highest first, but excluding the root.
function getAncestors(node) {
    var path = [];
    var current = node;
    while (current.parent) {
        path.unshift(current);
        current = current.parent;
    }
    return path;
}

function initializeBreadcrumbTrail() {
    // Add the svg area.
    var trail = d3.select("#sequence").append("svg:svg")
        .attr("width", width)
        .attr("height", 50)
        .attr("id", "trail");
    // defs to clip path of the text within trail polygon

    var defs = trail.append("svg:defs")
    // Add the label at the end, for the percentage.
    trail.append("svg:text")
        .attr("id", "endlabel")
        .style("fill", "#000");

    defs.append("svg:clipPath")
        .attr("id", "textclip")
        .append("svg:rect")
        .attr("width", b.w)
        .attr("height", b.h)
        .attr("x", 0)
        .attr("y", 0)
        .attr("clipPathUnits", "objectBoundingBox");
}

// Generate a string that describes the points of a breadcrumb polygon.
function breadcrumbPoints(d, i) {
    var points = [];
    points.push("0,0");
    points.push(b.w + ",0");
    points.push(b.w + b.t + "," + (b.h / 2));
    points.push(b.w + "," + b.h);
    points.push("0," + b.h);
    if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
        points.push(b.t + "," + (b.h / 2));
    }
    return points.join(" ");
}

// Update the breadcrumb trail to show the current sequence and percentage.
function updateBreadcrumbs(nodeArray, percentageString) {

    // Data join; key function combines name and depth (= position in sequence).
    var g = d3.select("#trail")
        .selectAll("g")
        .data(nodeArray, function (d) {
            //console.log(d.name+ d.depth);
            return d.name + d.depth;
        });

    // Add breadcrumb and label for entering nodes.
    //console.log(g.enter());
    var entering = g.enter().append("svg:g");
    entering.append("svg:polygon")
        .attr("points", breadcrumbPoints)
        .style("fill", function (d) {
            return colors[d.name];
        });

    entering.append("svg:text")
        .attr("x", (b.t) * 2)
        .attr("y", b.h / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", "left")
        .style("clip-path", "url(#textclip)")
        .text(function (d) {
            return d.name;
        });


    // Set position for entering and updating nodes.
    g.attr("transform", function (d, i) {
        return "translate(" + i * (b.w + b.s) + ", 0)";
    });

    // Remove exiting nodes.
    g.exit().remove();

    // Now move and update the percentage at the end.
    d3.select("#trail").select("#endlabel")
        .attr("x", (nodeArray.length + 0.5) * (b.w + b.s))
        .attr("y", b.h / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(percentageString);

    // Make the breadcrumb trail visible, if it's hidden.
    d3.select("#trail")
        .style("visibility", "");

}

function drawLegend() {

    // Dimensions of legend item: width, height, spacing, radius of rounded rect.
    var li = {
        w: 75, h: 30, s: 3, r: 3
    };

    var legend = d3.select("#legend").append("svg:svg")
        .attr("width", li.w)
        .attr("height", d3.keys(colors).length * (li.h + li.s));

    var g = legend.selectAll("g")
        .data(d3.entries(colors))
        .enter().append("svg:g")
        .attr("transform", function (d, i) {
            return "translate(0," + i * (li.h + li.s) + ")";
        });

    g.append("svg:rect")
        .attr("rx", li.r)
        .attr("ry", li.r)
        .attr("width", li.w)
        .attr("height", li.h)
        .style("fill", function (d) {
            return d.value;
        });

    g.append("svg:text")
        .attr("x", li.w / 2)
        .attr("y", li.h / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .text(function (d) {
            return d.key;
        });
}

function toggleLegend() {
    var legend = d3.select("#legend");
    if (legend.style("visibility") == "hidden") {
        legend.style("visibility", "");
    } else {
        legend.style("visibility", "hidden");
    }
}

function colorPoints(index,length){
   /* var fvalue = Math.floor(0xFFF*(index+1)/length).toString(16);
    if(fvalue.length == 1){
        fvalue = "00"+fvalue;
    }else if(fvalue.length == 2){
        fvalue = "0"+fvalue;
    }
    var color = "#"+fvalue;
    return color;*/
    var color = colorList[Math.floor((colorList.length*index)/length)];
    return color;
}
/*var U, V, R, G,B;
function colorPoints(scalevalue , Y){
    U = Math.cos(scalevalue);
    V = Math.sin(scalevalue);
    //R =Y+V/0.88;
    //G=Y-0.38*U-0.58*V;
    //B=Y+U/0.49;
    R = Math.floor(Math.abs(U*255));
    G = Math.floor(Math.abs(V*255));
    B = Math.floor(Math.abs(((U+V)/2)*255));
    return "rgb("+R+","+G+","+B+")";
}*/
/*
function colorPoints(fullscale,quadrantscale){
    var U = Math.cos(quadrantscale);
    var V = Math.sin(quadrantscale);
    var h = fullscale/60;			// sector 0 to 5
	var i = Math.floor( h );
    window.alert(fullscale+" , "+quadrantscale+" , "+U +" , "+V+" , "+h+" , "+i);
	var f = h - i;			// factorial part of h
	var p = V * ( 1 - U );
	var q = V * ( 1 - U * f );
	var t = V * ( 1 - U * ( 1 - f ) );
    var R,G,B;
    if( U == 0 ) {
		// achromatic (grey)
		R = G = B = V;
        return "rgb("+Math.floor(R*255)+","+Math.floor(G*255)+" ,"+Math.floor(B*255)+")";
	}
    else {
        switch (i) {
            case 0:
                R = V;
                G = t;
                B = p;
                break;
            case 1:
                R = q;
                G = V;
                B = p;
                break;
            case 2:
                R = p;
                G = V;
                B = t;
                break;
            case 3:
                R = p;
                G = q;
                B = V;
                break;
            case 4:
                R = t;
                G = p;
                B = V;
                break;
            default:		// case 5:
                R = V;
                G = p;
                B = q;
                break;
        }
    }
    return "rgb("+Math.floor(R*255)+","+Math.floor(G*255)+" ,"+Math.floor(B*255)+")";
}
*/

function initialzeColors(data) {

        var urls = JSON.parse(data);
        //console.log(urls.length);
        /*var linearScale = d3.scale.linear()
                                .domain([0,urls.length])
                                .range([0,Math.PI/2]);
        var fullLinearScale = d3.scale.linear()
                                .domain([0,urls.length])
                                .range([0,360]);
        var quadrantLinearScale = d3.scale.linear()
                                .domain([0,urls.length])
                                .range([0,Math.PI*2]);*/
        //console.log(linearScale(500))
        urls.map(function(currentvalue,index,array){
            //console.log(currentvalue,  colorPoints(linearScale(index),0.5));
             //colors[currentvalue] = colorPoints(linearScale(index),0.1);
            //colors[currentvalue] = colorPoints(fullLinearScale(index),quadrantLinearScale(index));
            colors[currentvalue] = colorPoints(index,urls.length);
        });
    return true;
}
function updateData() {

    // Select the section we want to apply our changes to
    var svg = d3.select("#container").transition();

    // For efficiency, filter nodes to keep only those large enough to see.
    var nodes = partition.nodes(json)
        .filter(function (d) {
            return (d.dx > 2*Math.PI*percentageSliderValue/100); // 0.005 radians = 0.29 degrees
        });

    // Make the changes
        svg.selectAll("path").remove();
        d3.select("#container").selectAll("path")
            .data(nodes)
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
        .on("mouseover", mouseover)
        .on("click", mouseclick);


    };

