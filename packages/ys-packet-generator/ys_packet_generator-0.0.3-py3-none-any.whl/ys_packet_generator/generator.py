import socket
import time


def get32bitRepetition(num):
    return int(num / 4)


def using_str_format(test_obj) -> str:
    res = []
    for idx, x in enumerate(test_obj):
        if idx >= 4:
            break

        res.append("{:02x}".format(x))
    return " ".join(res)


def send(ip: str, port: int = 5001, bandwidth: int = 1000, packet_size: int = 1488, debug: bool = False) -> None:
    """
    Send data in UDP - unlimited loop
    Each packet data is an increasing index that repeats every 32bit
    @param: ip - destination IP address
            port - destination port
            bandwidth - the bandwidth to allocate
            packet_size - size of each packet
            debug - use prints or not
    @returns: None
    """

    timeToSend = 1 / ((bandwidth * 1024 / 8) / packet_size)

    # Create UDP socket - IPv4
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if debug:
        print("Start sending data over UDP...")
    msg = 0
    while (True):
        msg = (msg + 1) % 0xFFFFFFFF
        data = msg.to_bytes(4, 'big') * get32bitRepetition(packet_size)

        if debug:
            print(f"{time.time()} - {timeToSend} -> " +
                  using_str_format(msg.to_bytes(4, 'big')))

        clientSock.sendto(data, (ip, port))
        time.sleep(timeToSend)
