## Programs

Using Python3. 

sender.sh, receiver.sh, and network_emulator.sh are used to run the python program. 

## Instruction

The bash file should set up the permission if not:
```
chmod u+x receiver.sh
chmod u+x sender.sh
chmod u+x network_emulator.sh
```

1. network_emulator.sh have arguments:
* UDP port number to receive data from sender
* Receiver's network address
* Receiver’s receiving UDP port number
* UDP port number to send data to receiver
* Sender's network address
* Sender's receiving UDP port number
* Maximum Delay
* Drop probability
* Verbose

2. receiver.sh have arguments:
* Host address of the network emulator
* Network emulator's UDP port number
* Network emulator's network address
* Filename to store received data

3. sender.sh have arguments:
* Host address of the network emulator
* UDP port number for the network emulator to receive data
* UDP port for receiving ACKs from the network emulator
* Sender timeout in milliseconds
* Name of file to transfer

## Example execution
Test the program on 
```
ubuntu2204-002.student.cs.uwaterloo.ca
ubuntu2204-004.student.cs.uwaterloo.ca
ubuntu2204-006.student.cs.uwaterloo.ca
```
1. On the host host1: ./network_emulator.sh 39991 ubuntu2204-004.student.cs.uwaterloo.ca 39994 39993 ubuntu2204-006.student.cs.uwaterloo.ca 39992 1 0.2 0
2. On the host host2: ./receiver.sh  ubuntu2204-002.student.cs.uwaterloo.ca 39993 39994 output.txt
3. On the host host3: ./sender.sh ubuntu2204-002.student.cs.uwaterloo.ca 39991 39992 50 input.txt
