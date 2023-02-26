#Group 10 - PA1 - 2023/02/22
#Master server
#
#
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import sys
import subprocess
import psutil
# Restrict to a particular path.
active_workers = {
    'worker-am': "23001",
    'worker-nz': "23002"
}


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
	
def is_not_alive(group):
    # Get a list of all running processes
    for process in psutil.process_iter():
        try:
            # Get the process cmdline and check if it matches the specified values
            #process.cmdline() returns ['python3', 'worker.py', '23001', 'am']            
            temp= process.cmdline()
            #print(temp)
            if len(temp) >3 and temp[0]=='python3':
                if temp[1]=='worker.py' and temp[3] == group:
                    return False
            #print("Process status:", process.status())
            #break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle any exceptions that might occur while accessing the process information
            print("Either psutil AccessDenied or psutil ZombieProcess")
    #else:
    #Process is not running
    return True


def create_process(port,group):
    # Replace "command" with the command you want to run
    command = "python3 worker.py "+str(port)+" "+group
    print("creating new process with '"+command+"'")

    # Start the process
    process = subprocess.Popen(command, shell=True)   
workers= {
    'worker-am': [23001],
    'worker-nz': [23002]
}
def is_qfull(port):
    #print(f"http://localhost:{port}/")
    temps=xmlrpc.client.ServerProxy(f"http://localhost:{port}/")
    print("is queue full at "+str(port)+" "+str(temps.is_queue_full()))
    return temps.is_queue_full()

def check_proc_status():
    if is_not_alive('am'):
        create_process(23001,"am")
        print("sending work to worker-am at 23001")
        active_workers['worker-am']="23001"
    if is_not_alive('nz'):
        create_process(23002,"nz")
        print("sending work to worker-nz at 23002")
        active_workers['worker-nz']="23002"
    
    for j in ['worker-am','worker-nz']:
        all_q_full=False
        for i in workers[j]:
            #print(workers)
            #print(i)
            if is_qfull(i):
                all_q_full=True
            else:
                all_q_full=False
                active_workers[j]=i
        if all_q_full:
            temp_port=find_free_port()
            create_process(temp_port,j.split("-")[1])
            print("sending work to "+j+" at "+str(temp_port))
            workers[j].append(str(temp_port))
            active_workers[j]=str(temp_port)
    print("active workers am: "+str(active_workers['worker-am'])+" nz: "+str(active_workers['worker-nz']))
class Query:
    def __init__(self,qtype, queries):
        self.name = queries[0]
        self.location = queries[0]
        self.year = queries[1]
        self.qtype = qtype
    def say_hello(self):
        print(f"Hello, my name is {self.name} and I am {self.location}")
        
    def process_req(self):
        #check if workers are alive
        check_proc_status()
        if self.qtype==1:            
            # bmc - print statement to see receipt of request
            print(f'Client => Asking for person with {self.name}')
            if self.name[0].lower() >='a' and self.name[0].lower()<='m':
                self.worker= 'worker-am'        
            else:
                self.worker= 'worker-nz'
            self.proxy= xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            print(f"http://localhost:{active_workers[self.worker]}/")
            self.result = self.proxy.handle_request('getbyname',self.name)
            print(f'The returned result = {self.result}')    
            return self.result["result"]
            
        elif self.qtype==2:
            # bmc - print statement to see receipt of request
            print(f'Client => Asking for person lived at {self.location}')
            #Results from worker-am
            self.worker= 'worker-am'
            self.proxy1= xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            self.result1 = self.proxy1.handle_request('getbylocation',self.location)   
            #Results from worker-nz
            self.worker= 'worker-nz'
            self.proxy2= xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/") 
            self.result2 = self.proxy2.handle_request('getbylocation',self.location)    
            #Error handling
            if self.result1["error"] and self.result2["error"]:
                return "No data found with given inputs"
            elif self.result1["error"]:
                return self.result2["result"]
            elif self.result2["error"]:
                return self.result1["result"]
            else:
                return self.result1["result"]+self.result2["result"]
        elif self.qtype==3:
            # bmc - print statement to see receipt of request
            print(f'Client => Asking for person lived in {self.location} in {self.year}')
            #Results from worker-am
            self.worker= 'worker-am'
            self.proxy1= xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            self.result1 = self.proxy1.handle_request('getbyyear',[self.location, self.year])
            
            #Results from worker-nz
            self.worker= 'worker-nz'
            self.proxy2= xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")    
            self.result2 = self.proxy2.handle_request('getbyyear',[self.location, self.year])
            
            #Error handling
            if self.result1["error"] and self.result2["error"]:
                return "No data found with given inputs"
            elif self.result1["error"]:
                return self.result2["result"]
            elif self.result2["error"]:
                return self.result1["result"]
            else:
                return self.result1["result"]+self.result2["result"]   
                

        


def getbyname(name):
    query1=Query(1,[name,2000])
    query1.say_hello()
    return query1.process_req()

    
def getbylocation(location):
    query1=Query(2,[location,2000])
    query1.say_hello()
    return query1.process_req()

def getbyyear(location, year):
    query1=Query(3,[location,year])
    query1.say_hello()
    return query1.process_req()



def main():
    port = int(sys.argv[1])
    server = SimpleXMLRPCServer(("localhost", port))
    check_proc_status()
    print(f"Listening on port {port}...")

    # TODO: register RPC functions
    # ben curtis - added register functions
    server.register_function(getbylocation, 'getbylocation')
    server.register_function(getbyname, 'getbyname')
    server.register_function(getbyyear, 'getbyyear')
    server.serve_forever()


if __name__ == '__main__':
    main()
