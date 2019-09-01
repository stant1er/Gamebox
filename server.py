import socket, json, time
from PIL import ImageGrab
from video import convert, calc_resolution
from pynput.mouse import Button, Controller
from mouse import move_mouse, click_mouse

if __name__ == "__main__":
    port = 8080
    gaming_machine = socket.socket()
    host_name = socket.gethostbyname(socket.gethostname())
    gaming_machine.bind((host_name, port))
    gaming_machine.listen(1)
    print(host_name)

    while True:
        # Initializations
        conn, addr = gaming_machine.accept()
        conn.send("Testing connection . . .".encode())
        image = ImageGrab.grab()

        mouse = Controller()

        width, height = calc_resolution(conn)
        # Streaming video
        while True:
            convert(image, gaming_machine, conn)

            #Wait for receive message, then captures screen again
            conn.recv(1096).decode()
            image = ImageGrab.grab()
            print("New Image")

            # Move mouse
            move_mouse(conn, mouse, width, height)

            # Click mouse
            click_mouse(conn, mouse)


        conn.close()