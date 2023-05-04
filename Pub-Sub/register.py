# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 12:08:05 2023

@author: gsvn32
"""
from xmlrpc.server import SimpleXMLRPCServer
import sqlite3
import threading
import time
port_for_topics=2
# Define a global counter variable
allowed_brokers=5
active_ports = []
b_ports=[8001,8002,8003,8004,8005]
r_port=8000
def create_database():
	with sqlite3.connect('data/brokers.db') as conn:
		   conn.execute('''CREATE TABLE IF NOT EXISTS brokers 
                    (topic TEXT, port NUMBER)''')
#call to create the brokers table in db
#create_database()
# update a broker record with the specified values
def assign_broker(topic, port):
	print(f'called assign port with {topic, port}')
	with sqlite3.connect('data/brokers.db') as conn:
		conn.execute('UPDATE brokers SET port = ? WHERE topic = ?', (port, topic))
		conn.commit()
		
	print(broker_info())
# Reset topic port to 0
def reset_broker(port):
	print(f'missing: {port}')
	with sqlite3.connect('data/brokers.db') as conn:
		conn.execute('UPDATE brokers SET port = 0 WHERE port = ?', (port,))
		conn.commit()
		
# retrieve the broker information
def broker_info():
    with sqlite3.connect('data/brokers.db') as conn:
        cursor = conn.execute('SELECT * FROM brokers WHERE port=0')
        result = cursor.fetchall()
        return result

# Define a function that runs on a separate thread and reset missing ports
def thread_function():
	global active_ports
	while True:
		time.sleep(60)  # Wait for 5 seconds
		if len(set(active_ports)) < allowed_brokers:
			#some brokers are missing
			for i in range(1,allowed_brokers+1):
				if r_port+i not in active_ports:
					reset_broker(r_port+i)
		active_ports=[]
# Start the thread
thread = threading.Thread(target=thread_function)
thread.start()

server = SimpleXMLRPCServer(("localhost", r_port))
print(f"Listening on port {r_port}...")
# Register topics function
def reg_topic():
	print('Started Register request')
	free_port=b_ports.pop(0)
	b_list = broker_info()
	print(b_list)
	if len(b_list)>=port_for_topics:
		for i in range(port_for_topics):
			temp=b_list.pop(0)
			assign_broker(temp[0],free_port)
	else:
		for i in b_list:
			assign_broker(i[0],free_port)
	return free_port
def reg_heartbeat(port):
	if port not in active_ports:
		active_ports.append(port)
	return 1


server.register_function(reg_topic)
server.register_function(reg_heartbeat)
# Run the server's main loop
server.serve_forever()

