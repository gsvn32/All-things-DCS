import json
from xmlrpc.server import SimpleXMLRPCServer
import sys

# Storage of data
data_table = {}


def load_data(group):
    global data_table
    with open('./data/data-' + group + '.json', 'r') as f:
        json_data = f.read()
        data_table = json.loads(json_data)
    return data_table


def getbyname(name):

    try:
        record = data_table[name]
        return {
            'error': False,
            'result': record
        }
    except KeyError:
        # Handle the case where the name is not found
        print(f"No record found for name '{name}'")
        return {
            'error': False,
            'result': ['No data found with given name']
        }


def getbylocation(location):

    # Create an empty list to store the matching records
    matching_records = []

    # Iterate over the dictionary and collect the records with the matching location
    for record in data_table.values():
        if record['location'] == location:
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
        if record['location'] == location and record['year'] == year:
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

    server = SimpleXMLRPCServer(("localhost", port))
    print(f"Listening on port {port}...")

    server.register_function(getbylocation, 'getbylocation')
    server.register_function(getbyname, 'getbyname')
    server.register_function(getbyyear, 'getbyyear')
    server.serve_forever()


if __name__ == '__main__':
    main()
