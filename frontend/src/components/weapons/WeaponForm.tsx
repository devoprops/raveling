import { useState, useEffect } from 'react';
import { EffectorConfig } from '../effectors/EffectorSelector';
import EffectorList from '../effectors/EffectorList';
import { EffectStyleConfig } from '../effectstyles';
import EffectStyleDesigner from '../effectstyles/EffectStyleDesigner';
import ThumbnailPicker from './ThumbnailPicker';
import SimpleEffectorSelector from './SimpleEffectorSelector';
import { ELEMENTS, createDefaultAffinities, createDefaultDetriments } from '../../utils/constants';
import './WeaponForm.css';

export interface WeaponFormData {
  name: string;
  short_desc: string;
  long_desc: string;
  weight_kg: number;
  length_cm: number;
  width_cm: number;
  material: string;
  effectors?: EffectorConfig[]; // Deprecated, kept for backwards compatibility
  primary_effect_styles?: EffectStyleConfig[];
  secondary_effect_styles?: EffectStyleConfig[];
  affinities: {
    elemental: Record<string, number>;
    race: Record<string, number>;
  };
  detriments: {
    elemental: Record<string, number>;
    race: Record<string, number>;
  };
  auxiliary_slots: number;
  size_constraints: [number, number] | null;
  thumbnail_path: string;
  restrictions?: Record<string, any>;
}

interface WeaponFormProps {
  initialData?: Partial<WeaponFormData>;
  onChange: (data: WeaponFormData) => void;
}

export default function WeaponForm({ initialData, onChange }: WeaponFormProps) {
  const [formData, setFormData] = useState<WeaponFormData>({
    name: initialData?.name || '',
    short_desc: initialData?.short_desc || '',
    long_desc: initialData?.long_desc || '',
    weight_kg: initialData?.weight_kg || 0,
    length_cm: initialData?.length_cm || 0,
    width_cm: initialData?.width_cm || 0,
    material: initialData?.material || '',
    effectors: initialData?.effectors || [],
    primary_effect_styles: initialData?.primary_effect_styles || [],
    secondary_effect_styles: initialData?.secondary_effect_styles || [],
    affinities: initialData?.affinities || createDefaultAffinities(),
    detriments: initialData?.detriments || createDefaultDetriments(),
    auxiliary_slots: initialData?.auxiliary_slots || 0,
    size_constraints: initialData?.size_constraints || null,
    thumbnail_path: initialData?.thumbnail_path || '',
    restrictions: initialData?.restrictions || {},
  });
  
  const [showStyleDesigner, setShowStyleDesigner] = useState(false);
  const [styleDesignerMode, setStyleDesignerMode] = useState<'primary' | 'secondary'>('primary');

  useEffect(() => {
    onChange(formData);
  }, [formData, onChange]);

  const updateField = <K extends keyof WeaponFormData>(field: K, value: WeaponFormData[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const updateAffinity = (type: 'elemental' | 'race', key: string, value: number) => {
    setFormData((prev) => ({
      ...prev,
      affinities: {
        ...prev.affinities,
        [type]: { ...prev.affinities[type], [key]: value },
      },
    }));
  };

  const updateDetriment = (type: 'elemental' | 'race', key: string, value: number) => {
    setFormData((prev) => ({
      ...prev,
      detriments: {
        ...prev.detriments,
        [type]: { ...prev.detriments[type], [key]: value },
      },
    }));
  };

  const handleAddEffector = (effector: EffectorConfig) => {
    setFormData((prev) => ({
      ...prev,
      effectors: [...(prev.effectors || []), effector],
    }));
  };

  const handleRemoveEffector = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      effectors: (prev.effectors || []).filter((_, i) => i !== index),
    }));
  };

  const handleAddEffectStyle = (style: EffectStyleConfig) => {
    setFormData((prev) => {
      if (styleDesignerMode === 'primary') {
        return {
          ...prev,
          primary_effect_styles: [...(prev.primary_effect_styles || []), style],
        };
      } else {
        return {
          ...prev,
          secondary_effect_styles: [...(prev.secondary_effect_styles || []), style],
        };
      }
    });
    setShowStyleDesigner(false);
  };

  const handleRemovePrimaryStyle = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      primary_effect_styles: (prev.primary_effect_styles || []).filter((_, i) => i !== index),
    }));
  };

  const handleRemoveSecondaryStyle = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      secondary_effect_styles: (prev.secondary_effect_styles || []).filter((_, i) => i !== index),
    }));
  };

  const toggleSizeConstraints = () => {
    if (formData.size_constraints) {
      updateField('size_constraints', null);
    } else {
      updateField('size_constraints', [0, 100]);
    }
  };

  return (
    <div className="weapon-form">
      <div className="form-section">
        <h3 className="section-title">Basic Information</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="Weapon name"
            />
          </div>
          <div className="form-group">
            <label>Material</label>
            <input
              type="text"
              value={formData.material}
              onChange={(e) => updateField('material', e.target.value)}
              placeholder="e.g., Steel, Wood"
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
        <h3 className="section-title">Physical Properties</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>Weight (kg)</label>
            <input
              type="number"
              step="0.1"
              value={formData.weight_kg}
              onChange={(e) => updateField('weight_kg', parseFloat(e.target.value) || 0)}
            />
          </div>
          <div className="form-group">
            <label>Length (cm)</label>
            <input
              type="number"
              step="0.1"
              value={formData.length_cm}
              onChange={(e) => updateField('length_cm', parseFloat(e.target.value) || 0)}
            />
          </div>
          <div className="form-group">
            <label>Width (cm)</label>
            <input
              type="number"
              step="0.1"
              value={formData.width_cm}
              onChange={(e) => updateField('width_cm', parseFloat(e.target.value) || 0)}
            />
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3 className="section-title">Thumbnail</h3>
        <ThumbnailPicker
          thumbnailPath={formData.thumbnail_path}
          itemName={formData.name || 'weapon'}
          onThumbnailChange={(path) => updateField('thumbnail_path', path)}
        />
      </div>

      <div className="form-section">
        <h3 className="section-title">Elemental Affinities</h3>
        <div className="affinity-grid">
          {ELEMENTS.map((element) => (
            <div key={element} className="affinity-item">
              <label>{element}</label>
              <input
                type="number"
                step="0.1"
                value={formData.affinities.elemental[element] || 1.0}
                onChange={(e) => updateAffinity('elemental', element, parseFloat(e.target.value) || 1.0)}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="form-section">
        <h3 className="section-title">Elemental Detriments</h3>
        <div className="affinity-grid">
          {ELEMENTS.map((element) => (
            <div key={element} className="affinity-item">
              <label>{element}</label>
              <input
                type="number"
                step="0.1"
                value={formData.detriments.elemental[element] || 1.0}
                onChange={(e) => updateDetriment('elemental', element, parseFloat(e.target.value) || 1.0)}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="form-section">
        <h3 className="section-title">Additional Properties</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>Auxiliary Slots</label>
            <input
              type="number"
              min="0"
              value={formData.auxiliary_slots}
              onChange={(e) => updateField('auxiliary_slots', parseInt(e.target.value) || 0)}
            />
          </div>
        </div>
        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.size_constraints !== null}
              onChange={toggleSizeConstraints}
            />
            Enable Size Constraints
          </label>
          {formData.size_constraints && (
            <div className="size-constraints-inputs">
              <input
                type="number"
                min="0"
                max="100"
                value={formData.size_constraints[0]}
                onChange={(e) =>
                  updateField('size_constraints', [
                    parseInt(e.target.value) || 0,
                    formData.size_constraints![1],
                  ])
                }
                placeholder="Min"
              />
              <span>to</span>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.size_constraints[1]}
                onChange={(e) =>
                  updateField('size_constraints', [
                    formData.size_constraints![0],
                    parseInt(e.target.value) || 100,
                  ])
                }
                placeholder="Max"
              />
            </div>
          )}
        </div>
      </div>

      <div className="form-section">
        <h3 className="section-title">Primary Effect Styles (Mutually Exclusive)</h3>
        <p className="section-description">
          Primary styles are mutually exclusive - only one executes per turn. Selection is based on subtype or relative weights.
        </p>
        <button
          className="add-style-btn"
          onClick={() => {
            setStyleDesignerMode('primary');
            setShowStyleDesigner(true);
          }}
        >
          + Add Primary Effect Style
        </button>
        {(formData.primary_effect_styles || []).length > 0 && (
          <div className="style-list">
            {(formData.primary_effect_styles || []).map((style, index) => (
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
                  onClick={() => handleRemovePrimaryStyle(index)}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="form-section">
        <h3 className="section-title">Secondary Effect Styles (Independent)</h3>
        <p className="section-description">
          Secondary styles execute independently based on their execution probability.
        </p>
        <button
          className="add-style-btn"
          onClick={() => {
            setStyleDesignerMode('secondary');
            setShowStyleDesigner(true);
          }}
        >
          + Add Secondary Effect Style
        </button>
        {(formData.secondary_effect_styles || []).length > 0 && (
          <div className="style-list">
            {(formData.secondary_effect_styles || []).map((style, index) => (
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
                  onClick={() => handleRemoveSecondaryStyle(index)}
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

      {/* Legacy effectors section (deprecated) */}
      <div className="form-section" style={{ opacity: 0.6 }}>
        <h3 className="section-title">Effectors (Deprecated - Use Effect Styles)</h3>
        <SimpleEffectorSelector onAdd={handleAddEffector} />
        <EffectorList effectors={formData.effectors || []} onRemove={handleRemoveEffector} />
      </div>
    </div>
  );
}

