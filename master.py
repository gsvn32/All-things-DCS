import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import sys
import subprocess
import psutil
import threading
import queue

# Restrict to a particular path.
active_workers = {
    'worker-am': "23001",
    'worker-nz': "23002"
}

workers = {
    'worker-am': [23001],
    'worker-nz': [23002]
}

req_count = 0

# Request queue for queuing the RPC requests coming from the Client.
request_queue = queue.Queue(maxsize=20)

# create a pool of worker threads
threads = {}


def find_free_port():
    # Find a free port on the machine by creating a new socket and binding it
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def is_not_alive(group):
    # Check if a process with the specified group is already running
    for process in psutil.process_iter():
        try:
            # Get the command line arguments of the process
            temp = process.cmdline()
            if len(temp) > 3 and temp[0] == 'python3':
                if temp[1] == 'worker.py' and temp[3] == group:
                    return False
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            # Handle any exceptions that might occur while accessing the process information
            #print("Either psutil AccessDenied or psutil ZombieProcess")

    # If no process with the specified group is running, return True
    return True


def create_process(port, group):
    # Create a command to start a new worker process
    command = "python3 worker.py " + str(port) + " " + group
    print("creating new process with '" + command + "'")

    # Start a new process to run the worker script
    subprocess.Popen(command, shell=True)


def is_qfull(port):
    # Check if the worker on the specified port has a full queue
    temps = xmlrpc.client.ServerProxy(f"http://localhost:{port}/")
    print("is queue full at " + str(port) + " " + str(temps.is_queue_full()))
    return temps.is_queue_full()


def check_proc_status():
    # Check if worker-am is alive, if not create a new process and update active_workers dictionary
    if is_not_alive('am'):
        create_process(23001, "am")
        print("sending work to worker-am at 23001")
        active_workers['worker-am'] = "23001"

    # Check if worker-nz is alive, if not create a new process and update active_workers dictionary
    if is_not_alive('nz'):
        create_process(23002, "nz")
        print("sending work to worker-nz at 23002")
        active_workers['worker-nz'] = "23002"

    # Check if queues of all workers are full
    for j in ['worker-am', 'worker-nz']:
        all_q_full = False
        for i in workers[j]:
            # If queue of a worker is full, mark all_q_full flag as true and break the inner loop
            if is_qfull(i):
                all_q_full = True
            else:
                # If queue of a worker is not full, mark all_q_full flag as false and update active_workers dictionary
                all_q_full = False
                active_workers[j] = i

        # If queues of all workers are full, create a new worker process and update workers and active_workers dictionary
        if all_q_full:
            temp_port = find_free_port()
            create_process(temp_port, j.split("-")[1])
            print("sending work to " + j + " at " + str(temp_port))
            workers[j].append(str(temp_port))
            active_workers[j] = str(temp_port)

    # Print the status of active workers
    print("active workers am: " + str(active_workers['worker-am']) + " nz: " + str(active_workers['worker-nz']))


class Query:
    def __init__(self, qtype, queries):
        self.name = queries[0]
        self.location = queries[0]
        self.year = queries[1]
        self.qtype = qtype

    def say_hello(self):
        # This method prints a greeting message, including the name and location of the Query object.
        print(f"Hello, my name is {self.name} and I am {self.location}")

    def process_req(self):
        # This method processes the query request.
        # It first checks if the workers are alive, and then performs the query according to the query type.

        # check if workers are alive
        check_proc_status()
        if self.qtype == 1:
            # This block of code handles the case when the query is for a person with a given name.
            # It determines which worker to use based on the first letter of the name, and sends the request to that worker.
            # It then prints some information about the request and the returned result, and returns the result.

            # bmc - print statement to see receipt of request
            print(f'Client => Asking for person with {self.name}')

            # Determine which worker to use based on the first letter of the name.
            if self.name[0].lower() >= 'a' and self.name[0].lower() <= 'm':
                self.worker = 'worker-am'
            else:
                self.worker = 'worker-nz'

            # Send the request to the worker using XML-RPC.
            self.proxy = xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            print(f"http://localhost:{active_workers[self.worker]}/")

            self.result = self.proxy.handle_request('getbyname', self.name)
            print(f'The returned result = {self.result}')
            return self.result["result"]

        elif self.qtype == 2:
            # This block of code handles the case when the query is for people who lived in a given location.
            # It sends the request to both workers and combines the results.
            # If one of the workers returns an error, it returns the result from the other worker.

            # bmc - print statement to see receipt of request
            print(f'Client => Asking for person lived at {self.location}')

            # Results from worker-am
            self.worker = 'worker-am'
            self.proxy1 = xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            self.result1 = self.proxy1.handle_request('getbylocation', self.location)

            # Results from worker-nz
            self.worker = 'worker-nz'
            self.proxy2 = xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            self.result2 = self.proxy2.handle_request('getbylocation', self.location)

            # Error handling
            if self.result1["error"] and self.result2["error"]:
                return "No data found with given inputs"
            elif self.result1["error"]:
                return self.result2["result"]
            elif self.result2["error"]:
                return self.result1["result"]
            else:
                return self.result1["result"] + self.result2["result"]

        elif self.qtype == 3:
            # This block of code handles the case when the query is for people who lived in a given location and year.
            # It sends the request to both workers and combines the results.
            # If one of the workers returns an error, it returns the result from the other worker.

            # bmc - print statement to see receipt of request
            print(f'Client => Asking for person lived in {self.location} in {self.year}')

            # Results from worker-am
            self.worker = 'worker-am'
            self.proxy1 = xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            self.result1 = self.proxy1.handle_request('getbyyear', [self.location, self.year])

            # Results from worker-nz
            self.worker = 'worker-nz'
            self.proxy2 = xmlrpc.client.ServerProxy(f"http://localhost:{active_workers[self.worker]}/")
            self.result2 = self.proxy2.handle_request('getbyyear', [self.location, self.year])

            # Error handling
            if self.result1["error"] and self.result2["error"]:
                return "No data found with given inputs"
            elif self.result1["error"]:
                return self.result2["result"]
            elif self.result2["error"]:
                return self.result1["result"]
            else:
                return self.result1["result"] + self.result2["result"]


# Request is processed here by mapping to the respective method.
def process_request(request):
    # Process the request here
    method = request['method']
    args = request['args']
    print(args)
    if method == 'getbyname':
        return getbyname(args)
    elif method == 'getbylocation':
        return getbylocation(args)
    elif method == 'getbyyear':
        return getbyyear(args[0], args[1])


def request_worker():
    # This function processes requests from the request queue and sends the result back to the client
    while True:
        # Get the next request from the queue
        request = request_queue.get()
        print(request)
        # Process the request
        result = process_request(request)
        print(result)
        # Put the result in the response queue
        request['response'].put(result)
        # Mark the request as done
        request_queue.task_done()


def handle_request_server(method, args):
    # This function creates a new request dictionary and puts it in the request queue
    # It also creates a new response queue to hold the response from the request worker
    # It waits for the response from the request worker and returns the response to the client
    response_queue = queue.Queue()

    # Create a new request dictionary
    request = {
        'method': method,
        'args': args,
        'response': response_queue
    }
    # Put the request in the queue
    try:
        request_queue.put(request, block=False)
    except queue.Full:
        raise Exception('Request queue is full')

    print("Processing request from client")

    print(response_queue.empty())

    # Wait for the response
    while True:
        if not response_queue.empty():
            # Get the response from the response queue
            response = response_queue.get()
            print(response)
            # Mark the response as done
            response_queue.task_done()
            # Return the response to the client
            return response


def getbyname(name):
    # This function creates a new Query object with 'name' and calls the process_req() method to handle the request
    query1 = Query(1, [name, 2000])
    query1.say_hello()
    return query1.process_req()


def getbylocation(location):
    # This function creates a new Query object with 'location' and calls the process_req() method to handle the request
    query1 = Query(2, [location, 2000])
    query1.say_hello()
    return query1.process_req()


def getbyyear(location, year):
    # This function creates a new Query object with 'location' and 'year' and calls the process_req() method to handle the request
    query1 = Query(3, [location, year])
    query1.say_hello()
    return query1.process_req()


def main():
    # This function starts the request worker thread, creates a new SimpleXMLRPCServer object and registers the handle_request_server function
    port = int(sys.argv[1])

    # Create a SimpleXMLRPCServer object on the specified port
    server = SimpleXMLRPCServer(("localhost", port))
    check_proc_status()
    print(f"Listening on port {port}...")

    # Start the server thread
    t = threading.Thread(target=request_worker)
    t.daemon = True
    t.start()

    # Register function to be used by the XML-RPC server
    server.register_function(handle_request_server, 'handle_request')
    server.serve_forever()


if __name__ == '__main__':
    # Entry point of the script
    main()
