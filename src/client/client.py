#!/usr/bin/python3

# Copyright (C) 2024 strangebit

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Dmitriy Kuptsov"
__copyright__ = "Copyright 2024, stangebit"
__license__ = "GPL"
__version__ = "0.0.1a"
__maintainer__ = "Dmitriy Kuptsov"
__email__ = "dmitriy.kuptsov@gmail.com"
__status__ = "development"

# Add current directory to Python path
import sys
import os
sys.path.append(os.getcwd())

import threading
import os
import socket
from config import config
from common import utils
from packets import packets
from binascii import hexlify

#from packets.packets import TputProbe, TputProbeACK, DataPacket, GenericPacket
import logging
from time import sleep, time

# Configure logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("rlnc-client.log"),
        logging.StreamHandler(sys.stdout)
    ]
);

from threading import Lock

general_lock = Lock()

stats = {
    "path1": {
        "bw": 0,
        "last": time()
    },
    "path2": {
        "bw": 0,
        "last": time()
    }
}

def open_socket(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    return sock

def open_socket_send_only():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock


buffer_size = config["general"]["buffer_size"]

path_1_source_ip = config["network"]["path1"]["source"]
path_1_destination_ip = config["network"]["path1"]["destination"]
path_1_source_port = config["network"]["path1"]["source_port"]
path_1_destination_port = config["network"]["path1"]["destination_port"]
path1_socket = open_socket(path_1_source_ip, path_1_source_port)

path_2_source_ip = config["network"]["path2"]["source"]
path_2_destination_ip = config["network"]["path2"]["destination"]
path_2_source_port = config["network"]["path2"]["source_port"]
path_2_destination_port = config["network"]["path2"]["destination_port"]
path2_socket = open_socket(path_2_source_ip, path_2_source_port)


path_1_data_destination_ip = config["data-plane"]["path1"]["ip"]
path_1_data_destination_port = config["data-plane"]["path1"]["port"]
path1_data_socket = open_socket_send_only()

path_2_data_destination_ip = config["data-plane"]["path2"]["ip"]
path_2_data_destination_port = config["data-plane"]["path2"]["port"]
path2_data_socket = open_socket_send_only()

matrix = utils.get_random_GF_matrix(config["encoder"]["generation_size"], config["encoder"]["coded_packets_size"])

def is_fastest_path_1(time_in_flight1, time_in_flight2):
    if stats["path1"]["last"] + time_in_flight1 < stats["path2"]["last"] + time_in_flight2:
        return True
    return False

def experiment_route_data_coding(number_of_packets, gen_size, packet_size, coded_packets_size):
    
    stats["path1"]["last"] = time()
    stats["path2"]["last"] = time()
    generation = 0
    for i in range(0, number_of_packets, gen_size):
        generation += 1
        packets_ = [bytearray(os.urandom(packet_size)) for p in range(0, gen_size)];
        coded_packets = utils.code_packets(matrix, packets_, gen_size, coded_packets_size, packet_size)        
        for k in range(0, coded_packets_size):
            time_in_flight1 = packet_size / stats["path1"]["bw"];
            time_in_flight2 = packet_size / stats["path2"]["bw"];
            if is_fastest_path_1(time_in_flight1, time_in_flight2):
                stats["path1"]["last"] = stats["path1"]["last"] + time_in_flight1
                codes = bytearray(matrix[k])
                packet = packets.DataPacket()
                packet.set_type(packets.DATA_PACKET_TYPE)
                packet.set_generation(generation)
                packet.set_generation_size(gen_size)
                packet.set_coefs(bytearray(codes))
                packet.set_symbols(bytearray(coded_packets[k]))
                path1_data_socket.sendto(packet.get_buffer(), (path_1_data_destination_ip, path_1_data_destination_port))
                # Send to the first path and update the stats
            else:
                # Send to the second path and update the stats
                stats["path2"]["last"] = stats["path2"]["last"] + time_in_flight2
                codes = bytearray(matrix[k])
                packet = packets.DataPacket()
                packet.set_type(packets.DATA_PACKET_TYPE)
                packet.set_generation(generation)
                packet.set_generation_size(gen_size)
                packet.set_coefs(bytearray(codes))
                logging.debug(bytearray(coded_packets[k]))
                packet.set_symbols(bytearray(coded_packets[k]))
                path2_data_socket.sendto(packet.get_buffer(), (path_2_data_destination_ip, path_2_data_destination_port))


def experiment_route_data_nocoding(number_of_packets, packet_size):
    
    stats["path1"]["last"] = time()
    stats["path2"]["last"] = time()
    generation = 0
    for i in range(0, number_of_packets):
        generation += 1
        packet_ = bytearray(os.urandom(packet_size));
        time_in_flight1 = packet_size / stats["path1"]["bw"];
        time_in_flight2 = packet_size / stats["path2"]["bw"];
        if is_fastest_path_1(time_in_flight1, time_in_flight2):
            stats["path1"]["last"] = stats["path1"]["last"] + time_in_flight1
            packet = packets.RegularDataPacket()
            packet.set_type(packets.DATA_PACKET_TYPE)
            packet.set_sequence(i)
            packet.set_payload(packet_)
            path1_data_socket.sendto(packet.get_buffer(), (path_1_data_destination_ip, path_1_data_destination_port))
            # Send to the first path and update the stats
        else:
            stats["path2"]["last"] = stats["path2"]["last"] + time_in_flight1
            packet = packets.RegularDataPacket()
            packet.set_type(packets.DATA_PACKET_TYPE)
            packet.set_sequence(i)
            packet.set_payload(packet_)
            path1_data_socket.sendto(packet.get_buffer(), (path_2_data_destination_ip, path_2_data_destination_port))


def path1_recv_loop(sock):
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.TPUT_ACK_TYPE:
            packet = packets.TputProbeACK(data);
            pps = packet.get_pps()
            delta = packet.get_time_delta()
            bw = (pps * config["general"]["bw_probe_size_bytes"] * 8) / delta * 1000 * 1000
            stats["path1"]["bw"] = bw
        else:
            logging.debug("Unknown packet type")

def path2_recv_loop(sock):
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.TPUT_ACK_TYPE:
            packet = packets.TputProbeACK(data);
            pps = packet.get_pps()
            delta = packet.get_time_delta()
            bw = (pps * config["general"]["bw_probe_size_bytes"] * 8) / delta * 1000 * 1000
            stats["path2"]["bw"] = bw
        else:
            logging.debug("Unknown packet type")

def path1_probe_send_loop(sock):
    index = 1
    while True:
        for i in range(0, config["general"]["bw_probe_train_size"]):
            packet = packets.TputProbe()
            packet.set_type(packets.TPUT_PROBE_TYPE)
            packet.set_index(index)
            payload = bytearray(os.urandom(config["general"]["bw_probe_size_bytes"]))
            packet.set_payload(payload)
            packet.set_length(len(packet.get_buffer()))
            sock.sendto(packet.get_buffer(), (config["network"]["path1"]["destination"], config["network"]["path1"]["destination_port"]))
        index += 1
        sleep(config["general"]["bw_probe_interval_s"])

def path2_probe_send_loop(sock):
    index = 1
    while True:
        for i in range(0, config["general"]["bw_probe_train_size"]):
            packet = packets.TputProbe()
            packet.set_type(packets.TPUT_PROBE_TYPE)
            packet.set_index(index)
            payload = bytearray(os.urandom(config["general"]["bw_probe_size_bytes"]))
            packet.set_payload(payload)
            packet.set_length(len(packet.get_buffer()))
            sock.sendto(packet.get_buffer(), (config["network"]["path2"]["destination"], config["network"]["path2"]["destination_port"]))
        index += 1
        sleep(config["general"]["bw_probe_interval_s"])

path1_recv_th = threading.Thread(target = path1_recv_loop, args = (path1_socket, ), daemon = True)
path2_recv_th = threading.Thread(target = path2_recv_loop, args = (path2_socket, ), daemon = True)

path1_send_th = threading.Thread(target = path1_probe_send_loop, args = (path1_socket, ), daemon = True)
path2_send_th = threading.Thread(target = path2_probe_send_loop, args = (path2_socket, ), daemon = True)

path1_recv_th.start()
path2_recv_th.start()

path1_send_th.start()
path2_send_th.start()

# Main loop
#while True:
sleep(20)
experiment_route_data_coding(config["experiment"]["number_of_packets"], \
                                 config["encoder"]["generation_size"], \
                                    config["experiment"]["packet_size"], \
                                    config["encoder"]["coded_packets_size"])

#sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))