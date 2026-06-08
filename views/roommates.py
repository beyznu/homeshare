import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox as msg
import db_manager as dbm


class RoommatesWindow(tk.Toplevel):

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.db = dbm.HomeShareDatabase()

        self.title("Ev Arkadaşları")
        self.geometry("500x420")
        self.resizable(False, False)

        self.build_ui()
        self.list_roommates()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window()

    def build_ui(self):
        frm_form = ttk.Labelframe(self, text="Ev Arkadaşı Ekle / Düzenle", bootstyle="success")
        frm_form.pack(fill="x", padx=15, pady=(15, 0))

        ttk.Label(frm_form, text="İsim:").grid(row=0, column=0, sticky="e", padx=(10, 5), pady=8)
        self.name_var = tk.StringVar()
        self.txt_name = ttk.Entry(frm_form, textvariable=self.name_var, width=25, bootstyle="success")
        self.txt_name.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=8)

        ttk.Label(frm_form, text="E-posta:").grid(row=1, column=0, sticky="e", padx=(10, 5), pady=8)
        self.email_var = tk.StringVar()
        self.txt_email = ttk.Entry(frm_form, textvariable=self.email_var, width=25, bootstyle="success")
        self.txt_email.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=8)

        frm_form.columnconfigure(1, weight=1)

        frm_btns = ttk.Frame(frm_form)
        frm_btns.grid(row=2, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))

        self.btn_save = ttk.Button(frm_btns, text="Ekle", bootstyle="success", command=self.on_save)
        self.btn_save.pack(side="left", padx=(0, 5))

        self.btn_update = ttk.Button(frm_btns, text="Güncelle", bootstyle="warning",
                                     command=self.on_update, state="disabled")
        self.btn_update.pack(side="left", padx=(0, 5))

        self.btn_cancel = ttk.Button(frm_btns, text="İptal", bootstyle="secondary-outline",
                                     command=self.on_cancel, state="disabled")
        self.btn_cancel.pack(side="left")

        frm_list = ttk.Labelframe(self, text="Ev Arkadaşları Listesi", bootstyle="success")
        frm_list.pack(fill="both", expand=True, padx=15, pady=10)

        self.tv = ttk.Treeview(frm_list, columns=("name", "email"),
                               show="headings", height=8, selectmode="browse",
                               bootstyle="success")
        self.tv.heading("name",  text="İsim",    anchor="w")
        self.tv.heading("email", text="E-posta", anchor="w")
        self.tv.column("name",  anchor="w", width=180)
        self.tv.column("email", anchor="w", width=220)

        scroll = ttk.Scrollbar(frm_list, orient="vertical", command=self.tv.yview,
                               bootstyle="success-round")
        self.tv.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tv.pack(fill="both", expand=True, padx=(8, 0), pady=8)

        lbl_info = ttk.Label(self, text="Çift tıkla: Düzenle", bootstyle="secondary")
        lbl_info.pack(side="bottom", pady=(0, 8))

        self.tv.bind("<<TreeviewSelect>>", self.on_select)
        self.tv.bind("<Double-1>",         self.on_edit)

        self.txt_name.focus_set()

    def list_roommates(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

        rows = self.db.get_roommates(self.user_id)
        for row in rows:
            self.tv.insert("", "end", iid=row[0], values=(row[2], row[3]))

    def on_save(self):
        try:
            name = dbm.HomeShareValidator.validate_roommate(self.name_var.get())
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            self.txt_name.focus_set()
            return

        self.db.add_roommate(self.user_id, name, self.email_var.get().strip())
        self.list_roommates()
        self.on_cancel()

    def on_update(self):
        selection = self.tv.selection()
        if not selection:
            return

        try:
            name = dbm.HomeShareValidator.validate_roommate(self.name_var.get())
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            self.txt_name.focus_set()
            return

        roommate_id = int(selection[0])
        self.db.update_roommate(roommate_id, name, self.email_var.get().strip())
        self.list_roommates()
        self.on_cancel()

    def on_delete(self, event=None):
        selection = self.tv.selection()
        if not selection:
            return

        answer = msg.askyesno("Sil", "Bu kişiyi silmek istediğine emin misin?", parent=self)
        if answer:
            roommate_id = int(selection[0])
            self.db.deactivate_roommate(roommate_id)
            self.list_roommates()
            self.on_cancel()

    def on_cancel(self):
        self.name_var.set("")
        self.email_var.set("")
        self.tv.selection_remove(self.tv.selection())
        self.btn_save.configure(state="normal")
        self.btn_update.configure(state="disabled")
        self.btn_cancel.configure(state="disabled")
        self.txt_name.focus_set()

    def on_select(self, event):
        if self.tv.selection():
            self.btn_update.configure(state="normal")
            self.btn_cancel.configure(state="normal")

    def on_edit(self, event):
        region = self.tv.identify("region", event.x, event.y)
        if region != "cell":
            return

        selection = self.tv.selection()
        if not selection:
            return

        values = self.tv.item(selection[0])["values"]
        self.name_var.set(values[0])
        self.email_var.set(values[1])
        self.btn_save.configure(state="disabled")
        self.btn_update.configure(state="normal")
        self.btn_cancel.configure(state="normal")
        self.txt_name.focus_set()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")