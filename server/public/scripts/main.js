let occupancyChart;
let socket = io();
let charts = {};

$(function () {

    $("#btn_N9").on("click", function () {
        socket.emit("room search", "N9");
    });

    $("#btn_N533").on("click", function () {
        socket.emit("room search", "N533");
    });

    $("#btn_N527").on("click", function () {
        socket.emit("room search", "N527");
    });



    /*
    * When the user connects, they receive a list of observations stored on the server
    * Create the corresponding chart if it doesn't exist, and render it with the data set
    */
    socket.on("new chart", (initialChartData) => {

        let chartTopic = initialChartData?.room;
        renderChart(initialChartData);
    })

    const renderChart = (heatmap_data) => {

        let room = heatmap_data.room,
            labels = Array.from({ length: 24 }, (_, i) => i),
            ylabel = "# Occupants",
            peaks = new Array(24).fill(0)

        heatmap_data.peaks.forEach(entry => {
            const hour = parseInt(entry.hour_interval, 10);
            peaks[hour] = parseInt(entry.peak, 10);
        })

        const ctx = document.getElementById('occupancy-chart').getContext('2d');
        
        const occupancyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: `Peak Occupancy for Room ${room}`,
                    data: peaks,  
                    backgroundColor: 'rgba(123, 26, 123, 0.6)',  
                    borderColor: 'rgba(123, 26, 123, 1)', 
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Hour of Day'
                        },
                        ticks: {
                            stepSize: 1
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Peak Occupancy'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });

    }


})