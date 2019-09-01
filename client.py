import socket, json
import cv2
from video import stream, send_resolution, get_resolution
from pynput.mouse import *
import time

global START, END
MOUSE_SCROLL = None

def on_click(x, y, button, pressed):
    global START
    global END
    if pressed:
        START = time.time()
    else:
        END = time.time()
        press_time = END - START
        if button == Button.left:
            CLICKS.append(("left", press_time))
        else:
            CLICKS.append(("right", press_time))


if __name__ == "__main__":
    stream_machine = socket.socket()
    host_name = socket.gethostbyname(socket.gethostname())
    port = 8080
    stream_machine.connect(('192.168.0.68', port))
    data = stream_machine.recv(4096)
    print("Message received: ", data.decode())
    CLICKS = []

    mouse = Controller()
    listener = Listener(on_click=on_click)#, on_scroll=on_scroll)
    listener.start()

    width, height = send_resolution(stream_machine)

    # Streaming video
    while True:
        # Retrieves frame
        frame = stream(stream_machine)

        # Displays frame
        cv2.namedWindow("Streaming", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Streaming",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Streaming", frame)
        if cv2.waitKey(1) == 27:
            break
        stream_machine.send("Received".encode())
        print("Received")

        # Send mouse position
        x, y = mouse.position
        x_ratio = x/width
        y_ratio = y/height
        stream_machine.send(str(x_ratio).encode())
        stream_machine.recv(1096)
        stream_machine.send(str(y_ratio).encode())
        stream_machine.recv(1096)

        # Send mouse clicks
        stream_clicks = json.dumps({"0": CLICKS})
        stream_machine.send(stream_clicks.encode())
        stream_machine.recv(1096)
        CLICKS.clear()





    cv2.destroyAllWindows()
    stream_machine.close()