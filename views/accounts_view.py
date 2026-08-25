import flet as ft
import database
from utils.persian_date import format_price, to_persian_digits
from utils.icons_helper import AVAILABLE_ICONS, AVAILABLE_COLORS, get_icon

ACCOUNT_TYPES = [
    ("bank_card", "کارت بانکی", ft.Icons.CREDIT_CARD_ROUNDED),
    ("cash", "کیف پول نقدی", ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED),
    ("savings", "صندوق / پس‌انداز", ft.Icons.SAVINGS_ROUNDED),
    ("crypto_gold", "طلا و دارایی", ft.Icons.DIAMOND_ROUNDED),
    ("other", "سایر دارایی‌ها", ft.Icons.FOLDER_SPECIAL_ROUNDED),
]

class AccountsView:
    def __init__(self, page: ft.Page, on_accounts_changed):
        self.page = page
        self.on_accounts_changed = on_accounts_changed
        self.container = ft.Container(expand=True)

    def show_add_account_dialog(self, e):
        name_input = ft.TextField(
            label="نام حساب یا بانک (مثلاً بانک ملت، صندوق)",
            border_radius=12,
            rtl=True,
            autofocus=True,
        )
        card_num_input = ft.TextField(
            label="۴ رقم آخر کارت (اختیاری)",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=4,
            text_align=ft.TextAlign.CENTER,
            hint_text="مثلاً ۶۰۳۷",
        )
        initial_balance_input = ft.TextField(
            label="موجودی اولیه (تومان)",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
            value="0",
            rtl=True,
        )

        selected_type_ref = {"val": ACCOUNT_TYPES[0][0]}
        selected_icon_ref = {"val": "credit_card_rounded"}
        selected_color_ref = {"val": AVAILABLE_COLORS[2]} # Blue

        # Type buttons
        type_buttons = []
        for atype_key, atype_title, atype_icon in ACCOUNT_TYPES:
            def make_type_btn(k=atype_key, t=atype_title, ic=atype_icon):
                def select_type(ev):
                    selected_type_ref["val"] = k
                    update_acc_dialog_ui()
                return ft.Chip(
                    label=ft.Text(t, size=11, rtl=True),
                    leading=ft.Icon(ic, size=16),
                    selected=selected_type_ref["val"] == k,
                    on_select=select_type,
                )
            type_buttons.append(make_type_btn())

        # Colors grid selector
        color_controls = []
        for col in AVAILABLE_COLORS:
            def make_color_btn(c=col):
                def select_color(ev):
                    selected_color_ref["val"] = c
                    update_acc_dialog_ui()
                return ft.Container(
                    width=28,
                    height=28,
                    border_radius=14,
                    bgcolor=c,
                    border=ft.Border.all(2, ft.Colors.WHITE if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT),
                    on_click=select_color,
                )
            color_controls.append(make_color_btn())

        type_row = ft.Row(wrap=True, spacing=6, controls=type_buttons)
        colors_row = ft.Row(wrap=True, spacing=6, controls=color_controls)

        def update_acc_dialog_ui():
            for idx, (k, _, _) in enumerate(ACCOUNT_TYPES):
                type_buttons[idx].selected = selected_type_ref["val"] == k
            for idx, c in enumerate(AVAILABLE_COLORS):
                color_controls[idx].border = ft.Border.all(3, ft.Colors.PRIMARY if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT)
            self.page.update()

        def confirm_add(ev):
            name = name_input.value.strip()
            if not name:
                name_input.error = "لطفاً نام حساب را وارد کنید"
                self.page.update()
                return
            
            raw_balance = initial_balance_input.value.replace(",", "").strip()
            initial_balance = float(raw_balance) if raw_balance.isdigit() else 0.0

            # Determine default icon based on type
            icon_name = "credit_card_rounded"
            if selected_type_ref["val"] == "cash":
                icon_name = "account_balance_wallet_rounded"
            elif selected_type_ref["val"] == "savings":
                icon_name = "savings_rounded"
            elif selected_type_ref["val"] == "crypto_gold":
                icon_name = "diamond_rounded"
            elif selected_type_ref["val"] == "other":
                icon_name = "folder_special_rounded"

            database.add_account(
                name=name,
                acc_type=selected_type_ref["val"],
                initial_balance=initial_balance,
                card_number=card_num_input.value.strip(),
                color=selected_color_ref["val"],
                icon=icon_name,
            )

            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_accounts_changed()

            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"حساب «{name}» با موفقیت اضافه شد.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("تعریف حساب یا کارت جدید", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=360,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        name_input,
                        card_num_input,
                        initial_balance_input,
                        ft.Text("نوع حساب / دارایی:", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        type_row,
                        ft.Text("رنگ کارت:", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        colors_row,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("ثبت حساب", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def delete_account_item(self, acc: dict):
        def confirm_del(e):
            database.delete_account(acc["id"])
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_accounts_changed()

            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("حساب با موفقیت حذف شد.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("حذف حساب", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Text(f"آیا از حذف حساب «{acc['name']}» اطمینان دارید؟", rtl=True),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("بله، حذف کن", bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, on_click=confirm_del),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def build_account_card(self, acc: dict):
        acc_color = acc.get("color") or "#3B82F6"
        acc_icon = get_icon(acc.get("icon") or "credit_card_rounded")
        balance = acc.get("current_balance") or 0.0
        card_num = acc.get("card_number")
        is_default = acc.get("is_default") == 1

        card_num_text = f"•••• {to_persian_digits(card_num)}" if card_num else "حساب / صندوق"

        return ft.Container(
            margin=ft.Margin.only(bottom=12),
            padding=ft.Padding.symmetric(horizontal=18, vertical=16),
            border_radius=18,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_RIGHT,
                end=ft.Alignment.BOTTOM_LEFT,
                colors=[acc_color, acc_color + "CC"],
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(acc_icon, color=ft.Colors.WHITE, size=22),
                                        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                                        border_radius=12,
                                        padding=8,
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(acc["name"], color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=15, rtl=True),
                                            ft.Text(card_num_text, color=ft.Colors.WHITE_70, size=11, rtl=True),
                                        ],
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.WHITE_70,
                                icon_size=20,
                                tooltip="حذف حساب",
                                visible=not is_default,
                                on_click=lambda _, a=acc: self.delete_account_item(a),
                            ) if not is_default else ft.Container(),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("موجودی فعلی", color=ft.Colors.WHITE_70, size=11, rtl=True),
                                    ft.Text(
                                        format_price(balance, persian_digits=True),
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD,
                                        size=18,
                                        rtl=True,
                                    ),
                                ],
                            ),
                            ft.Container(
                                content=ft.Text("فعال", color=ft.Colors.WHITE, size=10, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                border_radius=10,
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
        accounts = database.get_accounts()
        total_net_worth = database.get_total_net_worth()

        # Total Net Worth Top Banner
        total_card = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=18),
            border_radius=20,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#0F172A", "#1E293B"] if self.page.theme_mode == ft.ThemeMode.DARK else ["#1E3A8A", "#3B82F6"],
            ),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=14,
                color=ft.Colors.with_opacity(0.25, ft.Colors.PRIMARY),
                offset=ft.Offset(0, 6),
            ),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("مجموع کل موجودی و دارایی‌ها", size=13, color=ft.Colors.WHITE_70, rtl=True),
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_ROUNDED, color=ft.Colors.WHITE_70, size=20),
                        ],
                    ),
                    ft.Text(
                        format_price(total_net_worth, persian_digits=True),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        rtl=True,
                    ),
                    ft.Text(
                        f"شامل {to_persian_digits(str(len(accounts)))} کارت و صندوق دارایی",
                        size=11,
                        color=ft.Colors.WHITE_60,
                        rtl=True,
                    ),
                ],
            ),
        )

        add_account_btn = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.ADD_CARD_ROUNDED, size=20),
                    ft.Text("افزودن کارت بانکی یا صندوق جدید", weight=ft.FontWeight.BOLD, rtl=True),
                ],
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(vertical=14),
                shape=ft.RoundedRectangleBorder(radius=14),
            ),
            on_click=self.show_add_account_dialog,
        )

        account_cards = [self.build_account_card(acc) for acc in accounts]

        self.container.content = ft.ListView(
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=12, bottom=90),
            controls=[
                total_card,
                ft.Container(height=14),
                add_account_btn,
                ft.Container(height=16),
                ft.Text("کارت‌ها و صندوق‌های من", size=15, weight=ft.FontWeight.BOLD, rtl=True),
                ft.Container(height=10),
                *account_cards,
            ],
        )
        if self.page:
            self.page.update()
