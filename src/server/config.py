config = {
    "network": {
        "path1": {
            "source": "1.1.1.2",
            "destination": "1.1.1.6",
            "source_port": 10011,
            "destination_port": 10001,
        },
        "path2": {
            "source": "192.168.1.3",
            "destination": "192.168.1.101",
            "source_port": 10012,
            "destination_port": 10002
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
        "generation_size": 10,
        "coded_packets_size": 14
    },
    "experiment": {
        "number_of_packets": 100
    },
    "general": {
        "bw_probe_size_bytes": 1400,
        "bw_probe_train_size": 30,
        "buffer_size": 1400
    }
}