import socket
import time
import struct


class WhiteRabbitMaster:

    def __init__(self, bindIp, bindPort):

        self.bindIp = bindIp

        self.bindPort = bindPort

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.socket.bind((self.bindIp, self.bindPort))


    def GetCurrentTimeNs(self):

        currentTimeSeconds = time.time()

        currentTimeNanoseconds = int(currentTimeSeconds * 1000000000)

        return currentTimeNanoseconds


    def Log(self, message):

        currentTimeNanoseconds = self.GetCurrentTimeNs()

        print(f"[MASTER][{currentTimeNanoseconds}] {message}")


    def Run(self):

        self.Log("Master started")

        while True:

            data, address = self.socket.recvfrom(1024)

            receiveTime = self.GetCurrentTimeNs()

            messageType = struct.unpack("!I", data[0:4])[0]

            self.Log(f"RX from {address} type={messageType}")

            if messageType == 1:

                t1 = self.GetCurrentTimeNs()

                responsePayload = struct.pack("!IQ", 2, t1)

                self.socket.sendto(responsePayload, address)

                self.Log(f"TX SyncResponse t1={t1}")

            if messageType == 3:

                t4 = self.GetCurrentTimeNs()

                t3 = struct.unpack("!Q", data[4:12])[0]

                responsePayload = struct.pack("!IQQ", 4, t3, t4)

                self.socket.sendto(responsePayload, address)

                self.Log(f"TX DelayResponse t3={t3} t4={t4}")


if __name__ == "__main__":

    master = WhiteRabbitMaster("0.0.0.0", 5000)

    master.Run()
