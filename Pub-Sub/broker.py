# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 12:08:05 2023

@author: gsvn32
"""
import json
import threading
import queue
import socket
import sqlite3
import time
#global variables
broker_host='localhost'
notify_port=9000
notify_host='localhost'
# Create a message queue named 'my_q'

import xmlrpc.client

# Register broker to topics
try:
    with xmlrpc.client.ServerProxy("http://localhost:8000/") as proxy:

        # Call the remote re_topic() function
        broker_port = proxy.reg_topic()
        print(f"Broker registered on port: {broker_port}")
except xmlrpc.client.ProtocolError as error:
    print("ProtocolError: {}".format(error))

my_q = queue.Queue()

# retrieve the subs for a Topic given the topic name
def get_subs(name):
	with sqlite3.connect('data/topics.db') as conn:
		cursor = conn.execute('SELECT subscribers FROM topics WHERE name = ?', (str(name),))
		result = cursor.fetchone()
		return result

# Define a function to handle incoming message
def handle_data(sock):
    data = b''
    while True:
        # Receive data from the socket
        chunk = sock.recv(1024)
        if not chunk:
            break
        data += chunk

    # Decode the JSON object
    json_data = data.decode()
    data_obj = json.loads(json_data)

    # Put the data object in the message queue
    my_q.put(data_obj)

    # Close the socket
    sock.close()

# Define a thread to listen for incoming messages
def tcp_listener():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((broker_host, broker_port))
	print(f"Sratred TCP Listener on: {broker_port}")
	sock.listen(1)
	while True:
		conn, addr = sock.accept()
		threading.Thread(target=handle_data, args=(conn,)).start()


	
def send_heartbeat():
	global broker_port
	while True:
		time.sleep(5)  #
		try:
			with xmlrpc.client.ServerProxy("http://localhost:8000/") as proxy:
				#Call the remote pow() function
				proxy.reg_heartbeat(broker_port)
		except:
			print("Unable to send heartbeat")
# Define a function to process the messages in the message queue
def process_message():
	while True:
		try:
			# Get data from the message queue
			msg_dic = dict(my_q.get(block=True, timeout=1))
			# Process the message
			subs=get_subs(msg_dic['topic'])[0].split(',')
			data={}
			
			#send data to notify_service
			# Create a TCP connection to the notify service
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((notify_host, notify_port))
			
			# Create a JSON object
			data['content'] = msg_dic['content']
			data['subs'] = subs
			data['pubName'] = msg_dic['uname']
			data['topic'] = msg_dic['topic']
			data['title'] = msg_dic['title']
			json_data = json.dumps(data)
			print(f'Recieved {json_data}')
			# Send the JSON object to the notify service
			sock.send(json_data.encode())
			
			# Close the connection
			sock.close()
		except queue.Empty:
			pass

# Start the tcp listener thread
tcp_listener_thread = threading.Thread(target=tcp_listener, daemon=True)
tcp_listener_thread.start()

# Start the message processing thread
msg_processing_thread = threading.Thread(target=process_message, daemon=True)
msg_processing_thread.start()

# Start the heartbeat thread
threading.Thread(target=send_heartbeat, daemon=True).start()

# Wait for both threads to finish their jobs
tcp_listener_thread.join()
msg_processing_thread.join()


