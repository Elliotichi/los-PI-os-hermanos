let occupancyChart;
let socket = io();
let chart = null;

$(function () {

    $("#searchbar").keypress((event) => {
        if (event.key == "Enter") {
            event.preventDefault();
            let searchTerm = $("#searchbar").val().toUpperCase();
            socket.emit("room search", searchTerm);
        }
    });

    $("#btn_N9").on("click", function () {
        socket.emit("room search", "N9");
    });

    $("#btn_N533").on("click", function () {
        socket.emit("room search", "N533");
    });

    $("#btn_N527").on("click", function () {
        socket.emit("room search", "N527");
    });

    $(".report-checkbox").on('change', function () {
        const isChecked = $(this).is(':checked');

        first_name = text.split(" ")[0];
        last_name = text.split(" ")[1];

        console.log(`${first_name} ${last_name}`);

        if (isChecked) {
            socket.emit("report checkin", { first_name: first_name, last_name: last_name });
            console.log(`Checkbox changed: "${text}" is now checked`);
        }
    });

    $(".report-person").on("click", function (e) {
        if (!$(e.target).is(".report-checkbox")) {
            const $checkbox = $(this).find(".report-checkbox");
            $checkbox.prop("checked", !$checkbox.prop("checked"));
            let nameSplit = $(this).text().trim().split(" ");

            socket.emit("report checkin", {first_name:nameSplit[0], last_name:nameSplit[1]});

            $(this).remove();
            $(this).trigger("refresh");
        }
    });




    /*
    * When the user connects, they receive a list of observations stored on the server
    * Create the corresponding chart if it doesn't exist, and render it with the data set
    */
    socket.on("new chart", (initialChartData) => {
        chart = renderChart(initialChartData);
    })

    const renderChart = (heatmap_data) => {

        if (chart !== null) { chart.destroy(); }
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

        return occupancyChart;

    }


})