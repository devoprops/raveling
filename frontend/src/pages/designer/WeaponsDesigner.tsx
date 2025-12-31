import { useState, useEffect } from 'react';
import apiClient from '../../utils/api';
import { WeaponForm, WeaponFormData } from '../../components/weapons';
import PreviewTabs from '../../components/weapons/PreviewTabs';
import NotesButton from '../../components/collaboration/NotesButton';
import { createDefaultAffinities, createDefaultDetriments } from '../../utils/constants';
import './designer-page.css';
import './weapons-designer.css';

export default function WeaponsDesigner() {
  const [weaponConfig, setWeaponConfig] = useState<WeaponFormData>({
    name: '',
    short_desc: '',
    long_desc: '',
    weight_kg: 0,
    length_cm: 0,
    width_cm: 0,
    material: '',
    effectors: [],
    affinities: createDefaultAffinities(),
    detriments: createDefaultDetriments(),
    auxiliary_slots: 0,
    size_constraints: [0, 100],
    thumbnail_path: '',
    restrictions: {},
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
      const response = await apiClient.get('/api/weapons/list-configs');
      setAvailableConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Failed to load available configs:', error);
    } finally {
      setLoadingConfigs(false);
    }
  };

  const handleFormChange = (data: WeaponFormData) => {
    setWeaponConfig(data);
  };

  const handleSave = async () => {
    if (!weaponConfig.name) {
      alert('Please enter a weapon name before saving');
      return;
    }

    try {
      const response = await apiClient.post('/api/weapons/save-config', {
        weapon_config: weaponConfig,
      });
      alert(`Weapon "${weaponConfig.name}" saved successfully to GitHub!`);
      await loadAvailableConfigs();
    } catch (error: any) {
      console.error('Failed to save weapon:', error);
      alert(`Failed to save weapon: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleLoad = () => {
    setShowLoadModal(true);
    loadAvailableConfigs();
  };

  const handleLoadConfig = async (configName: string) => {
    try {
      const response = await apiClient.get(`/api/weapons/load-config/${configName}`);
      const loadedConfig = response.data.weapon_config;
      setWeaponConfig(loadedConfig);
      setShowLoadModal(false);
      alert(`Loaded weapon config: ${configName}`);
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
            <h1 className="page-title">⚔️ Weapons Designer</h1>
            <p className="page-subtitle">Create and manage weapon configurations</p>
          </div>
          <div className="weapon-actions">
            <NotesButton designerType="weapons" />
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
            <WeaponForm initialData={weaponConfig} onChange={handleFormChange} />
          </div>
          <div className="weapons-designer-preview-section">
            <PreviewTabs weaponConfig={weaponConfig} />
          </div>
        </div>
      </div>

      {showLoadModal && (
        <div className="modal-overlay" onClick={() => setShowLoadModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Load Weapon Config</h2>
              <button className="modal-close" onClick={() => setShowLoadModal(false)}>×</button>
            </div>
            <div className="modal-body">
              {loadingConfigs ? (
                <p>Loading configs...</p>
              ) : availableConfigs.length === 0 ? (
                <p>No weapon configs found in GitHub storage.</p>
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

