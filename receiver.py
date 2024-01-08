import os
import sys
import argparse
import socket
import math

from packet import Packet

# Writes the received content to file
def append_to_file(filename, data):
    file = open(filename, 'a')
    file.write(data)

# Appends the packet information to the log file
def append_to_log(recv_typ, recv_seqnum):
    with open('arrival.log', 'a') as file:
        if recv_typ == 3:
            file.write('SYN\n')
        elif recv_typ == 2:
            file.write('EOT\n')
        else:
            file.write('{}\n'.format(recv_seqnum))
    
# Sends ACKs, EOTs, and SYN to the network emulator. and logs the seqnum.
def send_ack(recv_sock, typ, expected_seq_num, host, port): 
    if typ == 3:
        syn_packet = Packet(3, 0, 0, '')
        recv_sock.sendto(syn_packet.encode(), (host, port))
    elif typ == 2:
        eot_packet = Packet(2, expected_seq_num, 0, '')
        recv_sock.sendto(eot_packet.encode(), (host, port))
    else:
        ack_packet = Packet(0, expected_seq_num, 0, '')
        recv_sock.sendto(ack_packet.encode(), (host, port))
    
    
if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description="Congestion Controlled GBN Receiver")
    parser.add_argument("ne_addr", type=str, metavar="<NE hostname>", help="network emulator's network address")
    parser.add_argument("ne_port", type=int, metavar="<NE port number>", help="network emulator's UDP port number")
    parser.add_argument("recv_port", type=int, metavar="<Receiver port number>", help="network emulator's network address")
    parser.add_argument("dest_filename", type=str, metavar="<Destination Filename>", help="Filename to store received data")
    args = parser.parse_args()

    # Clear the output and log files
    open(args.dest_filename, 'w').close()
    open('arrival.log', 'w').close()

    expected_seq_num = 0 # Current Expected sequence number
    seq_size = 32 # Max sequence number
    max_window_size = 10 # Max number of packets to buffer
    recv_buffer = {}  # Buffer to store the received data

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', args.recv_port))  # Socket to receive data

        while True:
            # Receive packets, log the seqnum, and send response
            packet, addr = s.recvfrom(1024)
            recv_typ, recv_seqnum, recv_length, recv_data = Packet(packet).decode()
            append_to_log(recv_typ, recv_seqnum)

            if recv_typ == 3:
                # Receive SYN packet and send back
                send_ack(s, 3, expected_seq_num, args.ne_addr, args.ne_port)
                print("SYN Received. Start.")
            else:
                print('Packet received. Packet:{} {} {}'.format(recv_typ, recv_seqnum, recv_length))
                # check sequence number
                if recv_seqnum == expected_seq_num:
                    # handle EOT packet
                    if recv_typ == 2: 
                        send_ack(s, 2, expected_seq_num, args.ne_addr, args.ne_port)
                        print("EOT Received. Terminate the program.")
                        s.close()
                        break
                    # receive data packet and write data to file
                    else:
                        append_to_file(args.dest_filename, recv_data)
                        expected_seq_num = (expected_seq_num + 1) % 32
                        
                        # check if next packet exists
                        while expected_seq_num in recv_buffer:
                            append_to_file(args.dest_filename, recv_buffer[expected_seq_num])
                            recv_buffer.pop(expected_seq_num)
                            expected_seq_num = (expected_seq_num + 1) % 32
                        
                        # send ack packet back
                        last_seq_num = (expected_seq_num - 1) % 32
                        send_ack(s, 0, last_seq_num, args.ne_addr, args.ne_port)

                # sequence number not the one expected
                else:
                    # within the next 10 sequence numbers 
                    if (recv_seqnum - expected_seq_num) % 32 <= 10 and recv_seqnum not in recv_buffer:
                        print('Store the data {}'.format(recv_seqnum))
                        recv_buffer[recv_seqnum] = recv_data

                    send_ack(s, 0, last_seq_num, args.ne_addr, args.ne_port)
