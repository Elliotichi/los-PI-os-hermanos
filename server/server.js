// Server config
const server = require("express")();
const http = require("http").Server(server);
const MongoClient = require('mongodb-legacy').MongoClient;
const bodyParser = require('body-parser');
const express = require("express");
const { connect } = require("http2");
io = require("socket.io")(http);

session = require("express-session")({
    secret: "my-secret",
    resave: true,
    saveUninitialized: true
});

// 
const uri = "mongodb+srv://visionstitch_dev:LosHermanos58@lospi.usv87.mongodb.net/?retryWrites=true&w=majority&appName=lospi";
const client = new MongoClient(uri);
const dbname = 'lospi-db';


server.use(session);
server.set("view engine", "ejs");
server.use(express.static("public"));
server.use(express.urlencoded({ extended: true }));

var connectedSockets = {};
var db;

// Routes
server.get("/", (req, res) => {
    // Landing page - should just be EJS template with a simple navbar & a search for room
    res.render("pages/home")
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
            return res.render("/");

        }

        // If the passwords match, update session variables
        if (result.pass == req.body.pass) {
            console.log("Successfully logged in!");

            req.session.loggedin = true;
            req.session.uname = result.user;
            req.session.new = result.new;

            if (err) throw err;
            res.redirect("/");
            return;
        }
    })
})

/*
* ROUTE - report generation
* If the user is logged in (ie, is an admin), then query for non-checked-out students and pass a list of them to the EJS template
*/
server.get("/report", async (req, res) => {
    if (!req.session.loggedin) {
        return res.render("pages/home");
    }

    let still_in_building = [];

    const cursor = db.collection("check_ins").find({ check_out_time: { "$eq": "" } });
    cursor.next((error, check_in) => {
        if (error) return handling(error);
        still_in_building.push(check_in);
        return res.render("pages/home", { data: still_in_building })
    });


    return res.redirect("/");

})

// Websockets
io.on("connection", (socket) => {
    connectedSockets[socket.id] = socket;

    socket.on("room search", (room) => {
        let in_room = 0;
        const cursor = db.collection("check_ins").find({ 
            check_out_time: { "$eq": "" },
            room: room
        });
        
        cursor.next((error, check_in) => {
            if (error) return handling(error);
            in_room++;

        });
        // socket.emit() a heatmap of the room that has been searched by the client
        // MongoDB query goes here? (overhead of rapid queries - consider a storage object)
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

