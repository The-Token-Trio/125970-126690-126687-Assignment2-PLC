from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from components.pipeline import format_tokens, run_pipeline


DEFAULT_SOURCE = """def add(a, b) {
    result = a + b;
    print(result);
    return result;
}

x = 10;
y = 20.5;
flag = true;
name = \"plc\";

if (x != 0) {
    print(name);
} else {
    print(x);
}

while (flag != false) {
    x = x - 1;
    flag = false;
}

z = add(x, y);
print(z);
"""


class LanguageWorkbench:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Programming Language Project")
        self.root.geometry("1200x760")
        self.current_file: Path | None = None

        self._build_layout()
        self.source_text.insert("1.0", DEFAULT_SOURCE)

    def _build_layout(self) -> None:
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="Open Script", command=self._open_script).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Run", command=self._run_source).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Clear Output", command=self._clear_output).pack(side=tk.LEFT, padx=(8, 0))

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(toolbar, textvariable=self.status_var).pack(side=tk.RIGHT)

        body = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        left_panel = ttk.Frame(body, padding=8)
        right_panel = ttk.Frame(body, padding=8)
        body.add(left_panel, weight=1)
        body.add(right_panel, weight=1)

        ttk.Label(left_panel, text="Input Script").pack(anchor=tk.W)
        self.source_text = tk.Text(left_panel, wrap=tk.NONE, font=("Consolas", 11))
        self.source_text.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.output_text = self._make_output_tab(notebook, "Execution Output")
        self.tokens_text = self._make_output_tab(notebook, "Tokens")
        self.ast_text = self._make_output_tab(notebook, "AST")
        self.types_text = self._make_output_tab(notebook, "Type Table")

    def _make_output_tab(self, notebook: ttk.Notebook, title: str) -> tk.Text:
        frame = ttk.Frame(notebook, padding=8)
        notebook.add(frame, text=title)
        text = tk.Text(frame, wrap=tk.NONE, font=("Consolas", 11), state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    def _open_script(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Open Script File",
            filetypes=[("Text Files", "*.txt *.pl *.src"), ("All Files", "*.*")],
        )
        if not file_path:
            return

        path = Path(file_path)
        self.current_file = path
        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", path.read_text(encoding="utf-8"))
        self.status_var.set(f"Loaded {path.name}")

    def _run_source(self) -> None:
        source = self.source_text.get("1.0", tk.END)
        try:
            result = run_pipeline(source)
        except Exception as error:
            self._write_text(self.output_text, str(error))
            self.status_var.set("Run failed")
            messagebox.showerror("Execution Error", str(error))
            return

        self._write_text(self.output_text, "\n".join(result.outputs) if result.outputs else "(no output)")
        self._write_text(self.tokens_text, format_tokens(result.tokens))
        self._write_text(self.ast_text, result.ast_text)
        self._write_text(self.types_text, result.checked_scope.format_table())

        current_label = self.current_file.name if self.current_file is not None else "editor contents"
        self.status_var.set(f"Ran {current_label}")

    def _clear_output(self) -> None:
        self._write_text(self.output_text, "")
        self._write_text(self.tokens_text, "")
        self._write_text(self.ast_text, "")
        self._write_text(self.types_text, "")
        self.status_var.set("Output cleared")

    @staticmethod
    def _write_text(widget: tk.Text, content: str) -> None:
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.config(state=tk.DISABLED)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    LanguageWorkbench().run()