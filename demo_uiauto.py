import uiautomation as auto


def test_uiauto():
    print("Fetching top-level windows...")
    fg = auto.GetForegroundWindow()
    print(f"Foreground Window: {fg.Name if fg else 'None'} | Class: {fg.ClassName if fg else 'None'}")
    focus = auto.GetFocusedControl()
    print(f"Focused Control: {focus.Name if focus else 'None'} | Type: {focus.ControlTypeName if focus else 'None'}")


if __name__ == "__main__":
    test_uiauto()
