import threading
import time

def worker():
    print("Worker thread started")
    time.sleep(5)  # 模拟耗时操作
    print("Worker thread finished")

if __name__ == "__main__":
    thread = threading.Thread(target=worker)
    thread.start()
    print("Main thread continues")
    thread.join()  # 主线程在这里等待 worker 线程结束
    print("Main thread finished")