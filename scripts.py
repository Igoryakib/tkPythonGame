import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import pygame
pygame.mixer.init()

bg_music = "sounds/MainTheme.wav"
hit_sound = pygame.mixer.Sound("sounds/Hit.wav")
victory_sound = pygame.mixer.Sound("sounds/PateregaLose.wav")
defeat_sound = pygame.mixer.Sound("sounds/OurDeath.wav")

root = tk.Tk()
root.title("Здача лабки Game")
root.geometry("1410x600+0+0")

pressed_keys = set()
paterega_direction = -1

# global variables
last_hit_time_ihor = 0
last_hit_time_wadzik = 0
damage_cooldown = 1000
last_paterega_attack = 0
canvas = None
ihor_id = None
wadzik_id = None
paterega_id = None
ihor_hp = 4
wadzik_hp = 4
paterega_hp = 15
ihor_hp_text = None
wadzik_hp_text = None
paterega_hp_text = None
ihor_texture = None
wadzik_texture = None
paterega_texture = None
Ihor_attack = [
"Ми написали нейронку з допомогою нейронки.",
"Наша прога - інтроверт, вона нормальна, просто Вас соромиться.",
"Ми підключили AI",
"Це не баг, це фіча",
"ШІ хвалить наш код",
"Цей раз з нами був Git"
]

Wadzik_attack = [
"Я скинув Кані Весту, він оцінив.",
"Наша прога знає ваше місцезнаходження.",
"Я попрошу Кані Веста автограф для Вас.",
"Цей код писався під бутилку пива і треки Кані Веста.",
"Наша нейронка знає багато геометричних і ультраправих фігур",
]

Paterega_attack = [
"Вадим, Ви фанат Кані Веста.",
"Хлопці, ви вайб-кодери.",
"Інтерфейс не user-friendly.",
"Ви спортили Захара і підсадили його на Кані Веста.",
"Немає обробника помилок і екрана завантаження.",
"Сьогодні 2, на наступний раз тоже 2",
"Я дав ГПТ на оцінку ваш код а він сказав шо це він його написав",
]
attack_flags = {
    "ihor": False,
    "wadzik": False,
    "paterega": False
}
last_attack_time = {
    "ihor": 0,
    "wadzik": 0,
    "paterega": 0
}

def is_collision(id1, id2):
    x1, y1 = canvas.coords(id1)
    x2, y2 = canvas.coords(id2)
    bbox1 = canvas.bbox(id1)
    bbox2 = canvas.bbox(id2)

    if not bbox1 or not bbox2:
        return False

    return (
        bbox1[2] > bbox2[0] and
        bbox1[0] < bbox2[2] and
        bbox1[3] > bbox2[1] and
        bbox1[1] < bbox2[3]
    )

def kill_character(character_id, hp_text_id, name):
    canvas.delete(character_id)
    canvas.delete(hp_text_id)
    canvas.create_text(700, 300, text=f"{name} програв!", fill="red", font=("Consolas", 32, "bold"))
    pygame.mixer.music.stop()
    if name == "Патерега":
        victory_sound.play()
    else:
        defeat_sound.play()
    root.after(3000, show_menu)


def attack(attack_script, character_id, target_ids, color, flag_key, direction=1):
    current_time = time.time()
    if attack_flags[flag_key] or (current_time - last_attack_time[flag_key] < 2):
        return

    attack_flags[flag_key] = True
    last_attack_time[flag_key] = current_time

    text = random.choice(attack_script)
    x, y = canvas.coords(character_id)
    attack_text = canvas.create_text(x + 180 * direction, y + 100, text=text, fill=color, font=("Consolas", 14, "bold"))
    animate_attack(attack_text, target_ids, color, direction)

    root.after(1000, lambda: set_attack_inactive(flag_key))

def show_menu():
    
    global canvas, ihor_hp, wadzik_hp, paterega_hp
    ihor_hp = 4
    wadzik_hp = 4
    paterega_hp = 15
    for widget in root.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(root, width=1410, height=600)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_menu, anchor="nw")

    play_button = tk.Button(root, text="Грати", command=start_game, **button_style)
    exit_button = tk.Button(root, text="Вихід", command=exit_game, **button_style)

    for button in [play_button, exit_button]:
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    center_x = 1410 // 2
    canvas.create_window(center_x, 250, window=play_button)
    canvas.create_window(center_x, 320, window=exit_button)


def set_attack_inactive(flag_key):
    attack_flags[flag_key] = False

def handle_damage(target_id):
    global ihor_hp, wadzik_hp, paterega_hp, ihor_id, wadzik_id, paterega_id
    hit_sound.play()
    if target_id == ihor_id:
        ihor_hp -= 1
        canvas.itemconfig(ihor_hp_text, text=f"🖤: {ihor_hp}")
        if ihor_hp <= 0:
            kill_character(ihor_id, ihor_hp_text, "Ігор")
            ihor_id = None
    elif target_id == wadzik_id:
        wadzik_hp -= 1
        canvas.itemconfig(wadzik_hp_text, text=f"🖤: {wadzik_hp}")
        if wadzik_hp <= 0:
            kill_character(wadzik_id, wadzik_hp_text, "Вадим")
            wadzik_id = None
    elif target_id == paterega_id:
        paterega_hp -= 1
        canvas.itemconfig(paterega_hp_text, text=f"🖤: {paterega_hp}")
        if paterega_hp <= 0:
            kill_character(paterega_id, paterega_hp_text, "Патерега")
            paterega_id = None


def animate_attack(text_id, target_ids, color, direction):
    def move():
        nonlocal text_id
        try:
            x, y = canvas.coords(text_id)
        except:
            return

        for target_id in target_ids:
            try:
                tx, ty = canvas.coords(target_id)
            except:
                continue

            hitbox_w, hitbox_h = 150, 150 

            
            if abs(x - tx) < hitbox_w and abs(y - ty) < hitbox_h:
                handle_damage(target_id)
                canvas.delete(text_id)
                return
        
        
        if 0 < x < 1410:
            canvas.move(text_id, direction * 6, 0)
            root.after(30, move)
        else:
            canvas.delete(text_id)
    
    move()


def start_game():
    global canvas
    for widget in root.winfo_children():
        widget.destroy()
    pygame.mixer.music.load(bg_music)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    # bg = Image.open("./img/background.png").resize((1410, 600), Image.Resampling.LANCZOS)
    # bg_image = ImageTk.PhotoImage(bg)
    # root.bg_image = bg_image

    canvas = tk.Canvas(root, width=1410, height=600)
    canvas.pack(fill="both", expand=True)
    # canvas.create_image(0, 0, image=bg_image, anchor="nw")

    create_characters()
    update_positions() 

def create_characters():
    global ihor_id, wadzik_id, paterega_id
    global ihor_texture, wadzik_texture, paterega_texture
    global ihor_hp_text, wadzik_hp_text, paterega_hp_text

    ihor_img = Image.open("img/IgorPlayer.png").resize((170, 200), Image.Resampling.LANCZOS)
    ihor_texture = ImageTk.PhotoImage(ihor_img)
    ihor_id = canvas.create_image(50, 300, anchor="nw", image=ihor_texture)

    wadzik_img = Image.open("img/WadikPlayer.png").resize((300, 200), Image.Resampling.LANCZOS)
    wadzik_texture = ImageTk.PhotoImage(wadzik_img)
    wadzik_id = canvas.create_image(50, 100, anchor="nw", image=wadzik_texture)

    paterega_img = Image.open("img/Paterega.png").resize((500, 300), Image.Resampling.LANCZOS)
    paterega_texture = ImageTk.PhotoImage(paterega_img)
    paterega_id = canvas.create_image(910, 290, anchor="nw", image=paterega_texture)

    ihor_hp_text = canvas.create_text(110, 280, text=f"🖤: {ihor_hp}", fill="red", font=("Consolas", 16, "bold"))
    wadzik_hp_text = canvas.create_text(200, 80, text=f"🖤: {wadzik_hp}", fill="blue", font=("Consolas", 16, "bold"))
    paterega_hp_text = canvas.create_text(1160 - 10, 270, text=f"🖤: {paterega_hp}", fill="green", font=("Consolas", 16, "bold"))

def update_positions():
    global paterega_direction, ihor_hp, wadzik_hp, last_hit_time_ihor, last_hit_time_wadzik, ihor_id, wadzik_id
    now = time.time() * 1000
    if not canvas: return  

    keys = pressed_keys.copy()
# wadzik move
    if ihor_id and wadzik_id:
        if 'Left' in keys:
            canvas.move(wadzik_id, -10, 0)
            canvas.move(wadzik_hp_text, -10, 0)
        if 'Right' in keys:
            canvas.move(wadzik_id, 10, 0)
            canvas.move(wadzik_hp_text, 10, 0)
        if 'Up' in keys:
            canvas.move(wadzik_id, 0, -10)
            canvas.move(wadzik_hp_text, 0, -10)
        if 'Down' in keys:
            canvas.move(wadzik_id, 0, 10)
            canvas.move(wadzik_hp_text, 0, 10)
        if 'Control_R' in keys:
            attack(Wadzik_attack, wadzik_id, [paterega_id], "blue", "wadzik")
# ihor move
        if 'a' in keys: 
            print("sf")
            canvas.move(ihor_id, -10, 0)
            canvas.move(ihor_hp_text, -10, 0)
        if 'd' in keys:
            canvas.move(ihor_id, 10, 0)
            canvas.move(ihor_hp_text, 10, 0)
        if 'w' in keys:
            canvas.move(ihor_id, 0, -10)
            canvas.move(ihor_hp_text, 0, -10)
        if 's' in keys:
            canvas.move(ihor_id, 0, 10)
            canvas.move(ihor_hp_text, 0, 10)
        if 'q' in keys:
            attack(Ihor_attack, ihor_id, [paterega_id], "red", "ihor")
    # Paterega move
    if paterega_id:
        canvas_width = canvas.winfo_width()
        paterega_width = 500
        min_x = canvas_width - 650 - 100 
        max_x = canvas_width - 100

        x, _ = canvas.coords(paterega_id)
        if x <= min_x:
            paterega_direction = 1
        elif x >= max_x:
            paterega_direction = -1
        canvas.move(paterega_id, paterega_direction * 3, 0)
        canvas.move(paterega_hp_text, paterega_direction * 3, 0)
        global last_paterega_attack
        current_time = time.time()
        if current_time - last_paterega_attack > 4.5:
            attack(Paterega_attack, paterega_id, [ihor_id, wadzik_id], "green", "paterega", -1)
            last_paterega_attack = current_time


    if is_collision(ihor_id, paterega_id) and now - last_hit_time_ihor > damage_cooldown:
        ihor_hp -= 1
        last_hit_time_ihor = now
        handle_damage(ihor_id)
        hit_sound.play()


    if is_collision(wadzik_id, paterega_id) and now - last_hit_time_wadzik > damage_cooldown:
        wadzik_hp -= 1
        last_hit_time_wadzik = now
        handle_damage(wadzik_id)
        hit_sound.play()

        
    if ihor_id is None or wadzik_id is None:
        canvas.create_text(700, 350, text="Патерега переміг!", fill="green", font=("Consolas", 28, "bold"))
        
        root.after(3000, show_menu)
        return

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
