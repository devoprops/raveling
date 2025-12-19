"""Item designer tab for creating and editing item configurations."""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTextEdit, QLabel,
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QGroupBox, QFormLayout,
    QPushButton, QFileDialog, QMessageBox, QScrollArea, QCheckBox,
)
from PySide6.QtCore import Signal, Qt
from pathlib import Path
import yaml
from src.utils.constants import (
    ITEM_TYPE_WEAPON, ITEM_TYPE_WEARABLE, ITEM_TYPE_CONSUMABLE,
    MELEE_BLADED, MELEE_BLUNT, MELEE_FLAILED, RANGED_BOW, RANGED_THROWABLE,
    EQUIPMENT_SLOTS, ELEMENTS, FUNCTIONAL_NODE_CLASSES,
)


class ItemDesignerTab(QWidget):
    """Tab for designing items (weapons, wearables, consumables)."""
    
    name_changed = Signal(str, str)  # old_name, new_name
    
    def __init__(self, item_type: str, subtype: Optional[str], initial_name: str):
        super().__init__()
        self.item_type = item_type
        self.subtype = subtype
        self.tab_name = initial_name
        self.unsaved_changes = False
        
        self.init_ui()
        self.update_yaml_preview()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Analysis section (for weapons)
        if self.item_type == ITEM_TYPE_WEAPON:
            analysis_layout = QHBoxLayout()
            analysis_layout.addWidget(QLabel("Analysis:"))
            self.analysis_combo = QComboBox()
            self.analysis_combo.addItems([
                "None",
                "Damage Over Cycles",
                "Damage Distribution",
            ])
            self.analysis_combo.currentTextChanged.connect(self.on_analysis_changed)
            analysis_layout.addWidget(self.analysis_combo)
            analysis_layout.addStretch()
            layout.addLayout(analysis_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Configuration controls
        config_widget = QWidget()
        config_scroll = QScrollArea()
        config_scroll.setWidget(config_widget)
        config_scroll.setWidgetResizable(True)
        config_layout = QVBoxLayout()
        config_widget.setLayout(config_layout)
        
        # Basic info group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.tab_name)
        self.name_edit.textChanged.connect(self.on_name_changed)
        self.name_edit.textChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Name:", self.name_edit)
        
        self.short_desc_edit = QLineEdit()
        self.short_desc_edit.textChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Short Description:", self.short_desc_edit)
        
        self.long_desc_edit = QTextEdit()
        self.long_desc_edit.setMaximumHeight(100)
        self.long_desc_edit.textChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Long Description:", self.long_desc_edit)
        
        self.weight_kg_spin = QDoubleSpinBox()
        self.weight_kg_spin.setRange(0.0, 1000.0)
        self.weight_kg_spin.setDecimals(2)
        self.weight_kg_spin.valueChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Weight (kg):", self.weight_kg_spin)
        
        self.length_cm_spin = QDoubleSpinBox()
        self.length_cm_spin.setRange(0.0, 1000.0)
        self.length_cm_spin.setDecimals(2)
        self.length_cm_spin.valueChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Length (cm):", self.length_cm_spin)
        
        self.width_cm_spin = QDoubleSpinBox()
        self.width_cm_spin.setRange(0.0, 1000.0)
        self.width_cm_spin.setDecimals(2)
        self.width_cm_spin.valueChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Width (cm):", self.width_cm_spin)
        
        self.material_edit = QLineEdit()
        self.material_edit.textChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Material:", self.material_edit)
        
        basic_group.setLayout(basic_layout)
        config_layout.addWidget(basic_group)
        
        # Weapon-specific fields
        if self.item_type == ITEM_TYPE_WEAPON:
            weapon_group = QGroupBox("Weapon Properties")
            weapon_layout = QFormLayout()
            
            if self.subtype in [MELEE_BLADED, MELEE_BLUNT, MELEE_FLAILED]:
                if self.subtype == MELEE_BLADED:
                    self.blade_length_spin = QDoubleSpinBox()
                    self.blade_length_spin.setRange(0.0, 100.0)
                    self.blade_length_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Blade Length:", self.blade_length_spin)
                    
                    self.sharpness_spin = QDoubleSpinBox()
                    self.sharpness_spin.setRange(0.0, 100.0)
                    self.sharpness_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Sharpness:", self.sharpness_spin)
                elif self.subtype == MELEE_BLUNT:
                    self.impact_force_spin = QDoubleSpinBox()
                    self.impact_force_spin.setRange(0.0, 100.0)
                    self.impact_force_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Impact Force:", self.impact_force_spin)
                    
                    self.stun_chance_spin = QDoubleSpinBox()
                    self.stun_chance_spin.setRange(0.0, 1.0)
                    self.stun_chance_spin.setDecimals(3)
                    self.stun_chance_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Stun Chance:", self.stun_chance_spin)
                elif self.subtype == MELEE_FLAILED:
                    self.chain_length_spin = QDoubleSpinBox()
                    self.chain_length_spin.setRange(0.0, 100.0)
                    self.chain_length_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Chain Length:", self.chain_length_spin)
                    
                    self.wrap_chance_spin = QDoubleSpinBox()
                    self.wrap_chance_spin.setRange(0.0, 1.0)
                    self.wrap_chance_spin.setDecimals(3)
                    self.wrap_chance_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Wrap Chance:", self.wrap_chance_spin)
            elif self.subtype in [RANGED_BOW, RANGED_THROWABLE]:
                self.range_spin = QDoubleSpinBox()
                self.range_spin.setRange(0.0, 1000.0)
                self.range_spin.valueChanged.connect(self.mark_unsaved)
                weapon_layout.addRow("Range:", self.range_spin)
                
                if self.subtype == RANGED_BOW:
                    self.ammo_type_edit = QLineEdit()
                    self.ammo_type_edit.textChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Ammo Type:", self.ammo_type_edit)
                    
                    self.draw_strength_spin = QDoubleSpinBox()
                    self.draw_strength_spin.setRange(0.0, 100.0)
                    self.draw_strength_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Draw Strength:", self.draw_strength_spin)
                elif self.subtype == RANGED_THROWABLE:
                    self.return_chance_spin = QDoubleSpinBox()
                    self.return_chance_spin.setRange(0.0, 1.0)
                    self.return_chance_spin.setDecimals(3)
                    self.return_chance_spin.valueChanged.connect(self.mark_unsaved)
                    weapon_layout.addRow("Return Chance:", self.return_chance_spin)
            
            weapon_group.setLayout(weapon_layout)
            config_layout.addWidget(weapon_group)
        
        # Wearable-specific fields
        elif self.item_type == ITEM_TYPE_WEARABLE:
            wearable_group = QGroupBox("Wearable Properties")
            wearable_layout = QFormLayout()
            
            self.slot_combo = QComboBox()
            self.slot_combo.addItems(EQUIPMENT_SLOTS)
            self.slot_combo.currentTextChanged.connect(self.mark_unsaved)
            wearable_layout.addRow("Slot:", self.slot_combo)
            
            self.defense_bonus_spin = QDoubleSpinBox()
            self.defense_bonus_spin.setRange(-100.0, 100.0)
            self.defense_bonus_spin.setDecimals(2)
            self.defense_bonus_spin.valueChanged.connect(self.mark_unsaved)
            wearable_layout.addRow("Defense Bonus:", self.defense_bonus_spin)
            
            wearable_group.setLayout(wearable_layout)
            config_layout.addWidget(wearable_group)
        
        # Functional nodes section (for weapons and wearables)
        if self.item_type in [ITEM_TYPE_WEAPON, ITEM_TYPE_WEARABLE]:
            from src.ui.functional_node_editor import FunctionalNodeEditor
            self.functional_node_editor = FunctionalNodeEditor()
            self.functional_node_editor.nodes_changed.connect(self.mark_unsaved)
            
            # For weapons, add default physical damage node
            if self.item_type == ITEM_TYPE_WEAPON:
                self.functional_node_editor.add_node()  # Adds default physical damage node
            
            config_layout.addWidget(self.functional_node_editor)
        
        config_layout.addStretch()
        
        splitter.addWidget(config_scroll)
        splitter.setStretchFactor(0, 3)  # 30% width
        
        # Right side: YAML preview
        yaml_widget = QWidget()
        yaml_layout = QVBoxLayout()
        yaml_layout.addWidget(QLabel("YAML Configuration Preview:"))
        
        self.yaml_preview = QTextEdit()
        self.yaml_preview.setReadOnly(True)
        self.yaml_preview.setFontFamily("Courier")
        yaml_layout.addWidget(self.yaml_preview)
        
        yaml_widget.setLayout(yaml_layout)
        splitter.addWidget(yaml_widget)
        splitter.setStretchFactor(1, 7)  # 70% width
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def on_name_changed(self, text: str):
        """Handle name change."""
        old_name = self.tab_name
        self.tab_name = text or f"{self.item_type.capitalize()} {id(self)}"
        if old_name != self.tab_name:
            self.name_changed.emit(old_name, self.tab_name)
    
    def mark_unsaved(self):
        """Mark that there are unsaved changes."""
        self.unsaved_changes = True
        self.update_yaml_preview()
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.unsaved_changes
    
    def update_yaml_preview(self):
        """Update the YAML preview."""
        # Check if yaml_preview exists (may not be created yet during initialization)
        if not hasattr(self, 'yaml_preview'):
            return
        
        config = self.get_config()
        try:
            yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
            self.yaml_preview.setPlainText(yaml_str)
        except Exception as e:
            self.yaml_preview.setPlainText(f"Error generating YAML: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration as a dictionary."""
        config = {
            "name": self.name_edit.text() or "Unnamed",
            "item_type": self.item_type,
            "short_desc": self.short_desc_edit.text(),
            "long_desc": self.long_desc_edit.toPlainText(),
            "weight_kg": self.weight_kg_spin.value(),
            "length_cm": self.length_cm_spin.value(),
            "width_cm": self.width_cm_spin.value(),
            "material": self.material_edit.text(),
        }
        
        if self.subtype:
            config["subtype"] = self.subtype
        
        # Weapon-specific config
        if self.item_type == ITEM_TYPE_WEAPON:
            if self.subtype == MELEE_BLADED:
                config["blade_length"] = self.blade_length_spin.value()
                config["sharpness"] = self.sharpness_spin.value()
            elif self.subtype == MELEE_BLUNT:
                config["impact_force"] = self.impact_force_spin.value()
                config["stun_chance"] = self.stun_chance_spin.value()
            elif self.subtype == MELEE_FLAILED:
                config["chain_length"] = self.chain_length_spin.value()
                config["wrap_chance"] = self.wrap_chance_spin.value()
            elif self.subtype == RANGED_BOW:
                config["range"] = self.range_spin.value()
                config["ammo_type"] = self.ammo_type_edit.text()
                config["draw_strength"] = self.draw_strength_spin.value()
            elif self.subtype == RANGED_THROWABLE:
                config["range"] = self.range_spin.value()
                config["return_chance"] = self.return_chance_spin.value()
        
        # Wearable-specific config
        elif self.item_type == ITEM_TYPE_WEARABLE:
            config["slot"] = self.slot_combo.currentText()
            config["defense_bonus"] = self.defense_bonus_spin.value()
        
        # Functional nodes
        if hasattr(self, "functional_node_editor"):
            config["functional_nodes"] = self.functional_node_editor.get_nodes()
        
        return config
    
    def on_analysis_changed(self, analysis_type: str):
        """Handle analysis type change."""
        if analysis_type == "None":
            # Remove analysis widget if present
            pass
        else:
            # TODO: Show analysis widget
            pass
    
    def save_config(self):
        """Save the configuration to a file."""
        config = self.get_config()
        config_dir = Path(__file__).parent.parent / "configs" / f"{self.item_type}s"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            str(config_dir / f"{config['name']}.yaml"),
            "YAML Files (*.yaml);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                self.unsaved_changes = False
                QMessageBox.information(self, "Success", f"Configuration saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

