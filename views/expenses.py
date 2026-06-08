import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox as msg
from datetime import date
import db_manager as dbm


class ExpensesWindow(tk.Toplevel):

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.db = dbm.HomeShareDatabase()

        self.title("Harcamalar")
        self.geometry("620x480")
        self.resizable(False, False)

        self.build_ui()
        self.list_expenses()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window()

    def build_ui(self):
        frm_top = ttk.Frame(self)
        frm_top.pack(fill="x", padx=15, pady=(15, 0))

        ttk.Label(frm_top, text="Harcamalar",
                  font=("Helvetica", 13, "bold"), bootstyle="success").pack(side="left")

        self.btn_add = ttk.Button(frm_top, text="+ Yeni Harcama",
                                  bootstyle="success", command=self.on_show_add_window)
        self.btn_add.pack(side="right")

        ttk.Separator(self, bootstyle="success").pack(fill="x", padx=15, pady=10)

        frm_list = ttk.Frame(self)
        frm_list.pack(fill="both", expand=True, padx=15)

        cols = ("date", "description", "category", "amount", "paid_by")
        self.tv = ttk.Treeview(frm_list, columns=cols, show="headings",
                               height=12, selectmode="browse", bootstyle="success")

        self.tv.heading("date",        text="Tarih",    anchor="center")
        self.tv.heading("description", text="Açıklama", anchor="w")
        self.tv.heading("category",    text="Kategori", anchor="w")
        self.tv.heading("amount",      text="Tutar",    anchor="center")
        self.tv.heading("paid_by",     text="Ödeyen",   anchor="w")

        self.tv.column("date",        anchor="center", width=85)
        self.tv.column("description", anchor="w",      width=160)
        self.tv.column("category",    anchor="w",      width=90)
        self.tv.column("amount",      anchor="center", width=80)
        self.tv.column("paid_by",     anchor="w",      width=110)

        scroll = ttk.Scrollbar(frm_list, orient="vertical", command=self.tv.yview,
                               bootstyle="success-round")
        self.tv.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tv.pack(fill="both", expand=True)

        ttk.Separator(self, bootstyle="success").pack(fill="x", padx=15, pady=(10, 0))

        frm_btns = ttk.Frame(self)
        frm_btns.pack(fill="x", padx=15, pady=10)

        self.btn_edit = ttk.Button(frm_btns, text="Güncelle", bootstyle="warning",
                                   command=self.on_show_edit_window, state="disabled")
        self.btn_edit.pack(side="left", padx=(0, 5))

        self.btn_delete = ttk.Button(frm_btns, text="Sil", bootstyle="danger-outline",
                                     command=self.on_delete, state="disabled")
        self.btn_delete.pack(side="left")

        self.bind("<Control-i>", lambda e: self.on_show_add_window())
        self.tv.bind("<<TreeviewSelect>>", self.on_select)
        self.tv.bind("<Double-1>", self.on_show_edit_window)

    def list_expenses(self):
        for item in self.tv.get_children():
            self.tv.delete(item)

        self.btn_edit.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

        rows = self.db.get_expenses(self.user_id)

        if not rows:
            self.tv.insert("", "end", values=("—", "Henüz harcama yok", "—", "—", "—"))
            return

        for row in rows:
            self.tv.insert("", "end", iid=row[0], values=(
                row[3], row[1], row[5] or "—", f"{row[2]:.2f} ₺", row[4]
            ))

    def on_select(self, event):
        selection = self.tv.selection()
        if selection:
            try:
                int(selection[0])
                self.btn_edit.configure(state="normal")
                self.btn_delete.configure(state="normal")
            except ValueError:
                self.btn_edit.configure(state="disabled")
                self.btn_delete.configure(state="disabled")

    def on_show_add_window(self):
        if not self.db.get_roommates(self.user_id):
            msg.showwarning("Uyarı", "Önce ev arkadaşı eklemelisiniz.", parent=self)
            return
        add_win = AddExpenseWindow(self, self.user_id)
        add_win.grab_set()
        self.wait_window(add_win)
        self.list_expenses()

    def on_show_edit_window(self, event=None):
        if event is not None:
            region = self.tv.identify("region", event.x, event.y)
            if region != "cell":
                return

        selection = self.tv.selection()
        if not selection:
            return

        try:
            expense_id = int(selection[0])
        except ValueError:
            return

        values = self.tv.item(expense_id)["values"]
        edit_win = EditExpenseWindow(self, self.user_id, expense_id, values)
        edit_win.grab_set()
        self.wait_window(edit_win)
        self.list_expenses()

    def on_delete(self):
        selection = self.tv.selection()
        if not selection:
            return
        try:
            expense_id = int(selection[0])
        except ValueError:
            return

        answer = msg.askyesno("Sil", "Bu harcamayı silmek istediğine emin misin?", parent=self)
        if answer:
            self.db.delete_expense(expense_id)
            self.list_expenses()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


class AddExpenseWindow(tk.Toplevel):

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.db = dbm.HomeShareDatabase()

        self.title("Yeni Harcama Ekle")
        self.resizable(False, False)

        self.roommates = self.db.get_roommates(user_id)
        self.categories = self.db.get_categories()

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window()

    def build_ui(self):
        frm = ttk.LabelFrame(self, text="Harcama Bilgileri", bootstyle="success")
        frm.pack(fill="both", expand=True, padx=15, pady=15)

        pad_lbl = {"padx": (10, 5), "pady": 7, "sticky": "e"}
        pad_ent = {"padx": (0, 10), "pady": 7, "sticky": "ew"}

        ttk.Label(frm, text="Açıklama:").grid(row=0, column=0, **pad_lbl)
        self.description_var = tk.StringVar()
        self.txt_description = ttk.Entry(frm, textvariable=self.description_var,
                                         width=28, bootstyle="success")
        self.txt_description.grid(row=0, column=1, **pad_ent)

        ttk.Label(frm, text="Tutar (₺):").grid(row=1, column=0, **pad_lbl)
        self.amount_var = tk.StringVar()
        self.txt_amount = ttk.Entry(frm, textvariable=self.amount_var,
                                    width=28, bootstyle="success")
        self.txt_amount.grid(row=1, column=1, **pad_ent)

        ttk.Label(frm, text="Tarih:").grid(row=2, column=0, **pad_lbl)
        self.date_var = tk.StringVar(value=str(date.today()))
        self.txt_date = ttk.Entry(frm, textvariable=self.date_var,
                                  width=28, bootstyle="success")
        self.txt_date.grid(row=2, column=1, **pad_ent)

        ttk.Label(frm, text="Kategori:").grid(row=3, column=0, **pad_lbl)
        category_names = [c[1] for c in self.categories]
        self.category_var = tk.StringVar()
        self.combo_category = ttk.Combobox(frm, textvariable=self.category_var,
                                           values=category_names, state="readonly",
                                           width=26, bootstyle="success")
        if category_names:
            self.combo_category.current(0)
        self.combo_category.grid(row=3, column=1, **pad_ent)

        ttk.Label(frm, text="Ödeyen:").grid(row=4, column=0, **pad_lbl)
        roommate_names = [r[2] for r in self.roommates]
        self.paid_by_var = tk.StringVar()
        self.combo_paid_by = ttk.Combobox(frm, textvariable=self.paid_by_var,
                                          values=roommate_names, state="readonly",
                                          width=26, bootstyle="success")
        if roommate_names:
            self.combo_paid_by.current(0)
        self.combo_paid_by.grid(row=4, column=1, **pad_ent)

        ttk.Label(frm, text="Paylaş:").grid(row=5, column=0, **pad_lbl)
        frm_splits = ttk.Frame(frm)
        frm_splits.grid(row=5, column=1, sticky="w", padx=(0, 10), pady=7)

        self.split_vars = {}
        for roommate in self.roommates:
            var = tk.BooleanVar(value=True)
            self.split_vars[roommate[0]] = var
            ttk.Checkbutton(frm_splits, text=roommate[2], variable=var,
                            bootstyle="success").pack(anchor="w")

        frm.columnconfigure(1, weight=1)

        frm_btns = ttk.Frame(frm)
        frm_btns.grid(row=6, column=0, columnspan=2, sticky="e", padx=10, pady=(5, 10))

        ttk.Button(frm_btns, text="Kaydet", bootstyle="success",
                   command=self.on_save).pack(side="left", padx=(0, 5))
        ttk.Button(frm_btns, text="İptal", bootstyle="secondary-outline",
                   command=self.destroy).pack(side="left")

        self.txt_description.focus_set()

    def on_save(self):
        try:
            description, amount = dbm.HomeShareValidator.validate_expense(
                self.description_var.get(), self.amount_var.get())
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            return

        paid_by_id = next((r[0] for r in self.roommates
                           if r[2] == self.paid_by_var.get()), None)
        if paid_by_id is None:
            msg.showwarning("Uyarı", "Lütfen ödeyen kişiyi seçin.", parent=self)
            return

        category_id = next((c[0] for c in self.categories
                            if c[1] == self.category_var.get()), None)

        selected = [r_id for r_id, var in self.split_vars.items() if var.get()]
        if not selected:
            msg.showwarning("Uyarı", "En az bir kişi seçilmelidir.", parent=self)
            return

        share_amount = round(amount / len(selected), 2)
        splits = [(r_id, share_amount) for r_id in selected]

        self.db.add_expense(self.user_id, paid_by_id, category_id,
                            amount, description, self.date_var.get(), splits)
        self.destroy()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


class EditExpenseWindow(tk.Toplevel):

    def __init__(self, parent, user_id, expense_id, values):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.expense_id = expense_id
        self.db = dbm.HomeShareDatabase()

        self.title("Harcamayı Düzenle")
        self.resizable(False, False)

        self.roommates = self.db.get_roommates(user_id)
        self.categories = self.db.get_categories()

        self.build_ui()

        self.date_var.set(values[0])
        self.description_var.set(values[1])
        self.category_var.set(values[2] if values[2] != "—" else "")
        self.amount_var.set(str(values[3]).replace(" ₺", ""))
        self.paid_by_var.set(values[4])

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window()

    def build_ui(self):
        frm = ttk.LabelFrame(self, text="Harcama Bilgileri", bootstyle="success")
        frm.pack(fill="both", expand=True, padx=15, pady=15)

        pad_lbl = {"padx": (10, 5), "pady": 7, "sticky": "e"}
        pad_ent = {"padx": (0, 10), "pady": 7, "sticky": "ew"}

        ttk.Label(frm, text="Açıklama:").grid(row=0, column=0, **pad_lbl)
        self.description_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.description_var,
                  width=28, bootstyle="success").grid(row=0, column=1, **pad_ent)

        ttk.Label(frm, text="Tutar (₺):").grid(row=1, column=0, **pad_lbl)
        self.amount_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.amount_var,
                  width=28, bootstyle="success").grid(row=1, column=1, **pad_ent)

        ttk.Label(frm, text="Tarih:").grid(row=2, column=0, **pad_lbl)
        self.date_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.date_var,
                  width=28, bootstyle="success").grid(row=2, column=1, **pad_ent)

        ttk.Label(frm, text="Kategori:").grid(row=3, column=0, **pad_lbl)
        self.category_var = tk.StringVar()
        ttk.Combobox(frm, textvariable=self.category_var,
                     values=[c[1] for c in self.categories],
                     state="readonly", width=26,
                     bootstyle="success").grid(row=3, column=1, **pad_ent)

        ttk.Label(frm, text="Ödeyen:").grid(row=4, column=0, **pad_lbl)
        self.paid_by_var = tk.StringVar()
        ttk.Combobox(frm, textvariable=self.paid_by_var,
                     values=[r[2] for r in self.roommates],
                     state="readonly", width=26,
                     bootstyle="success").grid(row=4, column=1, **pad_ent)

        frm.columnconfigure(1, weight=1)

        frm_btns = ttk.Frame(frm)
        frm_btns.grid(row=5, column=0, columnspan=2, sticky="e", padx=10, pady=(5, 10))

        ttk.Button(frm_btns, text="Güncelle", bootstyle="warning",
                   command=self.on_update).pack(side="left", padx=(0, 5))
        ttk.Button(frm_btns, text="İptal", bootstyle="secondary-outline",
                   command=self.destroy).pack(side="left")

    def on_update(self):
        try:
            description, amount = dbm.HomeShareValidator.validate_expense(
                self.description_var.get(), self.amount_var.get())
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            return

        paid_by_id = next((r[0] for r in self.roommates
                           if r[2] == self.paid_by_var.get()), None)
        if paid_by_id is None:
            msg.showwarning("Uyarı", "Lütfen ödeyen kişiyi seçin.", parent=self)
            return

        category_id = next((c[0] for c in self.categories
                            if c[1] == self.category_var.get()), None)

        self.db.update_expense(self.expense_id, paid_by_id, category_id,
                               amount, description, self.date_var.get())
        self.destroy()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")