import socket
import sys, os, signal
from urlparse import urlparse, parse_qs
import Queue
import thread

def EchoClientThread(queue, port) :
	while 1:
	
		if(queue.qsize() == 0):
			continue

		client_socket = queue.get()

		message = client_socket.recv(4096)
        
		while (len(message) > 0):

			if ("KILL_SERVICE" in message):
				client_socket.send("Server killed")
				print "*** Killing server"
				client_socket.close()
				os.kill(os.getpid(), signal.SIGINT)
			elif (message[:4] == "HELO"):
				message = message.rstrip()
				message = message + "\nIP:46.101.193.203\nPort:8000\nStudentID:16336670\n"
				client_socket.send(message)
			else:
				message = message.upper().rstrip()
				client_socket.send(message)
				
			message = client_socket.recv(4096)
		else:
			client_socket.close()
			return

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