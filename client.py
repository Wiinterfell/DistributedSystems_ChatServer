import socket
import sys

while 1:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try :
        client_socket.connect((sys.argv[1], int(sys.argv[2])))
    except :
        print 'Unable to connect'
        sys.exit()

    data = raw_input("What do you want to send ?\n")

    client_socket.send(data + "\n")
    result = client_socket.recv(4096)

    if (result == "Server killed"):
        client_socket.close()
        break;
    else:
        print result