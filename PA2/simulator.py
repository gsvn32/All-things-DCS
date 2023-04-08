#!/bin/python3
# Event simulator for COMP-SCI 5546/446 (Distributed Computing Systems)
# Developed by Yusuf Sarwar Uddin, UMKC

import heapq
import random

class Message(object):
    def __init__(self, message_id, src, dest, mtype, payload=None):
        self.message_id = message_id
        self.src = src
        self.dest = dest
        self.mtype = mtype
        self.payload = payload
     
    def __str__(self):
        return '' + str(self.message_id) +  'Type ' + self.mtype + '::' + str(self.src) + '=>' + str(self.dest) + '--[' + self.payload if self.payload else '' + ']'


class Event:
    def __init__(self, time, call, *args, **argv):
        self.event_time = time
        self.event_call = call
        self.event_args = args
        self.event_argv = argv
    
    def __lt__(self, other):
        return self.event_time < other.event_time

    def call(self):
        func = self.event_call
        if self.event_args and self.event_argv:
            func(*self.event_args, **self.event_argv)
        elif self.event_args:
            func(*self.event_args)
        elif self.event_argv:
            func(**self.event_argv)
        else:
            func()

class Timer:
    def __init__(self, sim, interval, func, *args, **argv):
        self.sim = sim
        self.interval = interval
        self.func = func
        self.args = args
        self.argv = argv
    
    def start(self):
        event = Event(self.sim.time + self.interval, self.func, *self.args, **self.argv)
        self.sim.add_event(event)


class Node:
    def __init__(self, sim, node_id, name = ''):
        self.sim = sim
        self.node_id = node_id
        self.name = name
        self.alive = True
        
    def get_id(self):
        return self.node_id
        
    def send_message(self, to, message):
        if not self.alive: return
        
        if self.sim.debug: 
            print (f'DEBUG {self} sending message [{message.message_id}] to {to}') 
        
        self.sim.send_message(self, to, message)
    
    def receive(self, time, frm, message):
        if not frm.alive: return
        
        if self.sim.debug:
            print (f'DEBUG Time {time}:: {self} received message {message} from {frm}')
        
        self.receive_message(frm, message, time)
        
    def receive_message(self, frm, message, time):
        raise NotImplementedError('No receive_message function is passed')
        
    def is_alive(self):
        return self.is_alive
        
    def failed(self):
        self.alive = False
    
    def recovered(self):
        self.alive = True
              
    def __hash__(self) -> int:
        return self.node_id

    def __str__(self):
        if self.name != '':
            return 'Node-' + self.name
        else:
            return 'Node-' + str(self.node_id)     
           

class Simulator:
    def __init__(self, debug=True, random_seed=1234):
        self.debug = debug 
        self.events = []
        self.time = 0
        self.max_latency = 100
        # Random number generator
        self.rng = random.Random(random_seed)
        
    def add_event(self, event):
        heapq.heappush(self.events, event)

    def send_message(self, src, dest, message):
        delay = self.rng.randint(1, self.max_latency)
        event_time = self.time + delay
        event = Event(event_time, dest.receive, event_time, src, message)
        self.add_event(event)
                
    def run(self):
        while len(self.events) > 0:
            event = heapq.heappop(self.events)
            self.time = event.event_time
            event.call()
        print(f'Simulation ended at time {self.time}')
