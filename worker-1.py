#Group 10 - PA1 - 2023/02/22
#Worker 1 - (same as worker 2)
#
#

from xmlrpc.server import SimpleXMLRPCServer
import sys
import json

global workerdata

# ben curtis - simple json open/load function
def load_data(filename):
    global workerdata
    f = open(filename)
    workerdata = json.load(f)
    return workerdata



def getbyname(name):
    # TODO
    # ben curtis - added dict search and simple return
    global workerdata
    print(f'Client => Asking for person with {name}')
    if name in workerdata:
        return workerdata[name]['name']
    return {
        'error': False,
        'result': []
    }


def getbylocation(location):
    # TODO
    # ben curtis - added dict search and simple return
    global workerdata
    print(f'Client => Asking for person lived in {location}')
    for i in workerdata:
        if workerdata[i]['location'] == location:
            print(workerdata[i]['location'])
            return workerdata[i]
    else:
        return {
            'error': False,
            'result': []
        }

def getbyyear(location, year):
    # TODO
    # ben curtis - added dict search and simple return
    global workerdata
    print(f'Client => Asking for person lived in {location} in {year}')
    for i in workerdata:
        if workerdata[i]['location'] == location and workerdata[i]['year'] == year:
            return workerdata[i]
    return {
        'error': False,
        'result': []
    }


def main():
    if len(sys.argv) < 3:
        print('Usage: worker.py <port> <group: am or nz>')
        sys.exit(0)

    port = int(sys.argv[1])
    group = sys.argv[2]
    server = SimpleXMLRPCServer(("localhost", port))
    print(f"Listening on port {port} {group}...")

    # ben curtis - added dict for json data with corresponding load_data function
    workertable = {
        'am': 'C:/Users/curtisb/PycharmProjects/PA1/data-am.json',
        'nz': 'C:/Users/curtisb/PycharmProjects/PA1/data-nz.json'
    }

    load_data(workertable[group])

    # TODO register RPC functions
    # ben curtis - added register functions
    server.register_function(getbylocation, 'getbylocation')
    server.register_function(getbyname, 'getbyname')
    server.register_function(getbyyear, 'getbyyear')
    server.serve_forever()


if __name__ == '__main__':
    main()