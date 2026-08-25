import flet as ft
import database
from utils.persian_date import (
    get_current_jalali_str,
    format_price,
    to_persian_digits
)
from utils.icons_helper import get_icon

class AddTransactionView:
    def __init__(self, page: ft.Page, on_saved_callback):
        self.page = page
        self.on_saved_callback = on_saved_callback
        
        self.current_type = "expense"
        self.selected_category_id = None
        self.selected_account_id = None
        self.current_date = get_current_jalali_str()
        
        self.amount_input = ft.TextField(
            label="مبلغ (تومان)",
            prefix_icon=ft.Icons.ATTACH_MONEY_ROUNDED,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
            text_size=20,
            border_radius=14,
            helper="",
            on_change=self.on_amount_changed,
            rtl=True,
        )
        
        self.desc_input = ft.TextField(
            label="توضیحات یا بابت (اختیاری)",
            prefix_icon=ft.Icons.EDIT_NOTE_ROUNDED,
            text_align=ft.TextAlign.RIGHT,
            border_radius=14,
            multiline=False,
            rtl=True,
        )
        
        self.date_input = ft.TextField(
            label="تاریخ شمسی",
            value=self.current_date,
            prefix_icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
            text_align=ft.TextAlign.CENTER,
            border_radius=14,
            rtl=False,
            hint_text="YYYY/MM/DD",
        )
        
        self.category_chips_container = ft.Column(spacing=8)
        self.account_chips_container = ft.Column(spacing=8)
        self.container = ft.Container(expand=True)

    def on_amount_changed(self, e):
        raw_val = self.amount_input.value.replace(",", "").strip()
        if raw_val.isdigit() and int(raw_val) > 0:
            num = int(raw_val)
            self.amount_input.helper = f"معادل: {format_price(num, persian_digits=True)}"
        else:
            self.amount_input.helper = ""
        self.page.update()

    def set_type(self, t_type: str):
        self.current_type = t_type
        self.selected_category_id = None
        self.update_categories_ui()
        self.update_accounts_ui()
        self.update_type_toggle_ui()
        self.page.update()

    def add_quick_amount(self, add_val: int):
        raw_val = self.amount_input.value.replace(",", "").strip()
        current = int(raw_val) if raw_val.isdigit() else 0
        new_val = current + add_val
        self.amount_input.value = str(new_val)
        self.amount_input.helper = f"معادل: {format_price(new_val, persian_digits=True)}"
        self.page.update()

    def select_category(self, cat_id: int):
        self.selected_category_id = cat_id
        self.update_categories_ui()
        self.page.update()

    def select_account(self, acc_id: int):
        self.selected_account_id = acc_id
        self.update_accounts_ui()
        self.page.update()

    def update_type_toggle_ui(self):
        is_expense = self.current_type == "expense"
        
        self.expense_btn.bgcolor = "#E11D48" if is_expense else ft.Colors.with_opacity(0.08, ft.Colors.GREY)
        self.expense_btn_text.color = ft.Colors.WHITE if is_expense else ft.Colors.GREY_500
        self.expense_btn_icon.color = ft.Colors.WHITE if is_expense else ft.Colors.GREY_500
        
        self.income_btn.bgcolor = "#0284C7" if not is_expense else ft.Colors.with_opacity(0.08, ft.Colors.GREY)
        self.income_btn_text.color = ft.Colors.WHITE if not is_expense else ft.Colors.GREY_500
        self.income_btn_icon.color = ft.Colors.WHITE if not is_expense else ft.Colors.GREY_500

    def update_accounts_ui(self):
        accounts = database.get_accounts()
        if not self.selected_account_id and accounts:
            self.selected_account_id = accounts[0]["id"]

        is_expense = self.current_type == "expense"
        title_text = "پرداخت از حساب / کارت:" if is_expense else "واریز به حساب / کارت:"

        chips = []
        for acc in accounts:
            is_selected = acc["id"] == self.selected_account_id
            acc_icon = get_icon(acc.get("icon") or "credit_card_rounded")
            acc_color = acc.get("color") or "#1E3A8A"
            
            chips.append(
                ft.Container(
                    on_click=lambda _, aid=acc["id"]: self.select_account(aid),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    border_radius=12,
                    bgcolor=acc_color if is_selected else ft.Colors.with_opacity(0.15, acc_color),
                    border=ft.Border.all(2, ft.Colors.WHITE if is_selected else ft.Colors.TRANSPARENT),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(
                                acc_icon, 
                                color=ft.Colors.WHITE if is_selected else ft.Colors.WHITE_70, 
                                size=16
                            ),
                            ft.Text(
                                acc["name"],
                                size=12,
                                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                                color=ft.Colors.WHITE if is_selected else (ft.Colors.WHITE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK_87),
                                rtl=True,
                            ),
                        ],
                    ),
                )
            )

        self.account_chips_container.controls = [
            ft.Text(title_text, size=13, weight=ft.FontWeight.BOLD, rtl=True),
            ft.ResponsiveRow(
                spacing=8,
                run_spacing=8,
                controls=[
                    ft.Container(c, col={"xs": 6, "sm": 4, "md": 4}) for c in chips
                ]
            )
        ]

    def update_categories_ui(self):
        categories = database.get_categories(self.current_type)
        if not self.selected_category_id and categories:
            self.selected_category_id = categories[0]["id"]

        chips = []
        for cat in categories:
            is_selected = cat["id"] == self.selected_category_id
            cat_icon = get_icon(cat["icon"])
            cat_color = cat["color"]
            
            chips.append(
                ft.Container(
                    on_click=lambda _, cid=cat["id"]: self.select_category(cid),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    border_radius=12,
                    bgcolor=cat_color if is_selected else ft.Colors.with_opacity(0.12, cat_color),
                    border=ft.Border.all(2, ft.Colors.WHITE if is_selected else ft.Colors.TRANSPARENT),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(
                                cat_icon, 
                                color=ft.Colors.WHITE if is_selected else cat_color, 
                                size=18
                            ),
                            ft.Text(
                                cat["name"],
                                size=12,
                                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                                color=ft.Colors.WHITE if is_selected else (ft.Colors.WHITE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK_87),
                                rtl=True,
                            ),
                        ],
                    ),
                )
            )

        self.category_chips_container.controls = [
            ft.Text("انتخاب دسته‌بندی:", size=13, weight=ft.FontWeight.BOLD, rtl=True),
            ft.ResponsiveRow(
                spacing=8,
                run_spacing=8,
                controls=[
                    ft.Container(c, col={"xs": 6, "sm": 4, "md": 3}) for c in chips
                ]
            )
        ]

    def save_transaction(self, e):
        raw_val = self.amount_input.value.replace(",", "").strip()
        if not raw_val.isdigit() or int(raw_val) <= 0:
            self.amount_input.error = "لطفاً مبلغ معتبر وارد کنید."
            self.page.update()
            return
        
        self.amount_input.error = None
        amount = float(raw_val)
        
        if not self.selected_category_id:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("لطفاً یک دسته‌بندی انتخاب کنید.", rtl=True),
                bgcolor=ft.Colors.RED_700
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        date_val = self.date_input.value.strip()
        if len(date_val.split('/')) != 3:
            self.date_input.error = "فرمت تاریخ باید YYYY/MM/DD باشد"
            self.page.update()
            return
        self.date_input.error = None
        
        database.add_transaction(
            t_type=self.current_type,
            amount=amount,
            category_id=self.selected_category_id,
            account_id=self.selected_account_id,
            date_str=date_val,
            description=self.desc_input.value or ""
        )
        
        self.amount_input.value = ""
        self.amount_input.helper = ""
        self.desc_input.value = ""
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(
                f"{'ورودی (درآمد)' if self.current_type == 'income' else 'خروجی (هزینه)'} با موفقیت ثبت شد.",
                rtl=True
            ),
            bgcolor=ft.Colors.GREEN_700
        )
        self.page.snack_bar.open = True
        self.page.update()
        
        self.on_saved_callback()

    def render(self):
        self.expense_btn_icon = ft.Icon(ft.Icons.ARROW_UPWARD_ROUNDED, size=20, color=ft.Colors.WHITE)
        self.expense_btn_text = ft.Text("خروجی (هزینه)", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.WHITE, rtl=True)
        self.expense_btn = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(vertical=12),
            border_radius=12,
            bgcolor="#E11D48",
            on_click=lambda _: self.set_type("expense"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    self.expense_btn_icon,
                    self.expense_btn_text,
                ],
            ),
        )

        self.income_btn_icon = ft.Icon(ft.Icons.ARROW_DOWNWARD_ROUNDED, size=20, color=ft.Colors.GREY_500)
        self.income_btn_text = ft.Text("ورودی (درآمد)", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREY_500, rtl=True)
        self.income_btn = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(vertical=12),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.GREY),
            on_click=lambda _: self.set_type("income"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    self.income_btn_icon,
                    self.income_btn_text,
                ],
            ),
        )

        type_toggle = ft.Container(
            padding=4,
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
            content=ft.Row(
                spacing=6,
                controls=[self.expense_btn, self.income_btn],
            ),
        )

        quick_amounts = [
            ("۵۰ هزار", 50000),
            ("۱۰۰ هزار", 100000),
            ("۵۰۰ هزار", 500000),
            ("۱ میلیون", 1000000),
            ("۵ میلیون", 5000000),
        ]
        
        quick_chips = [
            ft.Chip(
                label=ft.Text(label, size=11, rtl=True),
                on_click=lambda _, v=val: self.add_quick_amount(v),
            )
            for label, val in quick_amounts
        ]
        
        quick_amounts_row = ft.Row(
            wrap=True,
            spacing=6,
            controls=[
                ft.Text("مبالغ سریع:", size=11, color=ft.Colors.GREY_500, rtl=True),
                *quick_chips,
            ],
        )

        self.update_accounts_ui()
        self.update_categories_ui()
        self.update_type_toggle_ui()

        submit_btn = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=22),
                    ft.Text("ثبت تراکنش", size=16, weight=ft.FontWeight.BOLD, rtl=True),
                ],
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(vertical=16),
                shape=ft.RoundedRectangleBorder(radius=14),
            ),
            on_click=self.save_transaction,
        )

        self.container.content = ft.ListView(
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=12, bottom=90),
            controls=[
                type_toggle,
                ft.Container(height=14),
                self.amount_input,
                ft.Container(height=4),
                quick_amounts_row,
                ft.Container(height=14),
                self.account_chips_container,
                ft.Container(height=14),
                self.category_chips_container,
                ft.Container(height=14),
                self.date_input,
                ft.Container(height=12),
                self.desc_input,
                ft.Container(height=20),
                submit_btn,
            ],
        )
        return self.container
