import { useState, useEffect } from 'react';
import apiClient from '../../utils/api';
import './EffectorSelector.css';

export interface EffectorConfig {
  effector_type: string;
  effector_name: string;
  execution_probability?: number;
  damage_subtype?: string;
  element_type?: string;
  attribute_type?: string;
  affected_attributes?: string[];
  base_damage?: number;
  base_restoration?: number;
  base_buff?: number;
  base_debuff?: number;
  duration?: number;
  stackable?: boolean;
  distribution_parameters?: {
    type: string;
    params: Record<string, any>;
  };
  process_config?: Record<string, any>;
  input_effectors?: string[];
  output_effectors?: string[];
}

interface EffectorSelectorProps {
  onSelect: (effector: EffectorConfig) => void;
  selectedEffectors?: EffectorConfig[];
}

export default function EffectorSelector({ onSelect, selectedEffectors = [] }: EffectorSelectorProps) {
  const [effectors, setEffectors] = useState<EffectorConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEffectors();
  }, [selectedType]);

  const fetchEffectors = async () => {
    try {
      setLoading(true);
      const params = selectedType !== 'all' ? { effector_type: selectedType } : {};
      const response = await apiClient.get('/api/effectors/', { params });
      setEffectors(response.data.map((e: any) => ({
        ...e.config,
        effector_type: e.effector_type,
        effector_name: e.effector_name,
      })));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load effectors');
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (effector: EffectorConfig) => {
    // Check if already selected
    const isSelected = selectedEffectors.some(
      e => e.effector_name === effector.effector_name && e.effector_type === effector.effector_type
    );
    
    if (!isSelected) {
      onSelect(effector);
    }
  };

  if (loading) {
    return <div className="effector-selector loading">Loading effectors...</div>;
  }

  return (
    <div className="effector-selector">
      <div className="effector-selector-header">
        <h3>Add Effector</h3>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="type-filter"
        >
          <option value="all">All Types</option>
          <option value="damage">Damage</option>
          <option value="regenerative">Regenerative</option>
          <option value="buff">Buff</option>
          <option value="debuff">Debuff</option>
          <option value="process">Process</option>
        </select>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="effector-list">
        {effectors.map((effector, index) => {
          const isSelected = selectedEffectors.some(
            e => e.effector_name === effector.effector_name && e.effector_type === effector.effector_type
          );
          
          return (
            <div
              key={`${effector.effector_type}-${effector.effector_name}-${index}`}
              className={`effector-item ${isSelected ? 'selected' : ''}`}
              onClick={() => handleSelect(effector)}
            >
              <div className="effector-item-header">
                <span className="effector-type-badge">{effector.effector_type}</span>
                <span className="effector-name">{effector.effector_name}</span>
              </div>
              <div className="effector-item-details">
                {effector.damage_subtype && (
                  <span className="detail-tag">Damage: {effector.damage_subtype}</span>
                )}
                {effector.element_type && (
                  <span className="detail-tag">Element: {effector.element_type}</span>
                )}
                {effector.attribute_type && (
                  <span className="detail-tag">Attribute: {effector.attribute_type}</span>
                )}
                {effector.affected_attributes && (
                  <span className="detail-tag">
                    Attributes: {effector.affected_attributes.join(', ')}
                  </span>
                )}
                {effector.duration !== undefined && (
                  <span className="detail-tag">Duration: {effector.duration}s</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

