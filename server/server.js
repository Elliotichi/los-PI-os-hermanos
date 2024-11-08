
// Server config
const server = require("express")();
const http = require("http");
const MongoClient = require('mongodb-legacy').MongoClient;
const bodyParser = require('body-parser');
const express = require("express");
io = require("socket.io")(http);

session = require("express-session")({
    secret: "my-secret",
    resave: true,
    saveUninitialized: true
});


const url = "something"
const client = new MongoClient(url);
const dbname = 'lospi';


server.use(session);
app.set("view engine", "ejs");
app.use(express.static("public"));
app.use(express.urlencoded({ extended: true }));

var connectedSockets = {};
var db;

// Routes
server.get("/", (req, res) => {
    res.render("pages/chart");
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

}



http.listen(8080, () => {
    console.log("Listening on 8080");
});

