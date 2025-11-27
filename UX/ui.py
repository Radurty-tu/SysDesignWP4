# calculations.py
def compute(value):
    return value * 2  # placeholder

# ui.py
import tkinter as tk
from tkinter import ttk

def run_calculation():
    try:
        val = float(input_var.get())
    except ValueError:
        result_var.set("Invalid input")
        return

    result = compute(val)
    result_var.set(f"Result: {result}")

def main():
    global input_var, result_var

    root = tk.Tk()
    root.title("My Tool")

    # make it big, almost fullscreen
    # for fullscreen: root.attributes("-fullscreen", True)
    root.state("zoomed")  # Windows maximized, ignore if it errors on Linux

    input_var = tk.StringVar()
    result_var = tk.StringVar(value="Result:")

    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    ttk.Label(main_frame, text="Value").grid(row=0, column=0, sticky="w")
    ttk.Entry(main_frame, textvariable=input_var, width=20).grid(row=0, column=1, sticky="w")

    ttk.Button(main_frame, text="Run", command=run_calculation).grid(row=1, column=0, columnspan=2, pady=(10, 0))

    ttk.Label(main_frame, textvariable=result_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))

    root.mainloop()

if __name__ == "__main__":
    main()
