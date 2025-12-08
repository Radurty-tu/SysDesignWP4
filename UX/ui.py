import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import yaml
import ast
import importlib



class LugToolUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Lug Tools")
        self.geometry("1200x700")

        self.project_root = Path(__file__).resolve().parent.parent

        # will hold dicts loaded from YAML
        self.config_data = {}         # the raw dict from YAML
        self.config_values = {}       # config section (actual values)
        self.config_descriptions = {} # descriptions section
        self.param_vars = {}

        # layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)
        self.rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_middle_panel()
        self._build_right_panel()

    # --- left panel unchanged, omitted for brevity ---
    def _build_left_panel(self):
        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")

        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Calculation file").grid(
            row=0, column=0, sticky="w"
        )

        self.file_var = tk.StringVar()
        calc_dir = self.project_root / "Calculations"

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

        run_button = ttk.Button(
            left, text="Run selected",
            command=self._on_run_clicked
        )
        run_button.grid(row=2, column=0, sticky="ew")

    # --- middle panel with config editor ---
    def _build_middle_panel(self):
        mid = ttk.LabelFrame(self, text="Control panel", padding=10)
        mid.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        mid.columnconfigure(0, weight=1)
        mid.rowconfigure(2, weight=1)  # scrollable area

        # config file selector
        ttk.Label(mid, text="Config file (Data)").grid(
            row=0, column=0, sticky="w"
        )

        self.config_file_var = tk.StringVar()
        self.data_dir = self.project_root / "Data"

        if self.data_dir.is_dir():
            config_files = sorted(
                f.name for f in self.data_dir.iterdir()
                if f.is_file() and f.suffix.lower() in {".yaml", ".yml"}
            )
        else:
            config_files = []

        self.config_combo = ttk.Combobox(
            mid,
            textvariable=self.config_file_var,
            values=config_files,
            state="readonly",
        )
        self.config_combo.grid(row=1, column=0, sticky="ew", pady=(5, 10))
        self.config_combo.bind("<<ComboboxSelected>>", self._on_config_file_selected)

        # scrollable parameter area
        container = ttk.Frame(mid)
        container.grid(row=2, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self.param_canvas = tk.Canvas(container, highlightthickness=0)
        self.param_canvas.grid(row=0, column=0, sticky="nsew")

        vscroll = ttk.Scrollbar(
            container, orient="vertical", command=self.param_canvas.yview
        )
        vscroll.grid(row=0, column=1, sticky="ns")

        self.param_canvas.configure(yscrollcommand=vscroll.set)

        self.param_frame = ttk.Frame(self.param_canvas)
        self.param_canvas.create_window((0, 0), window=self.param_frame, anchor="nw")

        def _on_frame_configure(event):
            self.param_canvas.configure(scrollregion=self.param_canvas.bbox("all"))

        self.param_frame.bind("<Configure>", _on_frame_configure)

        def _on_mousewheel(event):
            self.param_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.param_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # save button
        self.save_button = ttk.Button(
            mid, text="Save config", command=self._on_save_clicked
        )
        self.save_button.grid(row=3, column=0, sticky="ew", pady=(5, 0))

        # load first config automatically if present
        if config_files:
            self.config_combo.current(0)
            self._on_config_file_selected()


    def _on_config_file_selected(self, event=None):
        filename = self.config_file_var.get()
        if not filename:
            return

        path = self.data_dir / filename
        if not path.is_file():
            return

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.yaml_data = data
        self.config_descriptions = data.get("descriptions", {}) or {}

        self._populate_param_frame()

    def _populate_param_frame(self):
        for child in self.param_frame.winfo_children():
            child.destroy()

        self.param_vars = {}
        self.param_index = {}  # "section.key" -> (section, key)

        ttk.Label(self.param_frame, text="Name", font=("", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 5), pady=(0, 5)
        )
        ttk.Label(self.param_frame, text="Value", font=("", 9, "bold")).grid(
            row=0, column=1, sticky="w", padx=(0, 5), pady=(0, 5)
        )
        ttk.Label(self.param_frame, text="Description", font=("", 9, "bold")).grid(
            row=0, column=2, sticky="w", padx=(0, 5), pady=(0, 5)
        )

        self.param_frame.columnconfigure(0, weight=1)
        self.param_frame.columnconfigure(1, weight=1)
        self.param_frame.columnconfigure(2, weight=2)

        row = 1
        for section, mapping in (self.yaml_data or {}).items():
            if not isinstance(mapping, dict):
                continue
            if section == "descriptions":
                continue

            ttk.Label(
                self.param_frame, text=section, font=("", 9, "bold")
            ).grid(row=row, column=0, sticky="w", padx=(0, 5), pady=(4, 2))
            row += 1

            for key, value in mapping.items():
                fullname = f"{section}.{key}"

                desc = (
                    self.config_descriptions.get(fullname, "")
                    or self.config_descriptions.get(key, "")
                )

                text_value = repr(value)
                var = tk.StringVar(value=text_value)

                self.param_vars[fullname] = var
                self.param_index[fullname] = (section, key)

                ttk.Label(self.param_frame, text=key).grid(
                    row=row, column=0, sticky="w", padx=(10, 5), pady=2
                )

                entry = ttk.Entry(self.param_frame, textvariable=var)
                entry.grid(
                    row=row, column=1, sticky="ew", padx=(0, 5), pady=2
                )

                ttk.Label(
                    self.param_frame,
                    text=desc,
                    wraplength=300,
                    justify="left",
                ).grid(
                    row=row, column=2, sticky="w", padx=(0, 5), pady=2
                )

                row += 1

    def get_current_sections(self):
        """
        Return all editable sections as a nested dict:
        {section: {key: value, ...}, ...}
        """
        result = {}
        for fullname, var in self.param_vars.items():
            section, key = self.param_index[fullname]
            text = var.get()
            try:
                value = ast.literal_eval(text)
            except Exception:
                value = text
            if section not in result:
                result[section] = {}
            result[section][key] = value
        return result


    def get_current_config_section(self):
        """
        Return the edited config section as a dict, preserving list types if possible.
        Uses ast.literal_eval on each entry; falls back to string if parsing fails.
        """
        result = {}
        for name, var in self.param_vars.items():
            text = var.get()
            try:
                value = ast.literal_eval(text)
            except Exception:
                value = text
            result[name] = value
        return result
    def _on_save_clicked(self):
        filename = self.config_file_var.get()
        if not filename:
            return
    
        path = self.data_dir / filename
        if not path.is_file():
            return
    
        # current values from UI
        sections = self.get_current_sections()
    
        # keep descriptions from original YAML
        original = self.yaml_data or {}
        descriptions = original.get("descriptions", {})
    
        data_out = dict(sections)
        if descriptions:
            data_out["descriptions"] = descriptions
    
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data_out, f, sort_keys=False)


    # --- right panel unchanged ---
    def _build_right_panel(self):
        right = ttk.LabelFrame(self, text="Status", padding=10)
        right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=0)
        right.rowconfigure(1, weight=1)

        # status text
        self.status_var = tk.StringVar(value="Idle.")
        self.status_label = ttk.Label(right, textvariable=self.status_var, anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # indeterminate progress bar
        self.progress = ttk.Progressbar(
            right,
            mode="indeterminate",
            orient="horizontal"
        )
        self.progress.grid(row=1, column=0, sticky="ew")


    def _on_run_clicked(self):
        selected = self.file_var.get()
        if not selected:
            self.status_var.set("No calculation file selected.")
            return

        module_name = selected.removesuffix(".py")

        # import module
        try:
            mod = importlib.import_module(f"Calculations.{module_name}")
        except ImportError as e:
            self.status_var.set(f"Import error: {e}")
            return

        # get sections from YAML editor
        sections = self.get_current_sections()
        config   = sections.get("config",   {})
        geometry = sections.get("geometry", {})
        loads    = sections.get("loads",    {})

        # start status + progress
        self.status_var.set(f"Running {module_name}...")
        self.progress.start(10)   # 10 ms step
        self.update_idletasks()

        try:
            npz_path = mod.run(config, geometry, loads)
        except Exception as e:
            self.progress.stop()
            self.status_var.set(f"Error in {module_name}.run: {e}")
            return

        # stop progress and report success
        self.progress.stop()
        self.status_var.set(f"Finished {module_name}. Output: {npz_path}")


#[]

if __name__ == "__main__":
    app = LugToolUI()
    app.mainloop()
