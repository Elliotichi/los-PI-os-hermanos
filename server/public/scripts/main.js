let socket = io();
let charts = {};

$(function () {
    
    /*
    * When the user connects, they receive a list of observations stored on the server
    * Create the corresponding chart if it doesn't exist, and render it with the data set
    */
    socket.on("new chart", (initialChartData) => {
        let chartTopic = initialChartData?.room;
        $("#chart-placeholder").append("<canvas id='"+chartTopic+"' style='width:60%' class='chartbox'</canvas>")
        let chart = (chartTopic in charts) ? charts[chartTopic] : renderChart(initialChartData);
        chart.update();
    })


    const renderChart = (heatmap_data) => {
        console.table(heatmap_data);

        let room = heatmap.room,
            ylabel = heatmap.yLabel,
            data = dataset.data

        const labels = heatmap_data.map(item => item.result_time);


        charts[room] = new Chart(room, {
            type: "bar",
            data: data,
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            },
        })

        return charts[room]
    }


})