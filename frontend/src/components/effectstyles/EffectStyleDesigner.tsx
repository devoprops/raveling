import { useState, useEffect } from 'react';
import axios from 'axios';
import DistributionParameterWidget, { DistributionParameters } from '../weapons/DistributionParameterWidget';
import './EffectStyleDesigner.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const STYLE_TYPES = ['Physical', 'Spell', 'Buff', 'Debuff', 'Regen', 'Process'];
const EFFECTOR_TYPES = ['damage', 'regenerative', 'buff', 'debuff', 'process'];
const ELEMENTS = ['earth', 'water', 'air', 'fire'];
const DAMAGE_SUBTYPES = ['physical', 'elemental'];

export interface EffectStyleConfig {
  name: string;
  style_type: string;
  subtype: string;
  description: string;
  process_verb: string;
  execution_probability: number;
  effector?: {
    effector_type: string;
    effector_name: string;
    [key: string]: any;
  }; // Single effector (backwards compat)
  effectors?: Array<{
    effector_type: string;
    effector_name: string;
    [key: string]: any;
  }>; // Multiple effectors (new)
  style_attributes?: {
    range?: number;
    area?: number;
    duration?: string;
    cost?: Record<string, any>;
    affected_attributes?: string[];
  };
}

interface EffectStyleDesignerProps {
  onSave: (style: EffectStyleConfig) => void;
  onCancel?: () => void;
  initialStyle?: EffectStyleConfig;
}

export default function EffectStyleDesigner({ onSave, onCancel, initialStyle }: EffectStyleDesignerProps) {
  const [styleType, setStyleType] = useState<string>(initialStyle?.style_type || '');
  const [selectionMode, setSelectionMode] = useState<'pre-designed' | 'custom'>(initialStyle ? 'custom' : 'custom');
  const [preDesignedStyles, setPreDesignedStyles] = useState<any[]>([]);
  const [selectedPreDesignedId, setSelectedPreDesignedId] = useState<number | null>(null);
  
  const [name, setName] = useState<string>(initialStyle?.name || '');
  const [subtype, setSubtype] = useState<string>(initialStyle?.subtype || '');
  const [description, setDescription] = useState<string>(initialStyle?.description || '');
  const [processVerb, setProcessVerb] = useState<string>(initialStyle?.process_verb || '');
  const [executionProbability, setExecutionProbability] = useState<number>(initialStyle?.execution_probability ?? 1.0);
  
  // Effector fields - handle both effector and effectors
  const effector = initialStyle?.effector || (initialStyle?.effectors && initialStyle.effectors[0]) || {};
  const [effectorType, setEffectorType] = useState<string>(effector?.effector_type || 'damage');
  const [effectorName, setEffectorName] = useState<string>(effector?.effector_name || '');
  const [damageSubtype, setDamageSubtype] = useState<string>(effector?.damage_subtype || 'physical');
  const [elementType, setElementType] = useState<string>(effector?.element_type || '');
  const [baseDamage, setBaseDamage] = useState<number>(effector?.base_damage || 0);
  
  // Distribution parameters
  const [distributionParams, setDistributionParams] = useState<DistributionParameters>({
    type: effector?.distribution_parameters?.type || 'uniform',
    params: effector?.distribution_parameters?.params || { min_val: 0, max_val: 10 },
  });

  // Style attributes (type-specific)
  const [range, setRange] = useState<number>(initialStyle?.style_attributes?.range ?? 1);
  const [area, setArea] = useState<number>(initialStyle?.style_attributes?.area ?? 1);
  const [duration, setDuration] = useState<string>(initialStyle?.style_attributes?.duration || '1-call');
  const [cost, setCost] = useState<Record<string, any>>(initialStyle?.style_attributes?.cost || {});
  const [affectedAttributes, setAffectedAttributes] = useState<string[]>(initialStyle?.style_attributes?.affected_attributes || []);
  const [newAttribute, setNewAttribute] = useState<string>('');

  // Load pre-designed styles when style type changes
  useEffect(() => {
    if (styleType && selectionMode === 'pre-designed') {
      loadPreDesignedStyles();
    }
  }, [styleType, selectionMode]);

  // Load selected pre-designed style
  useEffect(() => {
    if (selectedPreDesignedId && preDesignedStyles.length > 0) {
      const style = preDesignedStyles.find((s) => s.id === selectedPreDesignedId);
      if (style) {
        loadStyle(style);
      }
    }
  }, [selectedPreDesignedId]);

  const loadPreDesignedStyles = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/effect-styles/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { style_type: styleType },
      });
      
      const styles = response.data[styleType]?.pre_designed || [];
      setPreDesignedStyles(styles);
    } catch (error) {
      console.error('Failed to load pre-designed styles:', error);
    }
  };

  const loadStyle = (style: any) => {
    setName(style.name);
    setSubtype(style.subtype);
    setDescription(style.description || '');
    setProcessVerb(style.process_verb || style.subtype);
    setExecutionProbability(style.execution_probability);
    
    // Handle effector_config - can be single effector or array
    const effectorConfig = style.effector_config || {};
    const effector = Array.isArray(effectorConfig) ? effectorConfig[0] || {} : effectorConfig;
    
    setEffectorType(effector.effector_type || 'damage');
    setEffectorName(effector.effector_name || '');
    setDamageSubtype(effector.damage_subtype || 'physical');
    setElementType(effector.element_type || '');
    setBaseDamage(effector.base_damage || 0);
    
    if (effector.distribution_parameters) {
      setDistributionParams({
        type: effector.distribution_parameters.type || 'uniform',
        params: effector.distribution_parameters.params || {},
      });
    }

    // Load style attributes
    const attrs = style.style_attributes || {};
    setRange(attrs.range ?? 1);
    setArea(attrs.area ?? 1);
    setDuration(attrs.duration || '1-call');
    setCost(attrs.cost || {});
    setAffectedAttributes(attrs.affected_attributes || []);
  };

  const handleSave = async () => {
    if (!name || !subtype || !styleType) {
      alert('Please fill in name, subtype, and style type');
      return;
    }

    // Build effector config
    const effectorConfig: any = {
      effector_type: effectorType,
      effector_name: effectorName || `${name}_effector`,
    };

    if (effectorType === 'damage') {
      effectorConfig.damage_subtype = damageSubtype;
      effectorConfig.base_damage = baseDamage;
      if (damageSubtype === 'elemental') {
        if (!elementType) {
          alert('Please select an element type for elemental damage');
          return;
        }
        effectorConfig.element_type = elementType;
      }
      effectorConfig.distribution_parameters = distributionParams;
    }

    // Build style attributes based on style type
    const styleAttributes: any = {
      range,
      area,
    };

    // Add type-specific attributes
    if (styleType === 'Spell' || styleType === 'Buff' || styleType === 'Debuff') {
      styleAttributes.duration = duration;
    }
    
    if (styleType === 'Buff' || styleType === 'Debuff') {
      styleAttributes.affected_attributes = affectedAttributes;
    }

    // Add cost if provided
    if (Object.keys(cost).length > 0) {
      styleAttributes.cost = cost;
    }

    const styleConfig: EffectStyleConfig = {
      name,
      style_type: styleType,
      subtype,
      description,
      process_verb: processVerb || subtype,
      execution_probability: executionProbability,
      effector: effectorConfig,
      style_attributes: styleAttributes,
    };

    // If pre-designed and we want to save to library
    if (selectionMode === 'pre-designed' && selectedPreDesignedId) {
      try {
        const token = localStorage.getItem('token');
        await axios.put(
          `${API_URL}/api/effect-styles/${selectedPreDesignedId}`,
          styleConfig,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (error) {
        console.error('Failed to save to library:', error);
        alert('Failed to save to library, but style will be used inline');
      }
    }

    onSave(styleConfig);
  };

  const resetToDefaults = () => {
    setName('');
    setSubtype('');
    setDescription('');
    setProcessVerb('');
    setExecutionProbability(1.0);
    setEffectorType('damage');
    setEffectorName('');
    setDamageSubtype('physical');
    setElementType('');
    setBaseDamage(0);
    setDistributionParams({
      type: 'uniform',
      params: { min_val: 0, max_val: 10 },
    });
    setRange(1);
    setArea(1);
    setDuration('1-call');
    setCost({});
    setAffectedAttributes([]);
    setNewAttribute('');
  };

  const addAffectedAttribute = () => {
    if (newAttribute.trim() && !affectedAttributes.includes(newAttribute.trim())) {
      setAffectedAttributes([...affectedAttributes, newAttribute.trim()]);
      setNewAttribute('');
    }
  };

  const removeAffectedAttribute = (attr: string) => {
    setAffectedAttributes(affectedAttributes.filter(a => a !== attr));
  };

  return (
    <div className="effect-style-designer">
      <div className="style-designer-header">
        <h3>Effect Style Designer</h3>
        {onCancel && (
          <button className="cancel-btn" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>

      <div className="style-type-selector">
        <label>
          Style Type:
          <select
            value={styleType}
            onChange={(e) => {
              setStyleType(e.target.value);
              resetToDefaults();
            }}
          >
            <option value="">Select type...</option>
            {STYLE_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>

        {styleType && (
          <div className="selection-mode">
            <label>
              <input
                type="radio"
                checked={selectionMode === 'custom'}
                onChange={() => {
                  setSelectionMode('custom');
                  resetToDefaults();
                }}
              />
              Custom (start with defaults)
            </label>
            <label>
              <input
                type="radio"
                checked={selectionMode === 'pre-designed'}
                onChange={() => {
                  setSelectionMode('pre-designed');
                  loadPreDesignedStyles();
                }}
              />
              Pre-designed (load from library)
            </label>
          </div>
        )}

        {selectionMode === 'pre-designed' && preDesignedStyles.length > 0 && (
          <label>
            Select Pre-designed Style:
            <select
              value={selectedPreDesignedId || ''}
              onChange={(e) => setSelectedPreDesignedId(Number(e.target.value) || null)}
            >
              <option value="">Select a style...</option>
              {preDesignedStyles.map((style) => (
                <option key={style.id} value={style.id}>
                  {style.name} ({style.subtype})
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      {styleType && (
        <div className="style-form">
          <div className="form-section">
            <h4>Style Information</h4>
            <label>
              Name:
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Slash, Lightning"
              />
            </label>
            <label>
              Subtype:
              <input
                type="text"
                value={subtype}
                onChange={(e) => setSubtype(e.target.value)}
                placeholder="e.g., slash, thrust, lightning"
              />
            </label>
            <label>
              Description:
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Description of this effect style"
                rows={3}
              />
            </label>
            <label>
              Process Verb:
              <input
                type="text"
                value={processVerb}
                onChange={(e) => setProcessVerb(e.target.value)}
                placeholder="e.g., slash, thrust, kick (defaults to subtype)"
              />
            </label>
            <label>
              Execution Probability:
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={executionProbability}
                onChange={(e) => {
                  const val = parseFloat(e.target.value);
                  if (!isNaN(val)) {
                    setExecutionProbability(val);
                  }
                }}
                onBlur={(e) => {
                  const val = parseFloat(e.target.value);
                  if (isNaN(val) || val < 0) {
                    setExecutionProbability(0);
                  } else if (val > 1) {
                    setExecutionProbability(1);
                  } else {
                    setExecutionProbability(val);
                  }
                }}
              />
            </label>
          </div>

          <div className="form-section">
            <h4>Effector Configuration</h4>
            <label>
              Effector Type:
              <select
                value={effectorType}
                onChange={(e) => {
                  setEffectorType(e.target.value);
                  setEffectorName('');
                }}
              >
                {EFFECTOR_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Effector Name:
              <input
                type="text"
                value={effectorName}
                onChange={(e) => setEffectorName(e.target.value)}
                placeholder="Optional (auto-generated if empty)"
              />
            </label>

            {effectorType === 'damage' && (
              <>
                <label>
                  Damage Subtype:
                  <select
                    value={damageSubtype}
                    onChange={(e) => {
                      setDamageSubtype(e.target.value);
                      if (e.target.value === 'physical') {
                        setElementType('');
                      }
                    }}
                  >
                    {DAMAGE_SUBTYPES.map((subtype) => (
                      <option key={subtype} value={subtype}>
                        {subtype.charAt(0).toUpperCase() + subtype.slice(1)}
                      </option>
                    ))}
                  </select>
                </label>

                {damageSubtype === 'elemental' && (
                  <label>
                    Element Type:
                    <select
                      value={elementType}
                      onChange={(e) => setElementType(e.target.value)}
                    >
                      <option value="">Select element...</option>
                      {ELEMENTS.map((element) => (
                        <option key={element} value={element}>
                          {element.charAt(0).toUpperCase() + element.slice(1)}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                <label>
                  Base Damage:
                  <input
                    type="number"
                    step="0.1"
                    value={baseDamage}
                    onChange={(e) => setBaseDamage(parseFloat(e.target.value) || 0)}
                  />
                </label>

                <div className="distribution-section">
                  <h5>Damage Distribution</h5>
                  <DistributionParameterWidget
                    distributionType={distributionParams.type}
                    parameters={distributionParams.params}
                    onParametersChange={(params) => setDistributionParams(params)}
                  />
                </div>
              </>
            )}
          </div>

          <div className="form-section">
            <h4>Style Attributes</h4>
            <label>
              Range:
              <input
                type="number"
                min="1"
                value={range}
                onChange={(e) => setRange(parseInt(e.target.value) || 1)}
              />
            </label>
            <label>
              Area:
              <input
                type="number"
                min="1"
                value={area}
                onChange={(e) => setArea(parseInt(e.target.value) || 1)}
              />
            </label>

            {(styleType === 'Spell' || styleType === 'Buff' || styleType === 'Debuff') && (
              <label>
                Duration:
                <input
                  type="text"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  placeholder="e.g., 1-call, 3-rounds, permanent"
                />
              </label>
            )}

            {(styleType === 'Buff' || styleType === 'Debuff') && (
              <>
                <label>
                  Affected Attributes:
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <input
                      type="text"
                      value={newAttribute}
                      onChange={(e) => setNewAttribute(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addAffectedAttribute();
                        }
                      }}
                      placeholder="e.g., strength, agility"
                    />
                    <button type="button" onClick={addAffectedAttribute}>
                      Add
                    </button>
                  </div>
                  {affectedAttributes.length > 0 && (
                    <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                      {affectedAttributes.map((attr, idx) => (
                        <span
                          key={idx}
                          style={{
                            padding: '0.25rem 0.5rem',
                            background: 'rgba(74, 158, 255, 0.2)',
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                          }}
                        >
                          {attr}
                          <button
                            type="button"
                            onClick={() => removeAffectedAttribute(attr)}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: '#ff6b6b',
                              cursor: 'pointer',
                              padding: 0,
                              fontSize: '1.2rem',
                            }}
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </label>
              </>
            )}

            <label>
              Cost (JSON):
              <textarea
                value={JSON.stringify(cost, null, 2)}
                onChange={(e) => {
                  try {
                    setCost(JSON.parse(e.target.value));
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"mana": 10} or {"stamina": 5}'
                rows={3}
              />
            </label>
          </div>

          <div className="form-actions">
            <button className="save-btn" onClick={handleSave}>
              {selectionMode === 'pre-designed' ? 'Save & Use' : 'Use Style'}
            </button>
            {selectionMode === 'pre-designed' && (
              <button
                className="save-library-btn"
                onClick={async () => {
                  await handleSave();
                  // Also save to library as new
                  try {
                    const token = localStorage.getItem('token');
                    const effectorConfig: any = {
                      effector_type: effectorType,
                      effector_name: effectorName || `${name}_effector`,
                    };
                    if (effectorType === 'damage') {
                      effectorConfig.damage_subtype = damageSubtype;
                      effectorConfig.base_damage = baseDamage;
                      if (damageSubtype === 'elemental') {
                        effectorConfig.element_type = elementType;
                      }
                      effectorConfig.distribution_parameters = distributionParams;
                    }

                    // Build style attributes
                    const styleAttributes: any = {
                      range,
                      area,
                    };

                    if (styleType === 'Spell' || styleType === 'Buff' || styleType === 'Debuff') {
                      styleAttributes.duration = duration;
                    }
                    
                    if (styleType === 'Buff' || styleType === 'Debuff') {
                      styleAttributes.affected_attributes = affectedAttributes;
                    }

                    if (Object.keys(cost).length > 0) {
                      styleAttributes.cost = cost;
                    }

                    await axios.post(
                      `${API_URL}/api/effect-styles/`,
                      {
                        name,
                        style_type: styleType,
                        subtype,
                        description,
                        process_verb: processVerb || subtype,
                        execution_probability: executionProbability,
                        effector: effectorConfig,
                        style_attributes: styleAttributes,
                      },
                      { headers: { Authorization: `Bearer ${token}` } }
                    );
                    alert('Style saved to library!');
                  } catch (error) {
                    console.error('Failed to save to library:', error);
                    alert('Failed to save to library');
                  }
                }}
              >
                Save to Library
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

