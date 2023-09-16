import os
import pickle
from abc import ABC
from enum import Enum, unique
from typing import Type

from scapy.all import (Packet,load_layer,
                       sniff, wrpcap)
from scapy.layers.dns import DNS
from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse
from scapy.layers.inet import IP, TCP, UDP, Ether
from scapy.layers.inet6 import IPv6

from heifip.exceptions import FIPWrongParameterException
from heifip.layers.dns import DNSPacket
from heifip.layers.http import (HTTPPacket, HTTPRequestPacket,
                                HTTPResponsePacket)
from heifip.layers.ip import IPPacket
from heifip.layers.packet import EtherPacket, FIPPacket, UnknownPacket
from heifip.layers.transport import TransportPacket

__author__ = "Stefan Machmeier"
__copyright__ = "Copyright 2023, heiFIP"
__credits__ = ["Manuel Trageser"]
__license__ = "EUPL"
__version__ = "1.1.1"
__maintainer__ = "Stefan Machmeier"
__email__ = "stefan.machmeier@uni-heidelberg.de"
__status__ = "Production"

SUPPORTED_HEADERS = [IP, IPv6, DNS, HTTPRequest, HTTPResponse, TCP, UDP]


@unique
class PacketProcessorType(Enum):
    NONE = 1
    HEADER = 2


class PacketProcessor:
    def __init__(
        self,
        file_extension="pcap",
    ) -> None:
        self.hash_dict = set()
        # if os.path.isfile('hashes_pkt.pkl'):
        #     with open('hashes_pkt.pkl', 'rb') as f:
        #         self.hash_dict = pickle.load(f)
        load_layer("tls")

    def write_packet(self) -> None:
        # Write pcap
        wrpcap(f"{self.filename}_converted.pcap", self.packets, append=True)

    def read_packets_file(self, file: str, preprocessing_type: PacketProcessorType) -> [FIPPacket]:
        assert os.path.isfile(file)

        # Read PCAP file with Scapy
        packets = []
        # TODO Only read max number of packets
        pcap = sniff(offline=file, count=64)
        for pkt in pcap:
            # Start preprocessing for each packet
            processed_packet = self.__preprocessing(pkt, preprocessing_type)
            # TODO Run extract here to reduce amount of loops in code. Atm very inefficient for computation time and memory
            # In case packet returns None
            if processed_packet != None:
                if not processed_packet.hash in self.hash_dict:
                    # TODO Turn off/on hash filtering
                    # self.hash_dict.add(processed_packet.hash)
                    packets.append(processed_packet)
        return packets


    def read_packets_packet(self, packet: [Packet], preprocessing_type: PacketProcessorType) -> [FIPPacket]:
        # Read PCAP file with Scapy
        packets = []
        for pkt in packet:
            # Start preprocessing for each packet
            processed_packet = self.__preprocessing(pkt, preprocessing_type)
            # In case packet returns None
            if processed_packet != None:
                if not processed_packet.hash in self.hash_dict:
                    self.hash_dict.add(processed_packet.hash)
                    packets.append(processed_packet)
        return packets

    def __preprocessing(self, packet: Packet, preprocessing_type: PacketProcessorType) -> FIPPacket:
        fippacket = UnknownPacket(packet)
        if HTTP in fippacket.layer_map:
            if HTTPRequest in fippacket.layer_map:
                fippacket = fippacket.convert(HTTPRequestPacket, fippacket)
            elif HTTPResponse in fippacket.layer_map:
                fippacket = fippacket.convert(HTTPResponsePacket, fippacket)
            else:
                fippacket = fippacket.convert(HTTPPacket, fippacket)
        elif DNS in fippacket.layer_map:
            fippacket = fippacket.convert(DNSPacket, fippacket)
        elif TCP in fippacket.layer_map or UDP in fippacket.layer_map:
            fippacket = fippacket.convert(TransportPacket, fippacket)
        elif IP in fippacket.layer_map or IPv6 in fippacket.layer_map:
            fippacket = fippacket.convert(IPPacket, fippacket)
        elif Ether in fippacket.layer_map:
            fippacket = fippacket.convert(EtherPacket, fippacket)

        if preprocessing_type == "HEADER":
            fippacket.header_preprocessing()

        return fippacket
