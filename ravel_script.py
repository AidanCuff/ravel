from ravel import *
from ravel.utils import *
import socket

class LoadBalancer(App):
    def __init__(self):
        super().__init__()
        self.servers = [
            '10.0.0.2', # server1
            '10.0.0.3', # server2
            '10.0.0.4', # server3
        ]
        self.current_server = 0

    def start(self):
        lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lb_socket.bind(('10.0.0.1', 9000))
        lb_socket.listen()
        while True:
            conn, addr = lb_socket.accept()
            server = self.servers[self.current_server]
            self.current_server = (self.current_server + 1) % len(self.servers)
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server, 8000))
            data = conn.recv(1024)
            server_socket.sendall(data)
            response = server_socket.recv(1024)
            conn.sendall(response)
            conn.close()
            server_socket.close()

class LoadBalancerTopology(Topo):
    def build(self):
        lb = self.addHost('lb')
        server1 = self.addHost('server1')
        server2 = self.addHost('server2')
        server3 = self.addHost('server3')
        switch1 = self.addSwitch('switch1')
        switch2 = self.addSwitch('switch2')
        self.addLink(lb, switch1)
        self.addLink(server1, switch2)
        self.addLink(server2, switch2)
        self.addLink(server3, switch2)
        self.addLink(switch1, switch2)

if __name__ == '__main__':
    topo = LoadBalancerTopology()
    policy = BasicPolicy()
    policy.allow('all')
    network = ControlNetwork(controller=LocalController)
    network.start()
    network.addTopology(topo, policy)
    network.startApps([
        ('lb', LoadBalancer),
        ('server1', BasicWebServer),
        ('server2', BasicWebServer),
        ('server3', BasicWebServer),
    ])
    network.CLI()
    network.stop()
