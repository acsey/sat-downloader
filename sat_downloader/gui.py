# -*- coding: utf-8 -*-
"""Simple desktop GUI for downloading CFDI invoices from SAT."""

from __future__ import annotations

import datetime as dt
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import sat_api


def _run_download(
    params: dict,
    prog: ttk.Progressbar,
    info_var: tk.StringVar,
) -> None:
    """Background thread for running the download process."""

    def on_batch(total: int, _current: int) -> None:
        prog.config(maximum=total)
        info_var.set(f"Total paquetes: {total}")

    def on_progress(current: int, total: int) -> None:
        prog["value"] = current
        info_var.set(f"Descargando paquete {current}/{total}")

    try:
        sat_api.download_invoices(
            params["rfc"],
            params["cer"],
            params["key"],
            params["password"],
            params["start_date"],
            params["end_date"],
            batch_callback=on_batch,
            progress_callback=on_progress,
            output_dir=params["output_dir"],
        )
        messagebox.showinfo("Finalizado", "Descarga completada")
    except Exception as exc:  # pylint: disable=broad-except
        messagebox.showerror("Error", str(exc))
    finally:
        prog.stop()


def start_gui() -> None:
    """Launch the Tkinter GUI."""
    root = tk.Tk()
    root.title("SAT Descarga Masiva")

    frm = ttk.Frame(root, padding=10)
    frm.grid()

    # RFC
    ttk.Label(frm, text="RFC:").grid(column=0, row=0, sticky=tk.W)
    rfc_entry = ttk.Entry(frm, width=30)
    rfc_entry.grid(column=1, row=0)

    # Cert and key
    ttk.Label(frm, text="Certificado (.cer):").grid(
        column=0, row=1, sticky=tk.W
    )
    cer_entry = ttk.Entry(frm, width=30)
    cer_entry.grid(column=1, row=1)
    ttk.Button(
        frm,
        text="...",
        command=lambda: cer_entry.insert(0, filedialog.askopenfilename()),
    ).grid(column=2, row=1)

    ttk.Label(frm, text="Llave (.key):").grid(column=0, row=2, sticky=tk.W)
    key_entry = ttk.Entry(frm, width=30)
    key_entry.grid(column=1, row=2)
    ttk.Button(
        frm,
        text="...",
        command=lambda: key_entry.insert(0, filedialog.askopenfilename()),
    ).grid(column=2, row=2)

    ttk.Label(frm, text="Contraseña Key:").grid(column=0, row=3, sticky=tk.W)
    pwd_entry = ttk.Entry(frm, width=30, show="*")
    pwd_entry.grid(column=1, row=3)
    # Dates
    ttk.Label(frm, text="Fecha inicio (YYYY-MM-DD):").grid(
        column=0, row=4, sticky=tk.W
    )
    start_entry = ttk.Entry(frm, width=30)
    start_entry.grid(column=1, row=4)

    ttk.Label(frm, text="Fecha fin (YYYY-MM-DD):").grid(
        column=0, row=5, sticky=tk.W
    )
    end_entry = ttk.Entry(frm, width=30)
    end_entry.grid(column=1, row=5)

    ttk.Label(frm, text="Directorio de salida:").grid(
        column=0, row=6, sticky=tk.W
    )
    out_entry = ttk.Entry(frm, width=30)
    out_entry.grid(column=1, row=6)
    ttk.Button(
        frm,
        text="...",
        command=lambda: out_entry.insert(0, filedialog.askdirectory()),
    ).grid(column=2, row=6)

    prog = ttk.Progressbar(frm, length=200, mode="determinate")
    prog.grid(column=0, row=7, columnspan=3, pady=5)

    info_var = tk.StringVar(value="Esperando...")
    ttk.Label(frm, textvariable=info_var).grid(column=0, row=8, columnspan=3)

    def on_start() -> None:
        params = {
            "rfc": rfc_entry.get().strip(),
            "cer": cer_entry.get().strip(),
            "key": key_entry.get().strip(),
            "password": pwd_entry.get().strip(),
            "start_date": dt.datetime.strptime(
                start_entry.get().strip(), "%Y-%m-%d"
            ).date(),
            "end_date": dt.datetime.strptime(
                end_entry.get().strip(), "%Y-%m-%d"
            ).date(),
            "output_dir": out_entry.get().strip() or "downloads",
        }
        prog.config(value=0)
        threading.Thread(
            target=_run_download, args=(params, prog, info_var), daemon=True
        ).start()

    ttk.Button(frm, text="Iniciar descarga", command=on_start).grid(
        column=0, row=9, columnspan=3, pady=10
    )

    root.mainloop()


if __name__ == "__main__":
    start_gui()
