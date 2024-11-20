# Hub node

## Node role and functionalities
Hub node purpose is to receive observations from the room and parking node(s) and make relevant database queries to update, modify or remove records as necessary. When a user checks in to a room, the room node will itself query a separate collection for the associated first & last names, then send this to the hub for processing as  acheck_in. 

## Candidate microcontrollers/devices
Any network-enabled device with adequate specifications is capable of running the hub code, but it would be best deployed on a higher-power device capable of handling high traffic, with a high throughput of queries.

## Sensors/actuators
The hub node serves as a sink or information processing node, and has no hardware interface except that used to set it up (which can be done via SSH)

## Messaging protocols/technologies
The hub code has an associated MQTT client which is used to subscribe and receive messages. A PyMongo client is used thereafter to make queries and updates to the Atlas cluster.