import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

APP_NAME = "AstraVideo Studio"
VERSION = "0.1.0"


def build_plan(prompt: str):
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Inserisci prima un prompt.")
    scenes = []
    for i in range(60):
        start = i * 10
        end = start + 10
        scenes.append({
            "scene": i + 1,
            "start": start,
            "end": end,
            "description": f"Scena {i+1}: {prompt}"
        })
    return scenes


class AstraVideoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("980x700")
        self.minsize(800, 560)

        main = ttk.Frame(self, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text=APP_NAME, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(main, text="Planner video lungo: 10 minuti = 60 scene da 10 secondi").pack(anchor="w", pady=(2, 14))

        ttk.Label(main, text="Prompt video").pack(anchor="w")
        self.prompt = tk.Text(main, height=6, wrap="word", font=("Segoe UI", 11))
        self.prompt.pack(fill="x", pady=(4, 12))

        buttons = ttk.Frame(main)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Crea piano 10 minuti", command=self.generate_plan).pack(side="left")
        ttk.Button(buttons, text="Esporta piano TXT", command=self.export_plan).pack(side="left", padx=8)
        ttk.Button(buttons, text="Pulisci", command=self.clear_all).pack(side="left")

        self.status = ttk.Label(main, text="Pronto")
        self.status.pack(anchor="w", pady=(12, 4))

        self.output = tk.Text(main, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True)
        self.output.insert("1.0", "AstraVideo Studio è pronto.\nInserisci un prompt e crea il piano da 60 scene.\n")

        self.scenes = []

    def generate_plan(self):
        try:
            self.scenes = build_plan(self.prompt.get("1.0", "end"))
        except ValueError as e:
            messagebox.showwarning(APP_NAME, str(e))
            return

        self.output.delete("1.0", "end")
        self.output.insert("end", f"Progetto creato: 600 secondi / {len(self.scenes)} scene\n\n")
        for s in self.scenes:
            self.output.insert("end", f"Scena {s['scene']:02d}  [{s['start']:03d}s-{s['end']:03d}s]\n")
        self.status.config(text="Piano creato: 60 scene")

    def export_plan(self):
        if not self.scenes:
            messagebox.showinfo(APP_NAME, "Prima crea il piano.")
            return
        path = filedialog.asksaveasfilename(
            title="Salva piano AstraVideo",
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt")],
            initialfile="AstraVideo_Piano_10min.txt",
        )
        if not path:
            return
        lines = [f"{APP_NAME} {VERSION}", "Durata: 600 secondi", "Scene: 60", ""]
        lines.extend([f"Scena {s['scene']:02d}: {s['start']}s-{s['end']}s" for s in self.scenes])
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        self.status.config(text=f"Esportato: {path}")

    def clear_all(self):
        self.prompt.delete("1.0", "end")
        self.output.delete("1.0", "end")
        self.scenes = []
        self.status.config(text="Pronto")


if __name__ == "__main__":
    AstraVideoApp().mainloop()
