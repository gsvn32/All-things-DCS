# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 12:08:05 2023

@author: gsvn32
"""

import json
import threading
import queue
import socket
import smtplib
import sqlite3
port=9000
host='localhost'
# Create a message queue named 'my_q'
my_q = queue.Queue()

# retrieve the name,email for a user given their uname
def get_user_info(uname):
    with sqlite3.connect('data/user_db.db') as conn:
        cursor = conn.execute('SELECT name,email FROM users WHERE uname = ?', (str(uname),))
        result = cursor.fetchone()
        return result
	
def send_email(name, email,content):
	# Email settings
	print(name)
	print(email)
	print(content)

	sender_email = 'nikhilgangisetty222@gmail.com' # Enter sender email address
	sender_password = 'vpmuaocxhyjmeopp' # Enter sender email password
	receiver_email = email # Enter receiver email address
	message = f'Subject: Notification\n\nHello {name}\n\n' + content
	# Sending email
	try:
		with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
			smtp.starttls()
			smtp.ehlo()
			smtp.login(sender_email,sender_password)
			smtp.sendmail(sender_email, receiver_email, message)
	except Exception as e:
		print('Error sending email to', e)

 


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
    sock.bind((host, port))
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
			for i in msg_dic['subs']:
				user_records = get_user_info(i)
				if user_records is None or user_records[0]=='':
					#No user found
					pass
				else:
					#send email to sub
					send_email(user_records[0],user_records[1], msg_dic['content'])
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



