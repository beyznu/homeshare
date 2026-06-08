import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox as msg
import tkinter as tk
import db_manager as dbm


class LoginWindow(ttk.Window):

    def __init__(self):
        super().__init__(themename="minty")
        self.title("HomeShare - Giriş")
        self.geometry("400x480")
        self.resizable(False, False)

        self.db = dbm.HomeShareDatabase()
        self.db.create_tables()

        self.current_mode = "login"

        self.build_ui()
        self._center_window()

    def build_ui(self):
        # ── Başlık ──
        self.lbl_title = ttk.Label(self, text="🏠 HomeShare",
                                   font=("Helvetica", 22, "bold"), bootstyle="success")
        self.lbl_title.pack(pady=(35, 4))

        self.lbl_subtitle = ttk.Label(self, text="Ev arkadaşlarınla masrafları paylaş",
                                      font=("Helvetica", 10), bootstyle="secondary")
        self.lbl_subtitle.pack(pady=(0, 25))

        # ── Form frame ──
        self.frm = ttk.Labelframe(self, text="Giriş Yap", bootstyle="success")
        self.frm.pack(padx=40, fill="x")

        ttk.Label(self.frm, text="Kullanıcı Adı:").grid(row=0, column=0, sticky="e",
                                                         padx=(10, 5), pady=8)
        self.username_var = tk.StringVar()
        self.txt_username = ttk.Entry(self.frm, textvariable=self.username_var,
                                      width=25, bootstyle="success")
        self.txt_username.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=8)

        ttk.Label(self.frm, text="Şifre:").grid(row=1, column=0, sticky="e",
                                                 padx=(10, 5), pady=8)
        self.password_var = tk.StringVar()
        self.txt_password = ttk.Entry(self.frm, textvariable=self.password_var,
                                      width=25, show="●", bootstyle="success")
        self.txt_password.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=8)

        self.lbl_confirm = ttk.Label(self.frm, text="Şifre Tekrar:")
        self.confirm_var = tk.StringVar()
        self.txt_confirm = ttk.Entry(self.frm, textvariable=self.confirm_var,
                                     width=25, show="●", bootstyle="success")

        self.frm.columnconfigure(1, weight=1)

        # ── Ana buton ──
        self.btn_submit = ttk.Button(self, text="Giriş Yap", bootstyle="success",
                                     command=self.on_submit)
        self.btn_submit.pack(fill="x", padx=40, pady=(15, 0), ipady=5)

        # ── Mod değiştirme ──
        frm_toggle = ttk.Frame(self)
        frm_toggle.pack(pady=(10, 0))

        self.lbl_toggle_hint = ttk.Label(frm_toggle, text="Hesabın yok mu?")
        self.lbl_toggle_hint.pack(side="left")

        self.btn_toggle = ttk.Button(frm_toggle, text="Kayıt Ol",
                                     bootstyle="success-link", command=self.toggle_mode)
        self.btn_toggle.pack(side="left", padx=(5, 0))

        self.bind("<Return>", lambda e: self.on_submit())
        self.txt_username.focus_set()

    # ─────────────────────────────────────────────
    #  MOD DEĞİŞTİRME
    # ─────────────────────────────────────────────

    def toggle_mode(self):
        if self.current_mode == "login":
            self.current_mode = "register"
            self.frm.configure(text="Kayıt Ol")
            self.btn_submit.configure(text="Kayıt Ol")
            self.lbl_toggle_hint.configure(text="Zaten hesabın var mı?")
            self.btn_toggle.configure(text="Giriş Yap")
            self.geometry("400x540")

            self.lbl_confirm.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=8)
            self.txt_confirm.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=8)
        else:
            self.current_mode = "login"
            self.frm.configure(text="Giriş Yap")
            self.btn_submit.configure(text="Giriş Yap")
            self.lbl_toggle_hint.configure(text="Hesabın yok mu?")
            self.btn_toggle.configure(text="Kayıt Ol")
            self.geometry("400x480")

            self.lbl_confirm.grid_forget()
            self.txt_confirm.grid_forget()
            self.confirm_var.set("")

        self.txt_username.focus_set()

    # ─────────────────────────────────────────────
    #  SUBMIT
    # ─────────────────────────────────────────────

    def on_submit(self):
        if self.current_mode == "login":
            self.do_login()
        else:
            self.do_register()

    def do_login(self):
        try:
            username, password = dbm.HomeShareValidator.validate_user(
                self.username_var.get(), self.password_var.get()
            )
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            return

        user = self.db.get_user(username, password)
        if user is None:
            msg.showerror("Hata", "Kullanıcı adı veya şifre yanlış.", parent=self)
            self.txt_password.focus_set()
            return

        self.open_dashboard(user)

    def do_register(self):
        try:
            username, password = dbm.HomeShareValidator.validate_user(
                self.username_var.get(), self.password_var.get()
            )
        except dbm.ValidationError as e:
            msg.showwarning("Uyarı", str(e), parent=self)
            return

        if self.password_var.get() != self.confirm_var.get():
            msg.showwarning("Uyarı", "Şifreler eşleşmiyor.", parent=self)
            self.txt_confirm.focus_set()
            return

        success = self.db.create_user(username, password)
        if not success:
            msg.showerror("Hata", "Bu kullanıcı adı zaten alınmış.", parent=self)
            self.txt_username.focus_set()
            return

        msg.showinfo("Başarılı", f"Hoş geldin, {username}!\nŞimdi giriş yapabilirsin.", parent=self)
        self.toggle_mode()

    def open_dashboard(self, user):
        from views.dashboard import DashboardWindow
        DashboardWindow(self, user)
        self.withdraw()

    # ─────────────────────────────────────────────
    #  YARDIMCI
    # ─────────────────────────────────────────────

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()