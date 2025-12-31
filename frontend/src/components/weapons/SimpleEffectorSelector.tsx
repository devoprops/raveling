import { useState } from 'react';
import { EffectorConfig } from '../effectors/EffectorSelector';
import './SimpleEffectorSelector.css';

const EFFECTOR_TYPES = ['damage', 'regenerative', 'buff', 'debuff', 'process'];
const ELEMENTS = ['Earth', 'Water', 'Air', 'Fire'];
const DAMAGE_SUBTYPES = ['physical', 'elemental'];
const DISTRIBUTION_TYPES = ['uniform', 'gaussian', 'skewnorm', 'bimodal', 'die_roll'];

interface SimpleEffectorSelectorProps {
  onAdd: (effector: EffectorConfig) => void;
}

export default function SimpleEffectorSelector({ onAdd }: SimpleEffectorSelectorProps) {
  const [selectedType, setSelectedType] = useState<string>('');
  const [effectorName, setEffectorName] = useState<string>('');
  const [executionProbability, setExecutionProbability] = useState<number>(1.0);
  
  // Damage effector fields
  const [damageSubtype, setDamageSubtype] = useState<string>('physical');
  const [elementType, setElementType] = useState<string>('');
  const [baseDamage, setBaseDamage] = useState<number>(0);
  
  // Distribution fields
  const [distributionType, setDistributionType] = useState<string>('uniform');
  const [distParams, setDistParams] = useState<Record<string, any>>({
    min_val: 0,
    max_val: 10,
    mean: 5,
    std_dev: 2,
    skew: 0,
    mean1: 5,
    std1: 1,
    mean2: 10,
    std2: 1,
    weight: 0.5,
    notation: '1d6',
  });

  const handleApply = () => {
    if (!selectedType || !effectorName) {
      alert('Please select an effector type and provide a name');
      return;
    }

    const effector: EffectorConfig = {
      effector_type: selectedType,
      effector_name: effectorName,
      execution_probability: executionProbability,
    };

    if (selectedType === 'damage') {
      effector.damage_subtype = damageSubtype;
      effector.base_damage = baseDamage;
      
      if (damageSubtype === 'elemental') {
        if (!elementType) {
          alert('Please select an element type for elemental damage');
          return;
        }
        effector.element_type = elementType;
      }

      // Add distribution parameters
      const params: Record<string, any> = {};
      if (distributionType === 'uniform') {
        params.min_val = distParams.min_val;
        params.max_val = distParams.max_val;
      } else if (distributionType === 'gaussian') {
        params.mean = distParams.mean;
        params.std_dev = distParams.std_dev;
      } else if (distributionType === 'skewnorm') {
        params.mean = distParams.mean;
        params.std_dev = distParams.std_dev;
        params.skew = distParams.skew;
      } else if (distributionType === 'bimodal') {
        params.mean1 = distParams.mean1;
        params.std1 = distParams.std1;
        params.mean2 = distParams.mean2;
        params.std2 = distParams.std2;
        params.weight = distParams.weight;
      } else if (distributionType === 'die_roll') {
        params.notation = distParams.notation;
      }

      effector.distribution_parameters = {
        type: distributionType,
        params,
      };
    }

    onAdd(effector);
    
    // Reset form
    setSelectedType('');
    setEffectorName('');
    setExecutionProbability(1.0);
    setDamageSubtype('physical');
    setElementType('');
    setBaseDamage(0);
    setDistributionType('uniform');
  };

  return (
    <div className="simple-effector-selector">
      <div className="effector-selector-header">
        <h3>Add Effector</h3>
      </div>
      
      <div className="effector-form">
        <div className="form-row">
          <label>
            Effector Type:
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="effector-type-select"
            >
              <option value="">Select type...</option>
              {EFFECTOR_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </label>
        </div>

        {selectedType && (
          <>
            <div className="form-row">
              <label>
                Name:
                <input
                  type="text"
                  value={effectorName}
                  onChange={(e) => setEffectorName(e.target.value)}
                  placeholder="Effector name"
                />
              </label>
            </div>

            <div className="form-row">
              <label>
                Execution Probability:
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.05"
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

            {selectedType === 'damage' && (
              <>
                <div className="form-row">
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
                </div>

                {damageSubtype === 'elemental' && (
                  <div className="form-row">
                    <label>
                      Element:
                      <select
                        value={elementType}
                        onChange={(e) => setElementType(e.target.value)}
                      >
                        <option value="">Select element...</option>
                        {ELEMENTS.map((element) => (
                          <option key={element} value={element}>
                            {element}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                )}

                <div className="form-row">
                  <label>
                    Base Damage:
                    <input
                      type="number"
                      step="0.1"
                      value={baseDamage}
                      onChange={(e) => setBaseDamage(parseFloat(e.target.value) || 0)}
                    />
                  </label>
                </div>

                <div className="form-row">
                  <label>
                    Distribution Type:
                    <select
                      value={distributionType}
                      onChange={(e) => setDistributionType(e.target.value)}
                    >
                      {DISTRIBUTION_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                {distributionType === 'uniform' && (
                  <div className="form-row-group">
                    <label>
                      Min:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.min_val}
                        onChange={(e) =>
                          setDistParams({ ...distParams, min_val: parseFloat(e.target.value) || 0 })
                        }
                      />
                    </label>
                    <label>
                      Max:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.max_val}
                        onChange={(e) =>
                          setDistParams({ ...distParams, max_val: parseFloat(e.target.value) || 10 })
                        }
                      />
                    </label>
                  </div>
                )}

                {distributionType === 'gaussian' && (
                  <div className="form-row-group">
                    <label>
                      Mean:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.mean}
                        onChange={(e) =>
                          setDistParams({ ...distParams, mean: parseFloat(e.target.value) || 0 })
                        }
                      />
                    </label>
                    <label>
                      Std Dev:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.std_dev}
                        onChange={(e) =>
                          setDistParams({ ...distParams, std_dev: parseFloat(e.target.value) || 1 })
                        }
                      />
                    </label>
                  </div>
                )}

                {distributionType === 'skewnorm' && (
                  <div className="form-row-group">
                    <label>
                      Mean:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.mean}
                        onChange={(e) =>
                          setDistParams({ ...distParams, mean: parseFloat(e.target.value) || 0 })
                        }
                      />
                    </label>
                    <label>
                      Std Dev:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.std_dev}
                        onChange={(e) =>
                          setDistParams({ ...distParams, std_dev: parseFloat(e.target.value) || 1 })
                        }
                      />
                    </label>
                    <label>
                      Skew:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.skew}
                        onChange={(e) =>
                          setDistParams({ ...distParams, skew: parseFloat(e.target.value) || 0 })
                        }
                      />
                    </label>
                  </div>
                )}

                {distributionType === 'bimodal' && (
                  <div className="form-row-group">
                    <label>
                      Mean 1:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.mean1}
                        onChange={(e) =>
                          setDistParams({ ...distParams, mean1: parseFloat(e.target.value) || 0 })
                        }
                      />
                    </label>
                    <label>
                      Std 1:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.std1}
                        onChange={(e) =>
                          setDistParams({ ...distParams, std1: parseFloat(e.target.value) || 1 })
                        }
                      />
                    </label>
                    <label>
                      Mean 2:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.mean2}
                        onChange={(e) =>
                          setDistParams({ ...distParams, mean2: parseFloat(e.target.value) || 0 })
                        }
                      />
                    </label>
                    <label>
                      Std 2:
                      <input
                        type="number"
                        step="0.1"
                        value={distParams.std2}
                        onChange={(e) =>
                          setDistParams({ ...distParams, std2: parseFloat(e.target.value) || 1 })
                        }
                      />
                    </label>
                    <label>
                      Weight:
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={distParams.weight}
                        onChange={(e) =>
                          setDistParams({ ...distParams, weight: parseFloat(e.target.value) || 0.5 })
                        }
                      />
                    </label>
                  </div>
                )}

                {distributionType === 'die_roll' && (
                  <div className="form-row">
                    <label>
                      Notation (e.g., 2d6):
                      <input
                        type="text"
                        value={distParams.notation}
                        onChange={(e) =>
                          setDistParams({ ...distParams, notation: e.target.value })
                        }
                        placeholder="1d6"
                      />
                    </label>
                  </div>
                )}
              </>
            )}

            <div className="form-actions">
              <button onClick={handleApply} className="apply-btn">
                + Add Effector
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

