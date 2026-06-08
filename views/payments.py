import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox as msg
from datetime import date
import db_manager as dbm


class PaymentsWindow(tk.Toplevel):

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.db = dbm.HomeShareDatabase()

        self.title("Ödemeler")
        self.geometry("600x500")
        self.resizable(False, False)

        self.build_ui()
        self.list_payments()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window()

    def build_ui(self):
        frm_form = ttk.LabelFrame(self, text="Yeni Ödeme Ekle", bootstyle="success")
        frm_form.pack(fill="x", padx=15, pady=(15, 0))

        pad_lbl = {"padx": (10, 5), "pady": 7, "sticky": "e"}
        pad_ent = {"padx": (0, 10), "pady": 7, "sticky": "ew"}

        ttk.Label(frm_form, text="Ödeyen:").grid(row=0, column=0, **pad_lbl)
        self.from_var = tk.StringVar()
        self.combo_from = ttk.Combobox(frm_form, textvariable=self.from_var,
                                       state="readonly", width=22, bootstyle="success")
        self.combo_from.grid(row=0, column=1, **pad_ent)

        ttk.Label(frm_form, text="Alan:").grid(row=1, column=0, **pad_lbl)
        self.to_var = tk.StringVar()
        self.combo_to = ttk.Combobox(frm_form, textvariable=self.to_var,
                                     state="readonly", width=22, bootstyle="success")
        self.combo_to.grid(row=1, column=1, **pad_ent)

        ttk.Label(frm_form, text="Tutar (₺):").grid(row=2, column=0, **pad_lbl)
        self.amount_var = tk.StringVar()
        self.txt_amount = ttk.Entry(frm_form, textvariable=self.amount_var,
                                    width=24, bootstyle="success")
        self.txt_amount.grid(row=2, column=1, **pad_ent)

        ttk.Label(frm_form, text="Tarih:").grid(row=3, column=0, **pad_lbl)
        self.date_var = tk.StringVar(value=str(date.today()))
        self.txt_date = ttk.Entry(frm_form, textvariable=self.date_var,
                                  width=24, bootstyle="success")
        self.txt_date.grid(row=3, column=1, **pad_ent)

        ttk.Label(frm_form, text="Not:").grid(row=4, column=0, **pad_lbl)
        self.note_var = tk.StringVar()
        self.txt_note = ttk.Entry(frm_form, textvariable=self.note_var,
                                  width=24, bootstyle="success")
        self.txt_note.grid(row=4, column=1, **pad_ent)

        frm_form.columnconfigure(1, weight=1)

        frm_btns = ttk.Frame(frm_form)
        frm_btns.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))
        ttk.Button(frm_btns, text="Kaydet", bootstyle="success",
                   command=self.on_save).pack(side="left", padx=(0, 5))
        ttk.Button(frm_btns, text="Temizle", bootstyle="secondary-outline",
                   command=self.on_clear).pack(side="left")

        frm_list = ttk.LabelFrame(self, text="Ödeme Geçmişi", bootstyle="success")
        frm_list.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("date", "from_name", "to_name", "amount", "note")
        self.tv = ttk.Treeview(frm_list, columns=cols, show="headings",
                               height=7, selectmode="browse", bootstyle="success")

        self.tv.heading("date",      text="Tarih",  anchor="center")
        self.tv.heading("from_name", text="Ödeyen", anchor="w")
        self.tv.heading("to_name",   text="Alan",   anchor="w")
        self.tv.heading("amount",    text="Tutar",  anchor="center")
        self.tv.heading("note",      text="Not",    anchor="w")

        self.tv.column("date",      anchor="center", width=85)
        self.tv.column("from_name", anchor="w",      width=110)
        self.tv.column("to_name",   anchor="w",      width=110)
        self.tv.column("amount",    anchor="center", width=80)
        self.tv.column("note",      anchor="w",      width=150)

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
        self.load_roommates()
        self.txt_amount.focus_set()

    def load_roommates(self):
        self.roommates = self.db.get_roommates(self.user_id)
        names = [r[2] for r in self.roommates]
        self.combo_from.configure(values=names)
        self.combo_to.configure(values=names)
        if names:
            self.combo_from.current(0)
            self.combo_to.current(0)

    def list_payments(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

        self.btn_delete.configure(state="disabled")
        rows = self.db.get_payments(self.user_id)

        if not rows:
            self.tv.insert("", "end", values=("—", "Henüz ödeme yok", "—", "—", "—"))
            return

        for row in rows:
            self.tv.insert("", "end", iid=row[0], values=(
                row[2], row[4], row[5], f"{row[1]:.2f} ₺", row[3] or ""
            ))

    def on_save(self):
        from_name = self.from_var.get()
        to_name   = self.to_var.get()
        from_id = next((r[0] for r in self.roommates if r[2] == from_name), None)
        to_id   = next((r[0] for r in self.roommates if r[2] == to_name),   None)

        if from_id is None or to_id is None:
            msg.showwarning("Uyarı", "Lütfen ödeyen ve alan kişiyi seçin.", parent=self)
            return

        try:
            amount = dbm.HomeShareValidator.validate_payment(
                self.amount_var.get(), from_id, to_id)
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            return

        self.db.add_payment(self.user_id, from_id, to_id, amount,
                            self.date_var.get(), self.note_var.get().strip())
        self.list_payments()
        self.on_clear()

    def on_delete(self):
        selection = self.tv.selection()
        if not selection:
            return
        try:
            payment_id = int(selection[0])
        except ValueError:
            return
        answer = msg.askyesno("Sil", "Bu ödemeyi silmek istediğine emin misin?", parent=self)
        if answer:
            self.db.delete_payment(payment_id)
            self.list_payments()

    def on_clear(self):
        self.amount_var.set("")
        self.note_var.set("")
        self.date_var.set(str(date.today()))
        if self.combo_from["values"]:
            self.combo_from.current(0)
            self.combo_to.current(0)
        self.txt_amount.focus_set()

    def on_select(self, event):
        if self.tv.selection():
            try:
                int(self.tv.selection()[0])
                self.btn_delete.configure(state="normal")
            except ValueError:
                self.btn_delete.configure(state="disabled")

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")