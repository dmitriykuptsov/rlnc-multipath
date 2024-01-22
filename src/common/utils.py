import numpy as np
import galois
import random 

FIELD_ELEMENTS = [i for i in range(1, 256)]
gf=galois.GF(2**8)

def get_random_GF_matrix(n, m):
    matrix = []
    for i in range(0, m):
        matrix.append([])
        for j in range(0, n):
            matrix[i].append(int(random.uniform(1, 255)))
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
    coded_packets = []
    coded_packets_ = []
    for i in range(0, coded_packets_size):
        coded_packets.append([])
        coded_packets_.append([])
    for i in range(0, packet_size):
        a = []
        for j in range(0, gen_size):
            a.append(packets[j][i])
        output_packets.append(a)
    output_packets = get_GF_array(output_packets)
    for i in range(0, packet_size):
        codes = np.dot(matrix, np.transpose(output_packets[i]))
        coded_packets[j].append(codes)
        for j in range(0, coded_packets_size):
            coded_packets_[j].append(codes[j])
    return coded_packets_

def decode_packets(matrix, packets, gen_size, coded_packets_size, packet_size):
    matrix = find_inverse_matrix(matrix)
    output_packets = []
    coded_packets = []
    coded_packets_ = []
    for i in range(0, coded_packets_size):
        coded_packets.append([])
        coded_packets_.append([])
    for i in range(0, packet_size):
        a = []
        for j in range(0, gen_size):
            a.append(packets[j][i])
        output_packets.append(a)
    output_packets = get_GF_array(output_packets)
    for i in range(0, packet_size):
        codes = np.dot(matrix, np.transpose(output_packets[i]))
        coded_packets[j].append(codes)
        for j in range(0, coded_packets_size):
            coded_packets_[j].append(codes[j])
    return coded_packets_
    