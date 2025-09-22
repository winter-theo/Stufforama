import os, sys, json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

POSITIONS_FILE = "app/positions.json"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")

def update_total(*args):
    total = 0
    for var in entries_vars:
        try:
            val = int(var.get().replace(".", ""))
            total += val
            if var.get() != format_number(val):
                var.set(format_number(val))
        except ValueError:
            pass
    total_label.config(text=f"💰 Total: {format_number(total)}K")

def save_positions():
    positions = []
    for entry in entries:
        info = entry.place_info()
        positions.append({"x": int(info["x"]), "y": int(info["y"])})
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(positions, f, indent=2)
    messagebox.showinfo("Positions", f"Positions sauvegardées dans {POSITIONS_FILE}")

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [(int(p["x"]), int(p["y"])) for p in data]
    return None

def toggle_placement():
    global placement_mode
    placement_mode = not placement_mode
    state = "ACTIVÉ" if placement_mode else "désactivé"
    messagebox.showinfo("Mode placement", f"Mode placement {state}\n- Clique/Glisse un champ pour le déplacer\n- P pour basculer")

def on_press(event, idx):
    if placement_mode:
        event.widget.startX = event.x
        event.widget.startY = event.y

def on_drag(event, idx):
    if placement_mode:
        widget = event.widget
        dx = event.x - widget.startX
        dy = event.y - widget.startY
        new_x = widget.winfo_x() + dx
        new_y = widget.winfo_y() + dy
        widget.place(x=new_x, y=new_y)

# Fenêtre
root = tk.Tk()
root.title("Stufforama")
root.resizable(False, False)

# Image d'inventaire
img_path = resource_path("app/assets/inventaire.png")
if os.path.exists(img_path):
    bg_image = Image.open(img_path)
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas = tk.Canvas(root, width=bg_image.width, height=bg_image.height, highlightthickness=0)
    canvas.pack()
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
else:
    canvas = tk.Canvas(root, width=700, height=500, bg="gray")
    canvas.pack()

# Champs
entries_vars = [tk.StringVar() for _ in range(17)]
entries = []

positions = load_positions()
if positions is None:
    positions = [(50 + (i % 3) * 150, 50 + (i // 3) * 50) for i in range(17)]

for i, (x, y) in enumerate(positions):
    entry = tk.Entry(root, textvariable=entries_vars[i], width=14, justify="center", font=("Consolas", 12))
    entry.place(x=x, y=y)
    entries_vars[i].trace_add("write", update_total)

    entry.bind("<Button-1>", lambda e, idx=i: on_press(e, idx))
    entry.bind("<B1-Motion>", lambda e, idx=i: on_drag(e, idx))

    entries.append(entry)

# Label total
total_label = tk.Label(root, text="Total: 0K", font=("Segoe UI", 18, "bold"), fg="black", bg=canvas["bg"])
total_label.pack(side="bottom", pady=25)

# Menu
menubar = tk.Menu(root)
root.config(menu=menubar)
tools = tk.Menu(menubar, tearoff=0)
tools.add_command(label="Basculer mode placement (P)", command=toggle_placement)
tools.add_command(label="Sauvegarder positions", command=save_positions)
menubar.add_cascade(label="Outils", menu=tools)

root.bind("p", lambda e: toggle_placement())

placement_mode = False

root.mainloop()
