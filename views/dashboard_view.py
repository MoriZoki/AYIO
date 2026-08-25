import flet as ft
import database
from utils.persian_date import (
    to_persian_digits,
    format_price,
    get_current_jalali,
    get_month_name,
    format_jalali_display
)
from utils.icons_helper import get_icon

class DashboardView:
    def __init__(self, page: ft.Page, on_navigate_add, on_navigate_accounts, on_navigate_tools, on_refresh_all):
        self.page = page
        self.on_navigate_add = on_navigate_add
        self.on_navigate_accounts = on_navigate_accounts
        self.on_navigate_tools = on_navigate_tools
        self.on_refresh_all = on_refresh_all
        
        current_j = get_current_jalali()
        self.selected_year = current_j.year
        self.selected_month = current_j.month
        
    def prev_month(self, e):
        if self.selected_month == 1:
            self.selected_month = 12
            self.selected_year -= 1
        else:
            self.selected_month -= 1
        self.update_content()
        
    def next_month(self, e):
        if self.selected_month == 12:
            self.selected_month = 1
            self.selected_year += 1
        else:
            self.selected_month += 1
        self.update_content()

    def go_to_current_month(self, e):
        curr = get_current_jalali()
        self.selected_year = curr.year
        self.selected_month = curr.month
        self.update_content()

    def delete_item(self, t_id: int):
        def confirm_delete(e):
            database.delete_transaction(t_id)
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_refresh_all()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("تراکنش با موفقیت حذف شد.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel_delete(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("حذف تراکنش", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Text("آیا از حذف این مورد اطمینان دارید؟", rtl=True),
            actions=[
                ft.TextButton("انصراف", on_click=cancel_delete),
                ft.ElevatedButton("بله، حذف کن", bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def build_summary_card(self, title: str, amount: float, icon, bg_color: str, text_color: str, subtitle: str = ""):
        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_RIGHT,
                end=ft.Alignment.BOTTOM_LEFT,
                colors=[bg_color, bg_color + "DD"],
            ),
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            content=ft.Column(
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, color=text_color, size=22),
                                bgcolor=ft.Colors.with_opacity(0.2, text_color),
                                border_radius=10,
                                padding=6,
                            ),
                            ft.Text(title, size=12, color=text_color, weight=ft.FontWeight.W_600, rtl=True),
                        ],
                    ),
                    ft.Text(
                        format_price(amount, persian_digits=True),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK_87,
                        rtl=True,
                    ),
                    ft.Text(subtitle, size=11, color=ft.Colors.GREY_400, rtl=True) if subtitle else ft.Container(),
                ],
            ),
        )

    def build_mini_account_card(self, acc: dict):
        acc_color = acc.get("color") or "#1E3A8A"
        acc_icon = get_icon(acc.get("icon") or "credit_card_rounded")
        balance = acc.get("current_balance") or 0.0
        card_num = acc.get("card_number")
        
        return ft.Container(
            width=180,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            border_radius=16,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_RIGHT,
                end=ft.Alignment.BOTTOM_LEFT,
                colors=[acc_color, acc_color + "DD"],
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
            on_click=lambda _: self.on_navigate_accounts(),
            content=ft.Column(
                spacing=6,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Icon(acc_icon, color=ft.Colors.WHITE, size=18),
                            ft.Text(
                                f"•••• {to_persian_digits(card_num)}" if card_num else "",
                                size=10,
                                color=ft.Colors.WHITE_70,
                                rtl=True,
                            ),
                        ],
                    ),
                    ft.Text(
                        acc["name"],
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        rtl=True,
                    ),
                    ft.Text(
                        format_price(balance, persian_digits=True),
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        rtl=True,
                    ),
                ],
            ),
        )

    def build_transaction_tile(self, item: dict):
        is_income = item["type"] == "income"
        amount_sign = "+" if is_income else "-"
        amount_color = ft.Colors.CYAN_300 if is_income else ft.Colors.RED_400
        cat_color = item.get("category_color") or ("#0284C7" if is_income else "#EF4444")
        cat_icon = get_icon(item.get("category_icon"))
        account_name = item.get("account_name")
        
        subtitle_parts = [format_jalali_display(item["date"])]
        if account_name:
            subtitle_parts.append(account_name)
        if item.get("description"):
            subtitle_parts.append(item["description"])
            
        subtitle_text = " • ".join(subtitle_parts)
        
        return ft.Container(
            margin=ft.Margin.only(bottom=8),
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE_TINT) if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                content=ft.Icon(cat_icon, color=ft.Colors.WHITE, size=20),
                                bgcolor=cat_color,
                                border_radius=12,
                                width=42,
                                height=42,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                spacing=3,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        item.get("category_name") or ("ورودی" if is_income else "خروجی"),
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        rtl=True,
                                    ),
                                    ft.Text(
                                        subtitle_text,
                                        size=11,
                                        color=ft.Colors.GREY_400,
                                        rtl=True,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Text(
                                f"{amount_sign} {format_price(item['amount'], persian_digits=True)}",
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                color=amount_color,
                                rtl=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.GREY_400,
                                icon_size=18,
                                tooltip="حذف",
                                on_click=lambda _, tid=item["id"]: self.delete_item(tid),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def render(self):
        self.container = ft.Container(expand=True)
        self.update_content()
        return self.container

    def update_content(self):
        summary = database.get_monthly_summary(self.selected_year, self.selected_month)
        transactions = database.get_transactions(self.selected_year, self.selected_month, limit=50)
        accounts = database.get_accounts()
        total_net_worth = database.get_total_net_worth()
        
        month_name = get_month_name(self.selected_month)
        year_persian = to_persian_digits(str(self.selected_year))
        
        # 1. Total Net Worth Glassmorphic Banner
        net_worth_banner = ft.Container(
            padding=ft.Padding.symmetric(horizontal=18, vertical=16),
            border_radius=18,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#0F172A", "#1E293B"] if self.page.theme_mode == ft.ThemeMode.DARK else ["#1E3A8A", "#2563EB"],
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.25, ft.Colors.PRIMARY),
                offset=ft.Offset(0, 5),
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, color=ft.Colors.WHITE_70, size=16),
                                    ft.Text("موجودی کل کنونی (کارت‌ها و صندوق)", size=12, color=ft.Colors.WHITE_70, rtl=True),
                                ],
                            ),
                            ft.Text(
                                format_price(total_net_worth, persian_digits=True),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                                rtl=True,
                            ),
                        ],
                    ),
                    ft.ElevatedButton(
                        content=ft.Row(
                            spacing=4,
                            controls=[
                                ft.Icon(ft.Icons.CREDIT_CARD_ROUNDED, size=16, color=ft.Colors.WHITE),
                                ft.Text("کارت‌ها", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, rtl=True),
                            ],
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                        ),
                        on_click=lambda _: self.on_navigate_accounts(),
                    ),
                ],
            ),
        )

        # 2. Horizontal Mini Accounts Carousel
        accounts_scroll_row = ft.Row(
            spacing=10,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[self.build_mini_account_card(acc) for acc in accounts],
        )

        # 3. Month Header Selector
        month_selector = ft.Container(
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            margin=ft.Margin.only(bottom=12),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
            border_radius=16,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
                        icon_size=26,
                        tooltip="ماه قبل",
                        on_click=self.prev_month,
                    ),
                    ft.Container(
                        on_click=self.go_to_current_month,
                        tooltip="بازگشت به ماه جاری",
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=20, color=ft.Colors.PRIMARY),
                                ft.Text(
                                    f"{month_name} {year_persian}",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    rtl=True,
                                ),
                            ],
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
                        icon_size=26,
                        tooltip="ماه بعد",
                        on_click=self.next_month,
                    ),
                ],
            ),
        )

        # Summary Cards (Income & Expense)
        income_card = self.build_summary_card(
            title="ورودی‌های این ماه",
            amount=summary["income"],
            icon=ft.Icons.ARROW_DOWNWARD_ROUNDED,
            bg_color="#0F766E" if self.page.theme_mode == ft.ThemeMode.DARK else "#CCFBF1",
            text_color="#2DD4BF" if self.page.theme_mode == ft.ThemeMode.DARK else "#0F766E",
        )
        
        expense_card = self.build_summary_card(
            title="خروجی‌های این ماه",
            amount=summary["expense"],
            icon=ft.Icons.ARROW_UPWARD_ROUNDED,
            bg_color="#881337" if self.page.theme_mode == ft.ThemeMode.DARK else "#FFE4E6",
            text_color="#FB7185" if self.page.theme_mode == ft.ThemeMode.DARK else "#BE123C",
        )

        # Monthly Balance Card
        balance = summary["balance"]
        balance_card = ft.Container(
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(f"تراز عملکرد {month_name}:", size=13, color=ft.Colors.GREY_400, rtl=True),
                    ft.Text(
                        f"{'+' if balance >= 0 else ''}{format_price(balance, persian_digits=True)}",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.CYAN_300 if balance >= 0 else ft.Colors.RED_400,
                        rtl=True,
                    ),
                ],
            ),
        )

        # Transactions List or Empty State
        if not transactions:
            transactions_content = ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.all(30),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=56, color=ft.Colors.GREY_400),
                        ft.Text(
                            f"هنوز تراکنشی در {month_name} ثبت نشده است.",
                            size=14,
                            color=ft.Colors.GREY_500,
                            rtl=True,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                                    ft.Text("ثبت اولین ورودی یا خروجی", weight=ft.FontWeight.BOLD, rtl=True),
                                ],
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.PRIMARY,
                                color=ft.Colors.WHITE,
                                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                            on_click=lambda _: self.on_navigate_add(),
                        ),
                    ],
                ),
            )
        else:
            transaction_tiles = [self.build_transaction_tile(t) for t in transactions]
            transactions_content = ft.Column(
                spacing=0,
                controls=transaction_tiles,
            )

        # Quick Tools Bar
        tools_shortcut_btn = ft.Container(
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY)),
            on_click=lambda _: self.on_navigate_tools(),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=ft.Colors.AMBER_400, size=20),
                            ft.Text("ابزارهای مالی (اقساط و وام، طلب‌ها و بدهی‌ها)", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        ],
                    ),
                    ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, size=14, color=ft.Colors.GREY_400),
                ],
            ),
        )

        # Assembling view
        self.container.content = ft.ListView(
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=12, bottom=80),
            controls=[
                net_worth_banner,
                ft.Container(height=12),
                tools_shortcut_btn,
                ft.Container(height=12),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("کارت‌ها و صندوق‌ها", size=14, weight=ft.FontWeight.BOLD, rtl=True),
                        ft.TextButton(
                            "مدیریت همه",
                            on_click=lambda _: self.on_navigate_accounts(),
                        ),
                    ],
                ),
                accounts_scroll_row,
                ft.Container(height=14),
                month_selector,
                ft.Row(
                    spacing=12,
                    controls=[income_card, expense_card],
                ),
                ft.Container(height=10),
                balance_card,
                ft.Container(height=16),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"تراکنش‌های {month_name}", size=15, weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Text(
                            f"{to_persian_digits(str(len(transactions)))} مورد",
                            size=12,
                            color=ft.Colors.GREY_500,
                            rtl=True,
                        ),
                    ],
                ),
                ft.Container(height=10),
                transactions_content,
            ],
        )
        if self.page:
            self.page.update()
