import { useState, useEffect } from 'react';
import apiClient from '../../utils/api';
import { SpellForm, SpellFormData } from '../../components/spells';
import YAMLPreview from '../../components/spells/YAMLPreview';
import NotesButton from '../../components/collaboration/NotesButton';
import { createDefaultAffinities, createDefaultDetriments } from '../../utils/constants';
import './designer-page.css';
import './weapons-designer.css';

export default function SpellsDesigner() {
  const [spellConfig, setSpellConfig] = useState<SpellFormData>({
    name: '',
    short_desc: '',
    long_desc: '',
    effect_styles: [],
    category: '',
    school: '',
    affinities: createDefaultAffinities(),
    detriments: createDefaultDetriments(),
  });

  const [availableConfigs, setAvailableConfigs] = useState<string[]>([]);
  const [showLoadModal, setShowLoadModal] = useState(false);
  const [loadingConfigs, setLoadingConfigs] = useState(false);

  useEffect(() => {
    loadAvailableConfigs();
  }, []);

  const loadAvailableConfigs = async () => {
    try {
      setLoadingConfigs(true);
      const response = await apiClient.get('/api/spells/list-configs');
      setAvailableConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Failed to load available configs:', error);
    } finally {
      setLoadingConfigs(false);
    }
  };

  const handleFormChange = (data: SpellFormData) => {
    setSpellConfig(data);
  };

  const handleSave = async () => {
    if (!spellConfig.name) {
      alert('Please enter a spell name before saving');
      return;
    }

    try {
      const response = await apiClient.post('/api/spells/save-config', {
        spell_config: spellConfig,
      });
      alert(`Spell "${spellConfig.name}" saved successfully to GitHub!`);
      await loadAvailableConfigs();
    } catch (error: any) {
      console.error('Failed to save spell:', error);
      alert(`Failed to save spell: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleLoad = () => {
    setShowLoadModal(true);
    loadAvailableConfigs();
  };

  const handleLoadConfig = async (configName: string) => {
    try {
      const response = await apiClient.get(`/api/spells/load-config/${configName}`);
      const loadedConfig = response.data.spell_config;
      setSpellConfig(loadedConfig);
      setShowLoadModal(false);
      alert(`Loaded spell config: ${configName}`);
    } catch (error: any) {
      console.error('Failed to load config:', error);
      alert(`Failed to load config: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="designer-page">
      <div className="page-header">
        <div className="weapons-designer-header">
          <div>
            <h1 className="page-title">✨ Spells Designer</h1>
            <p className="page-subtitle">Create and manage spell configurations</p>
          </div>
          <div className="weapon-actions">
            <NotesButton designerType="spells" />
            <button onClick={handleSave} className="save-btn">
              Save
            </button>
            <button onClick={handleLoad} className="load-btn">
              Load
            </button>
          </div>
        </div>
      </div>
      <div className="weapons-designer-content">
        <div className="weapons-designer-main">
          <div className="weapons-designer-form-section">
            <SpellForm initialData={spellConfig} onChange={handleFormChange} />
          </div>
          <div className="weapons-designer-preview-section">
            <YAMLPreview spellConfig={spellConfig} />
          </div>
        </div>
      </div>

      {showLoadModal && (
        <div className="modal-overlay" onClick={() => setShowLoadModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Load Spell Config</h2>
              <button className="modal-close" onClick={() => setShowLoadModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {loadingConfigs ? (
                <p>Loading configs...</p>
              ) : availableConfigs.length === 0 ? (
                <p>No spell configs found in GitHub storage.</p>
              ) : (
                <div className="config-list">
                  {availableConfigs.map((configName) => (
                    <div
                      key={configName}
                      className="config-item"
                      onClick={() => handleLoadConfig(configName)}
                    >
                      {configName}
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

