### Alternative Boards for Power Saving

The current project uses only raspberry pi 3 boards, which are powerful and very flexible, however are costly and powerhungry compared to other boards, so as a next step to make the IOT project more efficent, a list of more appropriate boards are listed for the different nodes

## Hub Node

As the hub node has to process all the data from the other nodes, as well as communicate with multiple nodes all at the same time, we recommend that the hub node stay a raspberry pi 3, as a lower power board might not be able to keep up with demand

A recommendation would be to optimise the Pi settings, for example, turning off settings that are not needed, optimising the code fully, having the Pi shut off when they dont detect any users/when the building is closed.

## Room Node

# - ESP32
The esp32 is a smaller, less power hungry IOT device which can easily run the RFID for the room login, it supports mqtt and the esp32 also has on board wifi which helps with communication. The board is also less expensive than a Pi 3 and can help with costs

ESP32 max power consumption : 240mA
Pi 3 : 980mA 

## Parking Node

# - AML-S905X-CC (Le Potato)
The AML is a competetor to the Pi, made to perform better for a better cost and lesser power consumption, the AML also does better for processing and supports common video encodings which makes it a good choice to run the video processing, it also is a good performer in single and multi threaded performance.

The AML uses about half of what the Pi 3 uses in power which makes it great for lowering power use







# Sources for information
ESP Power Draw: https://hackaday.io/project/193628-metashunt-high-dynamic-range-current-measurement/log/225599-example-esp32-wifi-and-low-power-modes#:~:text=When%20connected%20to%20WiFi%20and%20operating%20at,level%2048%2C000%20times%20lower%20than%20its%20maximum!

Pi 3 Power Draw: https://www.pidramble.com/wiki/benchmarks/power-consumption#:~:text=Table_title:%20Raspberry%20Pi%203%20B+%20Table_content:%20header:,Power%20Consumption:%20980%20mA%20(5.1%20W)%20%7C

AML-S905X-CC: https://www.libre.computer/blogs/performance-and-power-consumption-comparison-for-aml-s905x-cc-le-potato-and-raspberry-pi-3-model-b/