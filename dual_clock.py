
import tkinter as tk
from tkinter import ttk
import math
from datetime import datetime

class DualClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Digital & Analogue Clock")
        self.root.geometry("460x560")
        self.root.minsize(380, 480)
        self.dark = True

        self.style = ttk.Style(self.root)
        self._apply_theme()

        # Top frame for digital clock and controls
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        self.digital_var = tk.StringVar(value="--:--:--")
        self.date_var = tk.StringVar(value="----- --, ----")

        self.digital_label = ttk.Label(top, textvariable=self.digital_var, font=("Segoe UI", 28, "bold"))
        self.digital_label.pack(anchor="center")

        self.date_label = ttk.Label(top, textvariable=self.date_var, font=("Segoe UI", 12))
        self.date_label.pack(anchor="center", pady=(4, 8))

        controls = ttk.Frame(top)
        controls.pack(fill="x", pady=(2, 6))

        self.format_24h = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls, variable=self.format_24h, text="24‑hour").pack(side="left")

        ttk.Button(controls, text="Toggle theme", command=self.toggle_theme).pack(side="right")

        # Canvas for analogue clock
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.bind("<Configure>", self._on_resize) # type: ignore

        # precompute face items
        self.face_items = []
        self.center = (0, 0)
        self.radius = 0

        self._draw_face()  # initial face
        self._tick()       # start updates

    # ---------- Theme ----------
    def _apply_theme(self):
        if self.dark:
            bg = "#0f172a"   # slate-900
            fg = "#e2e8f0"   # slate-200
            accent = "#38bdf8"  # sky-400
        else:
            bg = "#f8fafc"   # slate-50
            fg = "#0f172a"   # slate-900
            accent = "#2563eb"  # blue-600

        self.root.configure(bg=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.configure("TButton", background=bg, foreground=fg)
        self.bg = bg
        self.fg = fg
        self.accent = accent

        # Update canvas background if exists
        if hasattr(self, "canvas"):
            self.canvas.configure(background=bg)

    def toggle_theme(self):
        self.dark = not self.dark
        self._apply_theme()
        self._draw_face(force=True)

    # ---------- Layout helpers ----------
    def _on_resize(self):
        self._draw_face(force=True)

    def _draw_face(self, force=False):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 2 or h <= 2:
            return

        # compute center and radius
        cx, cy = w // 2, h // 2 + 10
        r = int(min(w, h) * 0.38)

        if (cx, cy, r) == (*self.center, self.radius) and not force:
            return

        self.center = (cx, cy)
        self.radius = r

        self.canvas.delete("face")
        # outer circle
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, width=3, outline=self.accent, fill=self.bg, tags="face")

        # minute ticks
        for i in range(60):
            angle = math.radians(i * 6)  # 360/60
            inner = r - (14 if i % 5 == 0 else 6)
            x1 = cx + (inner) * math.sin(angle)
            y1 = cy - (inner) * math.cos(angle)
            x2 = cx + (r - 2) * math.sin(angle)
            y2 = cy - (r - 2) * math.cos(angle)
            width = 3 if i % 5 == 0 else 1
            color = self.fg if i % 5 != 0 else self.accent
            self.canvas.create_line(x1, y1, x2, y2, width=width, fill=color, tags="face")

        # numerals 1..12
        for hr in range(1, 13):
            angle = math.radians(hr * 30)  # 360/12
            nr = r - 32
            x = cx + nr * math.sin(angle)
            y = cy - nr * math.cos(angle)
            self.canvas.create_text(x, y, text=str(hr), fill=self.fg, font=("Segoe UI", 14, "bold"), tags="face")

        # center cap
        self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=self.accent, outline="", tags="face")

    # ---------- Clock update ----------
    def _tick(self):
        now = datetime.now()

        # Digital
        if self.format_24h.get():
            self.digital_var.set(now.strftime("%H:%M:%S"))
        else:
            self.digital_var.set(now.strftime("%I:%M:%S %p"))
        self.date_var.set(now.strftime("%A, %d %B %Y"))

        # Analogue
        self._draw_hands(now)

        # schedule next update (every 200 ms for smoother seconds)
        self.root.after(200, self._tick)

    def _draw_hands(self, now):
        self.canvas.delete("hands")
        cx, cy = self.center
        r = self.radius

        # Angles
        sec = now.second + now.microsecond / 1_000_000.0
        minute = now.minute + sec / 60.0
        hour = (now.hour % 12) + minute / 60.0

        angle_s = math.radians(sec * 6)        # 360/60
        angle_m = math.radians(minute * 6)
        angle_h = math.radians(hour * 30)      # 360/12

        # Hand lengths
        len_h = r * 0.5
        len_m = r * 0.72
        len_s = r * 0.82

        # Back counterweights
        back = r * 0.15

        # Hour hand
        xh = cx + len_h * math.sin(angle_h)
        yh = cy - len_h * math.cos(angle_h)
        xhb = cx - back * math.sin(angle_h)
        yhb = cy + back * math.cos(angle_h)
        self.canvas.create_line(xhb, yhb, xh, yh, width=5, fill=self.fg, capstyle="round", tags="hands")

        # Minute hand
        xm = cx + len_m * math.sin(angle_m)
        ym = cy - len_m * math.cos(angle_m)
        xmb = cx - (back * 0.7) * math.sin(angle_m)
        ymb = cy + (back * 0.7) * math.cos(angle_m)
        self.canvas.create_line(xmb, ymb, xm, ym, width=3, fill=self.fg, capstyle="round", tags="hands")

        # Second hand
        xs = cx + len_s * math.sin(angle_s)
        ys = cy - len_s * math.cos(angle_s)
        xsb = cx - (back * 0.9) * math.sin(angle_s)
        ysb = cy + (back * 0.9) * math.cos(angle_s)
        self.canvas.create_line(xsb, ysb, xs, ys, width=1, fill=self.accent, capstyle="round", tags="hands")

        # Center cap on top
        self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=self.accent, outline="", tags="hands")

def main():
    root = tk.Tk()
    DualClockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
