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


const url = "mongodb+srv://visionstitch_dev:<db_password>@lospi.usv87.mongodb.net/?retryWrites=true&w=majority&appName=lospi";
const client = new MongoClient(url);
const dbname = 'lospi';


server.use(session);
server.set("view engine", "ejs");
server.use(express.static("public"));
server.use(express.urlencoded({ extended: true }));

var connectedSockets = {};
var db;

// Routes
server.get("/", (req, res) => {
    // Landing page - should just be EJS template with a simple navbar & a search for room
})

// Websockets
io.on("connection", (socket) => {
    connectedSockets[socket.id] = socket;

    socket.on("room search", (room) => {
        // Produce a heatmap of the room that has been searched by the client
        // MongoDB query goes here? (overhead of rapid queries?)
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

