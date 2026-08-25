import flet as ft
import database
from utils.persian_date import format_price, to_persian_digits, get_current_jalali_str
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
        selected_color_ref = {"val": AVAILABLE_COLORS[2]}

        type_buttons = []
        for atype_key, atype_title, atype_icon in ACCOUNT_TYPES:
            def make_type_btn(k=atype_key, t=atype_title, ic=atype_icon):
                return ft.Chip(
                    label=ft.Text(t, size=11, rtl=True),
                    leading=ft.Icon(ic, size=16),
                    selected=selected_type_ref["val"] == k,
                    on_select=lambda ev, key=k: select_type(key),
                )
            type_buttons.append(make_type_btn())

        def select_type(k):
            selected_type_ref["val"] = k
            for idx, (tk, _, _) in enumerate(ACCOUNT_TYPES):
                type_buttons[idx].selected = selected_type_ref["val"] == tk
            self.page.update()

        color_controls = []
        for col in AVAILABLE_COLORS:
            def make_color_btn(c=col):
                return ft.Container(
                    width=28,
                    height=28,
                    border_radius=14,
                    bgcolor=c,
                    border=ft.Border.all(2, ft.Colors.WHITE if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT),
                    on_click=lambda ev, color=c: select_color(color),
                )
            color_controls.append(make_color_btn())

        def select_color(c):
            selected_color_ref["val"] = c
            for idx, col in enumerate(AVAILABLE_COLORS):
                color_controls[idx].border = ft.Border.all(3, ft.Colors.PRIMARY if selected_color_ref["val"] == col else ft.Colors.TRANSPARENT)
            self.page.update()

        type_row = ft.Row(wrap=True, spacing=6, controls=type_buttons)
        colors_row = ft.Row(wrap=True, spacing=6, controls=color_controls)

        def confirm_add(ev):
            name = name_input.value.strip()
            if not name:
                name_input.error = "نام حساب را وارد کنید"
                self.page.update()
                return
            
            raw_balance = initial_balance_input.value.replace(",", "").strip()
            initial_balance = float(raw_balance) if raw_balance.isdigit() else 0.0

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

    def show_edit_account_dialog(self, acc: dict):
        name_input = ft.TextField(
            label="نام حساب",
            value=acc["name"],
            border_radius=12,
            rtl=True,
            autofocus=True,
        )
        card_num_input = ft.TextField(
            label="۴ رقم آخر کارت",
            value=acc.get("card_number") or "",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=4,
            text_align=ft.TextAlign.CENTER,
        )
        initial_balance_input = ft.TextField(
            label="موجودی اولیه (تومان)",
            value=str(int(acc.get("initial_balance") or 0)),
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
            rtl=True,
        )

        selected_color_ref = {"val": acc.get("color") or AVAILABLE_COLORS[0]}

        color_controls = []
        for col in AVAILABLE_COLORS:
            def make_color_btn(c=col):
                return ft.Container(
                    width=28,
                    height=28,
                    border_radius=14,
                    bgcolor=c,
                    border=ft.Border.all(3, ft.Colors.PRIMARY if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT),
                    on_click=lambda ev, color=c: select_color(color),
                )
            color_controls.append(make_color_btn())

        def select_color(c):
            selected_color_ref["val"] = c
            for idx, col in enumerate(AVAILABLE_COLORS):
                color_controls[idx].border = ft.Border.all(3, ft.Colors.PRIMARY if selected_color_ref["val"] == col else ft.Colors.TRANSPARENT)
            self.page.update()

        colors_row = ft.Row(wrap=True, spacing=6, controls=color_controls)

        def confirm_save(ev):
            name = name_input.value.strip()
            if not name:
                name_input.error = "نام حساب را وارد کنید"
                self.page.update()
                return

            raw_balance = initial_balance_input.value.replace(",", "").strip()
            initial_balance = float(raw_balance) if raw_balance.isdigit() else 0.0

            database.update_account(
                acc_id=acc["id"],
                name=name,
                acc_type=acc["type"],
                initial_balance=initial_balance,
                card_number=card_num_input.value.strip(),
                color=selected_color_ref["val"],
                icon=acc["icon"]
            )
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_accounts_changed()

            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"حساب «{name}» به‌روزرسانی شد.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("ویرایش حساب / کارت", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=360,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        name_input,
                        card_num_input,
                        initial_balance_input,
                        ft.Text("رنگ کارت:", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        colors_row,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("ذخیره تغییرات", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_transfer_dialog(self, e):
        accounts = database.get_accounts()
        if len(accounts) < 2:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("برای انتقال وجه، حداقل به ۲ حساب نیاز دارید.", rtl=True),
                bgcolor=ft.Colors.AMBER_700
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        from_acc_ref = {"id": accounts[0]["id"]}
        to_acc_ref = {"id": accounts[1]["id"]}

        from_dropdown = ft.Dropdown(
            label="از حساب (مبدأ)",
            value=str(from_acc_ref["id"]),
            options=[ft.dropdown.Option(str(a["id"]), f"{a['name']} ({format_price(a['current_balance'])})") for a in accounts],
            border_radius=12,
            rtl=True,
        )

        to_dropdown = ft.Dropdown(
            label="به حساب (مقصد)",
            value=str(to_acc_ref["id"]),
            options=[ft.dropdown.Option(str(a["id"]), f"{a['name']} ({format_price(a['current_balance'])})") for a in accounts],
            border_radius=12,
            rtl=True,
        )

        amount_input = ft.TextField(
            label="مبلغ انتقال (تومان)",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
            rtl=True,
        )
        desc_input = ft.TextField(
            label="توضیحات انتقال (اختیاری)",
            border_radius=12,
            rtl=True,
        )

        def confirm_transfer(ev):
            from_id = int(from_dropdown.value)
            to_id = int(to_dropdown.value)
            if from_id == to_id:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("حساب مبدأ و مقصد نمی‌توانند یکسان باشند.", rtl=True),
                    bgcolor=ft.Colors.RED_700
                )
                self.page.snack_bar.open = True
                self.page.update()
                return

            raw_amt = amount_input.value.replace(",", "").strip()
            if not raw_amt.isdigit() or int(raw_amt) <= 0:
                amount_input.error = "مبلغ معتبر وارد کنید"
                self.page.update()
                return

            amount = float(raw_amt)
            today_str = get_current_jalali_str()

            success = database.transfer_money(
                from_account_id=from_id,
                to_account_id=to_id,
                amount=amount,
                date_str=today_str,
                description=desc_input.value or ""
            )

            if success:
                dialog.open = False
                self.page.update()
                self.update_content()
                self.on_accounts_changed()

                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("انتقال وجه با موفقیت انجام و ثبت شد.", rtl=True),
                    bgcolor=ft.Colors.GREEN_700
                )
                self.page.snack_bar.open = True
                self.page.update()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("انتقال وجه بین کارت‌ها و حساب‌ها", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=360,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        from_dropdown,
                        to_dropdown,
                        amount_input,
                        desc_input,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("انتقال وجه", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_transfer),
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
            content=ft.Text(f"آیا از حذف کامل حساب «{acc['name']}» اطمینان دارید؟", rtl=True),
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
        acc_color = acc.get("color") or "#1E3A8A"
        acc_icon = get_icon(acc.get("icon") or "credit_card_rounded")
        balance = acc.get("current_balance") or 0.0
        card_num = acc.get("card_number")

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
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
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
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_ROUNDED,
                                        icon_color=ft.Colors.WHITE_70,
                                        icon_size=18,
                                        tooltip="ویرایش حساب",
                                        on_click=lambda _, a=acc: self.show_edit_account_dialog(a),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                        icon_color=ft.Colors.WHITE_70,
                                        icon_size=18,
                                        tooltip="حذف حساب",
                                        on_click=lambda _, a=acc: self.delete_account_item(a),
                                    ),
                                ],
                            ),
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

        # Total Net Worth Glassmorphic Top Banner
        total_card = ft.Container(
            padding=ft.Padding.symmetric(horizontal=20, vertical=18),
            border_radius=20,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#0F172A", "#1E293B"] if self.page.theme_mode == ft.ThemeMode.DARK else ["#1E3A8A", "#2563EB"],
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.WHITE)),
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

        action_buttons_row = ft.Row(
            spacing=8,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.ADD_CARD_ROUNDED, size=18),
                                ft.Text("کارت جدید", weight=ft.FontWeight.BOLD, size=13, rtl=True),
                            ],
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.WHITE,
                            padding=ft.Padding.symmetric(vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=14),
                        ),
                        on_click=self.show_add_account_dialog,
                    ),
                ),
                ft.Container(
                    expand=True,
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.SWAP_HORIZ_ROUNDED, size=20),
                                ft.Text("انتقال وجه", weight=ft.FontWeight.BOLD, size=13, rtl=True),
                            ],
                        ),
                        style=ft.ButtonStyle(
                            bgcolor="#0284C7",
                            color=ft.Colors.WHITE,
                            padding=ft.Padding.symmetric(vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=14),
                        ),
                        on_click=self.show_transfer_dialog,
                    ),
                ),
            ],
        )

        account_cards = [self.build_account_card(acc) for acc in accounts]

        self.container.content = ft.ListView(
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=12, bottom=90),
            controls=[
                total_card,
                ft.Container(height=12),
                action_buttons_row,
                ft.Container(height=16),
                ft.Text("کارت‌ها و صندوق‌های من", size=15, weight=ft.FontWeight.BOLD, rtl=True),
                ft.Container(height=10),
                *account_cards,
            ],
        )
        if self.page:
            self.page.update()
