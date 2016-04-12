d3.json("/topic/balsavimas-internetu/kpi/", function(jsonData) {
    var i = 1;
    var yLabel;
    var dataToChart = [], dataNames = [], yAxe = [], dataAndX = [], chartType = [];

    jsonData.indicators.forEach(function(jsonEachData) {
        var itemName = "data" + i;
        var date = ["x" + i];
        var mark = [itemName]; 
        dataAndX[itemName] = date[0];
        dataNames[itemName] = jsonEachData.title;
        chartType[itemName] = "line";
        yAxe[itemName] = 'y';
        yLabel = jsonEachData.ylabel;
        jsonEachData.data.forEach(function(dateAndMark) {
            dateAndMark.forEach(function(dateOrMark, j) {
                if (j % 2 == 0) 
                    date.push(dateOrMark)
                else 
                    mark.push(dateOrMark);
            });
        });
        dataToChart.push(date);
        dataToChart.push(mark);
        i++;
    });

    jsonData.events.forEach(function(jsonEachData) {
        var itemName = "data" + i;
        var date = ["x"+i];
        var mark = [itemName];
        var temporarMark; 
        dataAndX[itemName] = date[0];
        dataNames[itemName] = jsonEachData.title;
        chartType[itemName] = "scatter";
        yAxe[itemName] = 'y2';
        date.push(jsonEachData.date);
        temporarMark = jsonEachData.position;
        if (temporarMark == null) 
            temporarMark = 0;
        mark.push(temporarMark);
        dataToChart.push(date);
        dataToChart.push(mark);
        i++;
    });

    // window.alert(dataToChart);
    var chart = c3.generate( {	
        data: {
            xs: dataAndX,
            columns: dataToChart,
            names: dataNames,
            types: chartType,
            axes: yAxe,
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
            },
            y2: {
                show: true
            }
        }
    });	
});
