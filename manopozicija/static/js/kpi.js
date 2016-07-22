(function (d3) {
    var selector = '#kpi-chart';
    var margin = {top: 10, bottom: 100, left: 100, right: 100};
    var inner = {width: 800, height: 100};
    var bottom = {width: inner.width, height: 100, margin: {top: 10}};
    var outer = {
        width: margin.left + inner.width + margin.right,
        height: margin.top + inner.height + bottom.height + margin.bottom
    };
    var svg = d3.select(selector).append('svg')
        .attr('width', outer.width)
        .attr('height', outer.height);

    var timeline = {min: new Date(1990, 0, 1), max: Date.now()};

    var x = d3.scaleTime()
        .domain([timeline.min, timeline.max])
        .range([margin.left, margin.left + inner.width]);

    var xvalue = function (d) { return x(new Date(d[0])); };

    var color = d3.scaleOrdinal(d3.schemeCategory10);

    var identity = function (d) { return d; };

    d3.json($(selector).data('kpi-url'), function (json) {
        for (var i=0; i<json.indicators.length; i++) {
            var data = json.indicators[i].data;

            var y = d3.scaleLinear()
                .domain([
                    d3.min(data, function (d) { return d[1]; }),
                    d3.max(data, function (d) { return d[1]; })
                ])
                .range([margin.top + inner.height, margin.top]);

            var yvalue = function (d) { return y(d[1]); };

            svg.append('g')
                .attr('transform', 'translate(' + margin.left + ', 0)')
                .call(d3.axisLeft(y).ticks(5));

            svg.append('g').selectAll('path')
                .data([data])
                .enter().append('path')
                    .attr('fill', 'none')
                    .attr('stroke-width', '1')
                    .attr('stroke', color(i))
                    .attr('d', d3.line()
                        .x(xvalue)
                        .y(yvalue)
                    );

            svg.append('g').selectAll('circle')
                .data(data)
                .enter().append('circle')
                    .attr('cx', xvalue)
                    .attr('cy', yvalue)
                    .attr('r', 2)
                    .attr('fill', color(i));

        }

        var point = {radius: 4, margin: {top: 2, bottom: 2, left: 10}};
        var histogram = d3.histogram()
            .domain(x.range())
            .thresholds(Math.round(inner.width / (point.radius * 2 + point.margin.left * 2)))
            .value(function (d) { return x(new Date(d.date)) });
        var bins = histogram(json.events);
        var maxBinLength = d3.max(bins, function (d) { return d.length });
        console.log((inner.width / (point.radius * 2 + point.margin.left * 2)));
        console.log(Math.round(inner.width / (point.radius * 2 + point.margin.left * 2)));

        bottom.top = margin.top + inner.height + bottom.margin.top;
        bottom.bottom = bottom.top + maxBinLength * (point.radius * 2 + point.margin.top * 2);

        var yBottomScale = d3.scaleLinear()
            .domain([0, maxBinLength])
            .range([bottom.bottom, bottom.top]);

        svg.append('rect')
            .attr('x', 0)
            .attr('y', bottom.top)
            .attr('width', outer.width)
            .attr('height', bottom.bottom - bottom.top + point.radius + point.margin.bottom)
            .attr('fill', '#fff6f0');

        svg.append('g').selectAll('path')
            .data([[0, outer.width]])
            .enter().append('path')
                .attr('fill', 'none')
                .attr('stroke-width', 1)
                .attr('stroke', '#ffccaa')
                .attr('d', d3.line()
                    .x(identity)
                    .y(bottom.top)
                );

        svg.append('g')
            .attr('transform', 'translate(0, ' + (bottom.bottom + point.radius + point.margin.bottom) + ')')
            .call(d3.axisBottom(x));

        for (var i=0; i<bins.length; i++) {
            var bin = bins[i];
            for (var j=0; j<bin.length; j++) {
                svg.append('circle')
                    .attr('fill', '#ff6600')
                    .attr('cx', bin.x0)
                    .attr('cy', yBottomScale(j))
                    .attr('r', point.radius);
            }
        }


    });
}(d3));  //eslint-disable-line no-undef
