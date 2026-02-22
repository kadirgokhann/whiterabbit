import socket
import time
import struct


class WhiteRabbitSlave:

    def __init__(self, masterIp, masterPort):

        self.masterIp = masterIp

        self.masterPort = masterPort

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.localClockOffsetNanoseconds = 0


    def GetSystemTimeNs(self):

        currentTimeSeconds = time.time()

        currentTimeNanoseconds = int(currentTimeSeconds * 1000000000)

        return currentTimeNanoseconds


    def GetLocalTimeNs(self):

        systemTimeNanoseconds = self.GetSystemTimeNs()

        adjustedTimeNanoseconds = systemTimeNanoseconds + self.localClockOffsetNanoseconds

        return adjustedTimeNanoseconds


    def Log(self, message):

        currentTimeNanoseconds = self.GetLocalTimeNs()

        print(f"[SLAVE][{currentTimeNanoseconds}] {message}")


    def SendSyncRequest(self):

        payload = struct.pack("!I", 1)

        self.socket.sendto(payload, (self.masterIp, self.masterPort))

        self.Log("TX SyncRequest")

        data, _ = self.socket.recvfrom(1024)

        t2 = self.GetLocalTimeNs()

        messageType = struct.unpack("!I", data[0:4])[0]

        t1 = struct.unpack("!Q", data[4:12])[0]

        self.Log(f"RX SyncResponse t1={t1} t2={t2}")

        return t1, t2


    def SendDelayRequest(self):

        t3 = self.GetLocalTimeNs()

        payload = struct.pack("!IQ", 3, t3)

        self.socket.sendto(payload, (self.masterIp, self.masterPort))

        self.Log(f"TX DelayRequest t3={t3}")

        data, _ = self.socket.recvfrom(1024)

        messageType = struct.unpack("!I", data[0:4])[0]

        receivedT3 = struct.unpack("!Q", data[4:12])[0]

        t4 = struct.unpack("!Q", data[12:20])[0]

        self.Log(f"RX DelayResponse t3={receivedT3} t4={t4}")

        return t3, t4


    def Synchronize(self):

        t1, t2 = self.SendSyncRequest()

        t3, t4 = self.SendDelayRequest()

        roundTripDelayNanoseconds = ((t2 - t1) + (t4 - t3)) // 2

        offsetNanoseconds = (t2 - t1) - roundTripDelayNanoseconds

        self.localClockOffsetNanoseconds = -offsetNanoseconds

        self.Log(f"Computed delay={roundTripDelayNanoseconds} ns")

        self.Log(f"Computed offset={offsetNanoseconds} ns")

        self.Log(f"Applied correction={self.localClockOffsetNanoseconds} ns")


    def Run(self):

        self.Log("Slave started")

        while True:

            self.Synchronize()

            time.sleep(1)


if __name__ == "__main__":

    slave = WhiteRabbitSlave("127.0.0.1", 5000)

    slave.Run()
