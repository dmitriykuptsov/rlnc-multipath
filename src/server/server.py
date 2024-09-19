#!/usr/bin/python3

# Copyright (C) 2022 strangebit

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
__copyright__ = "Copyright 2024, strangebit"
__license__ = "GPL"
__version__ = "0.0.1a"
__maintainer__ = "Dmitriy Kuptsov"
__email__ = "dmitriy.kuptsov@gmail.com"
__status__ = "development"

# Add current directory to Python path
import sys
import os
sys.path.append(os.getcwd())
import os
import socket
from config import config
import common
from common import utils
from packets import packets
import logging
from time import sleep, time
import threading
from binascii import hexlify

# Configure logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("rlnc-server.log"),
        logging.StreamHandler(sys.stdout)
    ]
);

from threading import Lock

general_lock = Lock()

recieved_data = {}
recieved_timestamp = {}
app_timestamp = {}

def open_socket(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
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
path1_data_socket = open_socket(path_1_data_destination_ip, path_1_data_destination_port)
path1_data_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, 2000*1300)

path_2_data_destination_ip = config["data-plane"]["path2"]["ip"]
path_2_data_destination_port = config["data-plane"]["path2"]["port"]
path2_data_socket = open_socket(path_2_data_destination_ip, path_2_data_destination_port)
path2_data_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF, 2000*1300)

def process_loop():
    packet_size = config["experiment"]["packet_size"]
    num_packets = config["experiment"]["number_of_packets"]
    gen_size = config["encoder"]["generation_size"]
    current_gen_index = 1
    packets_prcessed = 0
    timeout = 1
    start = time()
    logging.info("Starting process loop....")
    while current_gen_index <= num_packets / gen_size:
        if (time() - start) > timeout:
            start = time()
            current_gen_index += 1;
            logging.info("SKIPPING THE GENERATION....")
            continue;
        if recieved_data.get(current_gen_index, None):
            if len(recieved_data.get(current_gen_index)) >= gen_size:
                logging.info("DOING %d GENERATION INDEX" % (current_gen_index))
                matrix = []
                packets_ = []
                counter = 0
                for packet in recieved_data[current_gen_index]:
                    if counter == gen_size:
                        break;
                    counter += 1
                    matrix.append(bytearray(packet.get_coefs()))
                    packets_.append(bytearray(packet.get_symbols()))
                start = time()
                matrix = utils.get_GF_matrix(matrix)
                try:
                    decoded_packets = utils.decode_packets(matrix, packets_, gen_size, packet_size)
                except:
                    logging.critical("FAILED TO DECODE THE PACKETS")
                    pass
                end = time()
                print("DECODED IN %f seconds" % (end-start))
                #for packet in decoded_packets:
                #    print(hexlify(bytearray(packet)))
                packets_prcessed += gen_size
                current_gen_index += 1
                start = time()
        if packets_prcessed >= num_packets:
            break;
        pass

def process_regular_loop():
    num_packets = config["experiment"]["number_of_packets"]
    current_packet_sequence = 1
    packets_prcessed = 0
    timeout = 0.1
    start = time()
    logging.info("Starting process loop....")
    while current_packet_sequence <= num_packets:
        if (time() - start) > timeout:
            start = time()
            current_packet_sequence += 1;
            logging.info("SKIPPING THE PACKET....")
            continue;
        if recieved_data.get(current_packet_sequence, None):
            logging.info("DOING PACKET %d" % (current_packet_sequence, ))
            current_packet_sequence += 1
            start = time()

        pass

def path1_recv_data_loop(sock):
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.DATA_PACKET_TYPE:
            packet = packets.DataPacket(data)
            if not recieved_data.get(packet.get_generation(), None):
                recieved_data[packet.get_generation()] = []
            recieved_data[packet.get_generation()].append(packet)
        elif packet.get_type() == packets.GENERIC_DATA_PACKET_TYPE:
            packet = packets.RegularDataPacket(data)
            recieved_data[packet.get_sequence()] = packet

def path2_recv_data_loop(sock):
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.DATA_PACKET_TYPE:
            packet = packets.DataPacket(data)
            if not recieved_data.get(packet.get_generation(), None):
                recieved_data[packet.get_generation()] = []                
            recieved_data[packet.get_generation()].append(packet)
        elif packet.get_type() == packets.GENERIC_DATA_PACKET_TYPE:
            packet = packets.RegularDataPacket(data)
            recieved_data[packet.get_sequence()] = packet

def path1_recv_loop(sock):
    current_index = -1
    probes = 0
    start_probe = -1
    end_probe = -1
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.TPUT_PROBE_TYPE:
            packet = packets.TputProbe(data);
            index = packet.get_index()
            if current_index < 0:
                start_probe = time();
                current_index = index;
            if current_index != index:
                start_probe = time();
                current_index = index;
                probes = 0
            probes += 1
            if probes == config["general"]["bw_probe_train_size"]:
                # send ack
                end_probe = time()
                packet = packets.TputProbeACK();
                packet.set_pps(probes)
                packet.set_time_delta(int((end_probe - start_probe)*1000*1000))
                packet.set_type(packets.TPUT_ACK_TYPE)
                packet.set_length(len(packet.get_buffer()))
                sock.sendto(packet.get_buffer(), (config["network"]["path1"]["destination"], config["network"]["path1"]["destination_port"]))
        else:
            logging.debug("Unknown packet type")

def path2_recv_loop(sock):
    current_index = -1
    probes = 0
    start_probe = -1
    end_probe = -1
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.TPUT_PROBE_TYPE:
            packet = packets.TputProbe(data);
            index = packet.get_index()
            if current_index < 0:
                start_probe = time();
                current_index = index;
            if current_index != index:
                start_probe = time();
                current_index = index;
                probes = 0
            probes += 1
            if probes == config["general"]["bw_probe_train_size"]:
                # send ack
                end_probe = time()
                packet = packets.TputProbeACK();
                packet.set_pps(probes)
                packet.set_time_delta(int((end_probe - start_probe)*1000*1000))
                packet.set_type(packets.TPUT_ACK_TYPE)
                packet.set_length(len(packet.get_buffer()))
                sock.sendto(packet.get_buffer(), (config["network"]["path2"]["destination"], config["network"]["path2"]["destination_port"]))
        else:
            logging.debug("Unknown packet type")

path1_recv_th = threading.Thread(target = path1_recv_loop, args = (path1_socket, ), daemon = True)
path2_recv_th = threading.Thread(target = path2_recv_loop, args = (path2_socket, ), daemon = True)
path1_recv_data_th = threading.Thread(target = path1_recv_data_loop, args = (path1_data_socket, ), daemon=True)
path2_recv_data_th = threading.Thread(target = path2_recv_data_loop, args = (path2_data_socket, ), daemon=True)


#decode_loop_th = threading.Thread(target = process_loop, args = ( ), daemon = True)

path1_recv_data_th.start()
path2_recv_data_th.start()
path1_recv_th.start()
path2_recv_th.start()
#decode_loop_th.start()

# Main loop
#while True:

sleep(20)
if config["experiment"]["type"] == "RNLC":
    process_loop()
else:
    process_regular_loop()
