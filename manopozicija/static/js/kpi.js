(function (d3) {
    function box(box, copy) {
        copy = copy || {};
        copy.margin = copy.margin || {};
        copy.padding = copy.padding || {};

        box.width = box.width || copy.width || 0;
        box.height = box.height || copy.height || 0;

        box.margin = box.margin || {};
        box.margin.top = box.margin.top || copy.margin.top || 0;
        box.margin.bottom = box.margin.bottom || copy.margin.bottom || 0;
        box.margin.left = box.margin.left || copy.margin.left || 0;
        box.margin.right = box.margin.right || copy.margin.right || 0;

        box.padding = box.padding || {};
        box.padding.top = box.padding.top || copy.padding.top || 0;
        box.padding.bottom = box.padding.bottom || copy.padding.bottom || 0;
        box.padding.left = box.padding.left || copy.padding.left || 0;
        box.padding.right = box.padding.right || copy.padding.right || 0;

        return box;
    }

    function boxOuterWidth(boxes) {
        var width = 0;
        for (var i=0; i<boxes.length; i++) {
            var box = boxes[i];
            width += box.margin.top + box.width + box.margin.bottom;
        }
        return width;
    }

    function boxOuterHeight(boxes) {
        var height = 0;
        for (var i=0; i<boxes.length; i++) {
            var box = boxes[i];
            height += box.margin.top + box.height + box.margin.bottom;
        }
        return height;
    }

    function identity(d) {
        return d;
    }

    var selector = '#kpi-chart';
    var margin = {top: 10, bottom: 10, left: 100, right: 100};
    var inner = {width: 800, height: 100};
    var bottom = {width: inner.width, height: 50, margin: {top: 10}};
    var outer = {
        width: margin.left + inner.width + margin.right,
        height: margin.top + inner.height + bottom.height + margin.bottom
    };


    d3.json($(selector).data('kpi-url'), function (json) {

        var timeline = {min: new Date(1990, 0, 1), max: d3.timeDay.floor(new Date)};

        var x = d3.scaleTime()
            .domain([timeline.min, timeline.max])
            .range([margin.left, margin.left + inner.width]);

        var histogram = d3.histogram()
            .domain(x.range())
            .value(function (d) { return x(new Date(d.date)); })
            .thresholds(d3.timeMonths(timeline.min, timeline.max, 6).map(function (d) { return x(d); }));
        var bins = histogram(json.events);
        var maxBinLength = d3.max(bins, function (d) { return d.length; });

        var charts = box({
            width: 800,
            height: 100
        });
        var events = box({
            height: 100
        }, charts);
        var canvas = box({  //eslint-disable-line no-unused-vars
            width: boxOuterWidth([charts]),
            height: boxOuterHeight([charts, events])
        });

        var svg = d3.select(selector).append('svg')
            .attr('width', outer.width)
            .attr('height', outer.height);


        var xvalue = function (d) { return x(new Date(d[0])); };

        var color = d3.scaleOrdinal(d3.schemeCategory10);


        var point = {radius: 4, margin: {top: 1, bottom: 1, left: 10}};

        bottom.top = margin.top + inner.height + bottom.margin.top;
        bottom.bottom = bottom.top + maxBinLength * (point.radius * 2 + point.margin.top * 2);

        var yBottomScale = d3.scaleLinear()
            .domain([0, maxBinLength])
            .range([bottom.bottom, bottom.top]);

        svg.append('rect')
            .attr('x', 0)
            .attr('y', bottom.top + point.radius - point.margin.top)
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
                    .y(bottom.top + point.radius - point.margin.top)
                );

        svg.append('g')
            .attr('transform', 'translate(0, ' + (bottom.bottom + point.radius + point.margin.bottom +
                            point.margin.top) + ')')
            .call(d3.axisBottom(x));

        var i, j, bin;

        for (i=0; i<bins.length; i++) {
            bin = bins[i];
            for (j=0; j<bin.length; j++) {
                svg.append('line')
                    .attr('x1', Math.round(bin.x0))
                    .attr('y1', margin.top)
                    .attr('x2', Math.round(bin.x0))
                    .attr('y2', bottom.bottom + point.radius + point.margin.bottom + point.margin.top)
                    .attr('stroke', '#ffccaa')
                    .attr('stroke-width', 1)
                    .attr('stroke-dasharray', '3,4');
            }
        }

        for (i=0; i<bins.length; i++) {
            bin = bins[i];
            for (j=0; j<bin.length; j++) {
                svg.append('circle')
                    .attr('fill', '#ff6600')
                    .attr('cx', Math.round(bin.x0))
                    .attr('cy', yBottomScale(j))
                    .attr('r', point.radius);
            }
        }


        for (i=0; i<json.indicators.length; i++) {
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
    });
}(d3));  //eslint-disable-line no-undef
