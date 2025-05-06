import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk


root = tk.Tk()
root.title("Dialog window")
root.geometry("1410x600+350+0")
def start_game():
    print("Гра почалась!")
    for widget in root.winfo_children():
        widget.destroy()
    bg = Image.open("./img/background.png")
    bg = bg.resize((1410, 600), Image.Resampling.LANCZOS) 
    bg_image = ImageTk.PhotoImage(bg)
    root.bg_image = bg_image
    canvas = tk.Canvas(root, width=1410, height=600)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

def exit_game():
    root.destroy()

def on_enter(e):
    e.widget.config(bg="#00ffff", fg="black")

def on_leave(e):
    e.widget.config(bg="#0ff", fg="black")

#menu bg
menu_bg = Image.open("./img/menuBg.png")
menu_bg = menu_bg.resize((1410, 600), Image.Resampling.LANCZOS)
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
play_button = tk.Button(root, text="Грати", command=start_game, **button_style)
exit_button = tk.Button(root, text="Вихід", command=exit_game, **button_style)
for button in [play_button, exit_button]:
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
center_x = 1410 // 2
canvas.create_window(center_x, 250, window=play_button)
canvas.create_window(center_x, 320, window=exit_button)

root.mainloop()