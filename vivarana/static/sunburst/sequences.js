var json;
var uniqueValues;
var engine;
// Dimensions of sunburst.
var width = 1300 / 2;
var height = 700;
//window.alert(width+","+height);
var seq_height = 70;
var radius = Math.min(width, height - seq_height) / 2;
// Breadcrumb dimensions: width, height, spacing, width of tip/tail.
var b = {
    w: 130, h: 30, s: 3, t: 10
};

// Mapping of step names to colors.
var colors = { null: "#000000"};
/*var colorList = ["#000080", "#00008B", "#0000CD", "#0000FF", "#006400", "#008000", "#008080", "#008B8B", "#00BFFF", "#00CED1",
 "#00FA9A", "#00FF00", "#00FF7F", "#00FFFF", "#191970", "#1E90FF", "#20B2AA", "#228B22", "#2E8B57", "#2F4F4F",
 "#32CD32", "#3CB371", "#40E0D0", "#4169E1", "#4682B4", "#483D8B", "#48D1CC", "#4B0082", "#556B2F", "#5F9EA0",
 "#6495ED", "#66CDAA", "#696969", "#6A5ACD", "#6B8E23", "#708090", "#778899", "#7B68EE", "#7CFC00", "#7FFF00",
 "#7FFFD4", "#800000", "#800080", "#808000", "#808080", "#87CEEB", "#87CEFA", "#8A2BE2", "#8B0000", "#8B008B",
 "#8B4513", "#8FBC8F", "#90EE90", "#9370DB", "#9400D3", "#98FB98", "#9932CC", "#9ACD32", "#A0522D", "#A52A2A",
 "#A9A9A9", "#ADD8E6", "#ADFF2F", "#AFEEEE", "#B0C4DE", "#B0E0E6", "#B22222", "#B8860B", "#BA55D3", "#BC8F8F",
 "#BDB76B", "#C0C0C0", "#C71585", "#CD5C5C", "#CD853F", "#D2691E", "#D2B48C", "#D3D3D3", "#D8BFD8", "#DA70D6",
 "#DAA520", "#DB7093", "#DC143C", "#DCDCDC", "#DDA0DD", "#DEB887", "#E6E6FA", "#E9967A", "#EE82EE", "#EEE8AA",
 "#F08080", "#F0E68C", "#F4A460", "#F5DEB3", "#FA8072", "#FAEBD7", "#FAF0E6", "#FAFAD2", "#FDF5E6", "#FF0000",
 "#FF00FF", "#FF00FF", "#FF1493", "#FF4500", "#FF6347", "#FF69B4", "#FF7F50", "#FF8C00", "#FFA07A", "#FFA500",
 "#FFB6C1", "#FFC0CB", "#FFD700", "#FFDAB9", "#FFDEAD", "#FFE4B5", "#FFE4C4", "#FFE4E1", "#FFEBCD", "#FFEFD5",
 "#FFFF00"];

 var colorscale20 = d3.scale.category20().range();
 var colorscale20b = d3.scale.category20().range();
 var colorscale20c = d3.scale.category20().range();
 var colorList = colorscale20b;//.concat(colorscale20b,colorscale20c);
 */
var colorList = ["#FFFF00", "#1CE6FF", "#FF34FF", "#FF4A46", "#008941", "#006FA6", "#A30059", "#FFDBE5", "#7A4900",
    "#0000A6", "#63FFAC", "#B79762", "#004D43", "#8FB0FF", "#997D87", "#5A0007", "#809693", "#FEFFE6", "#1B4400",
    "#4FC601", "#3B5DFF", "#4A3B53", "#FF2F80", "#61615A", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9",
    "#B903AA", "#D16100", "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
    "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09", "#00489C", "#6F0062",
    "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66", "#885578", "#FAD09F", "#FF8A9A", "#D157A0",
    "#BEC459", "#456648", "#0086ED", "#886F4C", "#34362D", "#B4A8BD", "#00A6AA", "#452C2C", "#636375", "#A3C8C9",
    "#FF913F", "#938A81", "#575329", "#00FECF", "#B05B6F", "#8CD0FF", "#3B9700", "#04F757", "#C8A1A1", "#1E6E00",
    "#7900D7", "#A77500", "#6367A9", "#A05837", "#6B002C", "#772600", "#D790FF", "#9B9700", "#549E79", "#FFF69F",
    "#201625", "#72418F", "#BC23FF", "#99ADC0", "#3A2465", "#922329", "#5B4534", "#FDE8DC", "#404E55", "#0089A3",
    "#CB7E98", "#A4E804", "#324E72", "#6A3A4C", "#83AB58", "#001C1E", "#D1F7CE", "#004B28", "#C8D0F6", "#A3A489",
    "#806C66", "#222800", "#BF5650", "#E83000", "#66796D", "#DA007C", "#FF1A59", "#8ADBB4", "#1E0200", "#5B4E51",
    "#C895C5", "#320033", "#FF6832", "#66E1D3", "#CFCDAC", "#D0AC94", "#7ED379", "#012C58", "#7A7BFF", "#D68E01",
    "#353339", "#78AFA1", "#FEB2C6", "#75797C", "#837393", "#943A4D", "#B5F4FF", "#D2DCD5", "#9556BD", "#6A714A",
    "#001325", "#02525F", "#0AA3F7", "#E98176", "#DBD5DD", "#5EBCD1", "#3D4F44", "#7E6405", "#02684E", "#962B75",
    "#8D8546", "#9695C5", "#E773CE", "#D86A78", "#3E89BE", "#CA834E", "#518A87", "#5B113C", "#55813B", "#E704C4",
    "#00005F", "#A97399", "#4B8160", "#59738A", "#FF5DA7", "#F7C9BF", "#643127", "#513A01", "#6B94AA", "#51A058",
    "#A45B02", "#1D1702", "#E20027", "#E7AB63", "#4C6001", "#9C6966", "#64547B", "#97979E", "#006A66", "#391406",
    "#F4D749", "#0045D2", "#006C31", "#DDB6D0", "#7C6571", "#9FB2A4", "#00D891", "#15A08A", "#BC65E9", "#FFFFFE",
    "#C6DC99", "#203B3C", "#671190", "#6B3A64", "#F5E1FF", "#FFA0F2", "#CCAA35", "#374527", "#8BB400", "#797868",
    "#C6005A", "#3B000A", "#C86240", "#29607C", "#402334", "#7D5A44", "#CCB87C", "#B88183", "#AA5199", "#B5D6C3",
    "#A38469", "#9F94F0", "#A74571", "#B894A6", "#71BB8C", "#00B433", "#789EC9", "#6D80BA", "#953F00", "#5EFF03",
    "#E4FFFC", "#1BE177", "#BCB1E5", "#76912F", "#003109", "#0060CD", "#D20096", "#895563", "#29201D", "#5B3213",
    "#A76F42", "#89412E", "#1A3A2A", "#494B5A", "#A88C85", "#F4ABAA", "#A3F3AB", "#00C6C8", "#EA8B66", "#958A9F",
    "#BDC9D2", "#9FA064", "#BE4700", "#658188", "#83A485", "#453C23", "#47675D", "#3A3F00", "#061203", "#DFFB71",
    "#868E7E", "#98D058", "#6C8F7D", "#D7BFC2", "#3C3E6E", "#D83D66", "#2F5D9B", "#6C5E46", "#D25B88", "#5B656C",
    "#00B57F", "#545C46", "#866097", "#365D25", "#252F99", "#00CCFF", "#674E60", "#FC009C", "#92896B"];

// Total size of all segments; we set this later, after loading the data.
var totalSize = 0;

var maxwidth = 0;

var zoom;
var vis;
var partition;
var arc;
var tip;

var innerRad = 100;
var radiusIncrement = 20;

$.get('/max_width/', function (data) {
    maxwidth = JSON.parse(data)["maxwidth"];
    console.log(maxwidth)
    //radius = (maxwidth * 10 + 40);
    console.log(radius);

    zoom = d3.behavior.zoom()
        .scaleExtent([-10, 10])
        .translate([width / 2, height / 2])
        .on("zoom", zoomed);

    vis = d3.select("#chart").append("svg:svg")
        .attr("width", width)
        .attr("height", height)
        .append("svg:g")
        .attr("id", "container")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")

    zoom(d3.selectAll("svg"));
    zoom.event(d3.selectAll("svg").transition().duration(500));

    partition = d3.layout.partition()
        .size([2 * Math.PI, radius * radius])
        .value(function (d) {
            return d.size;
        })

    arc = d3.svg.arc()
        .startAngle(function (d) {
            return d.x;
        })
        .endAngle(function (d) {
            return d.x + d.dx;
        })
        .innerRadius(function (d) {
            return  Math.min(1, d.depth) * innerRad + Math.max(0, d.depth - 1) * radiusIncrement;
        })
        .outerRadius(function (d) {
            return innerRad + d.depth * radiusIncrement;
        });

    tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function (d) {
            return "<span style='color:black'>" + d + "</span>";
        })

    vis.call(tip);

});

function zoomed() {
    vis.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

function showSunburst() {
    var colorsSet = false;
    initializeBreadcrumbTrail();
    drawLegend();
    $.get('/unique_strings/', function (data) {
        uniqueValues = JSON.parse(data).sort();

        colorsSet = initialzeColors(uniqueValues);
        engine = new Bloodhound({
            local: $.map(uniqueValues, function (state) {
                return { value: state };
            }),
            datumTokenizer: function (d) {
                return Bloodhound.tokenizers.whitespace(d.value);
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace
        });

        engine.initialize();

        $('#rule-input').tokenfield({
            typeahead: [null, { source: engine.ttAdapter() }], limit: 0
        });
        //Filter model
        $('#filter-input').tokenfield({
            typeahead: [null, { source: engine.ttAdapter() }]
        });
    });

    $.get('/tree_data/', function (data) {
        var csv_type = JSON.parse(data);
        json = buildHierarchy(csv_type)
        if (colorsSet) {
            createVisualization(json);
        }
        else {
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
        .on("mouseenter", function () {
            d3.select("#explanation").style("transform", "None");
        })
        .on("mouseleave", mouseleave());

    // For efficiency, filter nodes to keep only those large enough to see.
    var nodes = partition.nodes(json)
        .filter(function (d) {
            return (d.depth < 10 && d.dx > 0.005); // 0.005 radians = 0.29 degrees
        });

    var path = vis.data([json]).selectAll("path")
        .data(nodes)
        .enter().append("svg:path")
        .attr("display", function (d) {
            //edit middle to text
            return d.depth ? null : "none";
        })
        .attr("d", arc)
        .attr("fill-rule", "evenodd")
        .style("fill", function (d) {
            return colors[d.name];
        })
        .style("opacity", 1)
        .attr("data-toggle", "tooltip")
        .attr("data-placement", "top")
        .attr("title", function (d) {
            return d.name
        })
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
    var breadcrumbSequenceArray = sequenceArray.slice(sequenceArray.length - 10, sequenceArray.length);
    if (sequenceArray.length <= 10) {
        updateBreadcrumbs(sequenceArray, percentageString);
    } else {
        updateBreadcrumbs(breadcrumbSequenceArray, percentageString);
    }

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
            return (breadcrumbSequenceArray.indexOf(node) >= 0);
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
    // gets ancestors maximum amount of ancesters returned is 10
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
        .attr("width", $(window).width())
        .attr("height", 30)
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

function colorPoints(index, length) {

    var color = colorList[Math.floor((colorList.length * index) / length)];
    return color;
}

function initialzeColors(data) {

    var urls = data;
    urls.map(function (currentvalue, index, array) {
        colors[currentvalue] = colorPoints(index, urls.length);
    });
    return true;
}
function updateData() {
    d3.select("#container").selectAll("*").remove();

    // Select the section we want to apply our changes to
    var svg = d3.select("#container");//.transition();

    // For efficiency, filter nodes to keep only those large enough to see.
    var nodes = partition.nodes(json)
        .filter(function (d) {
            return (d.depth < maxwidth * percentageSliderValue / 100); // 0.005 radians = 0.29 degrees
        });

    // Make the changes
    svg.selectAll("path").remove();
    d3.select("#container").datum(json).selectAll("path")
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

function buildHierarchy(csv) {
    var root = {"name": "root", "children": []};
    for (var i = 0; i < csv.length; i++) {
        var sequence = csv[i][1];
        var size = +csv[i][0];
        if (isNaN(size)) { // e.g. if this is a header row
            continue;
        }
        var parts;
        try {
            parts = sequence.split("|-|");
        }
        catch (e) {
            window.cosole.log(e.message)
            parts = sequence
        }

        var currentNode = root;
        for (var j = 0; j < parts.length; j++) {
            var children = currentNode["children"];
            var nodeName = parts[j];
            var childNode;
            if (j + 1 < parts.length) {
                // Not yet at the end of the sequence; move down the tree.
                var foundChild = false;
                for (var k = 0; k < children.length; k++) {
                    if (children[k]["name"] == nodeName) {
                        childNode = children[k];
                        foundChild = true;
                        break;
                    }
                }
                // If we don't already have a child node for this branch, create it.
                if (!foundChild) {
                    childNode = {"name": nodeName, "children": []};
                    children.push(childNode);
                }
                currentNode = childNode;
            } else {
                // Reached the end of the sequence; create a leaf node.
                childNode = {"name": nodeName, "size": size};
                children.push(childNode);
            }
        }
    }
    return root;
};

