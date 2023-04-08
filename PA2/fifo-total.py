#!/bin/python3

### TODO: 
# Author name: 


from simulator import *

# Multicast events for the driver
multicast_events = [
    #(time, message_id, sending host_id, message/payload)
    (10, 'M1', 1, 'Januray'),
    (20, 'M2', 1, 'February'),
    (30, 'M3', 1, 'March'),
    (10, 'M4', 2, 'One'),
    (20, 'M5', 2, 'Two'),
    (30, 'M6', 2, 'Three')
]


class Host(Node):
    def __init__(self, sim, host_id):
        Node.__init__(self, sim, host_id)
        self.host_id = host_id
        self.gmembers = [] 
    
    def initialize(self):
        # TODO: Initilize any data structure or state
        pass

    def multicast(self, time, message_id, message_type, payload):
        # Multicast message to the group
        print(f'Time {time}:: {self} SENDING mulitcast message [{message_id}]')

        # Create message and send to all members of the group including itself
        for to in self.gmembers:
            mcast = Message(message_id, self, to, message_type, payload)
            self.send_message(to, mcast)

    def receive_message(self, frm, message, time):
        # This function is called when a message is received by this host (self)
        # frm --- from which host/node the message is came (source of the message)
        # message -- message that is received
        # time -- the time when the message is received (the current time)

        # TODO: Currently this simply delivers the received messages right away, does not implement any ordering
        # TODO: You need to implement your ordering code here
        print(f'Time {time}:: {self} RECEIVED message [{message.message_id}] from {frm}')
        
        # Code your staff

        # Deliver message when it is time
        self.deliver_message(time, message)
    
    def deliver_message(self, time, message):
        print(f'Time {time:4}:: {self} DELIVERED message [{message.message_id}] -- {message.payload}')
        

# Driver: you DO NOT need to change anything here
class Driver:
    def __init__(self, sim):
        self.hosts = []
        self.sim = sim

    def run(self, nhosts=3):
        for i in range(nhosts):
            host = Host(self.sim, i)
            self.hosts.append(host)
        
        for host in self.hosts:
            host.gmembers = self.hosts
            host.initialize()

        for event in multicast_events:
            time = event[0]
            message_id = event[1]
            message_type = 'DRIVER_MCAST'
            host_id = event[2]
            payload = event[3]
            self.sim.add_event(Event(time, self.hosts[host_id].multicast, time, message_id, message_type, payload))

def main():
    # Create simulation instance
    sim = Simulator(debug=False, random_seed=1233)

    # Start the driver and run for nhosts (should be >= 3)
    driver = Driver(sim)
    driver.run(nhosts=5)

    # Start the simulation
    sim.run()                 

if __name__ == "__main__":
    main()    
