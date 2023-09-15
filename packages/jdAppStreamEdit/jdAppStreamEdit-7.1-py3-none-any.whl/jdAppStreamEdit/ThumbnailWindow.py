from .ui_compiled.ThumbnailWindow import Ui_ThumbnailWindow
from .Types import ScreenshotDict, ScreenshotDictImage
from PyQt6.QtWidgets import QDialog, QMessageBox, QInputDialog, QListWidgetItem
from typing import Optional, TYPE_CHECKING
from PyQt6.QtCore import QCoreApplication
from .Functions import is_url_valid, set_layout_enabled, list_widget_contains_item
import requests
import copy


if TYPE_CHECKING:
    from .Environment import Environment


class ThumbnailWindow(QDialog, Ui_ThumbnailWindow):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        self.setupUi(self)

        self._env = env
        self._translated_images: list[ScreenshotDictImage] = []
        self._untranslated_image: Optional[ScreenshotDictImage] = None
        self._thumbnail_image_translations: dict[str, ScreenshotDictImage] = {}

        self.tab_widget.tabBar().setDocumentMode(True)
        self.tab_widget.tabBar().setExpanding(True)

        self.thumbnail_image_language_list.currentItemChanged.connect(self._thumbnail_image_language_list_item_changed)
        self.thumbnail_image_language_add_button.clicked.connect(self._thumbnail_image_language_add_button_clicked)
        self.thumbnail_image_language_remove_button.clicked.connect(self._thumbnail_image_language_remove_button_clicked)

        self.ok_button.clicked.connect(self._ok_button_clicked)

    def _update_thumbnail_image_language_list_buttons_enabled(self) -> None:
        enabled = self.thumbnail_image_language_list.currentRow() != -1
        self.thumbnail_image_language_remove_button.setEnabled(enabled)

    def _get_translated_thumbnail_image(self, lang: str) -> ScreenshotDictImage:
        return {
            "type": "thumbnail",
            "language": lang,
            "url": self.thumbnail_translation_url_edit.text().strip(),
            "width": self.thumbnail_translation_width_spin_box.value(),
            "height": self.thumbnail_translation_height_spin_box.value()
        }

    def _update_thumbnail_image_translation_widgets(self) -> None:
        if self.thumbnail_image_language_list.currentItem() is None:
            set_layout_enabled(self.thumbnail_image_translation_widgets_layout, False)
            self.thumbnail_translation_url_edit.setText("")
            self.thumbnail_translation_width_spin_box.setValue(0)
            self.thumbnail_translation_height_spin_box.setValue(0)
            return

        set_layout_enabled(self.thumbnail_image_translation_widgets_layout, True)

        image: ScreenshotDictImage = self._thumbnail_image_translations[self.thumbnail_image_language_list.currentItem().text()]

        self.thumbnail_translation_url_edit.setText(image["url"])
        self.thumbnail_translation_width_spin_box.setValue(image["width"] or 0)
        self.thumbnail_translation_height_spin_box.setValue(image["height"] or 0)

    def _thumbnail_image_language_list_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if previous is not None:
            previous_lang = previous.text()
            self._thumbnail_image_translations[previous_lang] = self._get_translated_thumbnail_image(previous_lang)

        self._update_thumbnail_image_translation_widgets()
        self._update_thumbnail_image_language_list_buttons_enabled()

    def _thumbnail_image_language_add_button_clicked(self) -> None:
        lang = QInputDialog.getItem(self, QCoreApplication.translate("ScreenshotWindow", "Add Language"), QCoreApplication.translate("ScreenshotWindow", "Please enter a Language Code"), self._env.language_codes)[0].strip()

        if lang == "":
            return

        if list_widget_contains_item(self.thumbnail_image_language_list, lang):
            QMessageBox.critical(self, QCoreApplication.translate("ScreenshotWindow", "Language exists"), QCoreApplication.translate("ScreenshotWindow", "There is already a translated Image for {{language}}").replace("{{language}}", lang))
            return

        self._thumbnail_image_translations[lang] = {
            "url": "",
            "type": "source",
            "language": lang,
            "width": None,
            "height": None
        }

        item = QListWidgetItem(lang)
        self.thumbnail_image_language_list.addItem(item)
        self.thumbnail_image_language_list.setCurrentItem(item)
        self._update_thumbnail_image_language_list_buttons_enabled()

    def _thumbnail_image_language_remove_button_clicked(self) -> None:
        del self._thumbnail_image_translations[self.thumbnail_image_language_list.currentItem().text()]
        self.thumbnail_image_language_list.takeItem(self.thumbnail_image_language_list.currentRow())
        self._update_thumbnail_image_language_list_buttons_enabled()

    def _ok_button_clicked(self) -> None:
        if self.thumbnail_image_language_list.currentItem() is not None:
            lang = self.thumbnail_image_language_list.currentItem().text()
            self._thumbnail_image_translations[lang] = self._get_translated_thumbnail_image(lang)

        self._untranslated_image = {
            "language": None,
            "type": "thumbnail",
            "url": self.thumbnail_url_edit.text(),
            "width": self.thumbnail_width_spin_box.value(),
            "height": self.thumbnail_height_spin_box.value()
        }

        for i in range(self.thumbnail_image_language_list.count()):
            self._translated_images.append(self._thumbnail_image_translations[self.thumbnail_image_language_list.item(i).text()])

        self.close()

    def open_window(self, untranslated_image: Optional[ScreenshotDictImage]) -> tuple[Optional[ScreenshotDictImage], list[ScreenshotDictImage]]:
        if untranslated_image is None:
            self.thumbnail_url_edit.setText("")
            self.thumbnail_width_spin_box.setValue(0)
            self.thumbnail_height_spin_box.setValue(0)
        else:
            self.thumbnail_url_edit.setText(untranslated_image["url"])
            self.thumbnail_width_spin_box.setValue(untranslated_image["width"])
            self.thumbnail_height_spin_box.setValue(untranslated_image["height"])

        self._untranslated_image = None
        self._translated_images.clear()

        self._update_thumbnail_image_language_list_buttons_enabled()
        self._update_thumbnail_image_translation_widgets()
        self.tab_widget.setCurrentIndex(0)

        self.exec()

        return self._untranslated_image, self._translated_images
