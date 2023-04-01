import tkinter as tk
from tkinter import ttk
#Imports for Http proto
import requests
import json
LARGEFONT =("Verdana", 35)

user = {'name':"",
		'email':"",
		'uname':"",
		'token':""
		}
class NewsletterApp(tk.Tk):
	
	# __init__ function for class NewsletterApp
	def __init__(self, *args, **kwargs):
		# __init__ function for class Tk
		tk.Tk.__init__(self, *args, **kwargs)
		# creating a container
		container = tk.Frame(self)
		container.pack(side = "top", fill = "both", expand = True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)
		# initializing frames to an empty array
		self.frames = {}
		# iterating through a tuple consisting
		# of the different page layouts
		for F in (LoginPage, RegisterPage, MainPage):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky ="nsew")
		self.show_frame(LoginPage)
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()

	def validate_login(self,uname,password):
		print("Validating Login")
		# define the request data
		request_data = {'action':'login','uname': uname,'pass':password}
		try:
			# send the POST request
			response = requests.post('http://localhost:25678', json=request_data, timeout=10)

			# extract the response data
			response_data = json.loads(response.content.decode())

			# print the response data
			print(response_data['message'])
			if response_data['error'] == False:
				#create the user object to maintain state
				user['name'] = response_data['name']
				user['email'] = response_data['email']
				user['uname'] = response_data['uname']
				user['token'] = response_data['token']				
				self.show_frame(MainPage)
				self.frames[MainPage].write_uname(user['name'],user['token'])
			else:
				self.frames[LoginPage].write_error(response_data['message'])
		except:
			self.frames[LoginPage].write_error("something went wrong!!, Please try after some time")
	def register_req(self,name,uname,passwd,email):
		print("Register user")
		# define the request data
		request_data = {'action':'register','uname': uname,'pass':passwd,'name':name,'email':email}
		try:
			# send the POST request
			response = requests.post('http://localhost:25678', json=request_data, timeout=10)

			# extract the response data
			response_data = json.loads(response.content.decode())

			# print the response data
			print(response_data['message'])
			if response_data['error'] == False:
				self.show_frame(LoginPage)
				self.frames[LoginPage].write_error(response_data['message'])
			else:
				self.frames[RegisterPage].write_error(response_data['message'])
		except:
			self.frames[RegisterPage].write_error("something went wrong!!, Please try after some time")
		
	def publish_req(self):
		pass
	def somethinf():
		pass

	
#LoginPage
class LoginPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		#Heading
		ttk.Label(self, text ="Login/Register", font = LARGEFONT).grid(row = 0, column = 4)
		#login entries
		ttk.Label(self, text="Username/Email").grid(row = 1, column = 4)
		uname_e = ttk.Entry(self)
		uname_e.grid(row = 2, column = 4, padx = 10, pady = 10)
		ttk.Label(self, text="Password").grid(row = 3, column = 4, padx = 10, pady = 10)
		passw_e = ttk.Entry(self,show="*")
		passw_e.grid(row = 4, column = 4, padx = 10, pady = 10)
		ttk.Button(self, text="Log In",command = lambda : controller.validate_login(uname_e.get(),passw_e.get())).grid(row = 1, column = 1, padx = 10, pady = 10)
		ttk.Button(self, text="Register",
		command = lambda : controller.show_frame(RegisterPage)).grid(row = 2, column = 1, padx = 10, pady = 10)

		ttk.Label(self, text="New here? click on Register").grid(row = 5, column = 4, padx = 10, pady = 10)
		self.tooltip_l = ttk.Label(self)
		self.tooltip_l.grid(row = 6, column = 4, padx = 10, pady = 10)

	def write_error(self,msg):
		self.tooltip_l.config(text=msg,foreground="red")
		
#RegisterPage
class RegisterPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		#Heading
		ttk.Label(self, text ="Registration Form", font = LARGEFONT).grid(row = 0, columnspan=2,sticky="e")
		#entries
		ttk.Label(self, text="Name").grid(row = 1, column = 0, padx = 10, pady = 10,sticky="e")
		name_r = ttk.Entry(self)
		name_r.grid(row = 1, column = 1, padx = 10, pady = 10)
		ttk.Label(self, text="Username").grid(row = 2, column = 0, padx = 10, pady = 10,sticky="e")
		uname_r = ttk.Entry(self)
		uname_r.grid(row = 2, column = 1, padx = 10, pady = 10)
		ttk.Label(self, text="Password").grid(row = 3, column = 0, padx = 10, pady = 10,sticky="e")
		pass_r = ttk.Entry(self,show="*")
		pass_r.grid(row = 3, column = 1, padx = 10, pady = 10)
		ttk.Label(self, text="Email").grid(row = 4, column = 0, padx = 10, pady = 10,sticky="e")
		email_r = ttk.Entry(self,show="*")
		email_r.grid(row = 4, column = 1, padx = 10, pady = 10)
		
		ttk.Button(self, text="Back",command = lambda : controller.show_frame(LoginPage)).grid(row = 5, column = 0, padx = 10, pady = 10)
		ttk.Button(self, text="Register",
		command = lambda : controller.register_req(name_r.get(),uname_r.get(),pass_r.get(),email_r.get())).grid(row = 5, column = 1, padx = 10, pady = 10)
		self.tooltip_l = ttk.Label(self)
		self.tooltip_l.grid(row = 6, column = 0, padx = 10, pady = 10)

	def write_error(self,msg):
		self.tooltip_l.config(text=msg,foreground="red")

#MainPage
class MainPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		#Heading
		ttk.Label(self, text ="Main Page", font = LARGEFONT).grid(row = 0, columnspan=1)	
		#entries
		ttk.Button(self, text="LogOut",command = lambda : controller.show_frame(LoginPage)).grid(row = 1, column = 1, padx = 10, pady = 10)
		ttk.Button(self, text="Publish",
		command = lambda : controller.publish_req()).grid(row = 2, column = 1, padx = 10, pady = 10)
		self.tooltip_l = ttk.Label(self)
		self.tooltip_l.grid(row = 6, column = 0, padx = 10, pady = 10)
		
	def write_uname(self,name,token):
		self.tooltip_l.config(text=name+" "+token,foreground="red")
		
# Driver Code
app = NewsletterApp()
app.mainloop()
