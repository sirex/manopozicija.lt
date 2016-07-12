(function (d3, c3) {
    function draw(url) {
        d3.json(url, function(jsonData) {
            var i = 1;
            var DATA_NAME = "data", SCATTER_CHART = "scatter";
            var yLabel, eventsLevel, eventsLevelSameDay, tempDate, tempLevel, eventDate;
            var dataMin = Number.MAX_VALUE, dataMax = Number.MIN_VALUE;
            var yearMin = Number.MAX_VALUE, yearMax = Number.MIN_VALUE;
            var dataToChart = [], dataNames = [], dataAndX = [], chartType = [], dataHide = [], webSource = [];

            jsonData.indicators.forEach(function(jsonEachData) {
                var itemName = DATA_NAME + i;
                var date = ["x" + i];
                var mark = [itemName]; 
                dataAndX[itemName] = date[0];
                dataNames[itemName] = jsonEachData.title;
                webSource[itemName] = jsonEachData.source;
                chartType[itemName] = "line";
                yLabel = jsonEachData.ylabel;
                jsonEachData.data.forEach(function(dateAndMark) {
                    dateAndMark.forEach(function(dateOrMark, j) {
                        if (j % 2 == 0) {
                            date.push(dateOrMark);
                            var year = new Date(dateOrMark);
                            yearMin = Math.min(yearMin, year.getFullYear());
                            yearMax = Math.max(yearMax, year.getFullYear());
                        } else {
                            mark.push(dateOrMark);
                            dataMin = Math.min(dataMin, dateOrMark);
                            dataMax = Math.max(dataMax, dateOrMark);
                        }   
                    });
                });
                dataToChart.push(date);
                dataToChart.push(mark);
                i++;
            });

            eventsLevel = dataMin - (dataMax - dataMin) * 0.1;
            eventsLevelSameDay = (dataMax - dataMin) * 0.07;
            yearMax = yearMax - yearMin;

            jsonData.events.forEach(function(jsonEachData) {
                var itemName = DATA_NAME + i;
                var date = ["x"+i];
                var mark = [itemName];
                dataAndX[itemName] = date[0];
                dataNames[itemName] = jsonEachData.title;
                webSource[itemName] = jsonEachData.source;
                chartType[itemName] = SCATTER_CHART;
                date.push(jsonEachData.date);
                eventDate = new  Date(jsonEachData.date);
                if (tempDate > eventDate){
                    tempLevel += eventsLevelSameDay;
                } else {
                    tempLevel = eventsLevel;
                }
                tempDate = eventDate; 
                tempDate.setDate(tempDate.getDate() + 100);
                mark.push(tempLevel);
                dataToChart.push(date);
                dataToChart.push(mark);
                dataHide.push(itemName);
                i++;
            });

            function changePointSize(typeOfChart){
                if (typeOfChart == SCATTER_CHART){
                    return 6;
                } else return 2.5; 
            }

            c3.generate( {
                data: {
                    xs: dataAndX,
                    columns: dataToChart,
                    names: dataNames,
                    types: chartType,
                    onclick: function (d){
                        window.open(webSource[d.id]);
                    }
                },
                zoom: {
                    enabled: true
                },
                legend: {
                    hide: dataHide
                },
                axis: {
                    x: {
                        type: 'timeseries',
                        tick: {
                            count: yearMax,
                            format: '%Y'
                        }
                    },
                    y: {
                        min: eventsLevel + 3,
                        label:{
                            text: yLabel,
                            position: 'outer-middle'
                        }
                    }
                },
                point: {
                    r: function(d) { 
                        return  changePointSize(chartType[d.id]);
                    }
                }
            });
        });
    }

    var container = $('#chart');

    if (container) {
        draw(container.data('kpi-url'));
    }
}(d3, c3));  //eslint-disable-line no-undef
