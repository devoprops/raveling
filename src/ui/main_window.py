"""Main Designer window for creating and editing game configurations."""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QMenu, QWidget, QVBoxLayout,
    QHBoxLayout, QSplitter, QTextEdit, QLabel, QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from pathlib import Path
import yaml


class DesignerMainWindow(QMainWindow):
    """Main window for the Designer application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MUD Designer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Track open tabs
        self.tabs: Dict[str, QWidget] = {}
        self.tab_counter: Dict[str, int] = {
            "weapon": 0,
            "wearable": 0,
            "skill": 0,
            "character": 0,
        }
        
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def create_toolbar(self):
        """Create the main toolbar with new item/character menus."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # New Item menu
        new_item_action = QAction("New Item", self)
        new_item_menu = QMenu(self)
        
        # Weapon submenu
        weapon_menu = QMenu("Weapon", self)
        weapon_menu.addAction("Melee - Bladed", lambda: self.new_item("weapon", "melee_bladed"))
        weapon_menu.addAction("Melee - Blunt", lambda: self.new_item("weapon", "melee_blunt"))
        weapon_menu.addAction("Melee - Flailed", lambda: self.new_item("weapon", "melee_flailed"))
        weapon_menu.addAction("Ranged - Bow", lambda: self.new_item("weapon", "ranged_bow"))
        weapon_menu.addAction("Ranged - Throwable", lambda: self.new_item("weapon", "ranged_throwable"))
        new_item_menu.addMenu(weapon_menu)
        
        new_item_menu.addAction("Wearable", lambda: self.new_item("wearable", None))
        new_item_menu.addAction("Consumable", lambda: self.new_item("consumable", None))
        
        new_item_action.setMenu(new_item_menu)
        toolbar.addAction(new_item_action)
        
        # New Skill menu
        new_skill_action = QAction("New Skill", self)
        new_skill_menu = QMenu(self)
        new_skill_menu.addAction("Attack - Physical", lambda: self.new_skill("attack_physical"))
        new_skill_menu.addAction("Attack - Elemental", lambda: self.new_skill("attack_elemental"))
        new_skill_menu.addAction("Buff", lambda: self.new_skill("buff"))
        new_skill_menu.addAction("Debuff", lambda: self.new_skill("debuff"))
        new_skill_menu.addAction("Regenerative", lambda: self.new_skill("regenerative"))
        new_skill_menu.addAction("Process", lambda: self.new_skill("process"))
        
        new_skill_action.setMenu(new_skill_menu)
        toolbar.addAction(new_skill_action)
        
        # New Character menu
        new_character_action = QAction("New Character", self)
        new_character_menu = QMenu(self)
        new_character_menu.addAction("Player Character", lambda: self.new_character("pc"))
        new_character_menu.addAction("NPC", lambda: self.new_character("npc"))
        
        new_character_action.setMenu(new_character_menu)
        toolbar.addAction(new_character_action)
        
        toolbar.addSeparator()
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_tab)
        toolbar.addAction(save_action)
    
    def new_item(self, item_type: str, subtype: Optional[str]):
        """Create a new item designer tab."""
        from src.ui.item_designer import ItemDesignerTab
        
        self.tab_counter[item_type] += 1
        tab_name = f"{item_type.capitalize()} {self.tab_counter[item_type]}"
        
        tab = ItemDesignerTab(item_type, subtype, tab_name)
        tab.name_changed.connect(self.on_tab_name_changed)
        
        index = self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.setCurrentIndex(index)
        
        self.tabs[tab_name] = tab
    
    def new_skill(self, skill_type: str):
        """Create a new skill designer tab."""
        from src.ui.skill_designer import SkillDesignerTab
        
        self.tab_counter["skill"] += 1
        tab_name = f"Skill {self.tab_counter['skill']}"
        
        tab = SkillDesignerTab(skill_type, tab_name)
        tab.name_changed.connect(self.on_tab_name_changed)
        
        index = self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.setCurrentIndex(index)
        
        self.tabs[tab_name] = tab
    
    def new_character(self, character_type: str):
        """Create a new character designer tab."""
        # TODO: Implement character designer
        QMessageBox.information(self, "Not Implemented", 
                               "Character designer will be implemented later.")
    
    def on_tab_name_changed(self, old_name: str, new_name: str):
        """Handle tab name change."""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == old_name:
                self.tab_widget.setTabText(i, new_name)
                # Update tabs dictionary
                if old_name in self.tabs:
                    self.tabs[new_name] = self.tabs.pop(old_name)
                break
    
    def close_tab(self, index: int):
        """Close a tab."""
        widget = self.tab_widget.widget(index)
        if widget and hasattr(widget, "has_unsaved_changes"):
            if widget.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    "This tab has unsaved changes. Do you want to close it?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
        
        self.tab_widget.removeTab(index)
    
    def save_current_tab(self):
        """Save the currently active tab."""
        current_widget = self.tab_widget.currentWidget()
        if current_widget and hasattr(current_widget, "save_config"):
            current_widget.save_config()

