config = {
    "network": {
        "path1": {
            "source": "1.1.1.6",
            "destination": "1.1.1.2",
            "source_port": 10001,
            "destination_port": 10011
        },
        "path2": {
            "source": "192.168.1.101",
            "destination": "192.168.1.3",
            "source_port": 10002,
            "destination_port": 10012
        }
    },
    "data-plane": {
        "path1": {
            "ip": "1.1.1.2",
            "port": 10003
        },
        "path2": {
            "ip": "192.168.1.3",
            "port": 10003
        }
    },
    "encoder": {
        "GF": 2**8,
        "generation_size": 5,
        "coded_packets_size": 10
    },
    "general": {
        "bw_probe_interval_s": 10,
        "bw_probe_size_bytes": 1400,
        "bw_probe_train_size": 30,
        "buffer_size": 1400
    },
    "experiment": {
        "number_of_packets": 100000,
        "packet_size": 1300
    }
}
