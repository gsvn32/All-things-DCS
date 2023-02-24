#Group 10 - PA1 - 2023/02/22
#Master server
#
#
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import sys
with xmlrpc.client.ServerProxy(f"http://localhost:23002/") as proxy:


# Restrict to a particular path.



#workers = {
#    'worker-1': ServerProxy("http://localhost:23001/"),
#    'worker-2': ServerProxy("http://localhost:23002/")
#}


    def getbylocation(location):
        # TODO
        # bmc - print statement to see receipt of request
        print(f'Client => Asking for person lived at {location}')
        result = proxy.getbylocation(location)
        return result


    def getbyname(name):
        # TODO
        # bmc - print statement to see receipt of request
        print(f'Client => Asking for person with {name}')
        result = proxy.getbyname(name)
        print(f'The returned result = {proxy.getbyname(name)}')
        return result


    def getbyyear(location, year):
        # TODO
        # bmc - print statement to see receipt of request
        print(f'Client => Asking for person lived in {location} in {year}')
        result = proxy.getbyyear(location, year)
        return result


def main():
    port = int(sys.argv[1])
    server = SimpleXMLRPCServer(("localhost", port))
    print(f"Listening on port {port}...")

    # TODO: register RPC functions
    # ben curtis - added register functions
    server.register_function(getbylocation, 'getbylocation')
    server.register_function(getbyname, 'getbyname')
    server.register_function(getbyyear, 'getbyyear')
    server.serve_forever()


if __name__ == '__main__':
    main()
