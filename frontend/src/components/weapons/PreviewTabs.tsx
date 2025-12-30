import { useState } from 'react';
import YAMLPreview from './YAMLPreview';
import AnalysisTools from './AnalysisTools';
import './PreviewTabs.css';

interface PreviewTabsProps {
  weaponConfig: any;
}

export default function PreviewTabs({ weaponConfig }: PreviewTabsProps) {
  const [activeTab, setActiveTab] = useState<'yaml' | 'analysis'>('yaml');

  return (
    <div className="preview-tabs">
      <div className="preview-tabs-header">
        <button
          className={`preview-tab ${activeTab === 'yaml' ? 'active' : ''}`}
          onClick={() => setActiveTab('yaml')}
        >
          YAML Preview
        </button>
        <button
          className={`preview-tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          Analysis
        </button>
      </div>
      <div className="preview-tabs-content">
        {activeTab === 'yaml' && <YAMLPreview weaponConfig={weaponConfig} />}
        {activeTab === 'analysis' && <AnalysisTools weaponConfig={weaponConfig} />}
      </div>
    </div>
  );
}

