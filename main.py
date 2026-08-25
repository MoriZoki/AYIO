import flet as ft
import database
from utils.persian_date import get_current_jalali_str, format_jalali_display
from views.dashboard_view import DashboardView
from views.accounts_view import AccountsView
from views.tools_view import ToolsView
from views.add_transaction_view import AddTransactionView
from views.history_view import HistoryView
from views.categories_view import CategoriesView

def main(page: ft.Page):
    # App Settings
    page.title = "AYIO"
    page.theme_mode = ft.ThemeMode.DARK
    page.rtl = True
    page.window.width = 440
    page.window.height = 840
    page.window.min_width = 360
    page.window.min_height = 600
    
    # Custom Luxury Navy / Midnight Blue Color Scheme
    page.theme = ft.Theme(
        color_scheme_seed="#0284C7",
        use_material3=True,
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed="#0284C7",
        use_material3=True,
    )
    
    # Initialize SQLite Database
    database.init_db()

    # Callbacks & Views
    def on_refresh_all():
        dashboard_view.update_content()
        accounts_view.update_content()
        tools_view.update_content()
        history_view.update_content()
        categories_view.update_content()
        page.update()

    def on_transaction_saved():
        on_refresh_all()
        nav_bar.selected_index = 0
        switch_tab(0)
        page.update()

    def on_categories_changed():
        add_view.update_categories_ui()
        dashboard_view.update_content()
        history_view.update_content()
        page.update()

    def on_accounts_changed():
        add_view.update_accounts_ui()
        dashboard_view.update_content()
        tools_view.update_content()
        history_view.update_content()
        accounts_view.update_content()
        page.update()

    # Views instances
    dashboard_view = DashboardView(
        page=page,
        on_navigate_add=lambda: (setattr(nav_bar, 'selected_index', 2), switch_tab(2), page.update()),
        on_navigate_accounts=lambda: (setattr(nav_bar, 'selected_index', 1), switch_tab(1), page.update()),
        on_navigate_tools=lambda: (setattr(nav_bar, 'selected_index', 3), switch_tab(3), page.update()),
        on_refresh_all=on_refresh_all
    )
    accounts_view = AccountsView(page=page, on_accounts_changed=on_accounts_changed)
    tools_view = ToolsView(page=page, on_data_changed=on_refresh_all)
    add_view = AddTransactionView(page=page, on_saved_callback=on_transaction_saved)
    history_view = HistoryView(page=page, on_data_changed=on_refresh_all)
    categories_view = CategoriesView(page=page, on_categories_changed=on_categories_changed)

    # Main Content Area
    content_area = ft.Container(
        expand=True,
        content=dashboard_view.render(),
    )

    def switch_tab(index: int):
        if index == 0:
            dashboard_view.update_content()
            content_area.content = dashboard_view.render()
        elif index == 1:
            accounts_view.update_content()
            content_area.content = accounts_view.render()
        elif index == 2:
            add_view.update_accounts_ui()
            add_view.update_categories_ui()
            content_area.content = add_view.render()
        elif index == 3:
            tools_view.update_content()
            content_area.content = tools_view.render()
        elif index == 4:
            history_view.update_content()
            content_area.content = history_view.render()
        elif index == 5:
            categories_view.update_content()
            content_area.content = categories_view.render()
        page.update()

    def open_categories(e):
        categories_view.update_content()
        content_area.content = categories_view.render()
        page.update()

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        theme_btn.icon = (
            ft.Icons.LIGHT_MODE_ROUNDED if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE_ROUNDED
        )
        on_refresh_all()
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE_ROUNDED,
        tooltip="تغییر تم (تاریک/روشن)",
        on_click=toggle_theme,
    )

    categories_btn = ft.IconButton(
        icon=ft.Icons.CATEGORY_ROUNDED,
        tooltip="مدیریت دسته‌بندی‌ها",
        on_click=open_categories,
    )

    today_str = get_current_jalali_str()
    today_badge = ft.Container(
        content=ft.Text(
            format_jalali_display(today_str),
            size=11,
            color=ft.Colors.CYAN_300,
            weight=ft.FontWeight.BOLD,
            rtl=True,
        ),
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=20,
    )

    # Top App Bar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, color=ft.Colors.CYAN_400),
        leading_width=40,
        title=ft.Row(
            spacing=10,
            controls=[
                ft.Text("AYIO", weight=ft.FontWeight.BOLD, size=19, rtl=False),
                today_badge,
            ],
        ),
        center_title=False,
        bgcolor=ft.Colors.SURFACE,
        actions=[
            categories_btn,
            theme_btn,
        ],
    )

    # Bottom Navigation Bar
    def on_nav_change(e):
        switch_tab(e.control.selected_index)

    nav_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD_ROUNDED,
                label="داشبورد",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CREDIT_CARD_OUTLINED,
                selected_icon=ft.Icons.CREDIT_CARD_ROUNDED,
                label="کارت‌ها",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                selected_icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                label="ثبت جدید",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                selected_icon=ft.Icons.AUTO_AWESOME_ROUNDED,
                label="ابزارها",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                selected_icon=ft.Icons.RECEIPT_LONG_ROUNDED,
                label="تاریخچه",
            ),
        ],
    )

    page.navigation_bar = nav_bar
    page.add(content_area)

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
