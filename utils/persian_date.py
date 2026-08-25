import jdatetime

PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]

PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}

def to_persian_digits(num_str: str) -> str:
    """Converts english digits to persian digits."""
    res = ""
    for char in str(num_str):
        res += PERSIAN_DIGITS.get(char, char)
    return res

def format_price(amount: int | float, persian_digits: bool = True, unit: str = "تومان") -> str:
    """Formats a number as separated thousands e.g. 1,250,000 تومان."""
    try:
        formatted = f"{int(amount):,}"
    except (ValueError, TypeError):
        formatted = "0"
    
    if persian_digits:
        formatted = to_persian_digits(formatted)
        
    return f"{formatted} {unit}" if unit else formatted

def get_current_jalali():
    """Returns current jdatetime.date."""
    return jdatetime.date.today()

def get_current_jalali_str() -> str:
    """Returns today's date formatted as YYYY/MM/DD in Jalali."""
    today = jdatetime.date.today()
    return f"{today.year:04d}/{today.month:02d}/{today.day:02d}"

def get_month_name(month_num: int) -> str:
    """Gets Persian month name from 1-12 index."""
    if 1 <= month_num <= 12:
        return PERSIAN_MONTHS[month_num - 1]
    return ""

def format_jalali_display(date_str: str) -> str:
    """Converts 1403/05/12 to ۱۲ مرداد ۱۴۰۳."""
    try:
        parts = [int(p) for p in date_str.split('/')]
        if len(parts) == 3:
            year, month, day = parts
            month_name = get_month_name(month)
            return f"{to_persian_digits(str(day))} {month_name} {to_persian_digits(str(year))}"
    except Exception:
        pass
    return to_persian_digits(date_str)
