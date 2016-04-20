(function (d3, c3) {
    d3.json("/topic/balsavimas-internetu/kpi/", function(jsonData) {
        var i = 1; 
        var yLabel, eventsLevel, eventsLevelSameDay, tempDate, tempLevel;
        var dataMin = Number.MAX_VALUE, dataMax = Number.MIN_VALUE;
        var dataToChart = [], dataNames = [], dataAndX = [], chartType = [], dataHide = [];

        jsonData.indicators.forEach(function(jsonEachData) {
            var itemName = "data" + i;
            var date = ["x" + i];
            var mark = [itemName]; 
            dataAndX[itemName] = date[0];
            dataNames[itemName] = jsonEachData.title;
            chartType[itemName] = "line";
            yLabel = jsonEachData.ylabel;
            jsonEachData.data.forEach(function(dateAndMark) {
                dateAndMark.forEach(function(dateOrMark, j) {
                    if (j % 2 == 0) {
                        date.push(dateOrMark);
                    } 
                    else {
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
        eventsLevelSameDay = (dataMax - dataMin) * 0.02;

        jsonData.events.forEach(function(jsonEachData) {
            var itemName = "data" + i;
            var date = ["x"+i];
            var mark = [itemName];
            dataAndX[itemName] = date[0];
            dataNames[itemName] = jsonEachData.title;
            chartType[itemName] = "scatter";
            date.push(jsonEachData.date);
            if (tempDate == jsonEachData.date) {
                tempLevel += eventsLevelSameDay;
            }
            else {
                tempLevel = eventsLevel;
            }
            tempDate = jsonEachData.date;
            mark.push(tempLevel);
            dataToChart.push(date);
            dataToChart.push(mark);
            dataHide.push(itemName);
            i++;
        });

        c3.generate( {
            data: {
                xs: dataAndX,
                columns: dataToChart,
                names: dataNames,
                types: chartType
            },
            legend: {
                hide: dataHide
            },
            axis: {
                x: {
                    type: 'timeseries',
                    tick: {
                        rotate: 45,
                        format: '%Y-%m-%d'
                    }
                },
                y: {
                    label:{
                        text: yLabel,
                        position: 'outer-middle'
                    }
                }
            }
        });
    });
}(d3, c3));  //eslint-disable-line no-undef
