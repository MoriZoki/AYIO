import flet as ft

# Available icons list for user selection when creating custom categories
AVAILABLE_ICONS = [
    ("wallet", "کیف پول", ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED),
    ("attach_money", "پول و درآمد", ft.Icons.ATTACH_MONEY_ROUNDED),
    ("card_giftcard", "هدیه و پاداش", ft.Icons.CARD_GIFTCARD_ROUNDED),
    ("trending_up", "رشد مالی", ft.Icons.TRENDING_UP_ROUNDED),
    ("storefront", "فروشگاه", ft.Icons.STOREFRONT_ROUNDED),
    ("laptop", "کار و پروژه", ft.Icons.LAPTOP_MAC_ROUNDED),
    ("shopping_cart", "خرید و سوپرمارکت", ft.Icons.SHOPPING_CART_ROUNDED),
    ("home", "خانه و مسکن", ft.Icons.HOME_ROUNDED),
    ("car", "خودرو و بنزین", ft.Icons.DIRECTIONS_CAR_ROUNDED),
    ("restaurant", "رستوران و غذا", ft.Icons.RESTAURANT_ROUNDED),
    ("receipt", "قبوض و چک", ft.Icons.RECEIPT_LONG_ROUNDED),
    ("medical", "پزشکی و دارو", ft.Icons.MEDICAL_SERVICES_ROUNDED),
    ("clothing", "لباس و پوشاک", ft.Icons.CHECKROOM_ROUNDED),
    ("school", "آموزش و کتاب", ft.Icons.SCHOOL_ROUNDED),
    ("game", "تفریح و بازی", ft.Icons.SPORTS_ESPORTS_ROUNDED),
    ("card", "کارت و قسط", ft.Icons.CREDIT_CARD_ROUNDED),
    ("build", "تعمیرات و ابزار", ft.Icons.BUILD_ROUNDED),
    ("phone", "موبایل و اینترنت", ft.Icons.PHONE_ANDROID_ROUNDED),
    ("flight", "سفر و مسافرت", ft.Icons.FLIGHT_ROUNDED),
    ("fitness", "ورزش و سلامتی", ft.Icons.FITNESS_CENTER_ROUNDED),
    ("pets", "حیوانات خانگی", ft.Icons.PETS_ROUNDED),
    ("other", "سایر موارد", ft.Icons.MORE_HORIZ_ROUNDED),
]

AVAILABLE_COLORS = [
    "#10B981", # Emerald
    "#06B6D4", # Cyan
    "#3B82F6", # Blue
    "#8B5CF6", # Purple
    "#EC4899", # Pink
    "#F59E0B", # Amber
    "#EF4444", # Red
    "#F97316", # Orange
    "#EAB308", # Yellow
    "#F43F5E", # Rose
    "#6366F1", # Indigo
    "#D946EF", # Fuchsia
    "#64748B", # Slate
    "#14B8A6", # Teal
    "#78716C", # Stone
    "#84CC16", # Lime
]

def get_icon(icon_name: str):
    """Safely retrieves a Flet icon by string name."""
    if not icon_name:
        return ft.Icons.CATEGORY_ROUNDED
        
    clean_name = icon_name.upper().replace("-", "_")
    if hasattr(ft.Icons, clean_name):
        return getattr(ft.Icons, clean_name)
    
    # Try with _ROUNDED
    if not clean_name.endswith("_ROUNDED") and hasattr(ft.Icons, clean_name + "_ROUNDED"):
        return getattr(ft.Icons, clean_name + "_ROUNDED")
        
    for key, _, icon_val in AVAILABLE_ICONS:
        if key in icon_name.lower():
            return icon_val
            
    return ft.Icons.CATEGORY_ROUNDED
