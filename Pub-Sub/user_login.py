#User Registration and Login 
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import sqlite3

def create_database():
	with sqlite3.connect('data/user_db.db') as conn:
		   conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (Uname TEXT, name TEXT, pass TEXT, email TEXT, token TEXT)''')
#call to create the users table in db
#create_database()

# create a new user record with the specified values
def create_new_user(uname, name, password, email):
    with sqlite3.connect('data/user_db.db') as conn:
        conn.execute('INSERT INTO users (uname, name, pass, email) VALUES (?, ?, ?, ?)', (uname, name, password, email))
        conn.commit()
# retrieve the uname and pass for a user given their uname or email
def get_user_credentials(uname_or_email,passwd):
    with sqlite3.connect('data/user_db.db') as conn:
        cursor = conn.execute('SELECT uname,name,email FROM users WHERE (uname = ? OR email = ?) AND pass = ?', (uname_or_email, uname_or_email,passwd))
        result = cursor.fetchone()
        return result
# retrieve the uname and pass for a user given their uname or email
def check_user_exists(uname,email):
    with sqlite3.connect('data/user_db.db') as conn:
        cursor = conn.execute('SELECT uname FROM users WHERE uname = ? OR email = ?', (uname, email))
        result = cursor.fetchone()
        return result

# update the token for a user given their uname or email
def update_user_token(uname,token):
    with sqlite3.connect('data/user_db.db') as conn:
        conn.execute('UPDATE users SET token = ? WHERE uname = ?', (token, uname))
        conn.commit()
# define the server class
class MyServer(BaseHTTPRequestHandler):
    
	# define the POST method handler
	def do_POST(self):
		# get the length of the incoming request body
		content_length = int(self.headers['Content-Length'])

		# read the request body
		request_body = self.rfile.read(content_length).decode('utf-8')

		# parse the request body as JSON
		request_data = json.loads(request_body)
		
		if request_data['action'] == 'register':
			response_data = action_register(request_data['name'] ,request_data['uname'] ,request_data['pass'] ,request_data['email'] )
		elif request_data['action'] == 'login':
			response_data = action_login(request_data['uname'], request_data['pass'])
		

		# convert the response data to JSON
		response_body = json.dumps(response_data).encode('utf-8')

		# set the response headers
		self.send_response(200)
		self.send_header('Content-Type', 'application/json')
		self.send_header('Content-Length', len(response_body))
		self.end_headers()
        
		# send the response body
		self.wfile.write(response_body)

		return
def action_login(uname,passwd):
	#Process user if found
	user_records = get_user_credentials(uname,passwd)
	print(user_records)
	if user_records is None or user_records[0]=='':
		response_data = {'error':True,'message': 'Invalid credentails'}			
	else:
		timestamp = int(time.time())
		token= user_records[0]+str(timestamp)
		update_user_token(token,user_records[0])
		response_data = {'error':False,'message': 'Hello, ' + user_records[0] + '!','token':token, 'uname':user_records[0],'name':user_records[1],'email':user_records[2]}
	return response_data
def action_register(name,uname,passwd,email):
	if check_user_exists(uname,email) is None:
		try:
			create_new_user(uname, name, passwd, email)
			response_data = {'error':False,'message': 'Registration complete, Please login'}	
		except:
			response_data = {'error':True,'message': 'something went wrong on our end!!!'}	
	else:
		response_data = {'error':True,'message': 'Username/Email alread Exists'}	
	return 	response_data
# create the server object
server = HTTPServer(('localhost', 25678), MyServer)

# start the server
print('Starting server...')
server.serve_forever()
