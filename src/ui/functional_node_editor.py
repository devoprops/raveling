"""Functional node editor widget for configuring functional nodes."""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QComboBox, QDoubleSpinBox, QFormLayout, QScrollArea, QFrame, QGridLayout,
)
from PySide6.QtCore import Signal, Qt
from src.utils.constants import (
    FUNCTIONAL_NODE_TYPES, FUNCTIONAL_NODE_DAMAGE, FUNCTIONAL_NODE_BUFF,
    FUNCTIONAL_NODE_DEBUFF, FUNCTIONAL_NODE_SKILL, FUNCTIONAL_NODE_SPELL,
    FUNCTIONAL_NODE_PROCESS, FUNCTIONAL_NODE_CLASSES, DAMAGE_SUBTYPES,
    DAMAGE_SUBTYPE_PHYSICAL, DAMAGE_SUBTYPE_ELEMENTAL, ELEMENTS,
)


class FunctionalNodeEditor(QWidget):
    """Editor for functional nodes with add/remove capabilities."""
    
    nodes_changed = Signal()  # Emitted when nodes change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes: List[Dict[str, Any]] = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header with add button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Functional Nodes:"))
        header_layout.addStretch()
        
        add_button = QPushButton("+ Add Node")
        add_button.clicked.connect(self.add_node)
        header_layout.addWidget(add_button)
        
        layout.addLayout(header_layout)
        
        # Scroll area for nodes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.nodes_container = QWidget()
        self.nodes_layout = QVBoxLayout()
        self.nodes_layout.setSpacing(10)
        self.nodes_container.setLayout(self.nodes_layout)
        
        scroll.setWidget(self.nodes_container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def add_node(self, node_data: Optional[Dict[str, Any]] = None):
        """Add a new functional node editor."""
        if node_data is None:
            # Default to physical damage node
            node_data = {
                "node_type": FUNCTIONAL_NODE_DAMAGE,
                "node_class": "primary",
                "execution_probability": 1.0,
                "damage_subtype": DAMAGE_SUBTYPE_PHYSICAL,
                "base_damage": 10.0,
                "distribution_parameters": {
                    "type": "gaussian",
                    "params": {"mean": 10.0, "std_dev": 2.0}
                },
            }
        
        node_widget = NodeEditorWidget(node_data, len(self.nodes))
        node_widget.node_changed.connect(self.on_node_changed)
        node_widget.remove_requested.connect(self.remove_node)
        
        self.nodes.append(node_data)
        self.nodes_layout.addWidget(node_widget)
        
        self.nodes_changed.emit()
    
    def remove_node(self, index: int):
        """Remove a functional node."""
        if 0 <= index < len(self.nodes):
            self.nodes.pop(index)
            # Remove widget
            item = self.nodes_layout.takeAt(index)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Update indices of remaining widgets
            for i in range(self.nodes_layout.count()):
                widget = self.nodes_layout.itemAt(i).widget()
                if widget and hasattr(widget, "set_index"):
                    widget.set_index(i)
            
            self.nodes_changed.emit()
    
    def on_node_changed(self, index: int, node_data: Dict[str, Any]):
        """Handle node data change."""
        if 0 <= index < len(self.nodes):
            self.nodes[index] = node_data
            self.nodes_changed.emit()
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get all node configurations."""
        return self.nodes.copy()
    
    def set_nodes(self, nodes: List[Dict[str, Any]]):
        """Set node configurations."""
        # Clear existing
        while self.nodes_layout.count():
            item = self.nodes_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        self.nodes = []
        
        # Add new nodes
        for node_data in nodes:
            self.add_node(node_data)


class NodeEditorWidget(QGroupBox):
    """Widget for editing a single functional node."""
    
    node_changed = Signal(int, dict)  # index, node_data
    remove_requested = Signal(int)  # index
    
    def __init__(self, node_data: Dict[str, Any], index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.node_data = node_data.copy()
        self.init_ui()
        self.update_ui_from_data()
    
    def set_index(self, index: int):
        """Update the index."""
        self.index = index
    
    def init_ui(self):
        """Initialize the UI."""
        main_layout = QVBoxLayout()
        
        # Two-column layout for basic fields
        two_col_layout = QHBoxLayout()
        
        # Left column: Basic node properties
        left_col = QFormLayout()
        
        # Node type
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems(FUNCTIONAL_NODE_TYPES)
        self.node_type_combo.currentTextChanged.connect(self.on_node_type_changed)
        left_col.addRow("Node Type:", self.node_type_combo)
        
        # Node class
        self.node_class_combo = QComboBox()
        self.node_class_combo.addItems(FUNCTIONAL_NODE_CLASSES)
        self.node_class_combo.currentTextChanged.connect(self.on_data_changed)
        left_col.addRow("Node Class:", self.node_class_combo)
        
        # Execution probability
        self.prob_spin = QDoubleSpinBox()
        self.prob_spin.setRange(0.0, 1.0)
        self.prob_spin.setDecimals(3)
        self.prob_spin.setSingleStep(0.01)
        self.prob_spin.setValue(1.0)  # Default value
        self.prob_spin.valueChanged.connect(self.on_data_changed)
        left_col.addRow("Execution Prob:", self.prob_spin)
        
        # Right column: Damage-specific fields (will be shown/hidden)
        right_col = QFormLayout()
        
        self.damage_subtype_combo = QComboBox()
        self.damage_subtype_combo.addItems(DAMAGE_SUBTYPES)
        self.damage_subtype_combo.currentTextChanged.connect(self.on_damage_subtype_changed)
        right_col.addRow("Damage Subtype:", self.damage_subtype_combo)
        
        self.element_combo = QComboBox()
        self.element_combo.addItems(ELEMENTS)
        self.element_combo.currentTextChanged.connect(self.on_data_changed)
        right_col.addRow("Element Type:", self.element_combo)
        
        self.base_damage_spin = QDoubleSpinBox()
        self.base_damage_spin.setRange(0.0, 1000.0)
        self.base_damage_spin.setDecimals(2)
        self.base_damage_spin.setValue(10.0)  # Default value
        self.base_damage_spin.valueChanged.connect(self.on_data_changed)
        right_col.addRow("Base Damage:", self.base_damage_spin)
        
        # Add columns to horizontal layout
        left_widget = QWidget()
        left_widget.setLayout(left_col)
        right_widget = QWidget()
        right_widget.setLayout(right_col)
        
        two_col_layout.addWidget(left_widget)
        two_col_layout.addWidget(right_widget)
        
        main_layout.addLayout(two_col_layout)
        
        # Distribution parameter widget (spans full width, includes type selector)
        from src.ui.distribution_parameter_widget import DistributionParameterWidget
        self.dist_param_widget = DistributionParameterWidget("gaussian")
        self.dist_param_widget.parameters_changed.connect(self.on_data_changed)
        main_layout.addWidget(self.dist_param_widget)
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.index))
        main_layout.addWidget(remove_btn)
        
        self.setLayout(main_layout)
        self.setTitle(f"Node {self.index + 1}")
    
    def update_ui_from_data(self):
        """Update UI from node data."""
        # Block signals temporarily to avoid triggering on_data_changed during initialization
        self.node_type_combo.blockSignals(True)
        self.node_class_combo.blockSignals(True)
        self.prob_spin.blockSignals(True)
        self.base_damage_spin.blockSignals(True)
        self.damage_subtype_combo.blockSignals(True)
        if hasattr(self, "element_combo"):
            self.element_combo.blockSignals(True)
        
        self.node_type_combo.setCurrentText(self.node_data.get("node_type", FUNCTIONAL_NODE_DAMAGE))
        self.node_class_combo.setCurrentText(self.node_data.get("node_class", "primary"))
        self.prob_spin.setValue(self.node_data.get("execution_probability", 1.0))
        
        if "damage_subtype" in self.node_data:
            self.damage_subtype_combo.setCurrentText(self.node_data["damage_subtype"])
        if "element" in self.node_data and hasattr(self, "element_combo"):
            self.element_combo.setCurrentText(self.node_data["element"])
        if "base_damage" in self.node_data:
            self.base_damage_spin.setValue(self.node_data["base_damage"])
        
        # Unblock signals
        self.node_type_combo.blockSignals(False)
        self.node_class_combo.blockSignals(False)
        self.prob_spin.blockSignals(False)
        self.base_damage_spin.blockSignals(False)
        self.damage_subtype_combo.blockSignals(False)
        if hasattr(self, "element_combo"):
            self.element_combo.blockSignals(False)
        
        # Set distribution parameters (new format: single field with type and params)
        dist_config = self.node_data.get("distribution_parameters", {})
        if not dist_config:
            # Handle old format for backwards compatibility
            dist_type = self.node_data.get("distribution_type", "gaussian")
            dist_params = self.node_data.get("distribution_params", {})
            if dist_type == "gaussian" and not dist_params:
                dist_params = {"mean": 10.0, "std_dev": 2.0}
            dist_config = {"type": dist_type, "params": dist_params}
        
        self.dist_param_widget.set_parameters(dist_config)
        
        self.update_visibility()
    
    def update_visibility(self):
        """Update visibility of fields based on node type."""
        is_damage = self.node_type_combo.currentText() == FUNCTIONAL_NODE_DAMAGE
        
        self.damage_subtype_combo.setVisible(is_damage)
        self.element_combo.setVisible(is_damage and self.damage_subtype_combo.currentText() == DAMAGE_SUBTYPE_ELEMENTAL)
        self.base_damage_spin.setVisible(is_damage)
        self.dist_type_combo.setVisible(is_damage)
        self.dist_param_widget.setVisible(is_damage)
    
    def on_node_type_changed(self, node_type: str):
        """Handle node type change."""
        self.update_visibility()
        self.on_data_changed()
    
    def on_damage_subtype_changed(self, subtype: str):
        """Handle damage subtype change."""
        self.update_visibility()
        self.on_data_changed()
    
    
    def on_data_changed(self):
        """Handle any data change."""
        self.node_data = {
            "node_type": self.node_type_combo.currentText(),
            "node_class": self.node_class_combo.currentText(),
            "execution_probability": self.prob_spin.value(),
        }
        
        if self.node_type_combo.currentText() == FUNCTIONAL_NODE_DAMAGE:
            self.node_data["damage_subtype"] = self.damage_subtype_combo.currentText()
            if self.damage_subtype_combo.currentText() == DAMAGE_SUBTYPE_ELEMENTAL:
                self.node_data["element"] = self.element_combo.currentText()
            self.node_data["base_damage"] = self.base_damage_spin.value()
            self.node_data["distribution_parameters"] = self.dist_param_widget.get_parameters()
        
        self.node_changed.emit(self.index, self.node_data)

