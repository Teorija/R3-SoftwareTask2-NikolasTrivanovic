import pygame as pg
import socket
import math

from pygame.version import ver

pg.init()
CLOCK = pg.time.Clock()

COLOURS = {
    "black" : (0, 0, 0),
    "gray1" : (32, 32, 32),
    "white" : (255, 255, 255)
}

class Rover:
    def __init__(self):
        # - initialize the starting conditions of the rover - #
        self.x_pos = 375
        self.y_pos = 375
        self.speed = 2
        self.rotation_angle = 0
        
        self.rover = pg.Surface((25,50)).convert_alpha()
        self.rover.fill(COLOURS['white'])

        # - a copy is made of the original rover surface because rotating the same surface results in quality loss - #
        # - as a result the copy of the rover rotates the original each time instead of rotating the same image each time - #
        self.rover_copy = self.rover.copy()
        self.rover_copy_rect = self.rover_copy.get_rect()
        self.rover_copy_rect.center = (self.x_pos, self.y_pos)

    def renderRover(self, surface):
    # ------------------------------------------------------ #
    # renderRover - draws the rover to the client GUI screen #
    # ------------------------------------------------------ #

        surface.blit(self.rover_copy, self.rover_copy_rect)

    def updateRover(self, horizontal_movement, vertical_movement):
    # ------------------------------------------------------------------------------------------------------ #
    # updateRover - updates the position of the rover on the client GUI screen based on the controller input #
    #                                                                                                        #
    #   arguments - takes in the 'horizontal_movement' and 'vertical_movement' from the controller joystick  #
    # ------------------------------------------------------------------------------------------------------ #

        # - the controller inputs goes from -1 to 1 so its multiplied by a constant to give it a max speed (pixels per frame) - #
        vertical_movement = vertical_movement * self.speed
        horizontal_movement = horizontal_movement * self.speed

        # - check if the joystick is turning to the left or the right - #
        # *** note: turning takes precedence over moving forward and backwards since the joystick can have inbetween positions *** #
        if horizontal_movement != 0:

            # - reset the direction that the rover is pointing in if it completes a full circle - #
            if abs(self.rotation_angle) >= 360:
                self.rotation_angle = 0

            # - rotate the rover in the direction of the joystick - #
            # *** note: midterms have started so I couldnt figure out how to rotate the rover around its center in the time I allotted myself to work on this *** #
            self.rotation_angle += -round(horizontal_movement)
            self.rover_copy = pg.transform.rotate(self.rover, self.rotation_angle)

        # - check if the rover is moving forward or backwards- #
        else:

            # - calculate the new position of the rover using trigonometry given that we have the direction (in degrees) that we are pointing in - #
            # - and the speed (vertical movement value) the rover is moving at - #
            new_x = math.sin(math.radians(self.rotation_angle)) * vertical_movement
            new_y = math.cos(math.radians(self.rotation_angle)) * vertical_movement
            self.x_pos += new_x
            self.y_pos += new_y
            self.__updateCenter()

    def __updateCenter(self):
    # -------------------------------------------------------------------------------- #
    # updateCenter - updates the center position of the rover on the client GUI screen #
    # -------------------------------------------------------------------------------- #

        self.rover_copy_rect.center = (self.x_pos, self.y_pos)

class Client:
    def __init__(self, host_ip, host_port):

        # - initialize the address to connect to - #
        self.server_ip = host_ip
        self.server_port = host_port

        # - initialize client flags - #
        self.running = True
        self.controller_connected = False
        self.server_running = False
        self.sending_data = False

        # - initialize GUI status indicators - #
        self.server_status = 'server status - offline'
        self.controller_status = 'controller status - disconnected'

        # - initialize GUI display and connections to the controller and server - #
        self.__initializeGUI()
        self.__initializeController()
        self.__initializeConnection()
       
    def runClient(self):
    # -------------------------------------------- #
    #  runClient - main loop that runs the client  #
    #                                              #
    #      renders and updates the GUI screen      #
    #                                              #
    #   checks controller and mouse interactions   #
    #                                              #
    # updates controller input and sends to server #
    # -------------------------------------------- #

        while self.running:
            CLOCK.tick(60)

            # - render and update GUI - #
            self.__renderScreen()
            self.__updateText()

            # - check controller and mouse interactions - #
            self.__checkInput()

            # - establish connection to controller and update inputs from it - #
            if self.controller_connected:

                # - establish connection to the server and send controller input - #
                if self.server_running and self.sending_data:
                    
                    self.__sendData((self.horizontal_movement_axis, self.vertical_movement_axis))
                    pg.time.delay(5)

                    # - updates the rover based on controller input sent to the server - #
                    self.rover.updateRover(self.horizontal_movement_axis, self.vertical_movement_axis)

                # - get new controller input - #
                self.__updateControllerInput()

    def __checkInput(self):
    # --------------------------------------------------------- #
    # checkInput - checks for controller and mouse interactions #
    # --------------------------------------------------------- #

        for event in pg.event.get():

            # - check if the GUI is closed out with the cursor - #
            if event.type == pg.QUIT:

                # - stop running the client and close its socket connection to the server - #
                self.running = False
                self.client_socket.close()
            
            # - if the controller isn't connected plug it in and press r to connect it - #
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.__initializeController()

            # - establish connection to the controller - #
            if self.controller_connected:

                # - press the triangle button on the controller (PS4) to connect to the server if it's not already connected - #
                if self.triangle_button and not self.server_running:
                    self.__initializeConnection()

                # - establish connection to the server - #
                if self.server_running:

                    # - press the square button on the controller (PS4) to start transmitting controller input to the server - #
                    if self.square_button:
                        print('starting data transfer')
                        self.sending_data = True
                        self.server_status = 'server status - online - sending data'

                    # - press the circle button on the controller (PS4) to stop transmitting controller input to the server - #
                    if self.circle_button:
                        print('stopping data transfer')
                        self.sending_data = False
                        self.server_status = 'server status - online'

                    # - press the x button on the controller (PS4) to shut the server down and close the client - #
                    if self.x_button:
                        print('shutting down server')
                        self.client_socket.sendall(b'close server') # message telling the server to close its socket
                        print('server is offline')
                        self.sending_data = False
                        self.server_running = False
                        self.running = False
                        self.client_socket.close()

    def __initializeConnection(self):
    # -------------------------------------------------------------------------- #
    # initializeConnection - attempts to connect to the specified server address #
    # -------------------------------------------------------------------------- #

        # - try to connect the client to the server using ipv4 format and TCP communication - #
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))

        # - if the server isn't running return to the loop to allow for another attempt at connecting - #
        except socket.error:
            print('server is offline')
            self.server_running = False
            self.server_status = 'server status - offline'
            return

        # - if the server connection was established set the appropriate flags - #
        print('server connection established')
        self.server_running = True
        self.server_status = 'server status - online'

    def __sendData(self, data):
    # --------------------------------------------------- #
    # sendData - sends the controller input to the server #
    # --------------------------------------------------- #

        # - convert the controller input to the appropriate format for transmission and send it to the server - #
        movement = self.__convertData(data)
        self.client_socket.sendall(movement)

    def __convertData(self, data):
    # ---------------------------------------------------------------------------------- #
    # convertData - converts the controller input to a byte-like object for transmission #
    #                                                                                    #
    #                  arguments - takes in the controller input 'data'                  #
    #                                                                                    #
    #        returns the controller input in a acceptable form for transmission          #
    # ---------------------------------------------------------------------------------- #

        # - converts data to ---> b'<horizontal joystick value> <vertical joystick value>' - #
        # - this is done because only byte-like objects are accepted for transmission - #
        horizontal_data = str(data[0])
        vertical_data = str(data[1])
        movement = horizontal_data + " " + vertical_data

        return movement.encode("ascii")
            
    def __initializeController(self):
    # --------------------------------------------------------------------------- #
    # initializeController - attempts to connect to a plugged in controller (PS4) #
    #                                                                             #
    #       initializes the controller inputs for 3 buttons and 1 joystick        #
    #                                                                             #
    #                   x button - closing client and server                      #
    #        square button - starts sending controller input to the server        #  
    #        circle button - stops sending controller input to the server         #
    #        triangle button - attempts to connect to the server                  #
    #                                                                             #
    #            left joystick - used to control the rover motors                 #                                                                   
    # --------------------------------------------------------------------------- #

        # - try to connect to a plugged in controller (PS4) if ones present - #
        try:
            pg.joystick.init()
            self.controller = pg.joystick.Joystick(0)

        # - if no controller (PS4) is pluggen in return to the loop allow for another attempt at connecting - #
        except pg.error:
            print('no controller detected, refresh the client (r - key) with a connected controller')
            self.controller_connected = False
            self.controller_status = 'controller status - disconnected'
            return

        # - if the controller was connected set the appropriate flags - #
        print('controller connection established')
        self.controller_connected = True
        self.controller_status = 'controller status - connected'

        # - initialize the buttons and joystick values - #
        self.horizontal_movement_axis = self.controller.get_axis(0)
        self.vertical_movement_axis = self.controller.get_axis(1)

        self.x_button = self.controller.get_button(0)
        self.circle_button = self.controller.get_button(1)
        self.triangle_button = self.controller.get_button(2)
        self.square_button = self.controller.get_button(3)
            
    def __updateControllerInput(self):
    #-------------------------------------------------------------------------------------- #
    # updateControllerInput - gets the current state of the controller buttons and joystick #
    # ------------------------------------------------------------------------------------- #

        self.horizontal_movement_axis = self.controller.get_axis(0)
        self.vertical_movement_axis = self.controller.get_axis(1)

        self.x_button = self.controller.get_button(0)
        self.circle_button = self.controller.get_button(1)
        self.triangle_button = self.controller.get_button(2)
        self.square_button = self.controller.get_button(3)

    def __initializeGUI(self):
    # -------------------------------------- #
    # initializeGUI - sets up the client GUI #
    # -------------------------------------- #

        self.screen_w = 750
        self.screen_h = 750

        # - create the GUI display and the screen drawn to the display - #
        self.display = pg.display.set_mode((self.screen_w, self.screen_h))
        pg.display.set_caption('R3 Software Task 2 - Client GUI')
        self.screen = pg.Surface((self.screen_w, self.screen_h))
        self.screen.fill(COLOURS["gray1"])

        # - set up variable to write text to the GUI screen and initialize the status text of the server and controller - #
        self.write_text = pg.font.Font('AltoneTrial-Regular.ttf', 15)
        self.server_status_text = self.write_text.render(self.server_status, True, COLOURS['white'], COLOURS['gray1'])
        self.controller_status_text = self.write_text.render(self.controller_status, True, COLOURS['white'], COLOURS['gray1'])

        # - set up the rover displayed on the client GUI to demonstrate what the controller inputs sent to the server are doing - #
        self.rover_boundary = pg.Rect(30,30,690,690)
        self.rover = Rover()

    def __updateText(self):
    # --------------------------------------------------------------------------------------- #
    # updateText - updates the state of the controller and server displayed on the client GUI #
    # --------------------------------------------------------------------------------------- #

        self.server_status_text = self.write_text.render(self.server_status, True, COLOURS['white'], COLOURS['gray1'])
        self.controller_status_text = self.write_text.render(self.controller_status, True, COLOURS['white'], COLOURS['gray1'])

    def __renderScreen(self):
    # -------------------------------------------------------------------------------------------- #
    # renderScreen - draws the controller text, server status text and the rover on the client GUI #
    # -------------------------------------------------------------------------------------------- #

        self.display.blit(self.screen, (0,0))
        self.screen.fill(COLOURS['gray1'])
        self.display.blit(self.server_status_text, (75,5))
        self.display.blit(self.controller_status_text, (450,5))

        # - if the server is running and connected to show what the rover is doing based on the controller input - #
        if self.server_running:
            pg.draw.rect(self.screen, COLOURS['white'], self.rover_boundary, width=1)
            self.rover.renderRover(self.screen)

        pg.display.update()

if __name__ == "__main__":
    client = Client('127.0.0.1', 33333)
    client.runClient()
