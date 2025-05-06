import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Dialog window")
root.geometry("1410x600+0+0")

pressed_keys = set()
paterega_direction = -1

# global variables
canvas = None
ihor_id = None
wadzik_id = None
paterega_id = None

ihor_texture = None
wadzik_texture = None
paterega_texture = None

def start_game():
    global canvas
    for widget in root.winfo_children():
        widget.destroy()

    bg = Image.open("./img/background.png").resize((1410, 600), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(bg)
    root.bg_image = bg_image

    canvas = tk.Canvas(root, width=1410, height=600)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    create_characters()
    update_positions() 

def create_characters():
    global ihor_id, wadzik_id, paterega_id
    global ihor_texture, wadzik_texture, paterega_texture

    ihor_img = Image.open("img/IgorPlayer.png").resize((170, 200), Image.Resampling.LANCZOS)
    ihor_texture = ImageTk.PhotoImage(ihor_img)
    ihor_id = canvas.create_image(50, 300, anchor="nw", image=ihor_texture)

    wadzik_img = Image.open("img/WadikPlayer.png").resize((300, 200), Image.Resampling.LANCZOS)
    wadzik_texture = ImageTk.PhotoImage(wadzik_img)
    wadzik_id = canvas.create_image(50, 100, anchor="nw", image=wadzik_texture)

    paterega_img = Image.open("img/Paterega.png").resize((500, 300), Image.Resampling.LANCZOS)
    paterega_texture = ImageTk.PhotoImage(paterega_img)
    paterega_id = canvas.create_image(910, 290, anchor="nw", image=paterega_texture)

def update_positions():
    global paterega_direction
    if not canvas: return  

    if ihor_id and wadzik_id:
        if 'Left' in pressed_keys:
            canvas.move(wadzik_id, -10, 0)
        if 'Right' in pressed_keys:
            canvas.move(wadzik_id, 10, 0)
        if 'Up' in pressed_keys:
            canvas.move(wadzik_id, 0, -10)
        if 'Down' in pressed_keys:
            canvas.move(wadzik_id, 0, 10)

        if 'a' in pressed_keys:
            canvas.move(ihor_id, -10, 0)
        if 'd' in pressed_keys:
            canvas.move(ihor_id, 10, 0)
        if 'w' in pressed_keys:
            canvas.move(ihor_id, 0, -10)
        if 's' in pressed_keys:
            canvas.move(ihor_id, 0, 10)

    # Paterega move
    if paterega_id:
        canvas_width = canvas.winfo_width()
        paterega_width = 500
        min_x = canvas_width - 100
        max_x = canvas_width - 100

        x, _ = canvas.coords(paterega_id)
        if x <= min_x:
            paterega_direction = 1
        elif x >= max_x:
            paterega_direction = -1
        canvas.move(paterega_id, paterega_direction * 5, 0)

    root.after(30, update_positions)

def key_press(event):
    pressed_keys.add(event.keysym)

def key_release(event):
    pressed_keys.discard(event.keysym)

def exit_game():
    root.destroy()

# menu
menu_bg = Image.open("./img/menuBg.png").resize((1410, 600), Image.Resampling.LANCZOS)
bg_menu = ImageTk.PhotoImage(menu_bg)

canvas = tk.Canvas(root, width=1410, height=600)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_menu, anchor="nw")

button_style = {
    "font": ("Consolas", 20, "bold"),
    "bg": "#0ff",
    "fg": "black",
    "activebackground": "#00cccc",
    "activeforeground": "black",
    "bd": 3,
    "relief": "ridge",
    "cursor": "hand2"
}

def on_enter(e): e.widget.config(bg="#00ffff", fg="black")
def on_leave(e): e.widget.config(bg="#0ff", fg="black")

play_button = tk.Button(root, text="Грати", command=start_game, **button_style)
exit_button = tk.Button(root, text="Вихід", command=exit_game, **button_style)

for button in [play_button, exit_button]:
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

center_x = 1410 // 2
canvas.create_window(center_x, 250, window=play_button)
canvas.create_window(center_x, 320, window=exit_button)

root.bind("<KeyPress>", key_press)
root.bind("<KeyRelease>", key_release)

root.mainloop()
