from ravel.app import App
from ravel.util import resolve
import random

class LoadBalancer(App):
    def init(self):
        self.listen("switchEnter", self.switch_enter)
        self.listen("packetIn", self.packet_in)
        self.hosts = []
        self.switches = []

    def switch_enter(self, event):
        self.switches.append(event.switch)

    def packet_in(self, event):
        packet = event.packet
        if packet.isArp():
            self.handle_arp(event)
        elif packet.isIp():
            self.handle_ip(event)

    def handle_arp(self, event):
        packet = event.packet
        for switch in self.switches:
            for port in switch.ports.values():
                if port.mac == packet.dst_mac:
                    event.output = port
                    return

    def handle_ip(self, event):
        packet = event.packet
        if packet.dst_ip in self.hosts:
            self.send_packet_to_host(event)
        else:
            self.load_balance(event)

    def send_packet_to_host(self, event):
        packet = event.packet
        for switch in self.switches:
            for port in switch.ports.values():
                if port.mac == packet.dst_mac:
                    event.output = port
                    return

    def load_balance(self, event):
        packet = event.packet
        hosts = [h for h in self.hosts if h != packet.src_ip]
        if len(hosts) > 0:
            ip = random.choice(hosts)
            self.send_packet_to_ip(ip, event)
        else:
            event.drop()

    def send_packet_to_ip(self, ip, event):
        packet = event.packet
        for switch in self.switches:
            for port in switch.ports.values():
                if port.mac == resolve(ip):
                    event.output = port
                    return

    def add_host(self, host):
        self.hosts.append(host)
