import rospy
from math import pi
from geometry_msgs.msg import Twist

speed = 0.2  # 默认移动速度 m/s
turn = 0.5  # 默认转向速度 rad/s, 2*pi = 360° pi/2 = 90°
x = 0  # 前进后退方向
th = 0  # 转向/横向移动方向
target_speed = 0  # 前进后退目标速度
target_turn = 0  # 转向目标速度
target_HorizonMove = 0  # 横向移动目标速度
control_speed = 0  # 前进后退实际控制速度
control_turn = 0  # 转向实际控制速度
control_HorizonMove = 0  # 横向移动实际控制速度

msg = """
My Control Your Turtlebot!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
space key, k : force stop
anything else : stop smoothly
b : switch to OmniMode/CommonMode
CTRL-C to quit
"""

# 键值对应移动/转向方向
moveBindings = {
    'i': (1, 0),  # 前进
    'o': (1, -1),
    'j': (0, 1),  # 左转
    'l': (0, -1),  # 右转
    'u': (1, 1),
    ',': (-1, 0),  # 后退
    '.': (-1, 1),
    'm': (-1, -1),
}

# 键值对应速度增量
speedBindings = {
    'q': (1.1, 1.1),
    'z': (0.9, 0.9),
    'w': (1.1, 1),
    'x': (0.9, 1),
    'e': (1, 1.1),
    'c': (1, 0.9),
}


# 以字符串格式返回当前速度
def vels(speed, turn):
    return "currently:\tspeed %s\tturn %s " % (speed, turn)


# 主函数
if __name__ == "__main__":

    rospy.init_node('turtlebot_teleop')  # 创建ROS节点
    pub = rospy.Publisher('~cmd_vel', Twist, queue_size=5)  # 创建速度话题发布者，'~cmd_vel'='节点名/cmd_vel'

    try:
        print(msg)  # 打印控制说明
        print(vels(speed, turn))  # 打印当前速度
        while (1):
            key = getKey()  # 获取键值

            # 切换是否为全向移动模式，全向轮/麦轮小车可以加入全向移动模式
            if key == 'b':
                print("OmniMode not support!")

            # 判断键值是否在移动/转向方向键值内
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                th = moveBindings[key][1]

            # 判断键值是否在速度增量键值内
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]
                print(vels(speed, turn))  # 速度发生变化，打印出来

            # 空键值/'k',相关变量置0
            elif key == ' ' or key == 'k':
                x = 0
                th = 0
                control_speed = 0
                control_turn = 0
                HorizonMove = 0

            # 长期识别到不明键值，相关变量置0
            else:
                if (key == '\x03'):
                    break

            # 根据速度与方向计算目标速度
            target_speed = speed * x
            target_turn = turn * th
            target_HorizonMove = speed * th

            # 平滑控制，计算前进后退实际控制速度
            if target_speed > control_speed:
                control_speed = min(target_speed, control_speed + 0.1)
            elif target_speed < control_speed:
                control_speed = max(target_speed, control_speed - 0.1)
            else:
                control_speed = target_speed

            # 平滑控制，计算转向实际控制速度
            if target_turn > control_turn:
                control_turn = min(target_turn, control_turn + 0.5)
            elif target_turn < control_turn:
                control_turn = max(target_turn, control_turn - 0.5)
            else:
                control_turn = target_turn

            # 平滑控制，计算横向移动实际控制速度
            if target_HorizonMove > control_HorizonMove:
                control_HorizonMove = min(target_HorizonMove, control_HorizonMove + 0.1)
            elif target_HorizonMove < control_HorizonMove:
                control_HorizonMove = max(target_HorizonMove, control_HorizonMove - 0.1)
            else:
                control_HorizonMove = target_HorizonMove

            twist = Twist()  # 创建ROS速度话题变量

            twist.linear.x = control_speed
            twist.linear.y = control_HorizonMove
            twist.linear.z = 0
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = 0

            pub.publish(twist)  # ROS发布速度话题

    # 运行出现问题则程序终止并打印相关错误信息
    except Exception as e:
        print(e)

    # 程序结束前发布速度为0的速度话题
    finally:
        twist = Twist()
        twist.linear.x = 0;
        twist.linear.y = 0;
        twist.linear.z = 0
        twist.angular.x = 0;
        twist.angular.y = 0;
        twist.angular.z = 0
        pub.publish(twist)
