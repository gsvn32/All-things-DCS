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
broker_port=8000
broker_host='localhost'
notify_port=9000
notify_host='localhost'
# Create a message queue named 'my_q'
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
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_data, args=(conn,)).start()

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

# Wait for both threads to finish their jobs
tcp_listener_thread.join()
msg_processing_thread.join()


