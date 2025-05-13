import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import pygame
pygame.mixer.init()

bg_music = "sounds/MainTheme.wav"
hit_sound = pygame.mixer.Sound("sounds/Hit.wav")
victory1_sound = pygame.mixer.Sound("sounds/victory1.mp3")
victory2_sound = pygame.mixer.Sound("sounds/victory2.mp3")
defeat_sound = pygame.mixer.Sound("sounds/OurDeath.wav")

root = tk.Tk()
root.title("Здача лабки Game")
root.geometry("1410x600+0+0")

pressed_keys = set()
teacher_direction = -1

# global variables
last_hit_time_player1 = 0
last_hit_time_player2 = 0
damage_cooldown = 1000
last_teacher_attack = 0
canvas = None
player1_id = None
player2_id = None
teacher_id = None
player1_hp = 4
player2_hp = 4
teacher_hp = 15
player1_hp_text = None
player2_hp_text = None
teacher_hp_text = None
player1_texture = None
player2_texture = None
teacher_texture = None
player1_attack = [
"Ми написали нейронку з допомогою нейронки.",
"Наша прога - інтроверт, вона нормальна, просто Вас соромиться.",
"Ми підключили AI",
"Це не баг, це фіча",
"ШІ хвалить наш код",
"Цей раз з нами був Git"
]

player2_attack = [
"Я скинув Кані Весту, він оцінив.",
"Наша прога знає ваше місцезнаходження.",
"Я попрошу Кані Веста автограф для Вас.",
"Цей код писався під бутилку пива і треки Кані Веста.",
"Наша нейронка знає багато геометричних і ультраправих фігур",
]

teacher_attack = [
"Вадим, Ви фанат Кані Веста.",
"Хлопці, ви вайб-кодери.",
"Інтерфейс не user-friendly.",
"Ви спортили Захара і підсадили його на Кані Веста.",
"Немає обробника помилок і екрана завантаження.",
"Сьогодні 2, на наступний раз тоже 2",
"Я дав ГПТ на оцінку ваш код а він сказав шо це він його написав",
]
attack_flags = {
    "player1": False,
    "player2": False,
    "teacher": False
}
last_attack_time = {
    "player1": 0,
    "player2": 0,
    "teacher": 0
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
    pygame.mixer.music.stop()
    if name == "Патерега":
        canvas.create_text(700, 300, text=f"{name} Програв! Так тримати ставлю 4, але можете краще", fill="red", font=("Consolas", 32, "bold"))
        victory1_sound.play()
        victory2_sound.play()
    else:
        canvas.create_text(700, 300, text=f"{name} Програв!", fill="red", font=("Consolas", 32, "bold"))
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
    
    global canvas, player1_hp, player2_hp, teacher_hp
    player1_hp = 4
    player2_hp = 4
    teacher_hp = 15
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
    global player1_hp, player2_hp, teacher_hp, player1_id, player2_id, teacher_id
    hit_sound.play()
    if target_id == player1_id:
        player1_hp -= 1
        canvas.itemconfig(player1_hp_text, text=f"🖤: {player1_hp}")
        if player1_hp <= 0:
            kill_character(player1_id, player1_hp_text, "Ігор")
            player1_id = None
    elif target_id == player2_id:
        player2_hp -= 1
        canvas.itemconfig(player2_hp_text, text=f"🖤: {player2_hp}")
        if player2_hp <= 0:
            kill_character(player2_id, player2_hp_text, "Вадим")
            player2_id = None
    elif target_id == teacher_id:
        teacher_hp -= 1
        canvas.itemconfig(teacher_hp_text, text=f"🖤: {teacher_hp}")
        if teacher_hp <= 0:
            kill_character(teacher_id, teacher_hp_text, "Патерега")
            teacher_id = None


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
    global player1_id, player2_id, teacher_id
    global player1_texture, player2_texture, teacher_texture
    global player1_hp_text, player2_hp_text, teacher_hp_text

    player1_img = Image.open("img/Player1.png").resize((170, 200), Image.Resampling.LANCZOS)
    player1_texture = ImageTk.PhotoImage(player1_img)
    player1_id = canvas.create_image(50, 300, anchor="nw", image=player1_texture)

    player2_img = Image.open("img/Player2.png").resize((300, 200), Image.Resampling.LANCZOS)
    player2_texture = ImageTk.PhotoImage(player2_img)
    player2_id = canvas.create_image(50, 100, anchor="nw", image=player2_texture)

    teacher_img = Image.open("img/Teacher.png").resize((500, 300), Image.Resampling.LANCZOS)
    teacher_texture = ImageTk.PhotoImage(teacher_img)
    teacher_id = canvas.create_image(910, 290, anchor="nw", image=teacher_texture)

    player1_hp_text = canvas.create_text(110, 280, text=f"🖤: {player1_hp}", fill="red", font=("Consolas", 16, "bold"))
    player2_hp_text = canvas.create_text(200, 80, text=f"🖤: {player2_hp}", fill="blue", font=("Consolas", 16, "bold"))
    teacher_hp_text = canvas.create_text(1160 - 10, 270, text=f"🖤: {teacher_hp}", fill="green", font=("Consolas", 16, "bold"))

def update_positions():
    global teacher_direction, player1_hp, player2_hp, last_hit_time_player1, last_hit_time_player2, player1_id, player2_id
    now = time.time() * 1000
    if not canvas: return  

    keys = pressed_keys.copy()
# player2 move
    if player1_id and player2_id:
        if 'Left' in keys:
            canvas.move(player2_id, -10, 0)
            canvas.move(player2_hp_text, -10, 0)
        if 'Right' in keys:
            canvas.move(player2_id, 10, 0)
            canvas.move(player2_hp_text, 10, 0)
        if 'Up' in keys:
            canvas.move(player2_id, 0, -10)
            canvas.move(player2_hp_text, 0, -10)
        if 'Down' in keys:
            canvas.move(player2_id, 0, 10)
            canvas.move(player2_hp_text, 0, 10)
        if 'Control_R' in keys:
            attack(player2_attack, player2_id, [teacher_id], "blue", "player2")
# player1 move
        if 'a' in keys: 
            print("sf")
            canvas.move(player1_id, -10, 0)
            canvas.move(player1_hp_text, -10, 0)
        if 'd' in keys:
            canvas.move(player1_id, 10, 0)
            canvas.move(player1_hp_text, 10, 0)
        if 'w' in keys:
            canvas.move(player1_id, 0, -10)
            canvas.move(player1_hp_text, 0, -10)
        if 's' in keys:
            canvas.move(player1_id, 0, 10)
            canvas.move(player1_hp_text, 0, 10)
        if 'q' in keys:
            attack(player1_attack, player1_id, [teacher_id], "red", "player1")
    # teacher move
    if teacher_id:
        canvas_width = canvas.winfo_width()
        teacher_width = 500
        min_x = canvas_width - 650 - 100 
        max_x = canvas_width - 100

        x, _ = canvas.coords(teacher_id)
        if x <= min_x:
            teacher_direction = 1
        elif x >= max_x:
            teacher_direction = -1
        canvas.move(teacher_id, teacher_direction * 3, 0)
        canvas.move(teacher_hp_text, teacher_direction * 3, 0)
        global last_teacher_attack
        current_time = time.time()
        if current_time - last_teacher_attack > 4.5:
            attack(teacher_attack, teacher_id, [player1_id, player2_id], "green", "teacher", -1)
            last_teacher_attack = current_time


    if is_collision(player1_id, teacher_id) and now - last_hit_time_player1 > damage_cooldown:
        player1_hp -= 1
        last_hit_time_player1 = now
        handle_damage(player1_id)
        hit_sound.play()


    if is_collision(player2_id, teacher_id) and now - last_hit_time_player2 > damage_cooldown:
        player2_hp -= 1
        last_hit_time_player2 = now
        handle_damage(player2_id)
        hit_sound.play()

        
    if player1_id is None or player2_id is None:
        canvas.create_text(700, 350, text="Патерега переміг: Не приймаю таке хлопці!", fill="green", font=("Consolas", 28, "bold"))
        
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