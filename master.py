#Group 10 - PA1 - 2023/02/22
#Master server
#
#
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import sys
# Restrict to a particular path.
workers = {
    'worker-am': "23001",
    'worker-nz': "23002"
}


def getbylocation(location):
    # TODO
    # bmc - print statement to see receipt of request
    print(f'Client => Asking for person lived at {location}')
    #Results from worker-am
    worker= 'worker-am'
    proxy1= xmlrpc.client.ServerProxy(f"http://localhost:{workers[worker]}/")
    result1 = proxy1.getbylocation(location)
    
    #Results from worker-nz
    worker= 'worker-nz'
    proxy2= xmlrpc.client.ServerProxy(f"http://localhost:{workers[worker]}/")    
    result2 = proxy2.getbylocation(location)
    if result1["error"] and result2["error"]:
        return "No data found with given inputs"
    elif result1["error"]:
        return result2["result"]
    elif result2["error"]:
        return result1["result"]
    else:
        return result1["result"]+result2["result"]
        


def getbyname(name):
    # TODO
    # bmc - print statement to see receipt of request
    print(f'Client => Asking for person with {name}')
    print(name[0].lower())
    if name[0].lower() >='a' and name[0].lower()<='m':
         worker= 'worker-am'        
    else:
        worker= 'worker-nz'
    proxy= xmlrpc.client.ServerProxy(f"http://localhost:{workers[worker]}/")
    result = proxy.getbyname(name)
    print(f'The returned result = {proxy.getbyname(name)}')
    return result


def getbyyear(location, year):
    # TODO
    # bmc - print statement to see receipt of request
    print(f'Client => Asking for person lived in {location} in {year}')
    #Results from worker-am
    worker= 'worker-am'
    proxy1= xmlrpc.client.ServerProxy(f"http://localhost:{workers[worker]}/")
    result1 = proxy1.getbyyear(location, year)
    
    #Results from worker-nz
    worker= 'worker-nz'
    proxy2= xmlrpc.client.ServerProxy(f"http://localhost:{workers[worker]}/")    
    result2 = proxy2.getbyyear(location, year)
    
    if result1["error"] and result2["error"]:
        return "No data found with given inputs"
    elif result1["error"]:
        return result2["result"]
    elif result2["error"]:
        return result1["result"]
    else:
        return result1["result"]+result2["result"]
    


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
