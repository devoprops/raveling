import { useState, useEffect, useRef } from 'react';
import apiClient from '../../utils/api';
import { EffectStyleConfig } from '../effectstyles';
import EffectStyleDesigner from '../effectstyles/EffectStyleDesigner';
import ThumbnailPicker from './ThumbnailPicker';
import ElementAffinitiesWidget from '../common/ElementAffinitiesWidget';
import { createDefaultAffinities, createDefaultDetriments } from '../../utils/constants';
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
  size_constraints: [number, number];
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
    size_constraints: initialData?.size_constraints || [0, 100],
    thumbnail_path: initialData?.thumbnail_path || '',
    restrictions: initialData?.restrictions || {},
  });
  
  const [showStyleDesigner, setShowStyleDesigner] = useState(false);
  const [styleDesignerMode, setStyleDesignerMode] = useState<'primary' | 'secondary'>('primary');
  const [editingStyleIndex, setEditingStyleIndex] = useState<number | null>(null);
  const [showLoadStyleModal, setShowLoadStyleModal] = useState(false);

  useEffect(() => {
    onChange(formData);
  }, [formData, onChange]);

  // Update formData when initialData changes (e.g., when loading a config)
  // Use JSON.stringify to detect deep changes
  const prevInitialDataStr = useRef<string>('');
  
  useEffect(() => {
    const currentDataStr = JSON.stringify(initialData);
    // Only update if initialData actually changed
    if (currentDataStr !== prevInitialDataStr.current && initialData) {
      const newFormData: WeaponFormData = {
        name: initialData.name ?? '',
        short_desc: initialData.short_desc ?? '',
        long_desc: initialData.long_desc ?? '',
        weight_kg: initialData.weight_kg ?? 0,
        length_cm: initialData.length_cm ?? 0,
        width_cm: initialData.width_cm ?? 0,
        material: initialData.material ?? '',
        effectors: initialData.effectors ?? [],
        primary_effect_styles: initialData.primary_effect_styles ?? [],
        secondary_effect_styles: initialData.secondary_effect_styles ?? [],
        affinities: initialData.affinities ?? createDefaultAffinities(),
        detriments: initialData.detriments ?? createDefaultDetriments(),
        auxiliary_slots: initialData.auxiliary_slots ?? 0,
        size_constraints: initialData.size_constraints ?? [0, 100],
        thumbnail_path: initialData.thumbnail_path ?? '',
        restrictions: initialData.restrictions ?? {},
      };
      setFormData(newFormData);
      prevInitialDataStr.current = currentDataStr;
    }
  }, [initialData]);

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


  const handleAddEffectStyle = (style: EffectStyleConfig) => {
    setFormData((prev) => {
      if (styleDesignerMode === 'primary') {
        if (editingStyleIndex !== null) {
          // Replace existing style
          const newStyles = [...(prev.primary_effect_styles || [])];
          newStyles[editingStyleIndex] = style;
          return { ...prev, primary_effect_styles: newStyles };
        } else {
          // Add new style
          return {
            ...prev,
            primary_effect_styles: [...(prev.primary_effect_styles || []), style],
          };
        }
      } else {
        if (editingStyleIndex !== null) {
          // Replace existing style
          const newStyles = [...(prev.secondary_effect_styles || [])];
          newStyles[editingStyleIndex] = style;
          return { ...prev, secondary_effect_styles: newStyles };
        } else {
          // Add new style
          return {
            ...prev,
            secondary_effect_styles: [...(prev.secondary_effect_styles || []), style],
          };
        }
      }
    });
    setShowStyleDesigner(false);
    setEditingStyleIndex(null);
  };

  const handleEditStyle = (index: number, mode: 'primary' | 'secondary') => {
    setStyleDesignerMode(mode);
    setEditingStyleIndex(index);
    setShowStyleDesigner(true);
  };

  const [availableStyles, setAvailableStyles] = useState<any[]>([]);
  const [loadingStyles, setLoadingStyles] = useState(false);

  const loadAvailableStyles = async () => {
    try {
      setLoadingStyles(true);
      const response = await apiClient.get('/api/effect-styles/');
      const allStyles: any[] = [];
      Object.values(response.data).forEach((typeGroup: any) => {
        if (typeGroup.pre_designed) {
          allStyles.push(...typeGroup.pre_designed);
        }
        if (typeGroup.custom) {
          allStyles.push(...typeGroup.custom);
        }
      });
      setAvailableStyles(allStyles);
    } catch (error) {
      console.error('Failed to load effect styles:', error);
    } finally {
      setLoadingStyles(false);
    }
  };

  const handleLoadStyle = async (styleId: number) => {
    try {
      const response = await apiClient.get(`/api/effect-styles/${styleId}`);
      const style = response.data;
      
      // Convert API response to EffectStyleConfig format
      const effectorConfig = Array.isArray(style.effector_config)
        ? style.effector_config[0] || {}
        : style.effector_config || {};
      
      const effectStyleConfig: EffectStyleConfig = {
        name: style.name,
        style_type: style.style_type,
        subtype: style.subtype,
        description: style.description || '',
        process_verb: style.process_verb || '',
        execution_probability: style.execution_probability,
        effector: effectorConfig,
        effectors: Array.isArray(style.effector_config) ? style.effector_config : [effectorConfig],
        style_attributes: style.style_attributes,
      };
      
      handleAddEffectStyle(effectStyleConfig);
      setShowLoadStyleModal(false);
    } catch (error: any) {
      console.error('Failed to load effect style:', error);
      alert(`Failed to load effect style: ${error.response?.data?.detail || error.message}`);
    }
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

  const updateSizeConstraints = (index: 0 | 1, value: number) => {
    const current = formData.size_constraints || [0, 100];
    const updated = [...current] as [number, number];
    updated[index] = value;
    updateField('size_constraints', updated);
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
        <h3 className="section-title">Primary Effect Styles (Mutually Exclusive)</h3>
        <p className="section-description">
          Primary styles are mutually exclusive - only one executes per turn. Selection is based on subtype or relative weights.
        </p>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <button
              className="add-style-btn"
              onClick={() => {
                setEditingStyleIndex(null);
                setStyleDesignerMode('primary');
                setShowStyleDesigner(true);
              }}
            >
              Add Primary Effect Style
            </button>
            <select
              className="add-style-btn"
              style={{ 
                marginLeft: '0.5rem',
                appearance: 'auto',
                paddingRight: '2rem',
                cursor: 'pointer'
              }}
              onChange={(e) => {
                if (e.target.value === 'new') {
                  setEditingStyleIndex(null);
                  setStyleDesignerMode('primary');
                  setShowStyleDesigner(true);
                  e.target.value = '';
                } else if (e.target.value === 'load') {
                  setShowLoadStyleModal(true);
                  loadAvailableStyles();
                  e.target.value = '';
                }
              }}
              value=""
            >
              <option value="" disabled>▼</option>
              <option value="new">New...</option>
              <option value="load">Load...</option>
            </select>
          </div>
        </div>
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
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="remove-btn"
                    onClick={() => handleEditStyle(index, 'primary')}
                    style={{ background: 'rgba(74, 158, 255, 0.2)', color: '#4a9eff', borderColor: 'rgba(74, 158, 255, 0.3)' }}
                  >
                    Edit
                  </button>
                  <button
                    className="remove-btn"
                    onClick={() => handleRemovePrimaryStyle(index)}
                  >
                    Remove
                  </button>
                </div>
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
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <button
              className="add-style-btn"
              onClick={() => {
                setEditingStyleIndex(null);
                setStyleDesignerMode('secondary');
                setShowStyleDesigner(true);
              }}
            >
              Add Secondary Effect Style
            </button>
            <select
              className="add-style-btn"
              style={{ 
                marginLeft: '0.5rem',
                appearance: 'auto',
                paddingRight: '2rem',
                cursor: 'pointer'
              }}
              onChange={(e) => {
                if (e.target.value === 'new') {
                  setEditingStyleIndex(null);
                  setStyleDesignerMode('secondary');
                  setShowStyleDesigner(true);
                  e.target.value = '';
                } else if (e.target.value === 'load') {
                  setShowLoadStyleModal(true);
                  loadAvailableStyles();
                  e.target.value = '';
                }
              }}
              value=""
            >
              <option value="" disabled>▼</option>
              <option value="new">New...</option>
              <option value="load">Load...</option>
            </select>
          </div>
        </div>
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
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="remove-btn"
                    onClick={() => handleEditStyle(index, 'secondary')}
                    style={{ background: 'rgba(74, 158, 255, 0.2)', color: '#4a9eff', borderColor: 'rgba(74, 158, 255, 0.3)' }}
                  >
                    Edit
                  </button>
                  <button
                    className="remove-btn"
                    onClick={() => handleRemoveSecondaryStyle(index)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="form-section">
        <h3 className="section-title">Physical Properties</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', alignItems: 'start' }}>
          <div>
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
            <div className="form-grid" style={{ marginTop: '1rem' }}>
              <div className="form-group">
                <label>Auxiliary Slots</label>
                <input
                  type="number"
                  min="0"
                  value={formData.auxiliary_slots}
                  onChange={(e) => updateField('auxiliary_slots', parseInt(e.target.value) || 0)}
                />
              </div>
              <div className="form-group">
                <label>Size Constraints</label>
                <div className="size-constraints-inputs">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.size_constraints?.[0] ?? 0}
                    onChange={(e) => updateSizeConstraints(0, parseInt(e.target.value) || 0)}
                    placeholder="Min"
                  />
                  <span>to</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.size_constraints?.[1] ?? 100}
                    onChange={(e) => updateSizeConstraints(1, parseInt(e.target.value) || 100)}
                    placeholder="Max"
                  />
                </div>
              </div>
            </div>
          </div>
          <div>
            <h4 style={{ marginTop: 0, marginBottom: '1rem' }}>Thumbnail</h4>
            <div style={{ aspectRatio: '1', maxWidth: '300px' }}>
              <ThumbnailPicker
                thumbnailPath={formData.thumbnail_path}
                itemName={formData.name || 'weapon'}
                onThumbnailChange={(path) => updateField('thumbnail_path', path)}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="form-section">
        <ElementAffinitiesWidget
          affinities={formData.affinities}
          detriments={formData.detriments}
          onAffinityChange={(element, value) => updateAffinity('elemental', element, value)}
          onDetrimentChange={(element, value) => updateDetriment('elemental', element, value)}
        />
      </div>

      {showStyleDesigner && (
        <div className="style-designer-overlay">
          <div className="style-designer-container">
            <EffectStyleDesigner
              onSave={handleAddEffectStyle}
              onCancel={() => {
                setShowStyleDesigner(false);
                setEditingStyleIndex(null);
              }}
              initialStyle={editingStyleIndex !== null ? (
                styleDesignerMode === 'primary' 
                  ? formData.primary_effect_styles?.[editingStyleIndex]
                  : formData.secondary_effect_styles?.[editingStyleIndex]
              ) : undefined}
            />
          </div>
        </div>
      )}

      {showLoadStyleModal && (
        <div className="modal-overlay" onClick={() => setShowLoadStyleModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Load Effect Style</h2>
              <button className="modal-close" onClick={() => setShowLoadStyleModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {loadingStyles ? (
                <p>Loading styles...</p>
              ) : availableStyles.length === 0 ? (
                <p>No effect styles found.</p>
              ) : (
                <div className="config-list">
                  {availableStyles.map((style) => (
                    <div
                      key={style.id}
                      className="config-item"
                      onClick={() => handleLoadStyle(style.id)}
                    >
                      <div>
                        <strong>{style.name}</strong> ({style.subtype})
                        <div style={{ fontSize: '0.85rem', color: 'rgba(255, 255, 255, 0.6)', marginTop: '0.25rem' }}>
                          {style.style_type} • {style.description || 'No description'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

