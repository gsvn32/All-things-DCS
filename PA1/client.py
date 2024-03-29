import xmlrpc.client
import sys

master_port = int(sys.argv[1])
x=int(sys.argv[2])
proxy= xmlrpc.client.ServerProxy(f"http://localhost:{master_port}/")
if x==1:
        name = sys.argv[3]
        print(f'Client => Asking for person with {name}')
        result = proxy.handle_request('getbyname',name)
        print(result)
        print()
elif x==2:
        location = input("Enter Location: ")
        print(f'Client => Asking for person lived at {location}')
        result = proxy.handle_request('getbylocation',location)   
        print(result)
        print()
elif x==3:
        location = input("Enter Location: ")
        year = int(input("Enter year: "))
        print(f'Client => Asking for person lived in {location} in {year}')
        result = proxy.handle_request('getbyyear',[location, year])
        print(result)
        print()
else:
    print("inputs must be 1,2,3 or 4 to exit")
    x=int(input("[1. getbyname,2. getbylocation,3. getbyyear,4. exit]"+" : ") )
