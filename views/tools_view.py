import flet as ft
import database
from utils.persian_date import format_price, to_persian_digits, get_current_jalali_str, format_jalali_display

class ToolsView:
    def __init__(self, page: ft.Page, on_data_changed):
        self.page = page
        self.on_data_changed = on_data_changed
        self.current_tab = "loans" # 'loans', 'receivables', 'payables'
        self.container = ft.Container(expand=True)

    def set_tab(self, tab_name: str):
        self.current_tab = tab_name
        self.update_content()

    # --- LOAN DIALOGS ---
    def show_add_loan_dialog(self, e):
        title_input = ft.TextField(label="عنوان وام یا قسط (مثلاً وام مسکن)", border_radius=12, rtl=True, autofocus=True)
        total_amount_input = ft.TextField(label="مبلغ کل وام (تومان)", border_radius=12, keyboard_type=ft.KeyboardType.NUMBER, rtl=True)
        monthly_amount_input = ft.TextField(label="مبلغ هر قسط (تومان)", border_radius=12, keyboard_type=ft.KeyboardType.NUMBER, rtl=True)
        total_installments_input = ft.TextField(label="تعداد کل اقساط (مثلاً ۳۶)", border_radius=12, keyboard_type=ft.KeyboardType.NUMBER, rtl=True)
        paid_installments_input = ft.TextField(label="اقساط پرداخت‌شده تا الان", value="0", border_radius=12, keyboard_type=ft.KeyboardType.NUMBER, rtl=True)
        due_day_input = ft.TextField(label="روز سررسید هر ماه (۱ تا ۳۱)", value="۱", border_radius=12, keyboard_type=ft.KeyboardType.NUMBER, rtl=True)

        def confirm_add(ev):
            title = title_input.value.strip()
            if not title:
                title_input.error = "عنوان وام را وارد کنید"
                self.page.update()
                return
                
            raw_monthly = monthly_amount_input.value.replace(",", "").strip()
            if not raw_monthly.isdigit() or int(raw_monthly) <= 0:
                monthly_amount_input.error = "مبلغ هر قسط را وارد کنید"
                self.page.update()
                return

            raw_total = total_amount_input.value.replace(",", "").strip()
            total_amount = float(raw_total) if raw_total.isdigit() else 0.0
            
            raw_inst = total_installments_input.value.strip()
            total_inst = int(raw_inst) if raw_inst.isdigit() and int(raw_inst) > 0 else 12
            
            raw_paid = paid_installments_input.value.strip()
            paid_inst = int(raw_paid) if raw_paid.isdigit() else 0
            
            raw_day = due_day_input.value.strip()
            due_day = int(raw_day) if raw_day.isdigit() and 1 <= int(raw_day) <= 31 else 1

            if total_amount == 0.0:
                total_amount = float(raw_monthly) * total_inst

            database.add_loan(
                title=title,
                total_amount=total_amount,
                monthly_amount=float(raw_monthly),
                total_installments=total_inst,
                paid_installments=paid_inst,
                due_day=due_day,
            )
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_data_changed()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"وام «{title}» با موفقیت ثبت شد.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("تعریف وام و قسط جدید", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=360,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        title_input,
                        monthly_amount_input,
                        total_amount_input,
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Container(total_installments_input, expand=True),
                                ft.Container(paid_installments_input, expand=True),
                            ],
                        ),
                        due_day_input,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("ثبت وام", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_pay_installment_dialog(self, loan: dict):
        accounts = database.get_accounts()
        selected_acc_ref = {"id": accounts[0]["id"] if accounts else None}
        
        acc_chips = []
        for acc in accounts:
            def make_chip(a=acc):
                return ft.Chip(
                    label=ft.Text(a["name"], size=11, rtl=True),
                    selected=selected_acc_ref["id"] == a["id"],
                    on_select=lambda ev, aid=a["id"]: select_acc(aid),
                )
            acc_chips.append(make_chip())

        def select_acc(aid):
            selected_acc_ref["id"] = aid
            for idx, a in enumerate(accounts):
                acc_chips[idx].selected = selected_acc_ref["id"] == a["id"]
            self.page.update()

        def confirm_pay(ev):
            today_str = get_current_jalali_str()
            database.pay_loan_installment(loan["id"], selected_acc_ref["id"], today_str)
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_data_changed()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"قسط وام «{loan['title']}» ثبت و از حساب کسر گردید.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("پرداخت قسط وام", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=340,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text(f"وام: {loan['title']}", weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Text(f"مبلغ قسط: {format_price(loan['monthly_amount'])}", size=14, color=ft.Colors.AMBER_400, rtl=True),
                        ft.Text("پرداخت از کدام کارت / حساب؟", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Row(wrap=True, spacing=6, controls=acc_chips),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("ثبت پرداخت قسط", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_pay),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def delete_loan_item(self, loan: dict):
        def confirm_del(e):
            database.delete_loan(loan["id"])
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_data_changed()

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("حذف وام", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Text(f"آیا از حذف وام «{loan['title']}» اطمینان دارید؟", rtl=True),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("بله، حذف کن", bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, on_click=confirm_del),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    # --- DEBT / RECEIVABLE DIALOGS ---
    def show_add_debt_dialog(self, debt_type: str):
        is_rec = debt_type == "receivable"
        title_text = "ثبت طلب جدید (از دیگران)" if is_rec else "ثبت بدهی جدید (به دیگران)"
        
        person_input = ft.TextField(
            label="نام شخص یا سازمان",
            border_radius=12,
            rtl=True,
            autofocus=True
        )
        amount_input = ft.TextField(
            label="مبلغ (تومان)",
            border_radius=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            rtl=True
        )
        date_input = ft.TextField(
            label="تاریخ سررسید یا موعد (اختیاری)",
            value=get_current_jalali_str(),
            border_radius=12,
            rtl=False,
            text_align=ft.TextAlign.CENTER
        )
        notes_input = ft.TextField(
            label="توضیحات و بابت (اختیاری)",
            border_radius=12,
            rtl=True
        )

        def confirm_add(ev):
            person = person_input.value.strip()
            if not person:
                person_input.error = "نام شخص را وارد کنید"
                self.page.update()
                return
                
            raw_amt = amount_input.value.replace(",", "").strip()
            if not raw_amt.isdigit() or int(raw_amt) <= 0:
                amount_input.error = "مبلغ معتبر وارد کنید"
                self.page.update()
                return

            database.add_debt(
                debt_type=debt_type,
                person_name=person,
                amount=float(raw_amt),
                due_date=date_input.value.strip(),
                notes=notes_input.value or ""
            )
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_data_changed()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{'طلب از' if is_rec else 'بدهی به'} «{person}» با موفقیت ثبت شد.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(title_text, weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=350,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        person_input,
                        amount_input,
                        date_input,
                        notes_input,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("ثبت", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_settle_debt_dialog(self, debt: dict):
        is_rec = debt["type"] == "receivable"
        title_text = "وصول طلب" if is_rec else "تسویه بدهی"
        accounts = database.get_accounts()
        selected_acc_ref = {"id": accounts[0]["id"] if accounts else None}
        
        acc_chips = []
        for acc in accounts:
            def make_chip(a=acc):
                return ft.Chip(
                    label=ft.Text(a["name"], size=11, rtl=True),
                    selected=selected_acc_ref["id"] == a["id"],
                    on_select=lambda ev, aid=a["id"]: select_acc(aid),
                )
            acc_chips.append(make_chip())

        def select_acc(aid):
            selected_acc_ref["id"] = aid
            for idx, a in enumerate(accounts):
                acc_chips[idx].selected = selected_acc_ref["id"] == a["id"]
            self.page.update()

        def confirm_settle(ev):
            today_str = get_current_jalali_str()
            database.settle_debt(debt["id"], selected_acc_ref["id"], today_str)
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_data_changed()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{'طلب' if is_rec else 'بدهی'} با موفقیت تسویه و در موجودی اعمال شد.", rtl=True),
                bgcolor=ft.Colors.GREEN_700
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(title_text, weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=340,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text(f"طرف حساب: {debt['person_name']}", weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Text(f"مبلغ: {format_price(debt['amount'])}", size=15, color=ft.Colors.CYAN_300 if is_rec else ft.Colors.RED_400, rtl=True),
                        ft.Text(f"{'واریز به کدام حساب؟' if is_rec else 'پرداخت از کدام حساب؟'}", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Row(wrap=True, spacing=6, controls=acc_chips),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("تأیید و تسویه", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_settle),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def delete_debt_item(self, debt: dict):
        def confirm_del(e):
            database.delete_debt(debt["id"])
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_data_changed()

        def cancel(e):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("حذف مورد", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Text(f"آیا از حذف این مورد اطمینان دارید؟", rtl=True),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("بله، حذف کن", bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, on_click=confirm_del),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    # --- UI BUILDERS ---
    def build_loan_card(self, loan: dict):
        total_inst = loan["total_installments"]
        paid_inst = loan["paid_installments"] or 0
        remaining_inst = max(0, total_inst - paid_inst)
        progress_val = paid_inst / total_inst if total_inst > 0 else 1.0
        remaining_amount = remaining_inst * loan["monthly_amount"]

        is_finished = remaining_inst == 0

        return ft.Container(
            margin=ft.Margin.only(bottom=12),
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            border_radius=18,
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.SURFACE_TINT) if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.OUTLINE)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.PAYMENTS_ROUNDED, color=ft.Colors.AMBER_400, size=22),
                                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.AMBER),
                                        border_radius=10,
                                        padding=6,
                                    ),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(loan["title"], size=15, weight=ft.FontWeight.BOLD, rtl=True),
                                            ft.Text(f"سررسید: هر ماه روز {to_persian_digits(str(loan.get('due_day', 1)))}", size=11, color=ft.Colors.GREY_400, rtl=True),
                                        ],
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.GREY_400,
                                icon_size=18,
                                on_click=lambda _, l=loan: self.delete_loan_item(l),
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"مبلغ قسط: {format_price(loan['monthly_amount'])}", size=13, weight=ft.FontWeight.W_600, rtl=True),
                            ft.Text(f"مانده: {format_price(remaining_amount)}", size=12, color=ft.Colors.RED_300 if not is_finished else ft.Colors.GREEN_400, rtl=True),
                        ],
                    ),
                    # Progress Bar
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"پرداخت شده: {to_persian_digits(str(paid_inst))} از {to_persian_digits(str(total_inst))} قسط", size=11, color=ft.Colors.GREY_400, rtl=True),
                                    ft.Text(f"{int(progress_val * 100)}%", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                                ],
                            ),
                            ft.ProgressBar(value=progress_val, color=ft.Colors.CYAN_400, bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREY)),
                        ],
                    ),
                    # Action button
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=18),
                                    ft.Text("ثبت پرداخت قسط این ماه", weight=ft.FontWeight.BOLD, size=13, rtl=True),
                                ],
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.PRIMARY,
                                color=ft.Colors.WHITE,
                                padding=ft.Padding.symmetric(vertical=10),
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                            disabled=is_finished,
                            on_click=lambda _, l=loan: self.show_pay_installment_dialog(l),
                        ) if not is_finished else ft.Container(
                            padding=ft.Padding.symmetric(vertical=6),
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text("✓ تمامی اقساط پرداخت و تسویه شده است", size=12, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, rtl=True),
                        ),
                    ),
                ],
            ),
        )

    def build_debt_card(self, debt: dict):
        is_rec = debt["type"] == "receivable"
        is_settled = debt.get("is_settled") == 1
        card_color = ft.Colors.CYAN_700 if is_rec else ft.Colors.RED_700
        status_text = "تسویه شده" if is_settled else ("در انتظار وصول" if is_rec else "پرداخت نشده")
        
        debt_controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.ARROW_DOWNWARD_ROUNDED if is_rec else ft.Icons.ARROW_UPWARD_ROUNDED,
                                    color=ft.Colors.WHITE,
                                    size=18,
                                ),
                                bgcolor=card_color,
                                border_radius=10,
                                padding=6,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(debt["person_name"], size=14, weight=ft.FontWeight.BOLD, rtl=True),
                                    ft.Text(f"موعد: {format_jalali_display(debt.get('due_date') or '')}", size=11, color=ft.Colors.GREY_400, rtl=True),
                                ],
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_color=ft.Colors.GREY_400,
                        icon_size=18,
                        on_click=lambda _, d=debt: self.delete_debt_item(d),
                    ),
                ],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        format_price(debt["amount"]),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.CYAN_300 if is_rec else ft.Colors.RED_400,
                        rtl=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            status_text,
                            size=11,
                            color=ft.Colors.GREEN_400 if is_settled else (ft.Colors.CYAN_200 if is_rec else ft.Colors.AMBER_300),
                            weight=ft.FontWeight.BOLD,
                            rtl=True,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREEN if is_settled else (ft.Colors.CYAN if is_rec else ft.Colors.AMBER)),
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=12,
                    ),
                ],
            ),
        ]

        if debt.get("notes"):
            debt_controls.append(ft.Text(debt["notes"], size=11, color=ft.Colors.GREY_400, rtl=True))

        if not is_settled:
            debt_controls.append(
                ft.ElevatedButton(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=16),
                            ft.Text("ثبت وصول طلب" if is_rec else "ثبت تسویه بدهی", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        ],
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.WHITE,
                        padding=ft.Padding.symmetric(vertical=8),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda _, d=debt: self.show_settle_debt_dialog(d),
                )
            )

        return ft.Container(
            margin=ft.Margin.only(bottom=10),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.SURFACE_TINT) if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.OUTLINE)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
            content=ft.Column(
                spacing=8,
                controls=debt_controls,
            ),
        )

    def render(self):
        self.update_content()
        return self.container

    def update_content(self):
        loans = database.get_loans()
        receivables = database.get_debts(debt_type="receivable")
        payables = database.get_debts(debt_type="payable")

        # Top Summary Card
        total_remaining_loans = sum(max(0, l["total_installments"] - (l["paid_installments"] or 0)) * l["monthly_amount"] for l in loans)
        total_rec = sum(r["amount"] for r in receivables if not r["is_settled"])
        total_pay = sum(p["amount"] for p in payables if not p["is_settled"])

        summary_card = ft.Container(
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            border_radius=18,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#0F172A", "#1E293B"] if self.page.theme_mode == ft.ThemeMode.DARK else ["#1E3A8A", "#2563EB"],
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY),
                offset=ft.Offset(0, 4),
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("مانده اقساط", size=11, color=ft.Colors.WHITE_70, rtl=True),
                            ft.Text(format_price(total_remaining_loans, persian_digits=True), size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300, rtl=True),
                        ],
                    ),
                    ft.Container(width=1, height=36, bgcolor=ft.Colors.WHITE_24),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("طلب‌های من", size=11, color=ft.Colors.WHITE_70, rtl=True),
                            ft.Text(format_price(total_rec, persian_digits=True), size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300, rtl=True),
                        ],
                    ),
                    ft.Container(width=1, height=36, bgcolor=ft.Colors.WHITE_24),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text("بدهی‌های من", size=11, color=ft.Colors.WHITE_70, rtl=True),
                            ft.Text(format_price(total_pay, persian_digits=True), size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300, rtl=True),
                        ],
                    ),
                ],
            ),
        )

        # Tab Selectors
        tabs_row = ft.Row(
            spacing=6,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(vertical=10),
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    bgcolor=ft.Colors.PRIMARY if self.current_tab == "loans" else ft.Colors.with_opacity(0.08, ft.Colors.GREY),
                    on_click=lambda _: self.set_tab("loans"),
                    content=ft.Text(
                        f"اقساط ({to_persian_digits(str(len(loans)))})",
                        color=ft.Colors.WHITE if self.current_tab == "loans" else ft.Colors.GREY_500,
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        rtl=True,
                    ),
                ),
                ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(vertical=10),
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    bgcolor=ft.Colors.PRIMARY if self.current_tab == "receivables" else ft.Colors.with_opacity(0.08, ft.Colors.GREY),
                    on_click=lambda _: self.set_tab("receivables"),
                    content=ft.Text(
                        f"طلب‌ها ({to_persian_digits(str(len(receivables)))})",
                        color=ft.Colors.WHITE if self.current_tab == "receivables" else ft.Colors.GREY_500,
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        rtl=True,
                    ),
                ),
                ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(vertical=10),
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    bgcolor=ft.Colors.PRIMARY if self.current_tab == "payables" else ft.Colors.with_opacity(0.08, ft.Colors.GREY),
                    on_click=lambda _: self.set_tab("payables"),
                    content=ft.Text(
                        f"بدهی‌ها ({to_persian_digits(str(len(payables)))})",
                        color=ft.Colors.WHITE if self.current_tab == "payables" else ft.Colors.GREY_500,
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        rtl=True,
                    ),
                ),
            ],
        )

        # Tab Action & List
        if self.current_tab == "loans":
            add_btn = ft.ElevatedButton(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                        ft.Text("افزودن وام و قسط جدید", weight=ft.FontWeight.BOLD, rtl=True),
                    ],
                ),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                    padding=ft.Padding.symmetric(vertical=12),
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
                on_click=self.show_add_loan_dialog,
            )
            items_list = [self.build_loan_card(l) for l in loans]
        elif self.current_tab == "receivables":
            add_btn = ft.ElevatedButton(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                        ft.Text("ثبت طلب جدید", weight=ft.FontWeight.BOLD, rtl=True),
                    ],
                ),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                    padding=ft.Padding.symmetric(vertical=12),
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
                on_click=lambda _: self.show_add_debt_dialog("receivable"),
            )
            items_list = [self.build_debt_card(r) for r in receivables]
        else: # payables
            add_btn = ft.ElevatedButton(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                        ft.Text("ثبت بدهی جدید", weight=ft.FontWeight.BOLD, rtl=True),
                    ],
                ),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                    padding=ft.Padding.symmetric(vertical=12),
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
                on_click=lambda _: self.show_add_debt_dialog("payable"),
            )
            items_list = [self.build_debt_card(p) for p in payables]

        if not items_list:
            content_view = ft.Container(
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.all(40),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=48, color=ft.Colors.GREY_400),
                        ft.Text("موردی در این بخش ثبت نشده است.", color=ft.Colors.GREY_500, size=14, rtl=True),
                    ],
                ),
            )
        else:
            content_view = ft.Column(controls=items_list, spacing=0)

        self.container.content = ft.ListView(
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=12, bottom=90),
            controls=[
                summary_card,
                ft.Container(height=12),
                tabs_row,
                ft.Container(height=12),
                add_btn,
                ft.Container(height=14),
                content_view,
            ],
        )
        if self.page:
            self.page.update()
