import json
import queue
import threading
from xmlrpc.server import SimpleXMLRPCServer
import sys

# Storage of data
data_table = {}

# Request queue
request_queue = queue.Queue(maxsize=20)

def load_data(group):
    global data_table
    with open('./data/data-' + group + '.json', 'r') as f:
        json_data = f.read()
        data_table = json.loads(json_data)
    return data_table

def process_request(request):
    # Process the request here
    method = request['method']
    args = request['args']
    if method == 'getbyname':
        return getbyname(*args)
    elif method == 'getbylocation':
        return getbylocation(*args)
    elif method == 'getbyyear':
        return getbyyear(*args)

def request_worker():
    while True:
        request = request_queue.get()
        result = process_request(request)
        request['response'].put(result)
        request_queue.task_done()

def handle_request(method, args):
    # Create a new queue to hold the response
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

    # Wait for the response
    response = response_queue.get()
    response_queue.task_done()

    if response['error']:
        return 'Queue is full'
    else:
        return response['result']

def is_queue_full():
    return request_queue.full()

def getbyname(name):
    try:
        record = data_table[name.lower()]
        return {
            'error': False,
            'result': record
        }
    except KeyError:
        # Handle the case where the name is not found
        print(f"No record found for name '{name}'")
        return {
            'error': True,
            'result': 'No data found with given name'
        }


def getbylocation(location):

    # Create an empty list to store the matching records
    matching_records = []

    # Iterate over the dictionary and collect the records with the matching location
    for record in data_table.values():
        if record['location'].casefold() == location.casefold():
            matching_records.append(record)

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

    # Return the matching records
    return {
        'error': False,
        'result': matching_records
    }


def main():
    if len(sys.argv) < 3:
        print('Usage: worker.py <port> <group: am or nz>')
        sys.exit(0)

    port = int(sys.argv[1])
    group = sys.argv[2]

    # Load the data
    load_data(group)

    # Start the request worker thread
    t = threading.Thread(target=request_worker)
    t.daemon = True
    t.start()

    server = SimpleXMLRPCServer(("localhost", port))
    print(f"Listening on port {port}...")

    server.register_function(getbylocation, 'getbylocation')
    server.register_function(getbyname, 'getbyname')
    server.register_function(getbyyear, 'getbyyear')
    server.register_function(is_queue_full, 'is_queue_full')
    server.serve_forever()


if __name__ == '__main__':
    main()
