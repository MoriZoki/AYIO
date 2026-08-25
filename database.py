import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_NAME = "dakhlo_kharj.db"

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DB_NAME)

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

DEFAULT_CATEGORIES = [
    # Incomes (ورودی‌ها / درآمدها)
    {"name": "حقوق و دستمزد", "type": "income", "icon": "account_balance_wallet_rounded", "color": "#10B981"},
    {"name": "پاداش و پورسانت", "type": "income", "icon": "card_giftcard_rounded", "color": "#06B6D4"},
    {"name": "سرمایه‌گذاری و سود", "type": "income", "icon": "trending_up_rounded", "color": "#3B82F6"},
    {"name": "فروش کالا/خدمات", "type": "income", "icon": "storefront_rounded", "color": "#8B5CF6"},
    {"name": "آزادکاری و پروژه", "type": "income", "icon": "laptop_mac_rounded", "color": "#F59E0B"},
    {"name": "هدیه و کادو", "type": "income", "icon": "redeem_rounded", "color": "#EC4899"},
    {"name": "طلب وصول شده", "type": "income", "icon": "handshake_rounded", "color": "#0D9488"},
    {"name": "سایر درآمدها", "type": "income", "icon": "add_circle_outline_rounded", "color": "#14B8A6"},

    # Expenses (خروجی‌ها / هزینه‌ها)
    {"name": "خوراک و خرید روزانه", "type": "expense", "icon": "shopping_cart_rounded", "color": "#EF4444"},
    {"name": "مسکن، اجاره و شارژ", "type": "expense", "icon": "home_rounded", "color": "#F97316"},
    {"name": "حمل و نقل و سوخت", "type": "expense", "icon": "directions_car_rounded", "color": "#EAB308"},
    {"name": "رستوران، کافه و تفریح", "type": "expense", "icon": "restaurant_rounded", "color": "#F43F5E"},
    {"name": "قبوض و اشتراک‌ها", "type": "expense", "icon": "receipt_long_rounded", "color": "#6366F1"},
    {"name": "سلامتی، درمان و دارو", "type": "expense", "icon": "medical_services_rounded", "color": "#06B6D4"},
    {"name": "پوشاک، لباس و مراقبت", "type": "expense", "icon": "checkroom_rounded", "color": "#D946EF"},
    {"name": "آموزش و کتاب", "type": "expense", "icon": "school_rounded", "color": "#3B82F6"},
    {"name": "اقساط و وام", "type": "expense", "icon": "credit_card_rounded", "color": "#64748B"},
    {"name": "پرداخت بدهی", "type": "expense", "icon": "payments_rounded", "color": "#E11D48"},
    {"name": "تعمیرات و نگهداری", "type": "expense", "icon": "build_rounded", "color": "#78716C"},
    {"name": "سایر هزینه‌ها", "type": "expense", "icon": "more_horiz_rounded", "color": "#94A3B8"}
]

DEFAULT_ACCOUNTS = [
    {"name": "کارت بانکی اصلی", "type": "bank_card", "card_number": "6037", "initial_balance": 0, "color": "#1E3A8A", "icon": "credit_card_rounded"},
    {"name": "کیف پول نقدی", "type": "cash", "card_number": "", "initial_balance": 0, "color": "#0F766E", "icon": "account_balance_wallet_rounded"},
    {"name": "صندوق پس‌انداز", "type": "savings", "card_number": "", "initial_balance": 0, "color": "#B45309", "icon": "savings_rounded"}
]

def init_db():
    """Initializes database tables, accounts, loans, debts, and handles migrations."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                icon TEXT NOT NULL,
                color TEXT NOT NULL,
                is_default INTEGER DEFAULT 0
            )
        """)
        
        # Accounts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                card_number TEXT,
                initial_balance REAL DEFAULT 0,
                color TEXT NOT NULL,
                icon TEXT NOT NULL,
                is_default INTEGER DEFAULT 0
            )
        """)
        
        # Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER,
                account_id INTEGER,
                date TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL,
                FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE SET NULL
            )
        """)

        # Loans & Installments Table (اقساط و وام‌ها)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                total_amount REAL NOT NULL,
                monthly_amount REAL NOT NULL,
                total_installments INTEGER NOT NULL,
                paid_installments INTEGER DEFAULT 0,
                due_day INTEGER DEFAULT 1,
                next_due_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Debts Table (طلب‌ها و بدهی‌ها)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL, -- 'receivable' (طلب از دیگران) or 'payable' (بدهی به دیگران)
                person_name TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT,
                is_settled INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Seed categories if none exist
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            for cat in DEFAULT_CATEGORIES:
                cursor.execute("""
                    INSERT INTO categories (name, type, icon, color, is_default)
                    VALUES (?, ?, ?, ?, 1)
                """, (cat["name"], cat["type"], cat["icon"], cat["color"]))

        # Seed accounts if none exist
        cursor.execute("SELECT COUNT(*) FROM accounts")
        if cursor.fetchone()[0] == 0:
            for acc in DEFAULT_ACCOUNTS:
                cursor.execute("""
                    INSERT INTO accounts (name, type, card_number, initial_balance, color, icon, is_default)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (acc["name"], acc["type"], acc["card_number"], acc["initial_balance"], acc["color"], acc["icon"]))
        
        conn.commit()

# --- Accounts CRUD & Balance calculation ---
def get_accounts() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts ORDER BY id ASC")
        accounts = [dict(row) for row in cursor.fetchall()]
        
        for acc in accounts:
            acc_id = acc["id"]
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE account_id = ? AND type = 'income'
            """, (acc_id,))
            inc = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM transactions 
                WHERE account_id = ? AND type = 'expense'
            """, (acc_id,))
            exp = cursor.fetchone()[0]
            
            acc["current_balance"] = (acc.get("initial_balance") or 0.0) + inc - exp
            acc["total_income"] = inc
            acc["total_expense"] = exp
            
        return accounts

def get_account_by_id(acc_id: int) -> Optional[Dict[str, Any]]:
    accounts = get_accounts()
    for acc in accounts:
        if acc["id"] == acc_id:
            return acc
    return None

def add_account(name: str, acc_type: str, initial_balance: float, card_number: str, color: str, icon: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO accounts (name, type, card_number, initial_balance, color, icon, is_default)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (name, acc_type, card_number.strip(), initial_balance, color, icon))
        conn.commit()
        return cursor.lastrowid

def update_account(acc_id: int, name: str, acc_type: str, initial_balance: float, card_number: str, color: str, icon: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE accounts 
            SET name = ?, type = ?, initial_balance = ?, card_number = ?, color = ?, icon = ?
            WHERE id = ?
        """, (name, acc_type, initial_balance, card_number.strip(), color, icon, acc_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_account(acc_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        # Set transactions referencing this account to NULL
        cursor.execute("UPDATE transactions SET account_id = NULL WHERE account_id = ?", (acc_id,))
        cursor.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_total_net_worth() -> float:
    accounts = get_accounts()
    return sum(acc["current_balance"] for acc in accounts)

def transfer_money(from_account_id: int, to_account_id: int, amount: float, date_str: str, description: str = "") -> bool:
    """Transfers money from one account to another by creating matching expense and income transactions."""
    if from_account_id == to_account_id or amount <= 0:
        return False
        
    from_acc = get_account_by_id(from_account_id)
    to_acc = get_account_by_id(to_account_id)
    if not from_acc or not to_acc:
        return False
        
    from_desc = f"انتقال به «{to_acc['name']}»" + (f" - {description}" if description else "")
    to_desc = f"انتقال از «{from_acc['name']}»" + (f" - {description}" if description else "")
    
    # 1. Expense from source
    add_transaction("expense", amount, None, date_str, from_desc, account_id=from_account_id)
    # 2. Income to destination
    add_transaction("income", amount, None, date_str, to_desc, account_id=to_account_id)
    return True

# --- Categories CRUD ---
def get_categories(category_type: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if category_type:
            cursor.execute("SELECT * FROM categories WHERE type = ? ORDER BY id ASC", (category_type,))
        else:
            cursor.execute("SELECT * FROM categories ORDER BY type DESC, id ASC")
        return [dict(row) for row in cursor.fetchall()]

def get_category_by_id(cat_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_category(name: str, cat_type: str, icon: str, color: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO categories (name, type, icon, color, is_default)
            VALUES (?, ?, ?, ?, 0)
        """, (name, cat_type, icon, color))
        conn.commit()
        return cursor.lastrowid

def update_category(cat_id: int, name: str, cat_type: str, icon: str, color: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE categories 
            SET name = ?, type = ?, icon = ?, color = ?
            WHERE id = ?
        """, (name, cat_type, icon, color, cat_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_category(cat_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        # Set transactions referencing this category to NULL
        cursor.execute("UPDATE transactions SET category_id = NULL WHERE category_id = ?", (cat_id,))
        cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- Transactions CRUD ---
def add_transaction(
    t_type: str, 
    amount: float, 
    category_id: Optional[int], 
    date_str: str, 
    description: str = "",
    account_id: Optional[int] = None
) -> int:
    parts = [int(p) for p in date_str.split('/')]
    year, month = parts[0], parts[1]
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (type, amount, category_id, account_id, date, year, month, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (t_type, amount, category_id, account_id, date_str, year, month, description.strip()))
        conn.commit()
        return cursor.lastrowid

def delete_transaction(t_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (t_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_transactions(
    year: Optional[int] = None, 
    month: Optional[int] = None, 
    t_type: Optional[str] = None,
    account_id: Optional[int] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT t.id, t.type, t.amount, t.category_id, t.account_id, t.date, t.year, t.month, t.description, t.created_at,
                   c.name as category_name, c.icon as category_icon, c.color as category_color,
                   a.name as account_name, a.icon as account_icon, a.color as account_color, a.card_number as account_card
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            LEFT JOIN accounts a ON t.account_id = a.id
            WHERE 1=1
        """
        params = []
        if year is not None:
            query += " AND t.year = ?"
            params.append(year)
        if month is not None:
            query += " AND t.month = ?"
            params.append(month)
        if t_type and t_type != "all":
            query += " AND t.type = ?"
            params.append(t_type)
        if account_id is not None:
            query += " AND t.account_id = ?"
            params.append(account_id)
            
        query += " ORDER BY t.date DESC, t.id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_monthly_summary(year: int, month: int) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE year = ? AND month = ? AND type = 'income'
        """, (year, month))
        total_income = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE year = ? AND month = ? AND type = 'expense'
        """, (year, month))
        total_expense = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT c.name, c.icon, c.color, t.type, SUM(t.amount) as total_amount, COUNT(t.id) as count
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.year = ? AND t.month = ?
            GROUP BY t.category_id
            ORDER BY total_amount DESC
        """, (year, month))
        categories_breakdown = [dict(row) for row in cursor.fetchall()]
        
        return {
            "income": total_income,
            "expense": total_expense,
            "balance": total_income - total_expense,
            "categories": categories_breakdown
        }

# --- Loans & Installments (اقساط و وام‌ها) ---
def get_loans() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM loans ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def add_loan(
    title: str,
    total_amount: float,
    monthly_amount: float,
    total_installments: int,
    paid_installments: int = 0,
    due_day: int = 1,
    next_due_date: str = "",
    notes: str = ""
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO loans (title, total_amount, monthly_amount, total_installments, paid_installments, due_day, next_due_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, total_amount, monthly_amount, total_installments, paid_installments, due_day, next_due_date, notes.strip()))
        conn.commit()
        return cursor.lastrowid

def pay_loan_installment(loan_id: int, account_id: Optional[int], date_str: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
        loan = cursor.fetchone()
        if not loan:
            return False
            
        new_paid = (loan["paid_installments"] or 0) + 1
        if new_paid > loan["total_installments"]:
            new_paid = loan["total_installments"]
            
        cursor.execute("UPDATE loans SET paid_installments = ? WHERE id = ?", (new_paid, loan_id))
        conn.commit()
        
        # Add expense transaction
        add_transaction(
            t_type="expense",
            amount=loan["monthly_amount"],
            category_id=None,
            date_str=date_str,
            description=f"پرداخت قسط {new_paid} از {loan['total_installments']} وام «{loan['title']}»",
            account_id=account_id
        )
        return True

def delete_loan(loan_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- Debts & Receivables (طلب‌ها و بدهی‌ها) ---
def get_debts(debt_type: Optional[str] = None, is_settled: Optional[int] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM debts WHERE 1=1"
        params = []
        if debt_type:
            query += " AND type = ?"
            params.append(debt_type)
        if is_settled is not None:
            query += " AND is_settled = ?"
            params.append(is_settled)
        query += " ORDER BY is_settled ASC, id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def add_debt(debt_type: str, person_name: str, amount: float, due_date: str = "", notes: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO debts (type, person_name, amount, due_date, is_settled, notes)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (debt_type, person_name.strip(), amount, due_date.strip(), notes.strip()))
        conn.commit()
        return cursor.lastrowid

def settle_debt(debt_id: int, account_id: Optional[int], date_str: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debts WHERE id = ?", (debt_id,))
        debt = cursor.fetchone()
        if not debt:
            return False
            
        cursor.execute("UPDATE debts SET is_settled = 1 WHERE id = ?", (debt_id,))
        conn.commit()
        
        # If receivable (طلب), money was received -> add income
        # If payable (بدهی), money was paid -> add expense
        if debt["type"] == "receivable":
            add_transaction(
                t_type="income",
                amount=debt["amount"],
                category_id=None,
                date_str=date_str,
                description=f"وصول طلب از «{debt['person_name']}»",
                account_id=account_id
            )
        else:
            add_transaction(
                t_type="expense",
                amount=debt["amount"],
                category_id=None,
                date_str=date_str,
                description=f"تسویه بدهی به «{debt['person_name']}»",
                account_id=account_id
            )
        return True

def delete_debt(debt_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
        conn.commit()
        return cursor.rowcount > 0
