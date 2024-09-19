import numpy as np
import galois
import random 
from time import time
import logging

FIELD_ELEMENTS = [i for i in range(1, 256)]
gf=galois.GF(2**8)

def get_random_GF_matrix(n, m):
    matrix = []
    for i in range(0, m):
        matrix.append([])
        for j in range(0, n):
            matrix[i].append(int(random.uniform(1, 256)))
    return gf(matrix)

def get_GF_array(a):
    return gf(a)

def mul_GF_matrix_and_vector(m, P):
    return np.dot(m, P)

def get_GF_matrix(m):
    return gf(m)

def find_inverse_matrix(m):
    np.linalg.inv(m)

def code_packets(matrix, packets, gen_size, coded_packets_size, packet_size):
    output_packets = []
    coded_packets_ = []
    for i in range(0, coded_packets_size):
        coded_packets_.append([])
    output_packets = np.transpose(packets)
    output_packets = get_GF_array(output_packets)
    for i in range(0, packet_size):
        codes = np.dot(matrix, np.transpose(output_packets[i]))
        for j in range(0, coded_packets_size):
            coded_packets_[j].append(codes[j])
    return coded_packets_

def decode_packets(matrix, packets, gen_size, packet_size):
    matrix = np.linalg.inv(gf(matrix))
    coded_packets_ = []
    codes = np.dot(matrix, packets)
    coded_packets_.append(codes)
    return np.transpose(coded_packets_)
    