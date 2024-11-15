# Web Server

## Node role and functionalities
- The web server's role is to act as a sink/gateway node to provide public-facing functionality for the data repository. Users will be able to search a room and view a chart of its occupancy levels, sorted by hour. It will also combine with the building-wide room node deployed at the reception area to offer administrative functionality - for example, a logged-in user (e.g. a fire marshal) to quickly display a list of checked-in students, take their attendance, and see who is unaccounted for.

## Candidate boards/microcontrollers
- Designed with no specific microcontroller in mind, the node is compatible with any network-enabled device capable of installing and running the dependencies specified in web_server_setup.md. Use on a non-microcontroller is legitimate and may be preferable due to outdated Node.js Linux support.

## Sensors and actuators
- The server node performs no sensing or actuation, & serves solely for descriptive/administrative purposes.


## Messaging protocols and technologies
- The web server uses a MongoDB legacy client to query an Atlas cluster.