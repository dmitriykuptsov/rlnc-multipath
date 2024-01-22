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
    level=logging.DEBUG,
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

path_2_data_destination_ip = config["data-plane"]["path2"]["ip"]
path_2_data_destination_port = config["data-plane"]["path2"]["port"]
path2_data_socket = open_socket(path_2_data_destination_ip, path_2_data_destination_port)

def process_loop():
    packet_size = config["experiment"]["packet_size"]
    num_packets = config["experiment"]["number_of_packets"]
    gen_size = config["encoder"]["generation_size"]
    current_gen_index = 1
    packets_prcessed = 0
    logging.debug("Starting process loop....")
    while True:
        if recieved_data.get(current_gen_index, None):
            if len(recieved_data.get(current_gen_index)) >= gen_size:
                logging.debug("DOING %d GENERATION INDEX" % (current_gen_index))
                current_gen_index += 1
                matrix = []
                packets_ = []
                counter = 0
                for packet in recieved_data[current_gen_index]:
                    if counter == gen_size:
                        break;
                    counter += 1
                    matrix.append(packet.get_coefs())
                    packets_.append(packet.get_symbols())
                matrix = utils.get_GF_matrix(matrix)
                decoded_packets = utils.decode_packets(matrix, packets_, gen_size, len(packets_), packet_size)
                for packet in decoded_packets:
                    logging.debug(hexlify(packet))
                packets_prcessed += gen_size
        if packets_prcessed >= num_packets:
            break;
        pass

def path1_recv_data_loop(sock):
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.DATA_PACKET_TYPE:
            #logging.debug("GOT DATA PACKET ON PATH 1")
            packet = packets.DataPacket(data)
            
            #logging.debug(packet.get_coefs())
            #logging.debug(packet.get_symbols())
            #logging.debug("PATH 1 GENERATION %d TIMESTAMP %f" % (packet.get_generation(), time()))

            #general_lock.acquire()
            if not recieved_data.get(packet.get_generation(), None):
                recieved_data[packet.get_generation()] = []
            recieved_data[packet.get_generation()].append(packet)
            #general_lock.release()

def path2_recv_data_loop(sock):
    while True:
        data, addr = sock.recvfrom(buffer_size)
        packet = packets.GenericPacket(data)
        if packet.get_type() == packets.DATA_PACKET_TYPE:
            packet = packets.DataPacket(data)
            #logging.debug(packet.get_coefs())
            #logging.debug(packet.get_symbols())
            #logging.debug("PATH 2 GENERATION %d TIMESTAMP %f" % (packet.get_generation(), time()))
            #general_lock.acquire()
            if not recieved_data.get(packet.get_generation(), None):
                recieved_data[packet.get_generation()] = []
                
            recieved_data[packet.get_generation()].append(packet)            
            #general_lock.release()

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
            #logging.debug("GOT BW ESTIMATE FOR PATH 1 %d %d" % (int(time() * 1000), probes))
            if probes == config["general"]["bw_probe_train_size"]:
                
                # send ack
                end_probe = time()
                packet = packets.TputProbeACK();
                packet.set_pps(probes)
                
                packet.set_time_delta(int((end_probe - start_probe)*1000*1000))
                #logging.debug(packet.get_time_delta())
                #logging.debug("==============")
                packet.set_type(packets.TPUT_ACK_TYPE)
                packet.set_length(len(packet.get_buffer()))
                #logging.debug("Send probe ACK %d" % (int((end_probe - start_probe)*1000*1000)))
                #logging.debug("Buffer size: 13000 bytes PATH 1")
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
            #logging.debug("GOT BW ESTIMATE FOR PATH 2")
            if probes == config["general"]["bw_probe_train_size"]:
                # send ack
                end_probe = time()
                packet = packets.TputProbeACK();
                packet.set_pps(probes)
                packet.set_time_delta(int((end_probe - start_probe)*1000*1000))
                #logging.debug(packet.get_time_delta())
                #logging.debug("============== 2 =========")
                packet.set_type(packets.TPUT_ACK_TYPE)
                packet.set_length(len(packet.get_buffer()))
                #logging.debug("Send probe (PATH 2) ACK %d" % (int((end_probe - start_probe)*1000*1000)))
                #logging.debug("Buffer size: 13000 bytes PATH 2")
                sock.sendto(packet.get_buffer(), (config["network"]["path2"]["destination"], config["network"]["path2"]["destination_port"]))
        else:
            logging.debug("Unknown packet type")

path1_recv_th = threading.Thread(target = path1_recv_loop, args = (path1_socket, ), daemon = True)
path2_recv_th = threading.Thread(target = path2_recv_loop, args = (path2_socket, ), daemon = True)
path1_recv_data_th = threading.Thread(target = path1_recv_data_loop, args = (path1_data_socket, ), daemon=True)
path2_recv_data_th = threading.Thread(target = path2_recv_data_loop, args = (path2_data_socket, ), daemon=True)


decode_loop_th = threading.Thread(target = process_loop, args = ( ), daemon = True)

path1_recv_data_th.start()
path2_recv_data_th.start()
path1_recv_th.start()
path2_recv_th.start()
decode_loop_th.start()

# Main loop
while True:
    sleep(1)