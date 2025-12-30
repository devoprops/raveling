import { useState } from 'react';
import { EffectorConfig } from './EffectorSelector';
import './EffectorList.css';

interface EffectorListProps {
  effectors: EffectorConfig[];
  onRemove: (index: number) => void;
  onEdit?: (index: number, effector: EffectorConfig) => void;
}

export default function EffectorList({ effectors, onRemove, onEdit }: EffectorListProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  if (effectors.length === 0) {
    return (
      <div className="effector-list empty">
        <p>No effectors added. Use the effector selector to add effects.</p>
      </div>
    );
  }

  return (
    <div className="effector-list">
      <h3>Effectors ({effectors.length})</h3>
      <div className="effector-list-items">
        {effectors.map((effector, index) => (
          <div key={index} className="effector-list-item">
            <div className="effector-list-item-header">
              <span className="effector-type-badge">{effector.effector_type}</span>
              <span className="effector-name">{effector.effector_name}</span>
              <div className="effector-actions">
                {onEdit && (
                  <button
                    className="edit-button"
                    onClick={() => setEditingIndex(index)}
                    title="Edit effector"
                  >
                    ✏️
                  </button>
                )}
                <button
                  className="remove-button"
                  onClick={() => onRemove(index)}
                  title="Remove effector"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="effector-list-item-details">
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
              {effector.base_damage !== undefined && (
                <span className="detail-tag">Base: {effector.base_damage}</span>
              )}
              {effector.base_restoration !== undefined && (
                <span className="detail-tag">Base: {effector.base_restoration}</span>
              )}
              {effector.base_buff !== undefined && (
                <span className="detail-tag">Base: {effector.base_buff}</span>
              )}
              {effector.base_debuff !== undefined && (
                <span className="detail-tag">Base: {effector.base_debuff}</span>
              )}
              {effector.duration !== undefined && (
                <span className="detail-tag">Duration: {effector.duration}s</span>
              )}
              {effector.stackable && (
                <span className="detail-tag">Stackable</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

