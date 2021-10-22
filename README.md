# R3-SoftwareTask2-NikolasTrivanovic

link to the video demo: https://streamable.com/nvfol5

## Foreword: 

-in the video demo of the programs running the rover appears at a constant speed but that is just because I held the joystick fully down during the demo, the speed will vary (PWM) depending on how extended the joystick is. 

-for the client GUI translation of what is happening to the rover during turns the rover doesn't turn around the center of its body. I wasn't able to fix this is the time I allowed myself to work on the task since midterms are about to start and I need to focus on those. If I have time before the final submission date I will try to fix it. Also, the white rectangle boundary is just for show, the rover can drive off the screen I will also fix this too if I have time since it's beyond the scope of the task and I just did it because I was having fun.

-if I have more time to spare I will also make it so the GUI of the rover is updated with the data sent back from the server. This way it's more accurate since the data that is actually received by the server is updating the clients GUI.

-also forgot to check that the controller wasn't unplugged in the middle of data so I need to check before input is gathered from the controller that it is still connected

## Program

-to run the programs you can run either the server first and have it wait for a client to connect or run the client first and wait for the server to start up

## Client.py

###### controller: PS4

###### controller commands

###### left joystick: controls the output and direction of the rover motors

###### x button: closes the client, the client GUI and the server

###### square button: initiates a data transfer to the server

###### circle button: stops a data transfer to the server

###### triangle button: attempts connection to the server


In the client.py file there are two classes that together send data from the controller to the server and allow the client to interact with a GUI. The GUI that the client sees displays if the server is up and running, if the controller is connected and if we are sending controller input to the server. When the client.py file is started and the server is not running the client can press the triangle button on the remote to try to connect to the server again after running server.py. Also upon starting the client will attempt to initialize the controller if one is plugged into the computer. If the controller is not yet connected the client can press the r key to attempt to initialize the controller again after it’s plugged in. Note pressing r immediately after connecting the controller will not connect the controller because it needs some time for the computer to register it. 

Once the client and server are running and the client is connected to the server they are shown a white border and a white rectangle in the center. This border represents the boundary where the theoretical rover can travel in and the white rectangle is the rover. At this point, the client can initiate a data transfer to the server by pressing the square button on the controller. This data transfer is sending the vertical and horizontal axis values of the left joystick on the controller. While the data is being sent the GUI of the client will translate what is happening to the rover as the joystick is controlled. Pressing the circle button on the controller will stop the data transfer.

After stopping the data transfer to the server the client can either close out of the GUI with the mouse, closing its socket/connection to the server, or by pressing the x button. Pressing the x button on the controller will close the clients connection to the server as well as close the server.

## Server.py

In the server.py file there is one class that runs the server that receives the data from the controller and prints out the data in a converted format. The converted format of the data represents 4 motors being powered with pulse width modulation and driving with differential steering. When the server.py file is started without the client started it will simply wait for the client to start and attempt a connection. If the client is already started when the server is running it will automatically connect and if the client closes while the server is running it will simply wait for them to start and connect again.


