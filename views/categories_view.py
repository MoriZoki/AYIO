import flet as ft
import database
from utils.icons_helper import AVAILABLE_ICONS, AVAILABLE_COLORS, get_icon
from utils.persian_date import to_persian_digits

class CategoriesView:
    def __init__(self, page: ft.Page, on_categories_changed):
        self.page = page
        self.on_categories_changed = on_categories_changed
        self.current_tab = "expense"
        self.container = ft.Container(expand=True)

    def show_add_category_dialog(self, e):
        new_name_input = ft.TextField(
            label="نام دسته‌بندی",
            border_radius=12,
            rtl=True,
            autofocus=True,
        )

        selected_icon_ref = {"val": AVAILABLE_ICONS[0][0]}
        selected_color_ref = {"val": AVAILABLE_COLORS[0]}

        icon_controls = []
        for icon_key, icon_title, icon_data in AVAILABLE_ICONS:
            def make_icon_btn(k=icon_key, d=icon_data):
                return ft.IconButton(
                    icon=d,
                    tooltip=icon_title,
                    icon_color=ft.Colors.PRIMARY if selected_icon_ref["val"] == k else ft.Colors.GREY_500,
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY) if selected_icon_ref["val"] == k else ft.Colors.TRANSPARENT,
                    on_click=lambda ev, key=k: select_this_icon(key),
                )
            icon_controls.append(make_icon_btn())

        def select_this_icon(k):
            selected_icon_ref["val"] = k
            update_dialog_ui()

        color_controls = []
        for col in AVAILABLE_COLORS:
            def make_color_btn(c=col):
                return ft.Container(
                    width=28,
                    height=28,
                    border_radius=14,
                    bgcolor=c,
                    border=ft.Border.all(2, ft.Colors.WHITE if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT),
                    on_click=lambda ev, color=c: select_this_color(color),
                )
            color_controls.append(make_color_btn())

        def select_this_color(c):
            selected_color_ref["val"] = c
            update_dialog_ui()

        icons_row = ft.Row(wrap=True, spacing=4, controls=icon_controls)
        colors_row = ft.Row(wrap=True, spacing=6, controls=color_controls)

        def update_dialog_ui():
            for idx, (k, _, _) in enumerate(AVAILABLE_ICONS):
                icon_controls[idx].icon_color = ft.Colors.PRIMARY if selected_icon_ref["val"] == k else ft.Colors.GREY_500
                icon_controls[idx].bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY) if selected_icon_ref["val"] == k else ft.Colors.TRANSPARENT
            
            for idx, c in enumerate(AVAILABLE_COLORS):
                color_controls[idx].border = ft.Border.all(3, ft.Colors.PRIMARY if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT)
                
            self.page.update()

        def confirm_add(ev):
            name = new_name_input.value.strip()
            if not name:
                new_name_input.error = "نام را وارد کنید"
                self.page.update()
                return
                
            database.add_category(
                name=name,
                cat_type=self.current_tab,
                icon=selected_icon_ref["val"],
                color=selected_color_ref["val"]
            )
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_categories_changed()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"دسته‌بندی جدید ({'ورودی' if self.current_tab == 'income' else 'خروجی'})", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=350,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        new_name_input,
                        ft.Text("انتخاب آیکون:", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Container(content=icons_row, height=120),
                        ft.Text("انتخاب رنگ:", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        colors_row,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("انصراف", on_click=cancel),
                ft.ElevatedButton("ذخیره", bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE, on_click=confirm_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_edit_category_dialog(self, cat: dict):
        name_input = ft.TextField(
            label="نام دسته‌بندی",
            value=cat["name"],
            border_radius=12,
            rtl=True,
            autofocus=True,
        )

        selected_icon_ref = {"val": cat.get("icon") or AVAILABLE_ICONS[0][0]}
        selected_color_ref = {"val": cat.get("color") or AVAILABLE_COLORS[0]}

        icon_controls = []
        for icon_key, icon_title, icon_data in AVAILABLE_ICONS:
            def make_icon_btn(k=icon_key, d=icon_data):
                return ft.IconButton(
                    icon=d,
                    tooltip=icon_title,
                    icon_color=ft.Colors.PRIMARY if selected_icon_ref["val"] == k else ft.Colors.GREY_500,
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY) if selected_icon_ref["val"] == k else ft.Colors.TRANSPARENT,
                    on_click=lambda ev, key=k: select_this_icon(key),
                )
            icon_controls.append(make_icon_btn())

        def select_this_icon(k):
            selected_icon_ref["val"] = k
            update_dialog_ui()

        color_controls = []
        for col in AVAILABLE_COLORS:
            def make_color_btn(c=col):
                return ft.Container(
                    width=28,
                    height=28,
                    border_radius=14,
                    bgcolor=c,
                    border=ft.Border.all(3, ft.Colors.PRIMARY if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT),
                    on_click=lambda ev, color=c: select_this_color(color),
                )
            color_controls.append(make_color_btn())

        def select_this_color(c):
            selected_color_ref["val"] = c
            update_dialog_ui()

        icons_row = ft.Row(wrap=True, spacing=4, controls=icon_controls)
        colors_row = ft.Row(wrap=True, spacing=6, controls=color_controls)

        def update_dialog_ui():
            for idx, (k, _, _) in enumerate(AVAILABLE_ICONS):
                icon_controls[idx].icon_color = ft.Colors.PRIMARY if selected_icon_ref["val"] == k else ft.Colors.GREY_500
                icon_controls[idx].bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY) if selected_icon_ref["val"] == k else ft.Colors.TRANSPARENT
            
            for idx, c in enumerate(AVAILABLE_COLORS):
                color_controls[idx].border = ft.Border.all(3, ft.Colors.PRIMARY if selected_color_ref["val"] == c else ft.Colors.TRANSPARENT)
                
            self.page.update()

        def confirm_save(ev):
            name = name_input.value.strip()
            if not name:
                name_input.error = "نام را وارد کنید"
                self.page.update()
                return

            database.update_category(
                cat_id=cat["id"],
                name=name,
                cat_type=cat["type"],
                icon=selected_icon_ref["val"],
                color=selected_color_ref["val"]
            )
            dialog.open = False
            self.page.update()
            self.update_content()
            self.on_categories_changed()

        def cancel(ev):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("ویرایش دسته‌بندی", weight=ft.FontWeight.BOLD, rtl=True),
            content=ft.Container(
                width=350,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        name_input,
                        ft.Text("انتخاب آیکون:", size=12, weight=ft.FontWeight.BOLD, rtl=True),
                        ft.Container(content=icons_row, height=120),
                        ft.Text("انتخاب رنگ:", size=12, weight=ft.FontWeight.BOLD, rtl=True),
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

    def set_tab(self, tab_type: str):
        self.current_tab = tab_type
        self.update_content()

    def build_category_item(self, cat: dict):
        cat_icon = get_icon(cat["icon"])
        cat_color = cat["color"]
        
        def delete_cat(e):
            database.delete_category(cat["id"])
            self.update_content()
            self.on_categories_changed()

        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            margin=ft.Margin.only(bottom=8),
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.SURFACE_TINT) if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                content=ft.Icon(cat_icon, color=ft.Colors.WHITE, size=20),
                                bgcolor=cat_color,
                                border_radius=12,
                                width=40,
                                height=40,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Text(cat["name"], weight=ft.FontWeight.BOLD, size=14, rtl=True),
                        ],
                    ),
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_ROUNDED,
                                icon_color=ft.Colors.GREY_400,
                                icon_size=18,
                                tooltip="ویرایش دسته",
                                on_click=lambda _, c=cat: self.show_edit_category_dialog(c),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                icon_size=18,
                                tooltip="حذف دسته",
                                on_click=delete_cat,
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
        categories = database.get_categories(self.current_tab)

        is_exp = self.current_tab == "expense"
        tab_buttons = ft.Row(
            spacing=8,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(vertical=10),
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    bgcolor="#EF4444" if is_exp else ft.Colors.with_opacity(0.08, ft.Colors.GREY),
                    on_click=lambda _: self.set_tab("expense"),
                    content=ft.Text(
                        "دسته‌های هزینه",
                        color=ft.Colors.WHITE if is_exp else ft.Colors.GREY_500,
                        weight=ft.FontWeight.BOLD,
                        size=13,
                        rtl=True,
                    ),
                ),
                ft.Container(
                    expand=True,
                    padding=ft.Padding.symmetric(vertical=10),
                    alignment=ft.Alignment.CENTER,
                    border_radius=12,
                    bgcolor="#10B981" if not is_exp else ft.Colors.with_opacity(0.08, ft.Colors.GREY),
                    on_click=lambda _: self.set_tab("income"),
                    content=ft.Text(
                        "دسته‌های درآمد",
                        color=ft.Colors.WHITE if not is_exp else ft.Colors.GREY_500,
                        weight=ft.FontWeight.BOLD,
                        size=13,
                        rtl=True,
                    ),
                ),
            ],
        )

        add_btn = ft.ElevatedButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                    ft.Text("افزودن دسته‌بندی جدید", weight=ft.FontWeight.BOLD, rtl=True),
                ],
            ),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(vertical=14),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            on_click=self.show_add_category_dialog,
        )

        cat_list = [self.build_category_item(c) for c in categories]

        self.container.content = ft.ListView(
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=12, bottom=90),
            controls=[
                tab_buttons,
                ft.Container(height=14),
                add_btn,
                ft.Container(height=14),
                ft.Text(f"لیست دسته‌ها ({to_persian_digits(str(len(categories)))} مورد)", size=14, weight=ft.FontWeight.BOLD, rtl=True),
                ft.Container(height=8),
                *cat_list,
            ],
        )
        if self.page:
            self.page.update()
