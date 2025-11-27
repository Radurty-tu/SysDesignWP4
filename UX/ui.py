import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path


class LugToolUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Lug Tools")
        self.geometry("1200x700")

        # Root frame with 3 columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)
        self.rowconfigure(0, weight=1)

        # Left panel: file select + run
        self._build_left_panel()

        # Middle panel: control panel
        self._build_middle_panel()

        # Right panel: graph area
        self._build_right_panel()

    def _build_left_panel(self):
        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")

        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Calculation file").grid(
            row=0, column=0, sticky="w"
        )

        # Dropdown with files from ./calculations
        self.file_var = tk.StringVar()

        calc_dir = Path(__file__).resolve().parent / "calculations"
        if calc_dir.is_dir():
            files = sorted(
                f.name for f in calc_dir.iterdir()
                if f.is_file() and f.suffix == ".py"
            )
        else:
            files = []

        self.file_combo = ttk.Combobox(
            left, textvariable=self.file_var,
            values=files, state="readonly"
        )
        self.file_combo.grid(row=1, column=0, sticky="ew", pady=(5, 10))
        if files:
            self.file_combo.current(0)

        # Run button, no real functionality yet
        run_button = ttk.Button(
            left, text="Run selected",
            command=self._on_run_clicked
        )
        run_button.grid(row=2, column=0, sticky="ew")

    def _build_middle_panel(self):
        mid = ttk.LabelFrame(self, text="Control panel", padding=10)
        mid.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        mid.columnconfigure(0, weight=1)

        # Placeholder widgets for now
        ttk.Label(mid, text="Input configuration").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(mid).grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(mid, text="Output file").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Entry(mid).grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Room for future buttons, toggles etc
        ttk.Button(mid, text="Future option 1").grid(
            row=4, column=0, sticky="ew", pady=(5, 0)
        )
        ttk.Button(mid, text="Future option 2").grid(
            row=5, column=0, sticky="ew", pady=(5, 0)
        )

    def _build_right_panel(self):
        right = ttk.LabelFrame(self, text="Graph area", padding=10)
        right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        # Placeholder canvas for future matplotlib embedding or custom drawing
        placeholder = tk.Canvas(right, bg="#222222")
        placeholder.grid(row=0, column=0, sticky="nsew")

        placeholder.create_text(
            10, 10,
            anchor="nw",
            fill="white",
            text="Graphs will go here"
        )

    def _on_run_clicked(self):
        # Placeholder for now
        selected = self.file_var.get()
        print(f"Run clicked. Selected file: {selected}")


if __name__ == "__main__":
    app = LugToolUI()
    app.mainloop()
