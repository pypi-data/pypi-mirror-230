from typing import Any
import json
import copy
import os


class Settings():
    def __init__(self):
        self._default_settings = {
            "language": "default",
            "recentFilesLength": 10,
            "windowTitleType": "filename",
            "checkSaveBeforeClosing": True,
            "showEditedTitle": True,
            "useEditorconfig": True,
            "whitespaceCount": 2,
            "useTabsInsteadOfSpaces": False,
            "addCommentSave": True,
            "showWelcomeDialog": True,
            "showWelcomeDialogExternalReleases": True,
            "disabledPlugins": []
        }

        self._user_settings = {}

    def get(self, key: str) -> Any:
        """Returns the given setting"""
        if key in self._user_settings:
            return copy.deepcopy(self._user_settings[key])
        elif key in self._default_settings:
            return copy.deepcopy(self._default_settings[key])
        else:
            return None

    def set(self, key: str, value: Any):
        """Set the value of a setting"""
        self._user_settings[key] = copy.deepcopy(value)

    def save(self, path: str):
        """Save settings into file"""
        if len(self._user_settings) == 0 and not os.path.isfile(path):
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._user_settings, f, ensure_ascii=False, indent=4)

    def load(self, path: str):
        """Load settings from file"""
        if not os.path.isfile(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            self._user_settings = json.load(f)

    def reset(self):
        """Resets all settings to the default values"""
        self._user_settings.clear()
