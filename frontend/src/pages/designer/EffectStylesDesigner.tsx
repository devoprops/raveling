import { useState, useEffect } from 'react';
import axios from 'axios';
import { EffectStyleConfig } from '../../components/effectstyles/EffectStyleDesigner';
import EffectStyleDesigner from '../../components/effectstyles/EffectStyleDesigner';
import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';
import './weapons-designer.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface EffectStyleListItem {
  id: number;
  name: string;
  style_type: string;
  subtype: string;
  description: string;
  process_verb: string;
  execution_probability: number;
  effector_config: any;
  style_attributes?: any;
  created_by_id: number;
  created_at: string;
  updated_at?: string;
}

export default function EffectStylesDesigner() {
  const [styles, setStyles] = useState<EffectStyleListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDesigner, setShowDesigner] = useState(false);
  const [editingStyle, setEditingStyle] = useState<EffectStyleListItem | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    loadStyles();
  }, []);

  const loadStyles = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/effect-styles/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Flatten the tree structure into a single array
      const allStyles: EffectStyleListItem[] = [];
      Object.values(response.data).forEach((typeGroup: any) => {
        if (typeGroup.pre_designed) {
          allStyles.push(...typeGroup.pre_designed);
        }
        if (typeGroup.custom) {
          allStyles.push(...typeGroup.custom);
        }
      });

      setStyles(allStyles);
    } catch (error) {
      console.error('Failed to load effect styles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNew = () => {
    setEditingStyle(null);
    setShowDesigner(true);
  };

  const handleEdit = (style: EffectStyleListItem) => {
    // Convert API response to EffectStyleConfig format
    const effectorConfig = Array.isArray(style.effector_config)
      ? style.effector_config[0] || {}
      : style.effector_config || {};

    setEditingStyle({
      ...style,
      effector_config: effectorConfig,
    });
    setShowDesigner(true);
  };

  const handleDelete = async (styleId: number) => {
    if (!confirm('Are you sure you want to delete this effect style?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/effect-styles/${styleId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await loadStyles();
    } catch (error) {
      console.error('Failed to delete effect style:', error);
      alert('Failed to delete effect style');
    }
  };

  const handleSave = async (styleConfig: EffectStyleConfig) => {
    try {
      const token = localStorage.getItem('token');
      
      if (editingStyle) {
        // Update existing style
        await axios.put(
          `${API_URL}/api/effect-styles/${editingStyle.id}`,
          styleConfig,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        // Create new style
        await axios.post(
          `${API_URL}/api/effect-styles/`,
          styleConfig,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      setShowDesigner(false);
      setEditingStyle(null);
      await loadStyles();
    } catch (error: any) {
      console.error('Failed to save effect style:', error);
      alert(`Failed to save effect style: ${error.response?.data?.detail || error.message}`);
    }
  };

  const filteredStyles = filterType === 'all'
    ? styles
    : styles.filter(s => s.style_type === filterType);

  const styleTypes = ['all', ...Array.from(new Set(styles.map(s => s.style_type)))];

  return (
    <div className="designer-page">
      <div className="page-header">
        <div className="weapons-designer-header">
          <div>
            <h1 className="page-title">🎨 Effect Styles Designer</h1>
            <p className="page-subtitle">Create and manage reusable effect styles for weapons, skills, and spells</p>
          </div>
          <div className="weapon-actions">
            <NotesButton designerType="effect-styles" />
            <button onClick={handleCreateNew} className="save-btn">
              + Create New Style
            </button>
          </div>
        </div>
      </div>

      <div className="weapons-designer-content">
        <div className="weapons-designer-main" style={{ flexDirection: 'column' }}>
          {/* Filter */}
          <div className="form-section" style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span>Filter by Type:</span>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                style={{
                  padding: '0.5rem',
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '4px',
                  color: '#fff',
                }}
              >
                {styleTypes.map(type => (
                  <option key={type} value={type}>
                    {type === 'all' ? 'All Types' : type}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {/* Styles List */}
          {loading ? (
            <div className="form-section">
              <p>Loading effect styles...</p>
            </div>
          ) : filteredStyles.length === 0 ? (
            <div className="form-section">
              <p>No effect styles found. Create your first one!</p>
            </div>
          ) : (
            <div className="form-section">
              <h3 className="section-title">Saved Effect Styles ({filteredStyles.length})</h3>
              <div className="style-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                {filteredStyles.map((style) => (
                  <div key={style.id} className="style-item" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <div className="style-info" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                        <div>
                          <strong style={{ fontSize: '1.1rem' }}>{style.name}</strong>
                          <span style={{ marginLeft: '0.5rem', color: 'rgba(255, 255, 255, 0.6)' }}>
                            ({style.subtype})
                          </span>
                        </div>
                        <span
                          style={{
                            padding: '0.25rem 0.5rem',
                            background: 'rgba(74, 158, 255, 0.2)',
                            borderRadius: '4px',
                            fontSize: '0.85rem',
                          }}
                        >
                          {style.style_type}
                        </span>
                      </div>
                      {style.description && (
                        <p style={{ margin: '0.5rem 0', color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.9rem' }}>
                          {style.description}
                        </p>
                      )}
                      <div className="style-details" style={{ marginTop: '0.5rem' }}>
                        {style.process_verb && <span>Verb: "{style.process_verb}"</span>}
                        <span> • Probability: {style.execution_probability}</span>
                        {style.style_attributes && (
                          <>
                            {style.style_attributes.range && <span> • Range: {style.style_attributes.range}</span>}
                            {style.style_attributes.area && <span> • Area: {style.style_attributes.area}</span>}
                            {style.style_attributes.duration && <span> • Duration: {style.style_attributes.duration}</span>}
                          </>
                        )}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', width: '100%' }}>
                      <button
                        className="remove-btn"
                        onClick={() => handleEdit(style)}
                        style={{ flex: 1, background: 'rgba(74, 158, 255, 0.2)', color: '#4a9eff', borderColor: 'rgba(74, 158, 255, 0.3)' }}
                      >
                        Edit
                      </button>
                      <button
                        className="remove-btn"
                        onClick={() => handleDelete(style.id)}
                        style={{ flex: 1 }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {showDesigner && (
        <div className="style-designer-overlay">
          <div className="style-designer-container">
            <EffectStyleDesigner
              onSave={handleSave}
              onCancel={() => {
                setShowDesigner(false);
                setEditingStyle(null);
              }}
              initialStyle={editingStyle ? {
                name: editingStyle.name,
                style_type: editingStyle.style_type,
                subtype: editingStyle.subtype,
                description: editingStyle.description || '',
                process_verb: editingStyle.process_verb || '',
                execution_probability: editingStyle.execution_probability,
                effector: Array.isArray(editingStyle.effector_config) 
                  ? editingStyle.effector_config[0] || {}
                  : editingStyle.effector_config || {},
                style_attributes: editingStyle.style_attributes,
              } : undefined}
            />
          </div>
        </div>
      )}
    </div>
  );
}
