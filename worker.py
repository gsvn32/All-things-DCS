import json
import queue
import threading
from xmlrpc.server import SimpleXMLRPCServer
import sys

# Data table for loading the data.
data_table = {}

# Request queue for queuing the RPC requests coming from the Master.
request_queue = queue.Queue(maxsize=20)


# Method for loading the data into the table based on the group ('am' or 'nz')
def load_data(group):
    global data_table
    with open('./data/data-' + group + '.json', 'r') as f:
        json_data = f.read()
        data_table = json.loads(json_data)
    return data_table


# Request is processed here by mapping to the respective method.
def process_request(request):
    # Extract the method and args from the request dictionary
    method = request['method']
    args = request['args']

    # Define if else conditions that maps the method to the corresponding function
    if method == 'getbyname':
        return getbyname(args)
    elif method == 'getbylocation':
        return getbylocation(args)
    elif method == 'getbyyear':
        return getbyyear(args[0], args[1])


# Thread function for processing requests in the queue
def request_worker():
    while True:
        # Get the next request from the queue
        request = request_queue.get()
        print(request)

        # Process the request and get the result
        result = process_request(request)
        print(result)

        # Put the result in the response queue for the request
        request['response'].put(result)

        # Mark the request as done
        request_queue.task_done()


# Function for handling requests from the Master
def handle_request(method, args):
    # Create a new queue to hold the response
    response_queue = queue.Queue()

    # Create a new request dictionary with method, args, and response queue
    request = {
        'method': method,
        'args': args,
        'response': response_queue
    }

    # Try to put the request in the queue, raise an exception if the queue is full
    try:
        request_queue.put(request, block=False)
    except queue.Full:
        raise Exception('Request queue is full')

    # Wait for the response
    while True:
        if not response_queue.empty():
            # Get the response from the queue
            response = response_queue.get()

            # Print the response
            print(response)

            # Mark the response as done
            response_queue.task_done()

            # Return the response to the Master
            return response


# Function for checking if the request queue is full
def is_queue_full():
    return request_queue.full()


# Function for getting data by name
def getbyname(name):
    try:
        # Find the record with the given name in the data table
        record = data_table[name.lower()]

        # Return the record as a dictionary.
        return {
            'error': False,
            'result': record
        }
    except KeyError:
        # Handle the case where the name is not found
        print(f"No record found for name '{name}'")

        # Return an error message as a dictionary with error=True and result='No data found with given name'
        return {
            'error': True,
            'result': 'No data found with given name'
        }


# Function for getting data by location
def getbylocation(location):
    # Create an empty list to store the matching records
    matching_records = []

    # Iterate over the dictionary and collect the records with the matching location
    for record in data_table.values():
        if record['location'].casefold() == location.casefold():
            matching_records.append(record)

    # Return error as true when no records are found
    if not matching_records:
        return {
            'error': True,
            'result': 'No matching records'
        }

    # Return the matching records
    return {
        'error': False,
        'result': matching_records
    }


def getbyyear(location, year):
    # Create an empty list to store the matching records
    matching_records = []

    # Iterate over the dictionary and collect the records with the matching location
    for record in data_table.values():
        if record['location'].casefold() == location.casefold() and record['year'] == year:
            matching_records.append(record)

    # Return error as true when no records are found
    if not matching_records:
        return {
            'error': True,
            'result': 'No matching recoreds'
        }

    # Return the matching records
    return {
        'error': False,
        'result': matching_records
    }


def main():
    # Check if the command line arguments are correct
    if len(sys.argv) < 3:
        print('Usage: worker.py <port> <group: am or nz>')
        sys.exit(0)

    # Extract the command line arguments
    port = int(sys.argv[1])
    group = sys.argv[2]

    # # Load the data based on the provided group
    load_data(group)

    # Create a SimpleXMLRPCServer object on the specified port
    server = SimpleXMLRPCServer(("localhost", port))
    print(f"Listening on port {port}...")

    # Start the request worker thread
    t = threading.Thread(target=request_worker)
    t.daemon = True
    t.start()

    # Register two functions to be used by the XML-RPC server
    server.register_function(is_queue_full, 'is_queue_full')
    server.register_function(handle_request, 'handle_request')

    # Start serving requests
    server.serve_forever()


if __name__ == '__main__':
    # Entry point of the script
    main()
