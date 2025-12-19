"""Skill designer tab for creating and editing skill configurations."""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTextEdit, QLabel,
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QGroupBox, QFormLayout,
    QPushButton, QFileDialog, QMessageBox, QScrollArea,
)
from PySide6.QtCore import Signal, Qt
from pathlib import Path
import yaml
from src.utils.constants import (
    SKILL_TYPE_ATTACK, SKILL_TYPE_BUFF, SKILL_TYPE_DEBUFF,
    SKILL_TYPE_REGENERATIVE, SKILL_TYPE_PROCESS,
    ATTACK_PHYSICAL, ATTACK_ELEMENTAL, ELEMENTS, REGEN_TYPES,
)


class SkillDesignerTab(QWidget):
    """Tab for designing skills."""
    
    name_changed = Signal(str, str)  # old_name, new_name
    
    def __init__(self, skill_type: str, initial_name: str):
        super().__init__()
        self.skill_type = skill_type
        self.tab_name = initial_name
        self.unsaved_changes = False
        
        self.init_ui()
        self.update_yaml_preview()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Analysis section
        analysis_layout = QHBoxLayout()
        analysis_layout.addWidget(QLabel("Analysis:"))
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems([
            "None",
            "Effect Over Cycles",
            "Effect Distribution",
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
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.textChanged.connect(self.mark_unsaved)
        basic_layout.addRow("Description:", self.description_edit)
        
        basic_group.setLayout(basic_layout)
        config_layout.addWidget(basic_group)
        
        # Skill type-specific fields
        if self.skill_type.startswith("attack_"):
            attack_group = QGroupBox("Attack Properties")
            attack_layout = QFormLayout()
            
            self.base_damage_spin = QDoubleSpinBox()
            self.base_damage_spin.setRange(0.0, 1000.0)
            self.base_damage_spin.setDecimals(2)
            self.base_damage_spin.valueChanged.connect(self.mark_unsaved)
            attack_layout.addRow("Base Damage:", self.base_damage_spin)
            
            if self.skill_type == "attack_elemental":
                self.element_combo = QComboBox()
                self.element_combo.addItems(ELEMENTS)
                self.element_combo.currentTextChanged.connect(self.mark_unsaved)
                attack_layout.addRow("Element Type:", self.element_combo)
            
            attack_group.setLayout(attack_layout)
            config_layout.addWidget(attack_group)
        
        elif self.skill_type in ["buff", "debuff"]:
            effect_group = QGroupBox("Effect Properties")
            effect_layout = QFormLayout()
            
            self.base_duration_spin = QSpinBox()
            self.base_duration_spin.setRange(1, 1000)
            self.base_duration_spin.valueChanged.connect(self.mark_unsaved)
            effect_layout.addRow("Base Duration (turns):", self.base_duration_spin)
            
            self.magnitude_spin = QDoubleSpinBox()
            self.magnitude_spin.setRange(0.0, 10.0)
            self.magnitude_spin.setDecimals(2)
            self.magnitude_spin.setValue(1.0)
            self.magnitude_spin.valueChanged.connect(self.mark_unsaved)
            effect_layout.addRow("Magnitude:", self.magnitude_spin)
            
            effect_group.setLayout(effect_layout)
            config_layout.addWidget(effect_group)
        
        elif self.skill_type == "regenerative":
            regen_group = QGroupBox("Regenerative Properties")
            regen_layout = QFormLayout()
            
            self.regen_type_combo = QComboBox()
            self.regen_type_combo.addItems(REGEN_TYPES)
            self.regen_type_combo.currentTextChanged.connect(self.mark_unsaved)
            regen_layout.addRow("Regen Type:", self.regen_type_combo)
            
            self.base_amount_spin = QDoubleSpinBox()
            self.base_amount_spin.setRange(0.0, 1000.0)
            self.base_amount_spin.setDecimals(2)
            self.base_amount_spin.valueChanged.connect(self.mark_unsaved)
            regen_layout.addRow("Base Amount:", self.base_amount_spin)
            
            regen_group.setLayout(regen_layout)
            config_layout.addWidget(regen_group)
        
        elif self.skill_type == "process":
            process_group = QGroupBox("Process Properties")
            process_layout = QFormLayout()
            
            self.process_type_edit = QLineEdit()
            self.process_type_edit.textChanged.connect(self.mark_unsaved)
            process_layout.addRow("Process Type:", self.process_type_edit)
            
            self.effect_desc_edit = QTextEdit()
            self.effect_desc_edit.setMaximumHeight(100)
            self.effect_desc_edit.textChanged.connect(self.mark_unsaved)
            process_layout.addRow("Effect Description:", self.effect_desc_edit)
            
            process_group.setLayout(process_layout)
            config_layout.addWidget(process_group)
        
        # Minimum requirements
        req_group = QGroupBox("Minimum Requirements")
        req_layout = QFormLayout()
        
        self.min_str_spin = QSpinBox()
        self.min_str_spin.setRange(0, 100)
        self.min_str_spin.valueChanged.connect(self.mark_unsaved)
        req_layout.addRow("Min STR:", self.min_str_spin)
        
        self.min_dex_spin = QSpinBox()
        self.min_dex_spin.setRange(0, 100)
        self.min_dex_spin.valueChanged.connect(self.mark_unsaved)
        req_layout.addRow("Min DEX:", self.min_dex_spin)
        
        self.min_int_spin = QSpinBox()
        self.min_int_spin.setRange(0, 100)
        self.min_int_spin.valueChanged.connect(self.mark_unsaved)
        req_layout.addRow("Min INT:", self.min_int_spin)
        
        self.min_wis_spin = QSpinBox()
        self.min_wis_spin.setRange(0, 100)
        self.min_wis_spin.valueChanged.connect(self.mark_unsaved)
        req_layout.addRow("Min WIS:", self.min_wis_spin)
        
        req_group.setLayout(req_layout)
        config_layout.addWidget(req_group)
        
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
        self.tab_name = text or f"Skill {id(self)}"
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
            "skill_type": self.skill_type.split("_")[0] if "_" in self.skill_type else self.skill_type,
            "description": self.description_edit.toPlainText(),
        }
        
        if self.skill_type.startswith("attack_"):
            config["subtype"] = "physical" if self.skill_type == "attack_physical" else "elemental"
            config["base_damage"] = self.base_damage_spin.value()
            if self.skill_type == "attack_elemental":
                config["element_type"] = self.element_combo.currentText()
        
        elif self.skill_type in ["buff", "debuff"]:
            config["base_duration"] = self.base_duration_spin.value()
            config["magnitude"] = self.magnitude_spin.value()
            # TODO: Add stat_modifiers
        
        elif self.skill_type == "regenerative":
            config["regen_type"] = self.regen_type_combo.currentText()
            config["base_amount"] = self.base_amount_spin.value()
        
        elif self.skill_type == "process":
            config["process_type"] = self.process_type_edit.text()
            config["effect_description"] = self.effect_desc_edit.toPlainText()
        
        # Minimum requirements
        min_reqs = {}
        if self.min_str_spin.value() > 0:
            min_reqs["str"] = self.min_str_spin.value()
        if self.min_dex_spin.value() > 0:
            min_reqs["dex"] = self.min_dex_spin.value()
        if self.min_int_spin.value() > 0:
            min_reqs["int"] = self.min_int_spin.value()
        if self.min_wis_spin.value() > 0:
            min_reqs["wis"] = self.min_wis_spin.value()
        
        if min_reqs:
            config["min_requirements"] = min_reqs
        
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
        config_dir = Path(__file__).parent.parent / "configs" / "skills"
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

