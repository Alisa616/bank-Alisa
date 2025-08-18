def center_main_window(root, width, height):
    root.geometry(f"{width}x{height}")
    root.update_idletasks()

    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")

def validate_float(value_string):
    pass

def format_currency(amount):
    pass