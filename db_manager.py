import sqlite3


# ─────────────────────────────────────────────
#  CUSTOM EXCEPTION
# ─────────────────────────────────────────────

class ValidationError(Exception):
    pass


# ─────────────────────────────────────────────
#  VALIDATOR CLASS
# ─────────────────────────────────────────────

class HomeShareValidator:

    @staticmethod
    def validate_user(username_raw, password_raw):
        username = username_raw.strip()
        password = password_raw.strip()

        if not username:
            raise ValidationError("Kullanıcı adı boş bırakılamaz.")
        if len(username) < 3:
            raise ValidationError("Kullanıcı adı en az 3 karakter olmalıdır.")
        if not password:
            raise ValidationError("Şifre boş bırakılamaz.")
        if len(password) < 6:
            raise ValidationError("Şifre en az 6 karakter olmalıdır.")

        return username, password

    @staticmethod
    def validate_roommate(name_raw):
        name = name_raw.strip()

        if not name:
            raise ValidationError("İsim boş bırakılamaz.")
        if len(name) < 2:
            raise ValidationError("İsim en az 2 karakter olmalıdır.")

        return name

    @staticmethod
    def validate_expense(description_raw, amount_raw):
        description = description_raw.strip()
        
        if not description:
            raise ValidationError("Açıklama boş bırakılamaz.")

        try:
            amount = float(amount_raw)
        except (ValueError, TypeError):
            raise ValidationError("Tutar geçerli bir sayı olmalıdır.")

        if amount <= 0:
            raise ValidationError("Tutar 0'dan büyük olmalıdır.")

        return description, amount

    @staticmethod
    def validate_payment(amount_raw, from_id, to_id):
        try:
            amount = float(amount_raw)
        except (ValueError, TypeError):
            raise ValidationError("Tutar geçerli bir sayı olmalıdır.")

        if amount <= 0:
            raise ValidationError("Tutar 0'dan büyük olmalıdır.")

        if from_id == to_id:
            raise ValidationError("Ödeyen ve alan kişi aynı olamaz.")

        return amount

    @staticmethod
    def validate_category(name_raw):
        name = name_raw.strip()

        if not name:
            raise ValidationError("Kategori adı boş bırakılamaz.")

        return name


# ─────────────────────────────────────────────
#  DATABASE CLASS
# ─────────────────────────────────────────────

class HomeShareDatabase:

    def __init__(self, db_name="homeshare.db"):
        self.db_name = db_name

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ── Tablo oluşturma ──

    def create_tables(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT    NOT NULL UNIQUE,
                    password      TEXT    NOT NULL,
                    created_at    TEXT    DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS roommates (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name      TEXT    NOT NULL,
                    email     TEXT    DEFAULT '',
                    is_active INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name  TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS expenses (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    paid_by     INTEGER NOT NULL REFERENCES roommates(id),
                    category_id INTEGER REFERENCES categories(id),
                    amount      REAL    NOT NULL,
                    description TEXT    NOT NULL,
                    date        TEXT    NOT NULL DEFAULT (date('now'))
                );

                CREATE TABLE IF NOT EXISTS expense_splits (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_id   INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
                    roommate_id  INTEGER NOT NULL REFERENCES roommates(id),
                    share_amount REAL    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS payments (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    from_id INTEGER NOT NULL REFERENCES roommates(id),
                    to_id   INTEGER NOT NULL REFERENCES roommates(id),
                    amount  REAL    NOT NULL,
                    date    TEXT    NOT NULL DEFAULT (date('now')),
                    note    TEXT    DEFAULT ''
                );
            """)

        # Tabloları oluşturduktan sonra varsayılan kategorileri ekle
        self.fill_default_categories()

    def fill_default_categories(self):
        default_categories = ["Kira", "Market", "Fatura", "Temizlik", "Diğer"]
        with self.get_connection() as conn:
            cur = conn.cursor()
            for cat in default_categories:
                # INSERT OR IGNORE: kategori zaten varsa tekrar ekleme
                cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))

    # ── users tablosu ──

    def create_user(self, username, password):
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
            return True
        except sqlite3.IntegrityError:
            # UNIQUE kısıtı ihlali — kullanıcı adı zaten var
            return False

    def get_user(self, username, password):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            return cur.fetchone()

    # ── roommates tablosu ──

    def get_roommates(self, user_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM roommates WHERE user_id = ? AND is_active = 1 ORDER BY name",
                (user_id,)
            )
            return cur.fetchall()

    def add_roommate(self, user_id, name, email=""):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO roommates (user_id, name, email) VALUES (?, ?, ?)",
                (user_id, name, email)
            )
            return cur.lastrowid

    def update_roommate(self, roommate_id, name, email=""):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE roommates SET name = ?, email = ? WHERE id = ?",
                (name, email, roommate_id)
            )

    def deactivate_roommate(self, roommate_id):
        # Silmek yerine pasife al — geçmiş harcamalar korunsun
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE roommates SET is_active = 0 WHERE id = ?",
                (roommate_id,)
            )

    # ── categories tablosu ──

    def get_categories(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM categories ORDER BY name")
            return cur.fetchall()

    def add_category(self, name):
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_category(self, category_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    # ── expenses tablosu ──

    def add_expense(self, user_id, paid_by, category_id, amount, description, date, splits):
        # splits: [(roommate_id, share_amount), ...] listesi
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO expenses (user_id, paid_by, category_id, amount, description, date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, paid_by, category_id, amount, description, date)
            )
            expense_id = cur.lastrowid

            # Her ev arkadaşının payını expense_splits tablosuna ekle
            for roommate_id, share_amount in splits:
                cur.execute(
                    "INSERT INTO expense_splits (expense_id, roommate_id, share_amount) VALUES (?, ?, ?)",
                    (expense_id, roommate_id, share_amount)
                )

    def get_expenses(self, user_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            # JOIN ile ödeyen kişinin adını ve kategori adını da getir
            cur.execute("""
                SELECT e.id, e.description, e.amount, e.date,
                       r.name AS paid_by_name,
                       c.name AS category_name
                FROM expenses e
                JOIN roommates r ON e.paid_by = r.id
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = ?
                ORDER BY e.date DESC
            """, (user_id,))
            return cur.fetchall()

    def get_expense_splits(self, expense_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT es.roommate_id, es.share_amount, r.name
                FROM expense_splits es
                JOIN roommates r ON es.roommate_id = r.id
                WHERE es.expense_id = ?
            """, (expense_id,))
            return cur.fetchall()

    def update_expense(self, expense_id, paid_by, category_id, amount, description, date):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE expenses
                SET paid_by = ?, category_id = ?, amount = ?, description = ?, date = ?
                WHERE id = ?
            """, (paid_by, category_id, amount, description, date, expense_id))

    def delete_expense(self, expense_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    # ── payments tablosu ──

    def add_payment(self, user_id, from_id, to_id, amount, date, note=""):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO payments (user_id, from_id, to_id, amount, date, note) VALUES (?,?,?,?,?,?)",
                (user_id, from_id, to_id, amount, date, note)
            )
            return cur.lastrowid

    def get_payments(self, user_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.amount, p.date, p.note,
                       r1.name AS from_name,
                       r2.name AS to_name
                FROM payments p
                JOIN roommates r1 ON p.from_id = r1.id
                JOIN roommates r2 ON p.to_id = r2.id
                WHERE p.user_id = ?
                ORDER BY p.date DESC
            """, (user_id,))
            return cur.fetchall()

    def delete_payment(self, payment_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM payments WHERE id = ?", (payment_id,))

    # ── Dashboard için özet sorgular ──

    def get_balance_summary(self, user_id):
        # Her ev arkadaşının toplam ödediği ve toplam borçlu olduğu miktarı hesapla
        with self.get_connection() as conn:
            cur = conn.cursor()

            # Kimin ne kadar harcama yaptığı
            cur.execute("""
                SELECT r.id, r.name,
                       COALESCE(SUM(e.amount), 0) AS total_paid
                FROM roommates r
                LEFT JOIN expenses e ON e.paid_by = r.id AND e.user_id = ?
                WHERE r.user_id = ? AND r.is_active = 1
                GROUP BY r.id
            """, (user_id, user_id))
            paid_rows = cur.fetchall()

            # Kimin ne kadar payı var
            cur.execute("""
                SELECT es.roommate_id,
                       COALESCE(SUM(es.share_amount), 0) AS total_share
                FROM expense_splits es
                JOIN expenses e ON es.expense_id = e.id
                WHERE e.user_id = ?
                GROUP BY es.roommate_id
            """, (user_id,))
            share_rows = cur.fetchall()

        # share_rows'u sözlüğe çevir: {roommate_id: total_share}
        share_dict = {row[0]: row[1] for row in share_rows}

        result = []
        for row in paid_rows:
            r_id   = row[0]
            r_name = row[1]
            paid   = row[2]
            share  = share_dict.get(r_id, 0)
            balance = paid - share  # Pozitif = alacaklı, Negatif = borçlu
            result.append((r_id, r_name, paid, share, balance))

        return result

    def get_category_totals(self, user_id):
        # Grafik penceresi için: kategoriye göre toplam harcama
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT c.name, SUM(e.amount) AS total
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = ?
                GROUP BY e.category_id
                ORDER BY total DESC
            """, (user_id,))
            return cur.fetchall()

    def get_monthly_totals(self, user_id):
        # Grafik penceresi için: aya göre toplam harcama (son 6 ay)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT strftime('%Y-%m', date) AS month,
                       SUM(amount) AS total
                FROM expenses
                WHERE user_id = ?
                GROUP BY month
                ORDER BY month DESC
                LIMIT 6
            """, (user_id,))
            return list(reversed(cur.fetchall()))


if __name__ == "__main__":
    db = HomeShareDatabase()
    db.create_tables()
    print("Veritabanı hazır.")