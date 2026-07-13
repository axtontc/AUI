import json

import pytest

from aui_controller import AUIController
from shadow_dom_daemon import ShadowDOMDaemon


@pytest.fixture
def temp_shadow_dom(tmp_path):
    path = tmp_path / "shadow_dom.json"
    return str(path)

def test_aui_controller_init():
    controller = AUIController()
    assert "shadow_dom.json" in controller.shadow_dom_path

def test_daemon_init():
    daemon = ShadowDOMDaemon()
    assert "shadow_dom.json" in daemon.output_path

def test_aui_controller_coords_lookup(temp_shadow_dom):
    # Setup mock shadow_dom tree
    mock_tree = {
        "windows": {
            "123": {
                "pid": 456,
                "title": "Open",
                "class_name": "#32770",
                "rect": [100, 100, 500, 400],
                "elements": [
                    {
                        "name": "File name:",
                        "class_name": "Edit",
                        "rect": [150, 200, 350, 220]
                    },
                    {
                        "name": "Open",
                        "class_name": "Button",
                        "rect": [380, 350, 480, 380]
                    }
                ]
            }
        },
        "last_updated": 1.0
    }

    # Write mock tree to file
    with open(temp_shadow_dom, "w", encoding="utf-8") as f:
        json.dump(mock_tree, f)

    controller = AUIController(shadow_dom_path=temp_shadow_dom)

    # Check Edit input coordinate translation
    edit_coords = controller.get_element_by_class("Open", "Edit")
    assert edit_coords == {"x": 250, "y": 210} # Center of [150, 200, 350, 220]

    # Check Button coordinate translation
    btn_coords = controller.get_element_by_class("Open", "Button", name_query="Open")
    assert btn_coords == {"x": 430, "y": 365} # Center of [380, 350, 480, 380]
