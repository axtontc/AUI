import ctypes


def test_win32_children():
    FindWindow = ctypes.windll.user32.FindWindowW
    EnumChildWindows = ctypes.windll.user32.EnumChildWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    GetClassName = ctypes.windll.user32.GetClassNameW
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowRect = ctypes.windll.user32.GetWindowRect

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    hwnd = FindWindow(None, "Untitled - Notepad")
    if not hwnd:
        print("Notepad window not found.")
        return

    print(f"Notepad HWND: {hwnd}")

    children = []

    def foreach_child(hwnd_child, lParam):
        class_name = ctypes.create_unicode_buffer(256)
        GetClassName(hwnd_child, class_name, 256)

        text_length = ctypes.windll.user32.GetWindowTextLengthW(hwnd_child)
        text_buff = ctypes.create_unicode_buffer(text_length + 1)
        GetWindowText(hwnd_child, text_buff, text_length + 1)

        rect = RECT()
        GetWindowRect(hwnd_child, ctypes.byref(rect))

        children.append(
            {
                "hwnd": hwnd_child,
                "class": class_name.value,
                "text": text_buff.value,
                "rect": (rect.left, rect.top, rect.right, rect.bottom),
            }
        )
        return True

    EnumChildWindows(hwnd, EnumWindowsProc(foreach_child), 0)

    print("Children of Notepad:")
    for child in children:
        print(f" - Class: {child['class']} | Text: {child['text']} | Rect: {child['rect']}")


if __name__ == "__main__":
    test_win32_children()
