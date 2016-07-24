"user strict";

(function (d3) {

    function Box(w, h) {
        var  box = {
            margin: {t: 0, b: 0, l: 0, r: 0},
            padding: {t: 0, b: 0, l: 0, r: 0},
            inner: {w: w, h: h},
            outer: {l: 0, t: 0},
            min: {h: 0, w: 0}
        };

        box.setSize = function (w, h) {
            box.inner.w = d3.max([box.min.w, w]);
            box.inner.h = d3.max([box.min.h, h]);
            return box.update();
        };

        box.setOuterSize = function (w, h) {
            box.inner.w = d3.max([box.min.w, w - box.margin.r - box.margin.l - box.padding.r - box.padding.l]);
            box.inner.h = d3.max([box.min.h, h - box.margin.t - box.margin.b - box.padding.t - box.padding.b]);
            return box.update();
        };

        box.setPosition = function (l, t) {
            box.outer.l = l;
            box.outer.t = t;
            return box.update();
        };

        box.setPositionInside = function (o) {
            box.outer.l = o.inner.l;
            box.outer.t = o.inner.t;
            return box.update();
        };

        box.setPositionBelow = function (o) {
            box.outer.t = o.outer.b;
            return box.update();
        };

        box.setPositionNextTo = function (o) {
            box.outer.l = o.outer.r;
            return box.update();
        };

        box.setMargin = function (v, h) {
            box.margin.t = v;
            box.margin.b = v;
            box.margin.l = h || v;
            box.margin.r = h || v;
            return box.update();
        };

        box.setMarginV = function (t, b) {
            box.margin.t = t;
            box.margin.b = b || t;
            return box.update();
        };

        box.setMarginH = function (l, r) {
            box.margin.l = l;
            box.margin.r = r || l;
            return box.update();
        };

        box.setPadding = function (v, h) {
            box.padding.t = v;
            box.padding.b = v;
            box.padding.l = h || v;
            box.padding.r = h || v;
            return box.update();
        };

        box.setPaddingV = function (t, b) {
            box.padding.t = t;
            box.padding.b = b || t;
            return box.update();
        };

        box.update = function () {
            box.w = box.padding.l + box.inner.w + box.padding.r;
            box.h = box.padding.t + box.inner.h + box.padding.b;
            box.l = box.outer.l + box.margin.l;
            box.r = box.l + box.w;
            box.t = box.outer.t + box.margin.t;
            box.b = box.t + box.h;

            box.inner.l = box.l + box.padding.l;
            box.inner.r = box.inner.l + box.inner.w;
            box.inner.t = box.t + box.padding.t;
            box.inner.b = box.inner.t + box.inner.h;

            box.outer.w = box.margin.l + box.w + box.margin.r;
            box.outer.h = box.margin.t + box.h + box.margin.b;
            box.outer.r = box.outer.l + box.outer.w;
            box.outer.b = box.outer.t + box.outer.h;

            return box;
        };

        return box.update();
    }

    var selector = '#kpi-chart';

    d3.json($(selector).data('kpi-url'), function (json) {

        var timeline = {min: new Date(1990, 0, 1), max: d3.timeDay.floor(new Date)};

        var left = Box();
        var charts = Box();
        var events = Box();
        var canvas = Box();

        canvas.setSize($(selector).outerWidth(), 0);
        canvas.setMargin(0, 0);

        left.setSize(55, 0);
        left.setPadding(10);
        left.setPositionInside(canvas);

        charts.setPadding(10, 0);
        events.setPadding(20, 0);

        charts.margin.t = 24;
        charts.setOuterSize(canvas.inner.w - left.outer.w, 140);
        if (json.indicators.length === 0) {
            // todo: remove this if statement when position graphs will be in place
            charts.inner.h = 1;
            charts.setPadding(0);
        }

        events.setSize(charts.inner.w, 0);
        events.setMarginV(0, 20);

        charts.setPositionInside(canvas);
        events.setPositionInside(canvas);
        events.setPositionBelow(charts);
        charts.setPositionNextTo(left);
        events.setPositionNextTo(left);

        var xScale = d3.scaleTime()
            .domain([timeline.min, timeline.max])
            .range([events.inner.l, events.inner.r]);

        var periods = d3.scaleQuantize()
            .domain([0, 2000])
            .range([24, 12, 6, 3]);

        var eventsIntervals = d3.timeMonths(timeline.min, timeline.max, periods(canvas.outer.w))
            .map(function (d) { return xScale(d); });

        var histogram = d3.histogram()
            .domain(xScale.range())
            .value(function (d) { return xScale(new Date(d.date)); })
            .thresholds(eventsIntervals);
        var bins = histogram(json.events);
        var maxBinLength = d3.max(bins, function (d) { return d.length; });

        events.point = Box();
        events.point.radius = 4;
        events.point.setPaddingV(2);
        events.point.setSize(events.point.radius * 2, events.point.radius * 2);

        events.min.h = 24; // Minumum space for events label on the left side.
        events.setPaddingV(1);
        events.setSize(charts.inner.w, maxBinLength * events.point.outer.h);

        canvas.setSize(canvas.inner.w, charts.outer.h + events.outer.h);

        var svg = d3.select(selector).append('svg')
            .attr('width', canvas.outer.w)
            .attr('height', canvas.outer.h);

        var xValue = function (d) { return xScale(new Date(d[0])); };

        var color = d3.scaleOrdinal(d3.schemeCategory10);

        var yEventsScale = d3.scaleLinear()
            .domain([0, maxBinLength - 1])
            .range([
                events.inner.b - events.point.margin.b - events.point.padding.b - events.point.radius,
                events.inner.b - maxBinLength * events.point.outer.h + events.point.inner.t + events.point.radius
            ]);

        function vLine(x, color) {
            svg.append('line')
                .attr('x1', x)
                .attr('y1', canvas.outer.t)
                .attr('x2', x)
                .attr('y2', canvas.outer.b)
                .attr('stroke', color || '#000')
                .attr('stroke-width', 1);
        }

        function hLine(y, color) {
            svg.append('line')
                .attr('x1', canvas.outer.l)
                .attr('y1', y)
                .attr('x2', canvas.outer.w)
                .attr('y2', y)
                .attr('stroke', color || '#000')
                .attr('stroke-width', 1);
        }

        // Events background rect
        svg.append('rect')
            .attr('x', canvas.outer.l)
            .attr('y', events.t)
            .attr('width', canvas.outer.w)
            .attr('height', events.h)
            .attr('fill', '#fff6f0');

        // Events background top line
        hLine(events.t, '#ffccaa');

        // Events timeline axis
        var xTicks = d3.scaleQuantize()
            .domain([0, 2000])
            .range([3, 4, 10, 16, 24, 32]);
        svg.append('g')
            .attr('transform', 'translate(0, ' + events.b + ')')
            .call(d3.axisBottom(xScale).tickSizeOuter(0).ticks(xTicks(canvas.outer.w)))
            .select('path.domain').remove();

        var i, j, bin;

        // Vertical event markers
        for (i=0; i<bins.length; i++) {
            bin = bins[i];
            for (j=0; j<bin.length; j++) {
                svg.append('line')
                    .attr('x1', Math.round(bin.x0))
                    .attr('y1', events.b)
                    .attr('x2', Math.round(bin.x0))
                    .attr('y2', charts.t)
                    .attr('stroke', '#ffccaa')
                    .attr('stroke-width', 1)
                    .attr('stroke-dasharray', '3,4');
            }
        }

        // Event points
        for (i=0; i<bins.length; i++) {
            bin = bins[i];
            for (j=0; j<bin.length; j++) {
                svg.append('circle')
                    .attr('fill', '#ff6600')
                    .attr('cx', Math.round(bin.x0))
                    .attr('cy', yEventsScale(j))
                    .attr('r', events.point.radius);
            }
        }

        // Y axis scale for all indicator charts
        var yValue = function (d) { return d[1]; };
        var yScale = d3.scaleLinear()
            .domain([
                d3.min(json.indicators.map(function (d) { return d3.min(d.data, yValue); })),
                d3.max(json.indicators.map(function (d) { return d3.max(d.data, yValue); }))
            ])
            .range([charts.inner.b, charts.inner.t]);

        var yScaledValue = function (d) { return yScale(d[1]); };

        // Vertical axis for indicators on the left side
        svg.append('g')
            .attr('transform', 'translate(' + charts.l + ', 0)')
            .call(d3.axisLeft(yScale).tickSizeOuter(0).ticks(5))
            .select('path.domain').remove();

        for (i=0; i<json.indicators.length; i++) {
            var data = json.indicators[i].data;

            // Line chart for indicator
            svg.append('g').selectAll('path')
                .data([data])
                .enter().append('path')
                    .attr('fill', 'none')
                    .attr('stroke-width', '1')
                    .attr('stroke', color(i))
                    .attr('d', d3.line()
                        .x(xValue)
                        .y(yScaledValue)
                    );

            // Points on top of indicator's line chart
            svg.append('g').selectAll('circle')
                .data(data)
                .enter().append('circle')
                    .attr('cx', xValue)
                    .attr('cy', yScaledValue)
                    .attr('r', 2)
                    .attr('fill', color(i));

        }

        // Drow chart lines
        vLine(charts.l);
        // vLine(charts.r);  // todo: add this line when position graphs will be implemented
        hLine(charts.t);
        hLine(events.b);

        svg.append('text')
            .attr('x', left.inner.r)
            .attr('y', charts.t - 8)
            .attr('text-anchor', 'end')
            .attr('font-size', '14px')
            .text('Kadencija');

        svg.append('text')
            .attr('x', left.inner.r)
            .attr('y', events.b - 8)
            .attr('text-anchor', 'end')
            .attr('font-size', '14px')
            .text('Įvykiai');

        svg.append('text')
            .attr('x', left.inner.r)
            .attr('y', events.b + 16)
            .attr('text-anchor', 'end')
            .attr('font-size', '14px')
            .text('Metai');

    });
}(d3));  //eslint-disable-line no-undef
