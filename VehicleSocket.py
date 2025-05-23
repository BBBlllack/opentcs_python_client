import os
# 设置加密启用标志, 小车默认不使用加密
ENC_ENABLE = os.getenv('ENC_ENABLE') if os.getenv('ENC_ENABLE') != "False" else False
import socket
import threading
import time
if ENC_ENABLE:
    from CryptUtils import DESdecrypt, DESencrpyt, SM4_encrypt, SM4_decrypt
import json
import re

HOST = "127.0.0.1"
# PORT = 40000
PORT = 30000
CODE = "utf-8"
BUF_SIZE = 1024 * 10
ENCR_METHOD = "SM4"
VEHICLE_NAME = "Vehicle-01"
RSA_PUB = ""
# 设置模拟标志, 默认为模拟环境
SIM_ENV = False if os.getenv("SIM_ENV") else True
DIR_VEL = [0,1] # 表示对准y方向 [-1,0]对准x负方向
if not ENC_ENABLE:
    ENCR_METHOD = "NON"

def print_config():
    print("=== 系统配置信息 ===")
    print(f"ENC_ENABLE     : {ENC_ENABLE}")
    print(f"SIM_ENV        : {SIM_ENV}")
    print(f"ENCR_METHOD    : {ENCR_METHOD}")
    print(f"HOST           : {HOST}")
    print(f"PORT           : {PORT}")
    print(f"CODE           : {CODE}")
    print(f"BUF_SIZE       : {BUF_SIZE}")
    print(f"VEHICLE_NAME   : {VEHICLE_NAME}")
    print(f"RSA_PUB        : {RSA_PUB if RSA_PUB else '未设置'}")
    print(f"当前朝向 DIR_VEL: {DIR_VEL}")
    print("====================\n")

# 小车发送对象
class ReceiveEntity:
    def __init__(self, operation=None, vehicleName=None, state=None, battery=None, position=None, instruction=None,
                 instructionFeedBack=None, timestamp=None):
        self.operation = operation
        self.vehicleName = vehicleName
        self.state = state
        self.battery = battery
        self.position = position
        self.instruction = instruction
        self.instructionFeedBack = instructionFeedBack
        self.timestamp = round(timestamp if timestamp else time.time() * 1000)

    def as_json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


first_point = None

# 小车接受对象
class SendEntity:
    def __init__(self):
        self.operation = None
        self.instruction = None
        self.message = None
        self.timestamp = None
        self.others = None

    def convertStepToDict(self):
        stepstr = self.instruction["step"]
        spx = re.findall(r"spx=(.*?)[,|}]", stepstr)[0]
        spy = re.findall(r"spy=(.*?)[,|}]", stepstr)[0]
        dpx = re.findall(r"dpx=(.*?)[,|}]", stepstr)[0]
        dpy = re.findall(r"dpy=(.*?)[,|}]", stepstr)[0]
        position = {
            "sourcePoint": {
                "pose": {
                    "position": {
                        "x": int(spx),
                        "y": int(spy),
                    }
                }
            },
            "destinationPoint": {
                "pose": {
                    "position": {
                        "x": int(dpx),
                        "y": int(dpy),
                    }
                }
            }
        }
        self.instruction['step'] = position

    @staticmethod
    def to_relative_position(reference_point: dict, target_point: dict) -> dict:
        ref_pos = reference_point['position']
        tgt_pos = target_point['position']

        relative_position = {
            'x': tgt_pos['x'] - ref_pos['x'],
            'y': tgt_pos['y'] - ref_pos['y'],
        }

        return {
            'position': relative_position,
        }

    @staticmethod
    def read_value(value: str):
        global first_point
        e = SendEntity()
        for k, v in json.loads(value).items():
            setattr(e, k, v)
        if e.instruction and e.instruction.get("step", None):
            e.convertStepToDict()
            # first_point = first_point if first_point else e.instruction["step"]["sourcePoint"]
            # e.instruction['step']['destinationPoint']['pose'] = SendEntity.to_relative_position(first_point["pose"],
            #                                                                          e.instruction['step'][
            #                                                                              'destinationPoint']['pose'])
            # 根据源点和目标点计算移动位置
            e.instruction['step']['destinationPoint']['pose'] = SendEntity.to_relative_position(
                e.instruction['step']['sourcePoint']['pose'], e.instruction['step']['destinationPoint']['pose'])
        return e

    def __str__(self):
        return str(self.__dict__)


def sendMsg(sock: socket.socket, m: ReceiveEntity, E=True):
    m: str = m.as_json()
    if not E:
        m += '\n'
        return sock.sendall(m.encode(CODE))
    if ENCR_METHOD == "NON":
        m = m
    elif ENCR_METHOD == "DES":
        m = DESencrpyt(m)
    elif ENCR_METHOD == "RSA":
        pass
    elif ENCR_METHOD == "SM4":
        m = SM4_encrypt(m)
    m += '\n'
    sock.sendall(m.encode(CODE))


def recvMsg(sock: socket.socket):
    tname = threading.current_thread().name
    while True:
        data = sock.recv(BUF_SIZE)
        data = data.decode(CODE)
        if ENCR_METHOD == "NON":
            pass
        elif ENCR_METHOD == "DES":
            data = DESdecrypt(data)
        elif ENCR_METHOD == "RSA":
            pass
        elif ENCR_METHOD == "SM4":
            # print(f"{tname} recv: {data}")
            data = SM4_decrypt(data)
        data = SendEntity.read_value(data)
        # 经过坐标变换的相对坐标
        if data.instruction and data.instruction['step'] and data.instruction['step']['destinationPoint']:
            dpx_r, dpy_r = data.instruction['step']['destinationPoint']['pose']['position']['x'], \
                data.instruction['step']['destinationPoint']['pose']['position']['y']
            print(f"{tname} : {data} \n dpx_r: {dpx_r} dpy_r: {dpy_r}")
            if not SIM_ENV:
                driveVehicleByCommand(data)
            continue
        print(f"{tname} : {data}")


def driveVehicleByCommand(command: SendEntity):
    global DIR_VEL
    scale = 1000
    '''
    根据命令驱动车辆 ↑y+ →x+
    :param command:
    :return:
    '''
    dpx_r, dpy_r = command.instruction['step']['destinationPoint']['pose']['position']['x'], \
        command.instruction['step']['destinationPoint']['pose']['position']['y']
    dpx_r_cm, dpy_r_cm = dpx_r / scale, dpy_r / scale # 比例缩放
    if DIR_VEL[0] == 1: # 对准x+
        pass
    elif DIR_VEL[0] == -1: # x-
        pass
    elif DIR_VEL[1] == 1: # y+
        pass
    elif DIR_VEL[1] == -1: # y-
        pass


if __name__ == '__main__':

    pub = None

    if not SIM_ENV:
        import rospy
        from geometry_msgs.msg import Twist

        rospy.init_node('turtlebot_teleop')  # 创建ROS节点
        pub = rospy.Publisher('~cmd_vel', Twist, queue_size=5)  # 创建速度话题发布者，'~cmd_vel'='节点名/cmd_vel'

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        trecv = threading.Thread(target=recvMsg, args=(client,), name="recvMsg")
        trecv.start()
        sendMsg(client, ReceiveEntity(operation="HANDSHAKE", vehicleName=VEHICLE_NAME,
                                      instructionFeedBack=f"{ENCR_METHOD}{VEHICLE_NAME}"),
                E=False)  # 通告服务器车辆名称, 并且协商加密方式, 此消息为明文
        while True:
            msg = input()
            r = ReceiveEntity(operation="MOV", vehicleName=VEHICLE_NAME,
                              instructionFeedBack=msg)
            if msg == "disconnect":
                sendMsg(client, r)
                break
            sendMsg(client, r)

        # trecv.join()
    except socket.error as msg:
        print(msg)
    finally:
        client.close()
