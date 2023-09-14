
import socket


def using_str_format(test_obj) -> str:
    res = []
    for idx, x in enumerate(test_obj):
        if idx >= 4:
            break

        res.append("{:02x}".format(x))
    return " ".join(res)


def listen(ip: str, port: int = 5001, buffer_size: int = 2000, full_debug: bool = False, debug: bool = False):
    """
    Receive data in UDP from the generator - unlimited loop
    Each packet data is an increasing index that repeats every 32bit
    @param: ip - local IP address
            port - local port
            buffer_size - buffer size to reveive packets
            full_debug - print all debug prints
            debug - print only missed packet's index
    @returns: None
    """
    # Create a datagram socket
    UDPServerSocket = socket.socket(
        family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    UDPServerSocket.bind((ip, port))

    if full_debug:
        print("UDP server up and listening")

    loopIndex = 0
    # Listen for incoming datagrams
    while(True):
        loopIndex = (loopIndex + 1) % 0xFFFFFFFF
        bytesAddressPair = UDPServerSocket.recvfrom(buffer_size)

        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        res = bytearray(b'')
        for idx, x in enumerate(message):
            if idx >= 4:
                break

            res.append(x)
        receivedIndex = int.from_bytes(res, "big")

        clientMsg = "Message from Client:{}".format(using_str_format(message))
        clientIP = "Client IP Address:{}".format(address)

        if loopIndex != receivedIndex:
            if full_debug or debug:
                print()
                print()
            while loopIndex != receivedIndex:
                if full_debug or debug:
                    print(f"ERROR!! missed index - {loopIndex}")
                loopIndex = (loopIndex + 1) % 0xFFFFFFFF
            if full_debug or debug:
                print()
                print()

        if full_debug:
            print(clientMsg)
            print(clientIP)
