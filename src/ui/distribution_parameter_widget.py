"""Distribution parameter widget with PDF preview."""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QDoubleSpinBox, QLineEdit, QGroupBox, QComboBox,
)
from PySide6.QtCore import Signal, Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from scipy import stats
from src.utils.common.distributions import (
    sample_uniform, sample_gaussian, sample_skewnorm, sample_bimodal, sample_die_roll
)


class DistributionParameterWidget(QWidget):
    """Widget for editing distribution parameters with live PDF preview."""
    
    parameters_changed = Signal(dict)  # Emitted when parameters change
    
    def __init__(self, distribution_type: str = "uniform", parent=None):
        super().__init__(parent)
        self.distribution_type = distribution_type
        self.parameters: Dict[str, Any] = {}
        self.init_ui()
        self.set_distribution_type(distribution_type)
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout()
        
        # Left side: Parameters form
        self.params_group = QGroupBox("Distribution Parameters")
        self.params_layout = QFormLayout()
        
        # Distribution type selector (now part of this widget)
        self.dist_type_combo = QComboBox()
        self.dist_type_combo.addItems(["uniform", "gaussian", "skewnorm", "bimodal", "die_roll"])
        self.dist_type_combo.currentTextChanged.connect(self.on_distribution_type_changed)
        self.params_layout.addRow("Distribution Type:", self.dist_type_combo)
        
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group, stretch=1)
        
        # Right side: PDF preview
        preview_group = QGroupBox("PDF Preview")
        preview_layout = QVBoxLayout()
        
        self.figure = Figure(figsize=(3, 2))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(150)
        self.canvas.setMinimumWidth(200)
        preview_layout.addWidget(self.canvas)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group, stretch=1)
        
        self.setLayout(layout)
    
    def on_distribution_type_changed(self, dist_type: str):
        """Handle distribution type change from combo box."""
        self.set_distribution_type(dist_type)
    
    def set_distribution_type(self, dist_type: str):
        """Set the distribution type and update UI."""
        self.distribution_type = dist_type
        if hasattr(self, "dist_type_combo"):
            # Block signals to avoid recursion
            self.dist_type_combo.blockSignals(True)
            self.dist_type_combo.setCurrentText(dist_type)
            self.dist_type_combo.blockSignals(False)
        
        # Clear existing fields
        while self.params_layout.rowCount():
            self.params_layout.removeRow(0)
        
        # Set defaults and create fields based on type
        if dist_type == "uniform":
            self.parameters = {"min": 0.0, "max": 10.0}
            self.create_uniform_fields()
        elif dist_type == "gaussian":
            self.parameters = {"mean": 10.0, "std_dev": 2.0}
            self.create_gaussian_fields()
        elif dist_type == "skewnorm":
            self.parameters = {"mean": 10.0, "std_dev": 2.0, "skew": 0.0}
            self.create_skewnorm_fields()
        elif dist_type == "bimodal":
            self.parameters = {"mean1": 5.0, "std1": 1.0, "mean2": 15.0, "std2": 1.0, "weight": 0.5}
            self.create_bimodal_fields()
        elif dist_type == "die_roll":
            self.parameters = {"notation": "1d6"}
            self.create_die_roll_fields()
        
        self.update_preview()
    
    def create_uniform_fields(self):
        """Create fields for uniform distribution."""
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(-1000.0, 1000.0)
        self.min_spin.setDecimals(2)
        self.min_spin.setValue(self.parameters["min"])
        self.min_spin.valueChanged.connect(self.on_uniform_changed)
        self.params_layout.addRow("Min:", self.min_spin)
        
        self.max_spin = QDoubleSpinBox()
        self.max_spin.setRange(-1000.0, 1000.0)
        self.max_spin.setDecimals(2)
        self.max_spin.setValue(self.parameters["max"])
        self.max_spin.valueChanged.connect(self.on_uniform_changed)
        self.params_layout.addRow("Max:", self.max_spin)
    
    def create_gaussian_fields(self):
        """Create fields for Gaussian distribution."""
        self.mean_spin = QDoubleSpinBox()
        self.mean_spin.setRange(-1000.0, 1000.0)
        self.mean_spin.setDecimals(2)
        self.mean_spin.setValue(self.parameters["mean"])
        self.mean_spin.valueChanged.connect(self.on_gaussian_changed)
        self.params_layout.addRow("Mean:", self.mean_spin)
        
        self.std_spin = QDoubleSpinBox()
        self.std_spin.setRange(0.01, 100.0)
        self.std_spin.setDecimals(2)
        self.std_spin.setValue(self.parameters["std_dev"])
        self.std_spin.valueChanged.connect(self.on_gaussian_changed)
        self.params_layout.addRow("Std Dev:", self.std_spin)
    
    def create_skewnorm_fields(self):
        """Create fields for skewed normal distribution."""
        self.mean_spin = QDoubleSpinBox()
        self.mean_spin.setRange(0, 1000.0)
        self.mean_spin.setDecimals(2)
        self.mean_spin.setValue(self.parameters["mean"])
        self.mean_spin.valueChanged.connect(self.on_skewnorm_changed)
        self.params_layout.addRow("Mean:", self.mean_spin)
        
        self.std_spin = QDoubleSpinBox()
        self.std_spin.setRange(0.01, 100.0)
        self.std_spin.setDecimals(2)
        self.std_spin.setValue(self.parameters["std_dev"])
        self.std_spin.valueChanged.connect(self.on_skewnorm_changed)
        self.params_layout.addRow("Std Dev:", self.std_spin)
        
        self.skew_spin = QDoubleSpinBox()
        self.skew_spin.setRange(-100.0, 100.0)
        self.skew_spin.setDecimals(2)
        self.skew_spin.setValue(self.parameters["skew"])
        self.skew_spin.valueChanged.connect(self.on_skewnorm_changed)
        self.params_layout.addRow("Skew (a):", self.skew_spin)
        
        # Display actual mean and std (calculated from scipy)
        self.actual_mean_label = QLabel("Actual Mean: --")
        self.params_layout.addRow("", self.actual_mean_label)
        
        self.actual_std_label = QLabel("Actual Std: --")
        self.params_layout.addRow("", self.actual_std_label)
    
    def create_bimodal_fields(self):
        """Create fields for bimodal distribution."""
        self.mean1_spin = QDoubleSpinBox()
        self.mean1_spin.setRange(0.0, 1000.0)
        self.mean1_spin.setDecimals(2)
        self.mean1_spin.setValue(self.parameters["mean1"])
        self.mean1_spin.valueChanged.connect(self.on_bimodal_changed)
        self.params_layout.addRow("Mean 1:", self.mean1_spin)
        
        self.std1_spin = QDoubleSpinBox()
        self.std1_spin.setRange(0.01, 100.0)
        self.std1_spin.setDecimals(2)
        self.std1_spin.setValue(self.parameters["std1"])
        self.std1_spin.valueChanged.connect(self.on_bimodal_changed)
        self.params_layout.addRow("Std Dev 1:", self.std1_spin)
        
        self.mean2_spin = QDoubleSpinBox()
        self.mean2_spin.setRange(-1000.0, 1000.0)
        self.mean2_spin.setDecimals(2)
        self.mean2_spin.setValue(self.parameters["mean2"])
        self.mean2_spin.valueChanged.connect(self.on_bimodal_changed)
        self.params_layout.addRow("Mean 2:", self.mean2_spin)
        
        self.std2_spin = QDoubleSpinBox()
        self.std2_spin.setRange(0.01, 100.0)
        self.std2_spin.setDecimals(2)
        self.std2_spin.setValue(self.parameters["std2"])
        self.std2_spin.valueChanged.connect(self.on_bimodal_changed)
        self.params_layout.addRow("Std Dev 2:", self.std2_spin)
        
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.0, 1.0)
        self.weight_spin.setDecimals(2)
        self.weight_spin.setValue(self.parameters["weight"])
        self.weight_spin.valueChanged.connect(self.on_bimodal_changed)
        self.params_layout.addRow("Weight (Mode 1):", self.weight_spin)
    
    def create_die_roll_fields(self):
        """Create fields for die roll distribution."""
        self.notation_edit = QLineEdit()
        self.notation_edit.setText(self.parameters["notation"])
        self.notation_edit.textChanged.connect(self.on_die_roll_changed)
        self.params_layout.addRow("Notation (e.g., 2d6):", self.notation_edit)
    
    def on_uniform_changed(self):
        """Handle uniform parameter changes."""
        self.parameters = {
            "min": self.min_spin.value(),
            "max": self.max_spin.value(),
        }
        self.update_preview()
        self.parameters_changed.emit(self.parameters)
    
    def on_gaussian_changed(self):
        """Handle Gaussian parameter changes."""
        self.parameters = {
            "mean": self.mean_spin.value(),
            "std_dev": self.std_spin.value(),
        }
        self.update_preview()
        self.parameters_changed.emit(self.parameters)
    
    def on_skewnorm_changed(self):
        """Handle skewnorm parameter changes."""
        self.parameters = {
            "mean": self.mean_spin.value(),
            "std_dev": self.std_spin.value(),
            "skew": self.skew_spin.value(),
        }
        self.update_preview()
        self.parameters_changed.emit(self.parameters)
    
    def on_bimodal_changed(self):
        """Handle bimodal parameter changes."""
        self.parameters = {
            "mean1": self.mean1_spin.value(),
            "std1": self.std1_spin.value(),
            "mean2": self.mean2_spin.value(),
            "std2": self.std2_spin.value(),
            "weight": self.weight_spin.value(),
        }
        self.update_preview()
        self.parameters_changed.emit(self.parameters)
    
    def on_die_roll_changed(self):
        """Handle die roll parameter changes."""
        self.parameters = {
            "notation": self.notation_edit.text(),
        }
        self.update_preview()
        self.parameters_changed.emit(self.parameters)
    
    def update_preview(self):
        """Update the PDF preview plot."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        try:
            if self.distribution_type == "uniform":
                min_val = self.parameters.get("min", 0.0)
                max_val = self.parameters.get("max", 10.0)
                x = np.linspace(min_val - (max_val - min_val) * 0.1, 
                               max_val + (max_val - min_val) * 0.1, 1000)
                # Uniform PDF: 1/(max-min) between min and max, 0 elsewhere
                y = np.where((x >= min_val) & (x <= max_val), 
                           1.0 / (max_val - min_val) if max_val > min_val else 1.0, 0.0)
                ax.plot(x, y, 'b-', linewidth=2)
                ax.fill_between(x, y, alpha=0.3)
                ax.set_xlabel("Value")
                ax.set_ylabel("Probability Density")
                ax.set_title("Uniform Distribution")
                ax.grid(True, alpha=0.3)
            
            elif self.distribution_type == "gaussian":
                mean = self.parameters.get("mean", 10.0)
                std = self.parameters.get("std_dev", 2.0)
                x = np.linspace(mean - 4 * std, mean + 4 * std, 1000)
                y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
                ax.plot(x, y, 'b-', linewidth=2)
                ax.fill_between(x, y, alpha=0.3)
                ax.set_xlabel("Value")
                ax.set_ylabel("Probability Density")
                ax.set_title("Gaussian Distribution")
                ax.grid(True, alpha=0.3)
            
            elif self.distribution_type == "skewnorm":
                loc = self.parameters.get("mean", 10.0)  # location parameter
                scale = self.parameters.get("std_dev", 2.0)  # scale parameter
                a = self.parameters.get("skew", 0.0)  # shape/skewness parameter
                
                # Create scipy skewnorm distribution
                skewnorm_dist = stats.skewnorm(a=a, loc=loc, scale=scale)
                
                # Calculate actual mean and std
                actual_mean = skewnorm_dist.mean()
                actual_std = skewnorm_dist.std()
                
                # Update labels if they exist
                if hasattr(self, "actual_mean_label"):
                    self.actual_mean_label.setText(f"Actual Mean: {actual_mean:.2f}")
                if hasattr(self, "actual_std_label"):
                    self.actual_std_label.setText(f"Actual Std: {actual_std:.2f}")
                
                # Calculate PDF
                x_min = skewnorm_dist.ppf(0.001)  # 0.1% quantile
                x_max = skewnorm_dist.ppf(0.999)  # 99.9% quantile
                x = np.linspace(x_min, x_max, 1000)
                y = skewnorm_dist.pdf(x)
                
                ax.plot(x, y, 'b-', linewidth=2)
                ax.fill_between(x, y, alpha=0.3)
                ax.axvline(actual_mean, color='r', linestyle='--', linewidth=1.5, label=f'Mean: {actual_mean:.2f}')
                ax.set_xlabel("Value")
                ax.set_ylabel("Probability Density")
                ax.set_title("Skewed Normal Distribution")
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            elif self.distribution_type == "bimodal":
                mean1 = self.parameters.get("mean1", 5.0)
                std1 = self.parameters.get("std1", 1.0)
                mean2 = self.parameters.get("mean2", 15.0)
                std2 = self.parameters.get("std2", 1.0)
                weight = self.parameters.get("weight", 0.5)
                
                x_min = min(mean1 - 4 * std1, mean2 - 4 * std2)
                x_max = max(mean1 + 4 * std1, mean2 + 4 * std2)
                x = np.linspace(x_min, x_max, 1000)
                
                # Mix of two Gaussians
                y1 = weight * (1 / (std1 * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean1) / std1) ** 2)
                y2 = (1 - weight) * (1 / (std2 * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean2) / std2) ** 2)
                y = y1 + y2
                
                ax.plot(x, y, 'b-', linewidth=2)
                ax.fill_between(x, y, alpha=0.3)
                ax.set_xlabel("Value")
                ax.set_ylabel("Probability Density")
                ax.set_title("Bimodal Distribution")
                ax.grid(True, alpha=0.3)
            
            elif self.distribution_type == "die_roll":
                notation = self.parameters.get("notation", "1d6")
                try:
                    from src.utils.common.distributions import calculate_dice_probabilities
                    
                    parts = notation.lower().split("d")
                    if len(parts) == 2:
                        num_dice = int(parts[0])
                        num_sides = int(parts[1])
                        
                        if num_dice < 1 or num_sides < 1:
                            raise ValueError("Invalid dice parameters")
                        
                        # Calculate exact probabilities
                        probabilities = calculate_dice_probabilities(num_dice, num_sides)
                        
                        # Extract values and probabilities
                        x = sorted(probabilities.keys())
                        y = [probabilities[val] for val in x]
                        
                        ax.bar(x, y, alpha=0.7, width=0.8)
                        ax.set_xlabel("Sum Value")
                        ax.set_ylabel("Probability")
                        ax.set_title(f"Die Roll Distribution ({notation})")
                        ax.grid(True, alpha=0.3, axis='y')
                    else:
                        raise ValueError("Invalid notation format")
                except Exception as e:
                    ax.text(0.5, 0.5, f"Invalid notation: {notation}\n{str(e)}", 
                           ha="center", va="center", transform=ax.transAxes)
                    ax.set_title("Die Roll Distribution")
        
        except Exception as e:
            ax.text(0.5, 0.5, f"Error: {str(e)}", 
                   ha="center", va="center", transform=ax.transAxes)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameters including distribution type."""
        return {
            "type": self.distribution_type,
            "params": self.parameters.copy()
        }
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set parameters. Accepts either old format (dict) or new format (dict with 'type' and 'params')."""
        # Handle both old format (just params) and new format (with type and params)
        if "type" in parameters and "params" in parameters:
            # New format
            dist_type = parameters["type"]
            params = parameters["params"]
            self.set_distribution_type(dist_type)
            self.parameters = params.copy()
            params_to_use = params
        else:
            # Old format - assume current distribution type
            self.parameters = parameters.copy()
            params_to_use = parameters
        
        # Update UI fields if they exist
        if self.distribution_type == "uniform":
            if hasattr(self, "min_spin"):
                self.min_spin.setValue(params_to_use.get("min", 0.0))
            if hasattr(self, "max_spin"):
                self.max_spin.setValue(params_to_use.get("max", 10.0))
        elif self.distribution_type == "gaussian":
            if hasattr(self, "mean_spin"):
                self.mean_spin.setValue(params_to_use.get("mean", 10.0))
            if hasattr(self, "std_spin"):
                self.std_spin.setValue(params_to_use.get("std_dev", 2.0))
        elif self.distribution_type == "skewnorm":
            if hasattr(self, "mean_spin"):
                self.mean_spin.setValue(params_to_use.get("mean", 10.0))
            if hasattr(self, "std_spin"):
                self.std_spin.setValue(params_to_use.get("std_dev", 2.0))
            if hasattr(self, "skew_spin"):
                self.skew_spin.setValue(params_to_use.get("skew", 0.0))
        elif self.distribution_type == "bimodal":
            if hasattr(self, "mean1_spin"):
                self.mean1_spin.setValue(params_to_use.get("mean1", 5.0))
            if hasattr(self, "std1_spin"):
                self.std1_spin.setValue(params_to_use.get("std1", 1.0))
            if hasattr(self, "mean2_spin"):
                self.mean2_spin.setValue(params_to_use.get("mean2", 15.0))
            if hasattr(self, "std2_spin"):
                self.std2_spin.setValue(params_to_use.get("std2", 1.0))
            if hasattr(self, "weight_spin"):
                self.weight_spin.setValue(params_to_use.get("weight", 0.5))
        elif self.distribution_type == "die_roll":
            if hasattr(self, "notation_edit"):
                self.notation_edit.setText(params_to_use.get("notation", "1d6"))
        self.update_preview()

