import socket

class Server:
    def __init__(self, ip, port):
        # - initialize the servers starting conditions - #
        # - host is used because this tasks requires using the local machine to talk to itself between programs - #
        self.host_ip = ip
        self.host_port = port

        # - set up the server for ipv4 format and TCP communication - #
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.bind((self.host_ip, self.host_port))

        # - variables to store the clients information when they connect to the server - #
        self.client_address = None
        self.client_socket = None
    
        # - flags to determine if the server has a client connected and is receiving data from them - #
        self.connected = False
        self.receiving = False

        # - small buffer size for data is used because a string representation of the joystick values is sent which is small - #
        # - example joystick string sent b'0.998 0.567' - #
        self.data_buffer_size = 128 

    def runServer(self):
    # -------------------------------------------------------------------------------------------------------------------- #
    # runServer - loop that tries to establish a connection to a client if its not already and then receive data from them #
    # -------------------------------------------------------------------------------------------------------------------- #

        while not self.connected:
            self.__establishConnection()

        self.__recieveData()

    def __establishConnection(self):
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # establishConnection - listen for a client to connect to the server and when they do accept the connection and store their information in a socket and address #
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------- #

        self.listening_socket.listen()
        print('waiting for connection...')
        self.connection_socket, self.client_address = self.listening_socket.accept()
        print('connection from: ', self.client_address)
        self.connected = True
        self.receiving = True

    def __recieveData(self):
    # -------------------------------------------------------------------------------------------------------------------------------------------- #
    # receiveData - while the server is receiving data from the client interpret that data into PWM motor control values for differential steering #
    # -------------------------------------------------------------------------------------------------------------------------------------------- #

        while self.receiving:
            data = self.connection_socket.recv(self.data_buffer_size)

            # - if the client disconnects stall the server and wait for a client to connect again - #
            if data == b'':
                print('connection to', self.client_address, 'was terminated')
                self.receiving = False
                self.connected = False
                self.runServer()

            # - if the client sends this message close down the server - #
            if data == b'close server':
                print('server shutting down')
                self.listening_socket.close()
                self.connection_socket.close()
                break

            self.__interpretData(data)

    def __interpretData(self, data):
    # ------------------------------------------------------------------------------------------------------------------- #
    # interpretData - translates the joystick data from the client into PWM values for motors using differential steering #
    #                                                                                                                     #
    #                       arguments - takes in the 'data' sent from the client to be interpreted                        #
    # ------------------------------------------------------------------------------------------------------------------- #

        # - the data was sent as a byte-like object so it must be decoded back to a string to split the joystick values into theyre respective variables - #
        movement = data.decode("ascii").split(" ")
        horizontal_movement = round(float(movement[0])*255)
        vertical_movement = round(float(movement[1])*255)

        # - print out how the motors of the rover should behave given the joystick input sent from the client - #
        if horizontal_movement < 0:
            print('[r' + str(abs(horizontal_movement)) + '][r' + str(abs(horizontal_movement)) + '][f' + str(abs(horizontal_movement)) + '][f' + str(abs(horizontal_movement)) + ']')
        elif horizontal_movement > 0:
            print('[f' + str(abs(horizontal_movement)) + '][f' + str(abs(horizontal_movement)) + '][r' + str(abs(horizontal_movement)) + '][r' + str(abs(horizontal_movement)) + ']')
        elif vertical_movement < 0:
            print('[f' + str(abs(vertical_movement)) + '][f' + str(abs(vertical_movement)) + '][f' + str(abs(vertical_movement)) + '][f' + str(abs(vertical_movement)) + ']')
        elif vertical_movement > 0:
            print('[r' + str(abs(vertical_movement)) + '][r' + str(abs(vertical_movement)) + '][r' + str(abs(vertical_movement)) + '][r' + str(abs(vertical_movement)) + ']')
        else:
            print('no movement')

if __name__ == "__main__":
    server = Server('127.0.0.1', 33333)
    server.runServer()