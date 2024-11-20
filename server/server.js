// Server config
const dotenv = require("dotenv").config();
const server = require("express")();
const http = require("http").Server(server);
const MongoClient = require('mongodb-legacy').MongoClient;
const bodyParser = require('body-parser');
const express = require("express");
const { connect } = require("http2");
const path = require("path");
io = require("socket.io")(http);

session = require("express-session")({
    secret: "my-secret",
    resave: true,
    saveUninitialized: true
});

// 
const uri = process.env.CONN_STRING;
const client = new MongoClient(uri);
const dbname = 'lospi-db';


server.use(session);
server.set("view engine", "ejs");
server.set("views", path.join(__dirname, "/views"));
server.use(express.static(path.join(__dirname, 'public')));
server.use(express.urlencoded({ extended: true }));

var connectedSockets = {};
var db;

// Routes
server.get("/", (req, res) => {
    // Landing page - should just be EJS template with a simple navbar & a search for room
    res.render("pages/home", { loggedin: req.session.loggedin })
})

/*
* ROUTE - LOGIN
* Get username & password from request body, update session variables accordingly
*/
server.post("/login", (req, res) => {
    let error = "";

    if (!db) { res.redirect("/"); req.session.loggedin = false; return; }

    db.collection("users").findOne({ "user": req.body.user }, (err, result) => {
        if (err) throw err;

        if (!result) {
            error = "Invalid username or password. Please try again.";
            req.session.loggedin = false;
            return res.redirect("/");

        }

        // If the passwords match, update session variables
        if (result.pass == req.body.pass) {
            console.log("Successfully logged in!");
            req.session.loggedin = true;
            req.session.uname = result.user;
            req.session.new = result.new;

            if (err) throw err;
            return res.redirect("/");

        }
    })
})

/*
* ROUTE - report generation
* If the user is logged in (ie, is an admin), then query for non-checked-out students and pass a list of them to the EJS template
*/
server.get("/report", async (req, res) => {
    if (!req.session.loggedin) {
        res.redirect("/")
    }

    let still_in_building = [];
    const cursor = db.collection("check_ins").find({ check_out_time: { "$eq": null } });


    for await (const check_in of cursor) {
        still_in_building.push(check_in);
    }

    return res.render("pages/report", { data: still_in_building })
})

// Websockets
io.on("connection", (socket) => {
    connectedSockets[socket.id] = socket;

    socket.on("room search", async (room) => {
        try {
            hourly_occupancies = await get_occupancies("N533");

            peaks = await get_peak_occupancies(hourly_occupancies);

            to_send = { "room": room, "peaks": peaks }
            socket.emit("new chart", { "room": room, "peaks": peaks });

        } catch (error) { console.error(error); }
    })

    socket.on("disconnect", () => {
        delete (connectedSockets[socket.id])
    });
}); // socket.io


const connectDB = async () => {
    // Use connect method to connect to the server
    try {
        await client.connect();
        console.log('Connected successfully to MongoDB Atlas');

        db = client.db(dbname);
    }
    catch (err) {
        console.log(err);
    }
}

connectDB();

http.listen(8080, () => {
    console.log("Listening on 8080");
});

async function get_peak_occupancies(result) {
    /**
     * Calculate the peak occupancies for each hour interval of the current day
     * @param {Array} result - A sorted array of dictionaries, each encapsulating the check-ins for that hour, as well as a total
     */

    let final_results = [];

    // For each hour, decompose its properties
    result.forEach((entry) => {
        const hour = entry["_id"];
        const totalCheckIns = entry["total_check_ins"];
        const checkIns = entry["check_ins"];

        let peakOccupancy = 0;

        // Loop over the check-ins for that hour and calculate a peak occupancy
        checkIns.forEach((checkIn) => {
            const checkInTime = new Date(checkIn["check_in_time"]);
            const checkOutTime = checkIn["check_out_time"] ? new Date(checkIn["check_out_time"]) : null;

            const checkInHour = checkInTime.getHours();
            const checkOutHour = checkOutTime ? checkOutTime.getHours() : null;

            if (checkInHour <= hour && (checkOutHour === null || checkOutHour >= hour)) {
                peakOccupancy += 1;
            }
        });

        final_results.push({ hour_interval: hour, peak: peakOccupancy });

        console.log(`Hour: ${hour}, Total Check-Ins: ${totalCheckIns}, Peak Occupancy: ${peakOccupancy}`);
    });

    return final_results;
}



async function get_occupancies(room) {
    /**
 * Get occupancies for each hour interval of the current day
 * @param {String} room - a string representing a room search
 */
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    // Aggregation pipeline - queries for the current day's check-ins in the room, projects & groups by (indexed) hours
    const pipeline = [
        {
            $match: {
                check_in_time: { $gte: today, $lt: tomorrow },
                room: room,
            },
        },
        {
            $project: {
                matriculation_no: 1,
                room: 1,
                check_in_time: 1,
                check_out_time: 1,
                check_in_hour: { $hour: "$check_in_time" },
                check_out_hour: {
                    $cond: [
                        { $ifNull: ["$check_out_time", false] },
                        { $hour: "$check_out_time" },
                        23,
                    ],
                },
            },
        },
        {
            $group: {
                _id: "$check_in_hour",
                total_check_ins: { $sum: 1 },
                check_ins: {
                    $push: {
                        check_in_time: "$check_in_time",
                        check_out_time: "$check_out_time",
                    },
                },
            },
        },
        {
            $sort: { _id: 1 },
        },
    ];

    const result = await db.collection("check_ins").aggregate(pipeline).toArray();
    return result;
}