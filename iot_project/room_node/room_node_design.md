# Room Node

## Node role and functionalities
- the node uses an RFID reader to detect the presence of a tag (a student card), scanning a matriculation number on the card and logging their presence in a room, then fetches corresponding name from a database & sends to hub

## Candidate microcontrollers
- Although prototyped using a Raspberry Pi 3b+, the node can be made compatible with any network-connected device capable of supplying 3V for the reader.
- The Raspberry Pi 3b+ likely provides an excess of size, software overhead and power consumption for its intended purpose. As documented, a lower-power alternative could be used.

## Sensors and actuators
- The node is currently programmed to use a RC522 RFID reader, a standard module used in this context. However, alternatives could be used, provided the implementation language has valid support.

## Messaging protocols and technologies
- MQTT was chosen for the deployment due to its lightness, helping to reduce the power consumption of the node devices, and for its extensive support by various programming languages (in this example, Python)