import xmlrpc.client
import sys

master_port = int(sys.argv[1])
x=int(input("[1. getbyname,2. getbylocation,3. getbyyear,4. exit]"+" : ") )
proxy= xmlrpc.client.ServerProxy(f"http://localhost:{master_port}/")
while(x!=4):
    if x==1:
        name = input("Enter Name: ")
        print(f'Client => Asking for person with {name}')
        result = proxy.getbyname(name)
        print(result)
        print()
    elif x==2:
        location = input("Enter Location: ")
        print(f'Client => Asking for person lived at {location}')
        result = proxy.getbylocation(location)
        print(result)
        print()
    elif x==3:
        location = input("Enter Location: ")
        year = int(input("Enter year: "))
        print(f'Client => Asking for person lived in {location} in {year}')
        result = proxy.getbyyear(location, year)
        print(result)
        print()
    else:
        print("inputs must be 1,2,3 or 4 to exit")
    x=int(input("[1. getbyname,2. getbylocation,3. getbyyear,4. exit]"+" : ") )
