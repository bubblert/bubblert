var bubbleChart = function(container) {
    var maxRadius = 6,
    title = "bubblert",
    marginTop = 100,
    newData = []
    
    var svg = d3.select(container).append('svg')
        .attr('width', window.innerWidth)
        .attr('height', window.innerHeight);

    var bubble = d3.layout.pack()
        .size([window.innerWidth, window.innerHeight])
        .value(function(d) {return d.size;}) // new data is loaded to bubble layout
        .padding(3);
    
    svg.append('text')
        .attr('x',window.innerWidth/2).attr('y',marginTop)
        .attr("text-anchor", "middle")
        .attr("font-size","1.8em")
        .text(title);

    this.render = function(item) {

        var nodes = bubble.nodes(this.processData(item));
            //.filter(function(d) { return !d.children; }); // filter out the outer bubble

        var circle = svg.selectAll('circle')
			.data(nodes, function(d) { return d.headline; });
        
        var duration = 500;
        var delay = 0;

        circle.transition()
            .duration(duration)
            .delay(function(d, i) {delay = i * 7; return delay;}) 
            .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; })
            .attr('r', scaleRadius)
            .style('opacity', 1); // force to 1, so they don't get stuck below 1 at enter()

        circle.enter().append('circle')
            .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; })
            .attr('r', function(d) { return 0; })
            .transition()
            .duration(duration * 1.2)
            .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; })
            .attr('r', scaleRadius)
            .style('opacity', 0.5);
    
        circle.append('text')
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
                return d.headline;
            });
        

        function scaleRadius(element) {
            // todo return proper scale
            return Math.random() * 40 + 10;
        }

    }

    this.processData = function(data) {
        data.size = Math.random() * 40 + 10;
        newData.push(data);
		return {children: newData, headline: "root", size: 1000};
	}


    return this;
}
