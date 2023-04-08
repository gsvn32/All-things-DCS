from simulator import *

class Host(Node):
    def __init__(self, sim, node_id, name=''):
        super().__init__(sim, node_id, name)
        self.host_id = node_id

    def receive_message(self, frm, message, time):
        if message.mtype == 'PING':
            print(f'{time} :: {self} received PING from {frm}')
            print(f'{time} :: {self} sending PONG to {frm}')
            pong_message = Message(message.message_id, self, message.src, 'PONG')
            self.send_message(frm, pong_message)
        elif message.mtype == 'PONG':
            print(f'{time} :: {self} received PONG from {frm}')

def main():
    # Create simulation instance
    sim = Simulator(debug=False, random_seed=234)

    host1 = Host(sim, 1)
    host2 = Host(sim, 2)

    ping_message1 = Message(1, host1, host2, 'PING')
    ping_message2 = Message(2, host2, host1, 'PING')
    
    print(f'{sim.time} :: {host1} is sending PING to {host2}')
    host1.send_message(host2, ping_message1)
    
    def send_task():
        print(f'{sim.time} :: {host2} is sending PING to {host1}')
        host2.send_message(host1, ping_message2)

    # Host2 sends PING to host1 after 100 seconds, schedule a timer
    timer = Timer(sim, 100, send_task)
    timer.start()

    # Same operation just like the above, 
    # Here passes the function and arguments that are called after a certin time (200) is elapsed
    timer = Timer(sim, 200, host2.send_message, host1, ping_message2)
    timer.start()

    # Start the simulation, should be the last line of your code
    sim.run()                 

if __name__ == "__main__":
    main()   
