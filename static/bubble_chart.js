function bubbleChart() {
    var width = 960,
        height = 960,
        maxRadius = 6;

    function chart(selection) {
        var title = "bubblert";
        var marginTop = 100;
        var data = selection.enter().data();
        var div = selection,
            svg = div.selectAll('svg');
        svg.attr('width', width).attr('height', height);
        
        var simulation = d3.forceSimulation(data)
            .force("charge", d3.forceManyBody().strength([-90]))
            .force("x", d3.forceX())
            .force("y", d3.forceY())
            .on("tick", ticked);

        var node = svg.selectAll("circle")
            .data(data)
            .enter()
            .append("g")
            .attr('transform', 'translate(' + [width / 2, height / 2] + ')')
            //.style("fill", function(d) { return colorCircles(d.category)});

        node.append('circle')
            .attr("id",function(d,i) {
                return i;
            })
            .attr('r', function(d) { return scaleRadius(d)})
            .style('opacity',0.5)
            .append("clipPath")
            .attr("id",function(d,i) {
                return "clip-"+i;
            })
    
            
        node.append('text')
            .attr("id",function(d,i) {
                return i;
            })
            .attr("clip-path",function(d,i) {
                return "url(#clip-" + i + ")"
            })
            .attr("text-anchor", "middle")
            .append("tspan")
            .attr("x",function(d) {
                return 0;//-1*scaleRadius(d[columnForRadius])/3;
            })
            .attr("y",function(d) {
                return ".3em";//scaleRadius(d[columnForRadius])/4;
            })
            .text(function(d) {
                console.log(d.headline);
                return d.headline;
            });

        svg.append('text')
			.attr('x',width/2).attr('y',marginTop)
			.attr("text-anchor", "middle")
			.attr("font-size","1.8em")
			.text(title);
        

        function ticked(e) {
            node.attr("transform",function(d) {
                return "translate(" + [d.x+(width / 2), d.y+((height+marginTop) / 2)] +")";
            });
        }
            
        function scaleRadius(element) {
            // todo return proper scale
            return Math.random() * 40 + 10;
        }
    }

    chart.width = function(value) {
        if (!arguments.length) {
            return width;
        }
        width = value;
        return chart;
    };

    chart.height = function(value) {
        if (!arguments.length) {
            return height;
        }
        height = value;
        return chart;
    };

    return chart;
}
