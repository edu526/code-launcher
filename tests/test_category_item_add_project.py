#!/usr/bin/env python3
"""
Test para verificar que "Agregar proyecto" funciona desde un CATEGORY_ITEM
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from context_menu import ContextMenuHandler, CATEGORY_ITEM


class TestCategoryItemAddProject(unittest.TestCase):
    """Test que verifica agregar proyecto desde category item"""

    def setUp(self):
        """Set up test fixtures"""
        self.column_browser = Mock()
        self.column_browser.load_mixed_content = Mock()
        self.column_browser.current_path = "categories"

        self.parent_window = Mock()
        self.parent_window.categories = {
            "Web": {
                "icon": "folder",
                "description": "Web projects",
                "subcategories": {
                    "Frontend": {
                        "icon": "folder",
                        "description": "Frontend projects"
                    }
                }
            }
        }
        self.parent_window.projects = {}
        self.parent_window.config = Mock()

        self.handler = ContextMenuHandler(self.column_browser, self.parent_window)

    def test_menu_has_add_project_option(self):
        """Test que el menú de category item tiene opción 'Agregar proyecto'"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        menu = self.handler.create_context_menu(context)

        # Verificar que el menú tiene 2 opciones
        menu_items = menu.get_children()
        self.assertEqual(len(menu_items), 2)

        # Verificar las etiquetas
        labels = [item.get_label() for item in menu_items]
        self.assertIn("Agregar subcategoría", labels)
        self.assertIn("Agregar proyecto", labels)

        print("✅ Menú de category item tiene 'Agregar proyecto'")

    @patch('dialogs.Dialogs')
    def test_add_project_from_category_item(self, mock_dialogs):
        """Test agregar proyecto desde category item (Web)"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        # Ejecutar acción
        self.handler.add_project_action(context)

        # Verificar que se llamó al diálogo
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verificar pre_config
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['category'], 'Web')
        self.assertIsNone(pre_config['subcategory'])
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web')

        print("✅ Pre-config correcto para category item 'Web'")

    @patch('dialogs.Dialogs')
    def test_add_project_from_nested_category_item(self, mock_dialogs):
        """Test agregar proyecto desde category item anidado (Web:Frontend)"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'cat:Web',
            'item_path': 'cat:Web:Frontend',
            'is_project': False
        }

        # Ejecutar acción
        self.handler.add_project_action(context)

        # Verificar que se llamó al diálogo
        mock_dialogs.show_add_project_dialog.assert_called_once()

        # Verificar pre_config
        call_args = mock_dialogs.show_add_project_dialog.call_args
        pre_config = call_args[1]['pre_config']

        self.assertEqual(pre_config['category'], 'Web')
        self.assertEqual(pre_config['subcategory'], 'Frontend')
        self.assertEqual(pre_config['hierarchy_path'], 'cat:Web:Frontend')

        print("✅ Pre-config correcto para category item anidado 'Web:Frontend'")

    @patch('dialogs.Dialogs')
    def test_add_project_callback_from_category_item(self, mock_dialogs):
        """Test que el callback agrega el proyecto correctamente"""
        context = {
            'type': CATEGORY_ITEM,
            'hierarchy_path': 'categories',
            'item_path': 'cat:Web',
            'is_project': False
        }

        # Ejecutar acción
        self.handler.add_project_action(context)

        # Obtener el callback
        call_args = mock_dialogs.show_add_project_dialog.call_args
        callback = call_args[0][2]

        # Simular agregar proyecto
        project_info = {
            "path": "/home/user/my-web-project",
            "category": "Web"
        }
        callback("MyWebProject", project_info)

        # Verificar que se agregó el proyecto
        self.assertIn("MyWebProject", self.parent_window.projects)
        self.assertEqual(self.parent_window.projects["MyWebProject"]["path"], "/home/user/my-web-project")
        self.assertEqual(self.parent_window.projects["MyWebProject"]["category"], "Web")

        # Verificar que se guardó y refrescó
        self.parent_window.config.save_projects.assert_called_once()
        self.column_browser.load_mixed_content.assert_called_once()

        print("✅ Proyecto agregado correctamente desde category item")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("TEST: Agregar Proyecto desde Category Item")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
