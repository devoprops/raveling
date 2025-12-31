import { useState, useEffect } from 'react';
import apiClient from '../../utils/api';
import { SkillForm, SkillFormData } from '../../components/skills';
import YAMLPreview from '../../components/skills/YAMLPreview';
import NotesButton from '../../components/collaboration/NotesButton';
import { createDefaultAffinities, createDefaultDetriments } from '../../utils/constants';
import './designer-page.css';
import './weapons-designer.css';

export default function SkillsDesigner() {
  const [skillConfig, setSkillConfig] = useState<SkillFormData>({
    name: '',
    short_desc: '',
    long_desc: '',
    effect_styles: [],
    category: '',
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
      const response = await apiClient.get('/api/skills/list-configs');
      setAvailableConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Failed to load available configs:', error);
    } finally {
      setLoadingConfigs(false);
    }
  };

  const handleFormChange = (data: SkillFormData) => {
    setSkillConfig(data);
  };

  const handleSave = async () => {
    if (!skillConfig.name) {
      alert('Please enter a skill name before saving');
      return;
    }

    try {
      const response = await apiClient.post('/api/skills/save-config', {
        skill_config: skillConfig,
      });
      alert(`Skill "${skillConfig.name}" saved successfully to GitHub!`);
      await loadAvailableConfigs();
    } catch (error: any) {
      console.error('Failed to save skill:', error);
      alert(`Failed to save skill: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleLoad = () => {
    setShowLoadModal(true);
    loadAvailableConfigs();
  };

  const handleLoadConfig = async (configName: string) => {
    try {
      const response = await apiClient.get(`/api/skills/load-config/${configName}`);
      const loadedConfig = response.data.skill_config;
      setSkillConfig(loadedConfig);
      setShowLoadModal(false);
      alert(`Loaded skill config: ${configName}`);
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
            <h1 className="page-title">⚔️ Skills Designer</h1>
            <p className="page-subtitle">Create and manage skill configurations</p>
          </div>
          <div className="weapon-actions">
            <NotesButton designerType="skills" />
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
            <SkillForm initialData={skillConfig} onChange={handleFormChange} />
          </div>
          <div className="weapons-designer-preview-section">
            <YAMLPreview skillConfig={skillConfig} />
          </div>
        </div>
      </div>

      {showLoadModal && (
        <div className="modal-overlay" onClick={() => setShowLoadModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Load Skill Config</h2>
              <button className="modal-close" onClick={() => setShowLoadModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {loadingConfigs ? (
                <p>Loading configs...</p>
              ) : availableConfigs.length === 0 ? (
                <p>No skill configs found in GitHub storage.</p>
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

