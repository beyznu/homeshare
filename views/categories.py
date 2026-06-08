import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox as msg
import db_manager as dbm


class CategoriesWindow(tk.Toplevel):

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.db = dbm.HomeShareDatabase()

        self.title("Kategoriler")
        self.geometry("380x420")
        self.resizable(False, False)

        self.build_ui()
        self.list_categories()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window()

    def build_ui(self):
        frm_form = ttk.LabelFrame(self, text="Kategori Ekle", bootstyle="success")
        frm_form.pack(fill="x", padx=15, pady=(15, 0))

        ttk.Label(frm_form, text="Kategori Adı:").grid(row=0, column=0, sticky="e",
                                                        padx=(10, 5), pady=10)
        self.name_var = tk.StringVar()
        self.txt_name = ttk.Entry(frm_form, textvariable=self.name_var, width=22, bootstyle="success")
        self.txt_name.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)

        frm_form.columnconfigure(1, weight=1)

        frm_btns = ttk.Frame(frm_form)
        frm_btns.grid(row=1, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))

        self.btn_add = ttk.Button(frm_btns, text="Ekle", bootstyle="success", command=self.on_add)
        self.btn_add.pack(side="left", padx=(0, 5))

        self.btn_cancel = ttk.Button(frm_btns, text="İptal", bootstyle="secondary-outline",
                                     command=self.on_cancel, state="disabled")
        self.btn_cancel.pack(side="left")

        frm_list = ttk.LabelFrame(self, text="Kategori Listesi", bootstyle="success")
        frm_list.pack(fill="both", expand=True, padx=15, pady=10)

        self.tv = ttk.Treeview(frm_list, columns=("name",), show="headings",
                               height=10, selectmode="browse", bootstyle="success")
        self.tv.heading("name", text="Kategori Adı", anchor="w")
        self.tv.column("name", anchor="w", width=280)

        scroll = ttk.Scrollbar(frm_list, orient="vertical", command=self.tv.yview,
                               bootstyle="success-round")
        self.tv.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tv.pack(fill="both", expand=True, padx=(8, 0), pady=8)

        ttk.Separator(self, bootstyle="success").pack(fill="x", padx=15, pady=(0, 5))

        frm_del = ttk.Frame(self)
        frm_del.pack(fill="x", padx=15, pady=(0, 10))

        self.btn_delete = ttk.Button(frm_del, text="Sil", bootstyle="danger-outline",
                                     command=self.on_delete, state="disabled")
        self.btn_delete.pack(side="left")

        self.tv.bind("<<TreeviewSelect>>", self.on_select)
        self.txt_name.bind("<Return>", lambda e: self.on_add())
        self.txt_name.focus_set()

    def list_categories(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

        self.btn_delete.configure(state="disabled")

        rows = self.db.get_categories()
        for row in rows:
            self.tv.insert("", "end", iid=row[0], values=(row[1],))

    def on_add(self):
        try:
            name = dbm.HomeShareValidator.validate_category(self.name_var.get())
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            self.txt_name.focus_set()
            return

        success = self.db.add_category(name)
        if not success:
            msg.showwarning("Uyarı", "Bu kategori zaten mevcut.", parent=self)
            self.txt_name.focus_set()
            return

        self.list_categories()
        self.on_cancel()

    def on_delete(self):
        selection = self.tv.selection()
        if not selection:
            return

        answer = msg.askyesno("Sil", "Bu kategoriyi silmek istediğine emin misin?", parent=self)
        if answer:
            category_id = int(selection[0])
            self.db.delete_category(category_id)
            self.list_categories()
            self.on_cancel()

    def on_cancel(self):
        self.name_var.set("")
        self.tv.selection_remove(self.tv.selection())
        self.btn_cancel.configure(state="disabled")
        self.txt_name.focus_set()

    def on_select(self, event):
        if self.tv.selection():
            self.btn_delete.configure(state="normal")
            self.btn_cancel.configure(state="normal")

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")