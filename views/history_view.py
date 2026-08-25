import flet as ft
import database
from utils.persian_date import (
    to_persian_digits,
    format_price,
    format_jalali_display
)
from utils.icons_helper import get_icon

class HistoryView:
    def __init__(self, page: ft.Page, on_data_changed):
        self.page = page
        self.on_data_changed = on_data_changed
        self.filter_type = "all" # 'all', 'income', 'expense'
        self.search_query = ""
        self.container = ft.Container(expand=True)

    def set_filter(self, f_type: str):
        self.filter_type = f_type
        self.update_content()

    def on_search_changed(self, e):
        self.search_query = e.control.value.strip().lower()
        self.update_content()

    def delete_item(self, t_id: int):
        def confirm_delete(e):
            database.delete_transaction(t_id)
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_data_changed()
            
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

    def build_transaction_tile(self, item: dict):
        is_income = item["type"] == "income"
        amount_sign = "+" if is_income else "-"
        amount_color = ft.Colors.GREEN_400 if is_income else ft.Colors.RED_400
        cat_color = item.get("category_color") or ("#10B981" if is_income else "#EF4444")
        cat_icon = get_icon(item.get("category_icon"))
        
        return ft.Container(
            margin=ft.Margin.only(bottom=8),
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.PRIMARY) if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE)),
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
                                        format_jalali_display(item["date"]) + (f" • {item['description']}" if item.get("description") else ""),
                                        size=11,
                                        color=ft.Colors.GREY_500,
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
        self.update_content()
        return self.container

    def update_content(self):
        t_type = self.filter_type if self.filter_type != "all" else None
        all_transactions = database.get_transactions(t_type=t_type, limit=200)

        # Apply search filter
        if self.search_query:
            filtered = []
            for t in all_transactions:
                desc = (t.get("description") or "").lower()
                cname = (t.get("category_name") or "").lower()
                date_str = (t.get("date") or "").lower()
                if self.search_query in desc or self.search_query in cname or self.search_query in date_str:
                    filtered.append(t)
            transactions = filtered
        else:
            transactions = all_transactions

        # Filter Chips
        chips = [
            ft.Chip(
                label=ft.Text("همه تراکنش‌ها", rtl=True),
                selected=self.filter_type == "all",
                on_select=lambda _: self.set_filter("all"),
            ),
            ft.Chip(
                label=ft.Text("فقط ورودی‌ها (درآمد)", rtl=True),
                selected=self.filter_type == "income",
                selected_color=ft.Colors.GREEN_100,
                on_select=lambda _: self.set_filter("income"),
            ),
            ft.Chip(
                label=ft.Text("فقط خروجی‌ها (هزینه)", rtl=True),
                selected=self.filter_type == "expense",
                selected_color=ft.Colors.RED_100,
                on_select=lambda _: self.set_filter("expense"),
            ),
        ]

        search_bar = ft.TextField(
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            hint_text="جستجو در توضیحات یا دسته‌ها...",
            border_radius=14,
            on_change=self.on_search_changed,
            rtl=True,
        )

        tiles = [self.build_transaction_tile(t) for t in transactions]

        if not tiles:
            content_list = ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.all(40),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=48, color=ft.Colors.GREY_400),
                        ft.Text("موردی یافت نشد.", color=ft.Colors.GREY_500, size=14, rtl=True),
                    ],
                ),
            )
        else:
            content_list = ft.Column(controls=tiles, spacing=0)

        self.container.content = ft.ListView(
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=12, bottom=90),
            controls=[
                search_bar,
                ft.Container(height=10),
                ft.Row(wrap=True, spacing=6, controls=chips),
                ft.Container(height=14),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("تاریخچه تراکنش‌ها", size=15, weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Text(f"{to_persian_digits(str(len(transactions)))} تراکنش", size=12, color=ft.Colors.GREY_500, rtl=True),
                    ],
                ),
                ft.Container(height=8),
                content_list,
            ],
        )
        if self.page:
            self.page.update()
