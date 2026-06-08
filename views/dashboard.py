import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox as msg
import db_manager as dbm


class DashboardWindow(tk.Toplevel):

    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.user_id = user[0]
        self.db = dbm.HomeShareDatabase()

        self.title(f"HomeShare - {self.user[1]}")
        self.geometry("700x580")
        self.resizable(False, False)

        self.build_ui()
        self.refresh()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._center_window()

    def build_ui(self):
        # ── Üst bar ──
        frm_top = ttk.Frame(self, bootstyle="success")
        frm_top.pack(fill="x")

        inner_top = ttk.Frame(frm_top, bootstyle="success")
        inner_top.pack(fill="x", padx=15, pady=10)

        ttk.Label(inner_top, text="🏠 HomeShare", font=("Helvetica", 16, "bold"),
                  bootstyle="inverse-success").pack(side="left")

        self.lbl_user = ttk.Label(inner_top, text="", font=("Helvetica", 10),
                                   bootstyle="inverse-success")
        self.lbl_user.pack(side="right", padx=(0, 5))

        # ── Orta alan ──
        frm_middle = ttk.Frame(self)
        frm_middle.pack(fill="both", expand=True, padx=15, pady=10)

        frm_middle.columnconfigure(0, weight=1)
        frm_middle.columnconfigure(1, weight=2)

        # ── Sol: Bakiye özeti ──
        frm_balance = ttk.Labelframe(frm_middle, text="Bakiye Özeti", bootstyle="success")
        frm_balance.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.tv_balance = ttk.Treeview(frm_balance, columns=("name", "balance"),
                                       show="headings", height=8, selectmode="none",
                                       bootstyle="success")
        self.tv_balance.heading("name",    text="Kişi",   anchor="w")
        self.tv_balance.heading("balance", text="Bakiye", anchor="center")
        self.tv_balance.column("name",    anchor="w",      width=120)
        self.tv_balance.column("balance", anchor="center", width=90)
        self.tv_balance.pack(fill="both", expand=True, padx=8, pady=8)

        # ── Sağ: Son harcamalar ──
        frm_expenses = ttk.Labelframe(frm_middle, text="Son Harcamalar", bootstyle="success")
        frm_expenses.grid(row=0, column=1, sticky="nsew")

        cols = ("date", "description", "amount", "paid_by")
        self.tv_expenses = ttk.Treeview(frm_expenses, columns=cols,
                                        show="headings", height=8, selectmode="none",
                                        bootstyle="success")
        self.tv_expenses.heading("date",        text="Tarih",    anchor="center")
        self.tv_expenses.heading("description", text="Açıklama", anchor="w")
        self.tv_expenses.heading("amount",      text="Tutar",    anchor="center")
        self.tv_expenses.heading("paid_by",     text="Ödeyen",   anchor="w")

        self.tv_expenses.column("date",        anchor="center", width=85)
        self.tv_expenses.column("description", anchor="w",      width=130)
        self.tv_expenses.column("amount",      anchor="center", width=70)
        self.tv_expenses.column("paid_by",     anchor="w",      width=90)

        scroll = ttk.Scrollbar(frm_expenses, orient="vertical",
                               command=self.tv_expenses.yview, bootstyle="success-round")
        self.tv_expenses.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tv_expenses.pack(fill="both", expand=True, padx=(8, 0), pady=8)

        # ── Alt: Navigasyon butonları (iki satır) ──
        ttk.Separator(self, bootstyle="success").pack(fill="x", padx=15, pady=(5, 5))

        frm_nav1 = ttk.Frame(self)
        frm_nav1.pack(fill="x", padx=15, pady=(0, 5))

        frm_nav2 = ttk.Frame(self)
        frm_nav2.pack(fill="x", padx=15, pady=(0, 15))

        row1 = [
            ("Ev Arkadaşları", self.open_roommates),
            ("Harcamalar",     self.open_expenses),
            ("Ödemeler",       self.open_payments),
        ]

        row2 = [
            ("Kategoriler", self.open_categories),
            ("Grafik",      self.open_charts),
            ("Rapor",       self.open_reports),
        ]

        for text, command in row1:
            ttk.Button(frm_nav1, text=text, command=command,
                       bootstyle="success-outline").pack(
                side="left", expand=True, fill="x", padx=3)

        for text, command in row2:
            ttk.Button(frm_nav2, text=text, command=command,
                       bootstyle="success-outline").pack(
                side="left", expand=True, fill="x", padx=3)

    # ─────────────────────────────────────────────
    #  VERİ YÜKLEME
    # ─────────────────────────────────────────────

    def refresh(self):
        self.lbl_user.configure(text=f"👤 {self.user[1]}")
        self.load_balance()
        self.load_expenses()

    def load_balance(self):
        for item in self.tv_balance.get_children():
            self.tv_balance.delete(item)

        rows = self.db.get_balance_summary(self.user_id)

        if not rows:
            self.tv_balance.insert("", "end", values=("Henüz kimse yok", ""))
            return

        for r_id, name, paid, share, balance in rows:
            if balance > 0:
                label = f"+{balance:.2f} ₺"
                tag = "positive"
            elif balance < 0:
                label = f"{balance:.2f} ₺"
                tag = "negative"
            else:
                label = "0.00 ₺"
                tag = "zero"

            self.tv_balance.insert("", "end", values=(name, label), tags=(tag,))

        self.tv_balance.tag_configure("positive", foreground="#78c2ad")
        self.tv_balance.tag_configure("negative", foreground="#f3969a")
        self.tv_balance.tag_configure("zero",     foreground="gray")

    def load_expenses(self):
        for item in self.tv_expenses.get_children():
            self.tv_expenses.delete(item)

        rows = self.db.get_expenses(self.user_id)

        if not rows:
            self.tv_expenses.insert("", "end", values=("—", "Henüz harcama yok", "—", "—"))
            return

        for row in rows[:10]:
            self.tv_expenses.insert("", "end", values=(
                row[3],
                row[1],
                f"{row[2]:.2f} ₺",
                row[4]
            ))

    # ─────────────────────────────────────────────
    #  NAVİGASYON
    # ─────────────────────────────────────────────

    def open_roommates(self):
        from views.roommates import RoommatesWindow
        win = RoommatesWindow(self, self.user_id)
        win.grab_set()
        self.wait_window(win)
        self.refresh()

    def open_expenses(self):
        from views.expenses import ExpensesWindow
        win = ExpensesWindow(self, self.user_id)
        win.grab_set()
        self.wait_window(win)
        self.refresh()

    def open_payments(self):
        from views.payments import PaymentsWindow
        win = PaymentsWindow(self, self.user_id)
        win.grab_set()
        self.wait_window(win)
        self.refresh()

    def open_categories(self):
        from views.categories import CategoriesWindow
        win = CategoriesWindow(self, self.user_id)
        win.grab_set()
        self.wait_window(win)
        self.refresh()

    def open_charts(self):
        from views.charts import ChartsWindow
        win = ChartsWindow(self, self.user_id)
        win.grab_set()

    def open_reports(self):
        from views.reports import ReportsWindow
        win = ReportsWindow(self, self.user_id)
        win.grab_set()

    # ─────────────────────────────────────────────
    #  YARDIMCI
    # ─────────────────────────────────────────────

    def on_close(self):
        self.parent.destroy()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")