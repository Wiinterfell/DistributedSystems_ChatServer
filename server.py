import socket
import sys, os, signal
from urlparse import urlparse, parse_qs
import Queue
import thread

chatRoomsClients = {}
chatRoomsNames = []
clientNames = []

def messageToRoom(message, roomName):
	for client in chatRoomsClients[roomName]:
		print chatRoomsClients[roomName]
		socket = chatRoomsClients[roomName][client]
		socket.send(message)
		print message

def EchoClientThread(queue, port) :
	while 1:
	
		if(queue.qsize() == 0):
			continue

		client_socket = queue.get()

		message = client_socket.recv(4096)
        
		while (len(message) > 0):

			if ("KILL_SERVICE" in message):
				client_socket.send("Server killed\n")
				print "*** Killing server"
				client_socket.close()
				os.kill(os.getpid(), signal.SIGINT)

			elif (message[:4] == "HELO"):
				message = message.rstrip()
				message = message + "\nIP:46.101.193.203\nPort:8000\nStudentID:16336670\n"
				client_socket.send(message)

			elif ("JOIN_CHATROOM" in message):
				infos = message.split("\n")
				print infos
				roomName = infos[0][15:]
				ipServer = "46.101.193.203"
				portServer = port
				if (roomName in chatRoomsNames):
					roomRef = chatRoomsNames.index(roomName)
				else:
					roomRef = len(chatRoomsNames)
					chatRoomsNames.append(roomName)
					chatRoomsClients[roomName] = {}
				clientName = infos[3][13:]
				if not (clientName in clientNames):
					clientId = len(clientNames)
					clientNames.append(clientName)
				else:
					clientId = clientNames.index(clientName)
				if not (clientId in chatRoomsClients[roomName]):
					chatRoomsClients[roomName][clientId] = client_socket
				print roomName
				print roomRef
				print clientId
				print clientName
				result = "JOINED_CHATROOM: " + roomName + "\nSERVER_IP: " + str(ipServer) + "\nPORT: " + str(portServer) + "\nROOM_REF: " + str(roomRef) + "\nJOIN_ID: " + str(clientId) + "\n"
				chatMessage = "CHAT: " + str(roomRef) + "\nCLIENT_NAME: " + clientName + "\nMESSAGE: " + clientName + "joined Chatroom\n\n"
				client_socket.send(result)
				messageToRoom(chatMessage, roomName)

			elif ("LEAVE_CHATROOM" in message):
				infos = message.split("\n")
				roomRef = int(infos[0][16:])
				clientId = int(infos[1][9:])
				clientName = infos[2][13:]
				print clientName
				if clientName in clientNames:
					realClientId = clientNames.index(clientName)
				else:
					result = "ERROR: Client not recognized\n"
					client_socket.send(result)
					break
				if roomRef < len(chatRoomsNames):
					roomName = chatRoomsNames[roomRef]
				else:
					result = "ERROR: Unknown channel\n"
					client_socket.send(result)
					break
				result = "LEFT_CHATROOM: " + str(roomRef) + "\nJOIN_ID: " + str(clientId) + "\n"
				messageToRoom(result, roomName)
				print len(chatRoomsClients[roomName])
				if (realClientId in chatRoomsClients[roomName]):
					del chatRoomsClients[roomName][realClientId]
					print len(chatRoomsClients[roomName])
				else:
					client_socket.send(result)
				

			elif ("DISCONNECT" in message):
				infos = message.split("\n")
				clientName = infos[2][13:]
				if (clientName in clientNames):
					clientId = clientNames.index(clientName)
					found = False
					for i in chatRoomsClients:
						if  clientId in chatRoomsClients[i]:
							roomRef = chatRoomsNames.index(i)
							result = "LEFT_CHATROOM: " + str(roomRef) + "\nJOIN_ID: " + str(clientId) + "\n"
							messageToRoom(result, i)
							del chatRoomsClients[i][clientId]
							found = True
					del clientNames[clientId]
					if not(found):
						client_socket.send(result)
				else:
					result = "ERROR: Client not recognized\n"
					client_socket.send(result)

			elif ("CHAT" in message):
				infos = message.split("\n")
				roomRef = int(infos[0][6:])
				clientName = infos[2][13:]
				clientMessage = infos[3][9:]
				if clientName in clientNames:
					realClientId = clientNames.index(clientName)
				else:
					result = "ERROR: Client not recognized\n"
					client_socket.send(result)
					break
				if roomRef < len(chatRoomsNames):
					print "ok"
					roomName = chatRoomsNames[roomRef]
				else:
					result = "ERROR: Unknown channel\n"
					client_socket.send(result)
					break
				result = "CHAT: " + str(roomRef) + "\nCLIENT_NAME: " + clientName + "\nMESSAGE: " + clientMessage + "\n\n"
				messageToRoom(result, roomName)

			else:
				message = message.upper().rstrip()
				client_socket.send(message)
				


			message = client_socket.recv(4096)
		
		#else:
			#client_socket.close()
			#return

if __name__ == "__main__":
	print "*** Creating server socket"
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	print "*** Binding to port"
	server_socket.bind(("0.0.0.0", int(sys.argv[1])))

	server_socket.listen(100)
	print "*** Listening"

	maxThreads = int(sys.argv[2]);
	queue = Queue.Queue()

	for i in range(0, maxThreads):
		t = thread.start_new_thread(EchoClientThread, (queue, int(sys.argv[1])))

	while 1:
	    print "*** Waiting for client connections"

	    print "*** Adding a new client to the queue"
	    client_socket, address = server_socket.accept()
	    queue.put(client_socket)