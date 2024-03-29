import socket, json, time
import cv2
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Key
from pynput.keyboard import Controller as KeyController
from pynput.keyboard import Listener as KeyListener
from mouse import send_mouse_pos, send_mouse_clicks
from video import stream, send_resolution
from keyboard import send_keyboard_input

CURRENT_CLICK = []
CLICKS = []
CURRENT_KEY = {}
KEYPRESS = []

def on_click(x, y, button, pressed):
    if pressed:
        CURRENT_CLICK.append(time.time())
    else:
        if button == Button.left:
            CLICKS.append(("left", time.time() - CURRENT_CLICK[0]))
        else:
            CLICKS.append(("right", time.time() - CURRENT_CLICK[0]))
        CURRENT_CLICK.clear()


def on_press(key):
    CURRENT_KEY[str(key)] = time.time()


def on_release(key):
    try:
        KEYPRESS.append((str(key), time.time() - CURRENT_KEY[str(key)]))
        CURRENT_KEY.pop(str(key))
    except:
        None

def gaming(ip):
    port = 5000
    game_machine = socket.socket()
    game_machine.connect((ip, port))
    data = game_machine.recv(4096)
    print("Message received: ", data.decode())

    mouse = MouseController()
    mouse_listener = MouseListener(on_click=on_click)
    mouse_listener.start()

    keyboard = KeyController()
    keyboard_listener = KeyListener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    width, height = send_resolution(game_machine)

    # Streaming video
    while True:
        # Retrieves frame
        frame = stream(game_machine)

        # Displays frame
        cv2.namedWindow("Streaming", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Streaming",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Streaming", frame)
        if cv2.waitKey(1) == 27:
            break
        game_machine.send("Received".encode())
        print("Received")

        # Send mouse position
        send_mouse_pos(game_machine, mouse, width, height)

        # Send mouse clicks
        send_mouse_clicks(game_machine, CLICKS)
        CLICKS.clear()

        # Send keyboard input
        send_keyboard_input(game_machine, KEYPRESS)
        KEYPRESS.clear()
        CURRENT_KEY.clear()

    keyboard_listener.stop()
    mouse_listener.stop()
    cv2.destroyAllWindows()
    game_machine.close()