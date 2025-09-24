import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import subprocess
import platform
import win32print
import re


class BarcodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de códigos de barras")
        self.root.geometry("650x550")
        self.root.resizable(True, True)

        # Database file
        self.db_file = "barcode_database.txt"

        # Create codes folder
        self.codes_folder = "codes"
        self.ensure_codes_folder()

        self.load_database()

        # Printer name
        self.printer_name_var = tk.StringVar(value="SAT TT448-2 USE (ZPL)")

        # Create GUI
        self.create_widgets()

    def sanitize_filename(self, text):
        return re.sub(r'[\\/:*?"<>|]', "_", text)

    def ensure_codes_folder(self):
        if not os.path.exists(self.codes_folder):
            os.makedirs(self.codes_folder)

    def load_database(self):
        self.barcode_list = []
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            parts = line.split("|")
                            if len(parts) >= 3:
                                self.barcode_list.append(
                                    {
                                        "code": parts[0],
                                        "timestamp": parts[1],
                                        "filename": parts[2],
                                        "full_line": line,
                                    }
                                )
                            elif len(parts) >= 2:
                                self.barcode_list.append(
                                    {
                                        "code": parts[0],
                                        "timestamp": parts[1],
                                        "filename": "",
                                        "full_line": line,
                                    }
                                )
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando la base de datos: {e}")

    def save_to_database(self, code, filename):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{code}|{timestamp}|{filename}"
        try:
            with open(self.db_file, "a", encoding="utf-8") as file:
                file.write(entry + "\n")

            self.barcode_list.append(
                {
                    "code": code,
                    "timestamp": timestamp,
                    "filename": filename,
                    "full_line": entry,
                }
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando en la base de datos: {e}")

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        # --- Generador tab ---
        main_frame = ttk.Frame(notebook, padding="10")
        notebook.add(main_frame, text="Generador")

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        title_label = ttk.Label(
            main_frame,
            text="Generador de Códigos de Barras - Code128",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Entrada", padding="10")
        input_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Texto:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_frame, textvariable=self.input_var, width=40
        )
        self.input_entry.grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10)
        )
        self.input_var.trace("w", self.on_input_change)

        self.generate_btn = ttk.Button(
            input_frame, text="Generar Código", command=self.generate_barcode
        )
        self.generate_btn.grid(row=0, column=2)

        # Database table
        db_frame = ttk.LabelFrame(main_frame, text="Base de Datos", padding="10")
        db_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(0, 10),
        )
        db_frame.columnconfigure(0, weight=1)
        db_frame.rowconfigure(0, weight=1)

        columns = ("Código", "Fecha/Hora", "Estado", "Imagen")
        self.tree = ttk.Treeview(
            db_frame,
            columns=columns,
            show="headings",
            height=15,
            selectmode="extended",
        )
        self.tree.heading("Código", text="Código")
        self.tree.heading("Fecha/Hora", text="Fecha/Hora")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Imagen", text="Imagen")

        self.tree.column("Código", width=200)
        self.tree.column("Fecha/Hora", width=150)
        self.tree.column("Estado", width=100)
        self.tree.column("Imagen", width=100)

        scrollbar = ttk.Scrollbar(
            db_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Buttons
        buttons_frame = ttk.Frame(db_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        self.view_image_btn = ttk.Button(
            buttons_frame, text="Ver Imagen", command=self.view_selected_image
        )
        self.view_image_btn.grid(row=0, column=0, padx=(0, 10))

        self.clean_db_btn = ttk.Button(
            buttons_frame, text="Limpiar Base de Datos", command=self.clean_database
        )
        self.clean_db_btn.grid(row=0, column=1, padx=(0, 10))

        self.print_btn = ttk.Button(
            buttons_frame, text="Imprimir", command=self.choose_codes_popup
        )
        self.print_btn.grid(row=0, column=2, padx=(0, 10))

        self.update_treeview()

        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN
        )
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.input_entry.focus()

        # --- Settings tab ---
        settings_frame = ttk.Frame(notebook, padding="10")
        notebook.add(settings_frame, text="Configuración")

        ttk.Label(settings_frame, text="Nombre de la impresora:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        printer_entry = ttk.Entry(
            settings_frame, textvariable=self.printer_name_var, width=40
        )
        printer_entry.grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        settings_frame.columnconfigure(1, weight=1)

    def choose_codes_popup(self):
        """Popup with two dropdowns and a quantity to choose codes before printing."""
        if not self.barcode_list:
            messagebox.showwarning("Advertencia", "La base de datos está vacía")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Seleccionar códigos para imprimir")
        popup.geometry("400x250")

        ttk.Label(popup, text="Código izquierda:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Label(popup, text="Código derecha:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        ttk.Label(popup, text="Cantidad de filas:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        codes = [item["code"] for item in self.barcode_list]

        left_var = tk.StringVar()
        right_var = tk.StringVar()
        qty_var = tk.IntVar(value=1)

        left_cb = ttk.Combobox(popup, textvariable=left_var, values=codes, state="readonly")
        left_cb.grid(row=0, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

        right_cb = ttk.Combobox(popup, textvariable=right_var, values=codes, state="readonly")
        right_cb.grid(row=1, column=1, padx=10, pady=10, sticky=(tk.W, tk.E))

        qty_spin = ttk.Spinbox(popup, from_=1, to=500, textvariable=qty_var, width=10)
        qty_spin.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        def confirm():
            left_code = left_var.get().strip() or None
            right_code = right_var.get().strip() or None
            qty = qty_var.get()

            if not left_code and not right_code:
                messagebox.showwarning("Advertencia", "Debe seleccionar al menos un código")
                return

            self.print_barcode(left_code, right_code, qty)
            popup.destroy()

        btn = ttk.Button(popup, text="Imprimir", command=confirm)
        btn.grid(row=3, column=0, columnspan=2, pady=20)

    def on_input_change(self, *args):
        current_input = self.input_var.get().strip()
        if current_input:
            exists = any(item["code"] == current_input for item in self.barcode_list)
            if exists:
                self.status_var.set(f"El código '{current_input}' ya existe en la base de datos")
            else:
                self.status_var.set(f"El código '{current_input}' es nuevo")
        else:
            self.status_var.set("Listo")

    def generate_barcode(self):
        text = self.input_var.get().strip().replace(" ", "").replace("\n", "").replace("/", "")
        if not text:
            messagebox.showwarning(
                "Advertencia", "Ingrese un texto para generar código"
            )
            return
        if any(item["code"] == text for item in self.barcode_list):
            result = messagebox.askyesno(
                "Código existente",
                f"El código '{text}' ya existe en la base de datos. ¿Generar de todas formas?",
            )
            if not result:
                return
        try:
            code128_barcode = barcode.get("code128", text, writer=ImageWriter())
            safe_text = self.sanitize_filename(text)
            filename = (
                f"barcode_{safe_text}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            filepath = os.path.join(self.codes_folder, filename)
            code128_barcode.save(filepath, options={"write_text": False})

            self.save_to_database(text, filename)
            self.update_treeview()
            self.input_var.set("")
            messagebox.showinfo(
                "Éxito",
                f"Código generado y guardado como '{filename}.png' en la carpeta codes",
            )
            self.status_var.set("Código generado con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando código: {e}")
            self.status_var.set("Error generando código")

    def view_selected_image(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un código para ver la imagen")
            return
        item_values = self.tree.item(selected_item[0])["values"]
        if len(item_values) >= 4:
            code = item_values[0]
            for item in self.barcode_list:
                if item["code"] == code:
                    self.open_image(item["filename"])
                    return
        messagebox.showwarning("Advertencia", "No hay imagen asociada a esta entrada")

    def open_image(self, filename):
        if not filename:
            messagebox.showwarning("Advertencia", "No hay imagen asociada a esta entrada")
            return
        filepath = os.path.join(self.codes_folder, filename + ".png")
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"No se encontró la imagen: {filepath}")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
            elif platform.system() == "Darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen: {e}")

    def clean_database(self):
        if not self.barcode_list:
            messagebox.showinfo("Info", "La base de datos ya está vacía")
            return
        count = len(self.barcode_list)
        result = messagebox.askyesno(
            "Confirmar limpieza",
            f"Esto eliminará permanentemente:\n"
            f"• {count} entradas en la base de datos\n"
            f"• Todas las imágenes en la carpeta codes\n\n"
            f"¿Está seguro de continuar?",
        )
        if not result:
            return
        try:
            deleted_images = 0
            for item in self.barcode_list:
                if item["filename"]:
                    filepath = os.path.join(
                        self.codes_folder, item["filename"] + ".png"
                    )
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        deleted_images += 1
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
            self.barcode_list = []
            self.update_treeview()
            messagebox.showinfo(
                "Base de datos limpiada",
                f"Se eliminaron:\n"
                f"• {count} entradas de la base de datos\n"
                f"• {deleted_images} imágenes",
            )
            self.status_var.set("Base de datos limpiada")
        except Exception as e:
            messagebox.showerror("Error", f"Error limpiando base de datos: {e}")
            self.status_var.set("Error limpiando base de datos")

    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.barcode_list:
            status = "Existe"
            has_image = "Sí" if item["filename"] else "No"
            self.tree.insert(
                "", "end", values=(item["code"], item["timestamp"], status, has_image)
            )

    def print_barcode(self, left_text=None, right_text=None, qty=1):
        """Send ZPL barcode(s) to printer with quantity support."""
        try:
            zpl = "^XA\n"
            if left_text:
                zpl += f"^FO50,50^BY2.5,2,80^BCN,80,Y,N,N^FD{left_text}^FS\n"
            if right_text:
                zpl += f"^FO500,50^BY2.5,2,80^BCN,80,Y,N,N^FD{right_text}^FS\n"
            zpl += f"^PQ{qty}\n"
            zpl += "^XZ"

            printer_name = self.printer_name_var.get().strip()
            if not printer_name:
                messagebox.showerror("Error", "El nombre de la impresora está vacío. Configúrelo en la pestaña Configuración.")
                return

            hPrinter = win32print.OpenPrinter(printer_name)
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("ZPL Label", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, zpl.encode("utf-8"))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            win32print.ClosePrinter(hPrinter)

            msg = f"Impreso {qty} fila(s): "
            if left_text and right_text:
                msg += f"'{left_text}' (izq) y '{right_text}' (der)"
            elif left_text:
                msg += f"'{left_text}' en columna izquierda"
            elif right_text:
                msg += f"'{right_text}' en columna derecha"
            else:
                msg = "Nada para imprimir"

            self.status_var.set(msg)
            messagebox.showinfo("Imprimir", msg)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo imprimir: {e}")
            self.status_var.set("Error al imprimir")


def main():
    root = tk.Tk()
    app = BarcodeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
