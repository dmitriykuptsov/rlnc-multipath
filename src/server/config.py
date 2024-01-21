config = {
    "network": {
        "path1": {
            "source": "1.1.1.2",
            "destination": "1.1.1.6",
            "source_port": 10011,
            "destination_port": 10001
        },
        "path2": {
            "source": "192.168.1.3",
            "destination": "192.168.1.101",
            "source_port": 10012,
            "destination_port": 10002
        }
    },
    "encoder": {
        "GF": 2**8
    },
    "general": {
        "bw_probe_size_bytes": 1300,
        "bw_probe_train_size": 10,
        "buffer_size": 1400
    }
}