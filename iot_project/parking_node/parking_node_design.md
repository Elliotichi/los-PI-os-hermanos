# Parking Node

## Node role and functionalities
- Detection of approaching vehicle, camera snapshot of registration plate, image processing & OCR to extract string of registration.

## Candidate microcontrollers
- Although prototyped using a Raspberry Pi 3b+, the node can be made compatible with any network-connected device with reasonable computational power (!benchmark code with tracemalloc)
- The Raspberry Pi 3b+ likely provides an excess of size, software overhead and power consumption for its intended purpose. A tree-based ontology could be used which sends pixel arrays for processing by a more powerful sink node, instead of performing capture and processing on the samae device.

## Sensors and actuators
- The node is currently programmed to use a Raspberry Pi camera module, although with minor changes this could be adapted to other, lower-power alternatives. Given the right photographing conditions, higher resolutions are not necessarily a priority.

## Messaging protocols and technologies
- MQTT was chosen for the deployment due to its lightness, helping to reduce the power consumption of the node devices, and for its extensive support by various programming languages (in this example, Python)