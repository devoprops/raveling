import { useState, useEffect } from 'react';
import { EffectStyleConfig } from '../effectstyles';
import EffectStyleDesigner from '../effectstyles/EffectStyleDesigner';
import './SpellForm.css';

export interface SpellFormData {
  name: string;
  short_desc: string;
  long_desc: string;
  effect_styles: EffectStyleConfig[];
  category?: string; // e.g., "offensive", "defensive", "utility", etc.
  school?: string; // e.g., "fire", "ice", "arcane", etc.
}

interface SpellFormProps {
  initialData?: Partial<SpellFormData>;
  onChange: (data: SpellFormData) => void;
}

export default function SpellForm({ initialData, onChange }: SpellFormProps) {
  const [formData, setFormData] = useState<SpellFormData>({
    name: initialData?.name || '',
    short_desc: initialData?.short_desc || '',
    long_desc: initialData?.long_desc || '',
    effect_styles: initialData?.effect_styles || [],
    category: initialData?.category || '',
    school: initialData?.school || '',
  });
  
  const [showStyleDesigner, setShowStyleDesigner] = useState(false);

  useEffect(() => {
    onChange(formData);
  }, [formData, onChange]);

  const updateField = <K extends keyof SpellFormData>(field: K, value: SpellFormData[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddEffectStyle = (style: EffectStyleConfig) => {
    setFormData((prev) => ({
      ...prev,
      effect_styles: [...prev.effect_styles, style],
    }));
    setShowStyleDesigner(false);
  };

  const handleRemoveEffectStyle = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      effect_styles: prev.effect_styles.filter((_, i) => i !== index),
    }));
  };

  return (
    <div className="spell-form">
      <div className="form-section">
        <h3 className="section-title">Basic Information</h3>
        <div className="form-group">
          <label>Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => updateField('name', e.target.value)}
            placeholder="Spell name"
          />
        </div>
        <div className="form-grid">
          <div className="form-group">
            <label>Category</label>
            <input
              type="text"
              value={formData.category || ''}
              onChange={(e) => updateField('category', e.target.value)}
              placeholder="e.g., offensive, defensive"
            />
          </div>
          <div className="form-group">
            <label>School</label>
            <input
              type="text"
              value={formData.school || ''}
              onChange={(e) => updateField('school', e.target.value)}
              placeholder="e.g., fire, ice, arcane"
            />
          </div>
        </div>
        <div className="form-group">
          <label>Short Description</label>
          <input
            type="text"
            value={formData.short_desc}
            onChange={(e) => updateField('short_desc', e.target.value)}
            placeholder="Brief description"
          />
        </div>
        <div className="form-group">
          <label>Long Description</label>
          <textarea
            value={formData.long_desc}
            onChange={(e) => updateField('long_desc', e.target.value)}
            placeholder="Detailed description"
            rows={3}
          />
        </div>
      </div>

      <div className="form-section">
        <h3 className="section-title">Effect Styles</h3>
        <p className="section-description">
          Spells are composed of one or more EffectStyles that define their behavior.
        </p>
        <button
          className="add-style-btn"
          onClick={() => setShowStyleDesigner(true)}
        >
          + Add Effect Style
        </button>
        {formData.effect_styles.length > 0 && (
          <div className="style-list">
            {formData.effect_styles.map((style, index) => (
              <div key={index} className="style-item">
                <div className="style-info">
                  <strong>{style.name}</strong> ({style.subtype})
                  {style.process_verb && <span> - "{style.process_verb}"</span>}
                  <div className="style-details">
                    {style.style_type} • Probability: {style.execution_probability}
                  </div>
                </div>
                <button
                  className="remove-btn"
                  onClick={() => handleRemoveEffectStyle(index)}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {showStyleDesigner && (
        <div className="style-designer-overlay">
          <div className="style-designer-container">
            <EffectStyleDesigner
              onSave={handleAddEffectStyle}
              onCancel={() => setShowStyleDesigner(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
