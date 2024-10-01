import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import queue

def triangular_membership(x, a, b, c):
    if x < a or x > c:
        return 0
    elif a <= x < b:
        return (x - a) / (b - a)
    elif b <= x < c:
        return (c - x) / (c - b)
    elif x == c:
        return 0
    else:
        return 1

def browning_membership(browning):
    light = triangular_membership(browning, 0, 0, 5)
    medium = triangular_membership(browning, 3, 5, 7)
    dark = triangular_membership(browning, 5, 10, 10)
    return light, medium, dark

def bread_type_membership(bread_type):
    white = triangular_membership(bread_type, 0, 0, 5)
    whole_grain = triangular_membership(bread_type, 3, 5, 7)
    rye = triangular_membership(bread_type, 5, 10, 10)
    return white, whole_grain, rye

def calculate_toasting_time(browning, bread_type):
    light, medium, dark = browning_membership(browning)
    white, whole_grain, rye = bread_type_membership(bread_type)

    toasting_time = (
        (light * white * 4) + (light * whole_grain * 6) + (light * rye * 8) +
        (medium * white * 7) + (medium * whole_grain * 9) + (medium * rye * 12) +
        (dark * white * 10) + (dark * whole_grain * 13) + (dark * rye * 15)
    )

    total_membership = (
        light * white + light * whole_grain + light * rye +
        medium * white + medium * whole_grain + medium * rye +
        dark * white + dark * whole_grain + dark * rye
    )
    
    if total_membership > 0:
        toasting_time /= total_membership
    return toasting_time

toasting_in_progress = False

def animate_toasting(browning, bread_type, progress_label, bread_label, temp_label):
    global toasting_in_progress
    toasting_in_progress = True
    toasting_time = calculate_toasting_time(browning, bread_type)
    progress_label.config(text=f'Toasting Time: {toasting_time:.2f} seconds')

    if browning <= 3:
        bread_states = ["bread(1).png", "bread(2).png", "bread(2).png", "bread(2).png"]
    elif 3 < browning <= 7:
        bread_states = ["bread(1).png", "bread(2).png", "bread(3).png", "bread(3).png"]
    else:
        bread_states = ["bread(1).png", "bread(2).png", "bread(3).png", "bread(4).png"]

    interval = toasting_time / len(bread_states)

    def toast(q):
        for i in range(len(bread_states)):
            bread_image_pil = Image.open(bread_states[i])
            bread_image = ImageTk.PhotoImage(bread_image_pil)
            q.put(bread_image)

            for sec in range(int(interval), 0, -1):
                time.sleep(1)
                remaining_time = toasting_time - (i * interval + (interval - sec))
                current_temp = 150 + (i * 30)
                q.put(f"Time left: {int(remaining_time)} seconds")
                q.put(f"Temperature: {current_temp} °C")

        q.put("Toasting complete!")
        q.put("enable")
        global toasting_in_progress
        toasting_in_progress = False

    q = queue.Queue()
    threading.Thread(target=toast, args=(q,)).start()

    def update_ui():
        try:
            while True:
                msg = q.get_nowait()
                if isinstance(msg, str):
                    if msg == "enable":
                        start_button.config(state="normal")
                    else:
                        if "Temperature" in msg:
                            temp_label.config(text=msg)
                        else:
                            progress_label.config(text=msg)
                else:
                    bread_label.config(image=msg)
                    bread_label.image = msg
        except queue.Empty:
            root.after(100, update_ui)

    root.after(100, update_ui)

def start_toasting():
    global toasting_in_progress
    if toasting_in_progress:
        messagebox.showwarning("Warning", "Toast process is already in progress!")
        return

    try:
        desired_browning = browning_scale.get()
        bread_type_input = bread_type_scale.get()
        start_button.config(state="disabled")
        animate_toasting(desired_browning, bread_type_input, progress_label, bread_label, temp_label)
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numeric values.")

def reset_bread_image():
    if toasting_in_progress:
        messagebox.showwarning("Warning", "Cannot reset while toasting is in progress.")
        return

    bread_image_pil = Image.open("bread(1).png")
    bread_image = ImageTk.PhotoImage(bread_image_pil)
    bread_label.config(image=bread_image)
    bread_label.image = bread_image

    progress_label.config(text="Ready to toast!")
    start_button.config(state="normal")
    temp_label.config(text="Temperature: 0 °C")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Toaster Namin To")
    root.configure(bg="lightblue")

    toaster_image_pil = Image.open("toaster.png")
    toaster_image = ImageTk.PhotoImage(toaster_image_pil)

    canvas = tk.Canvas(root, width=400, height=400, bg="lightblue")
    canvas.pack()

    bread_image_pil = Image.open("bread(1).png")
    bread_image = ImageTk.PhotoImage(bread_image_pil)
    bread_label = tk.Label(canvas, image=bread_image, bg="lightblue")

    bread_x = 85
    bread_y = 50
    toaster_x = 30
    toaster_y = 190

    bread_label.place(x=bread_x, y=bread_y)
    toaster_label = tk.Label(canvas, image=toaster_image, bg="lightblue")
    toaster_label.place(x=toaster_x, y=toaster_y)

    label_font = ('Helvetica', 12)

    tk.Label(root, text="Desired Browning Level (0-10):", bg="lightblue", fg="black", font=label_font).pack(pady=5)
    browning_scale = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, font=label_font)
    browning_scale.pack(pady=0)

    tk.Label(root, text="Bread Type (0=white, 5=whole grain, 10=rye):", bg="lightblue", fg="black", font=label_font).pack(pady=5)
    bread_type_scale = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, font=label_font)
    bread_type_scale.pack(pady=0)

    start_button = tk.Button(root, text="Start Toasting", command=start_toasting, font=label_font)
    start_button.pack(pady=3)

    reset_button = tk.Button(root, text="Reset", command=reset_bread_image, font=label_font)
    reset_button.pack(pady=3)

    progress_label = tk.Label(root, text="", bg="lightblue", fg="black", font=label_font)
    progress_label.pack(pady=5)

    temp_label = tk.Label(root, text="Temperature: 0 °C", bg="lightblue", fg="black", font=label_font)
    temp_label.place(x=250, y=20)

    root.mainloop()
