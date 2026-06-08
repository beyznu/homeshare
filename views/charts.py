import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import db_manager as dbm


class ChartsWindow(tk.Toplevel):

    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.parent = parent
        self.user_id = user_id
        self.db = dbm.HomeShareDatabase()

        self.title("Harcama Grafikleri")
        self.geometry("600x500")
        self.resizable(False, False)

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._center_window()

    def build_ui(self):
        # ── Notebook: iki sekme ──
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=15)

        # Sekme 1: Pasta grafik
        self.tab_pie = ttk.Frame(notebook)
        notebook.add(self.tab_pie, text="Kategoriye Göre")

        # Sekme 2: Bar grafik
        self.tab_bar = ttk.Frame(notebook)
        notebook.add(self.tab_bar, text="Aylara Göre")

        # Sekme değişince grafiği çiz
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # ── Pasta grafik ──
        self.fig_pie = Figure(figsize=(5.5, 4))
        self.ax_pie = self.fig_pie.add_subplot()
        self.canvas_pie = FigureCanvasTkAgg(master=self.tab_pie, figure=self.fig_pie)
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True)

        # ── Bar grafik ──
        self.fig_bar = Figure(figsize=(5.5, 4))
        self.ax_bar = self.fig_bar.add_subplot()
        self.canvas_bar = FigureCanvasTkAgg(master=self.tab_bar, figure=self.fig_bar)
        self.canvas_bar.get_tk_widget().pack(fill="both", expand=True)

        # İlk açılışta pasta grafiği çiz
        self.draw_pie_chart()

    # ─────────────────────────────────────────────
    #  SEKME DEĞİŞİMİ
    # ─────────────────────────────────────────────

    def on_tab_change(self, event):
        selected = event.widget.index("current")
        if selected == 0:
            self.draw_pie_chart()
        else:
            self.draw_bar_chart()

    # ─────────────────────────────────────────────
    #  PASTA GRAFİK — kategoriye göre harcama
    # ─────────────────────────────────────────────

    def draw_pie_chart(self):
        self.ax_pie.clear()

        rows = self.db.get_category_totals(self.user_id)

        if not rows:
            self.ax_pie.text(0.5, 0.5, "Henüz harcama verisi yok.",
                             ha="center", va="center", fontsize=12,
                             transform=self.ax_pie.transAxes)
            self.canvas_pie.draw()
            return

        # DB'den gelen veriler: (category_name, total)
        labels = [row[0] if row[0] else "Diğer" for row in rows]
        sizes  = [row[1] for row in rows]

        # En büyük dilimi öne çıkar
        explode = [0.05] * len(sizes)

        self.ax_pie.pie(
            sizes,
            labels=labels,
            explode=explode,
            autopct="%.1f%%",
            shadow=True,
            startangle=90
        )
        self.ax_pie.set_title("Kategoriye Göre Harcama Dağılımı")

        self.canvas_pie.draw()

    # ─────────────────────────────────────────────
    #  BAR GRAFİK — aylara göre harcama
    # ─────────────────────────────────────────────

    def draw_bar_chart(self):
        self.ax_bar.clear()

        rows = self.db.get_monthly_totals(self.user_id)

        if not rows:
            self.ax_bar.text(0.5, 0.5, "Henüz harcama verisi yok.",
                             ha="center", va="center", fontsize=12,
                             transform=self.ax_bar.transAxes)
            self.canvas_bar.draw()
            return

        # DB'den gelen veriler: (month, total) — örnek: ("2026-05", 1200.0)
        months = [row[0] for row in rows]
        totals = [row[1] for row in rows]

        colors = ["#1D9E75", "#378ADD", "#BA7517", "#7F77DD", "#E05C5C", "#5CB85C"]

        bars = self.ax_bar.bar(months, totals, color=colors[:len(months)], edgecolor="white")

        # Her barın üstüne tutarı yaz
        for bar, total in zip(bars, totals):
            self.ax_bar.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(totals) * 0.01,
                f"{total:.0f}₺",
                ha="center", va="bottom", fontsize=9
            )

        self.ax_bar.set_title("Aylara Göre Toplam Harcama")
        self.ax_bar.set_xlabel("Ay")
        self.ax_bar.set_ylabel("Tutar (₺)")
        self.ax_bar.grid(visible=True, axis="y", linestyle="--", alpha=0.5)

        self.fig_bar.tight_layout()
        self.canvas_bar.draw()

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