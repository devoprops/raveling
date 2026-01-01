import { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import apiClient from '../../utils/api';
import { COLORS, ELEMENT_COLORS, COLORS_RGBA } from '../../constants/colors';
import './AnalysisTools.css';

interface AnalysisToolsProps {
  weaponConfig: any;
}

interface AnalysisData {
  strikes: number[];
  cumulative_damage: number[];
  damage_values: number[];
  damage_per_strike: number[];
  effector_breakdown?: Record<string, number[]>;
  effector_cumulative?: Record<string, number[]>;
  style_breakdown?: Record<string, number[]>;
  style_cumulative?: Record<string, number[]>;
  min_damage: number;
  max_damage: number;
}

function getEffectorColor(effector: any): string {
  if (effector.effector_type === 'damage') {
    if (effector.damage_subtype === 'elemental' && effector.element_type) {
      return ELEMENT_COLORS[effector.element_type] || COLORS.PRIMARY_BLUE;
    }
    return COLORS.DAMAGE_PHYSICAL;
  }
  return COLORS.PRIMARY_BLUE; // Default color
}

export default function AnalysisTools({ weaponConfig }: AnalysisToolsProps) {
  const [numStrikes, setNumStrikes] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);

  const runAnalysis = async () => {
    // Check for effect styles (new system) or effectors (legacy)
    const hasEffectStyles = 
      (weaponConfig.primary_effect_styles && weaponConfig.primary_effect_styles.length > 0) ||
      (weaponConfig.secondary_effect_styles && weaponConfig.secondary_effect_styles.length > 0);
    const hasEffectors = weaponConfig.effectors && weaponConfig.effectors.length > 0;
    
    if (!weaponConfig.name || (!hasEffectStyles && !hasEffectors)) {
      setError('Please configure the weapon with at least one effect style or effector before running analysis.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await apiClient.post('/api/weapons/analyze-damage', {
        weapon_config: weaponConfig,
        num_strikes: numStrikes,
      });

      setAnalysisData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run analysis');
      setAnalysisData(null);
    } finally {
      setLoading(false);
    }
  };

  // Prepare cumulative data with per-effector or per-style breakdown
  const cumulativeData = useMemo(() => {
    if (!analysisData) return [];

    const data = analysisData.strikes.map((strike, index) => {
      const point: any = {
        strike,
        Overall: analysisData.cumulative_damage[index],
      };

      // Add per-style cumulative damage (new system)
      if (analysisData.style_cumulative) {
        Object.keys(analysisData.style_cumulative).forEach((styleId) => {
          point[styleId] = analysisData.style_cumulative![styleId][index];
        });
      }
      
      // Add per-effector cumulative damage (legacy)
      if (analysisData.effector_cumulative) {
        Object.keys(analysisData.effector_cumulative).forEach((effectorId) => {
          point[effectorId] = analysisData.effector_cumulative![effectorId][index];
        });
      }

      return point;
    });

    return data;
  }, [analysisData]);

  // Prepare damage vs call data with per-effector or per-style breakdown
  const damageVsCallData = useMemo(() => {
    if (!analysisData) return [];

    const data = analysisData.strikes.map((strike, index) => {
      const point: any = {
        strike,
        Overall: analysisData.damage_per_strike[index],
      };

      // Add per-style damage per strike (new system)
      if (analysisData.style_breakdown) {
        Object.keys(analysisData.style_breakdown).forEach((styleId) => {
          point[styleId] = analysisData.style_breakdown![styleId][index];
        });
      }
      
      // Add per-effector damage per strike (legacy)
      if (analysisData.effector_breakdown) {
        Object.keys(analysisData.effector_breakdown).forEach((effectorId) => {
          point[effectorId] = analysisData.effector_breakdown![effectorId][index];
        });
      }

      return point;
    });

    return data;
  }, [analysisData]);

  // Prepare distribution data (bin damage values)
  const distributionData = useMemo(() => {
    if (!analysisData || analysisData.damage_values.length === 0) return [];

    const values = analysisData.damage_values;
    const min = analysisData.min_damage;
    const max = analysisData.max_damage;
    const numBins = 20;
    const binSize = (max - min) / numBins;

    const bins: number[] = new Array(numBins).fill(0);
    const binLabels: string[] = [];

    values.forEach((value) => {
      const binIndex = Math.min(Math.floor((value - min) / binSize), numBins - 1);
      bins[binIndex]++;
    });

    for (let i = 0; i < numBins; i++) {
      const binStart = min + i * binSize;
      const binEnd = min + (i + 1) * binSize;
      binLabels.push(`${binStart.toFixed(1)}-${binEnd.toFixed(1)}`);
    }

    return bins.map((count, index) => ({
      range: binLabels[index],
      count,
    }));
  }, [analysisData]);

  // Get style or effector info for legend
  const styleOrEffectorInfo = useMemo(() => {
    const info: Array<{id: string; name: string; color: string; type?: string; element?: string}> = [];
    
    // Add effect styles (new system)
    if (weaponConfig.primary_effect_styles) {
      weaponConfig.primary_effect_styles.forEach((style: any, idx: number) => {
        const styleId = style.name || style.subtype || `primary_style_${idx}`;
        const effector = style.effector || (style.effectors && style.effectors[0]) || {};
        info.push({
          id: styleId,
          name: style.name || `Primary Style ${idx + 1}`,
          color: getEffectorColor(effector),
          type: effector.effector_type,
          element: effector.element_type,
        });
      });
    }
    
    if (weaponConfig.secondary_effect_styles) {
      weaponConfig.secondary_effect_styles.forEach((style: any, idx: number) => {
        const styleId = style.name || style.subtype || `secondary_style_${idx}`;
        const effector = style.effector || (style.effectors && style.effectors[0]) || {};
        info.push({
          id: styleId,
          name: style.name || `Secondary Style ${idx + 1}`,
          color: getEffectorColor(effector),
          type: effector.effector_type,
          element: effector.element_type,
        });
      });
    }
    
    // Add effectors (legacy)
    if (weaponConfig.effectors && info.length === 0) {
      weaponConfig.effectors.forEach((effector: any, idx: number) => {
        info.push({
          id: effector.effector_name || `effector_${idx}`,
          name: effector.effector_name || `Effector ${idx + 1}`,
          color: getEffectorColor(effector),
          type: effector.effector_type,
          element: effector.element_type,
        });
      });
    }
    
    return info;
  }, [weaponConfig.primary_effect_styles, weaponConfig.secondary_effect_styles, weaponConfig.effectors]);

  return (
    <div className="analysis-tools">
      <div className="analysis-header">
        <h3 className="analysis-title">Damage Analysis</h3>
        <div className="analysis-controls">
          <label>
            Number of Strikes:
            <input
              type="number"
              min="1"
              max="10000"
              value={numStrikes}
              onChange={(e) => setNumStrikes(parseInt(e.target.value) || 100)}
              className="strikes-input"
            />
          </label>
          <button onClick={runAnalysis} disabled={loading} className="analyze-btn">
            {loading ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>
      </div>

      {error && <div className="analysis-error">{error}</div>}

      {analysisData && (
        <div className="analysis-results">
          <div className="analysis-stats">
            <div className="stat-item">
              <span className="stat-label">Min Damage:</span>
              <span className="stat-value">{analysisData.min_damage.toFixed(2)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Max Damage:</span>
              <span className="stat-value">{analysisData.max_damage.toFixed(2)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Strikes:</span>
              <span className="stat-value">{analysisData.strikes.length}</span>
            </div>
          </div>

          {/* Cumulative Damage Chart */}
          <div className="chart-container">
            <h4 className="chart-title">Cumulative Damage Over Strikes</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={cumulativeData}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS_RGBA.PRIMARY_BLUE_20} />
                <XAxis
                  dataKey="strike"
                  stroke="#c4c4c4"
                  style={{ fontSize: '0.85rem' }}
                />
                <YAxis stroke="#c4c4c4" style={{ fontSize: '0.85rem' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: COLORS.OVERLAY_DARK,
                    border: `1px solid ${COLORS_RGBA.PRIMARY_BLUE_30}`,
                    color: COLORS.TEXT_SECONDARY,
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="Overall"
                  stroke={COLORS.PRIMARY_BLUE}
                  strokeWidth={2}
                  dot={false}
                  name="Overall"
                />
                {styleOrEffectorInfo.map((item, index) => {
                  // Check if this is a primary style
                  const isPrimary = weaponConfig.primary_effect_styles?.some(
                    (style: any) => (style.name || style.subtype) === item.id
                  );
                  return (
                    <Line
                      key={item.id}
                      type="monotone"
                      dataKey={item.id}
                      stroke={item.color}
                      strokeWidth={2}
                      strokeDasharray={isPrimary ? "5 5" : "0"}
                      dot={false}
                      name={item.name}
                    />
                  );
                })}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Damage vs Call Chart */}
          <div className="chart-container">
            <h4 className="chart-title">Damage vs Call (Per Strike)</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={damageVsCallData}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS_RGBA.PRIMARY_BLUE_20} />
                <XAxis
                  dataKey="strike"
                  stroke="#c4c4c4"
                  style={{ fontSize: '0.85rem' }}
                />
                <YAxis stroke="#c4c4c4" style={{ fontSize: '0.85rem' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: COLORS.OVERLAY_DARK,
                    border: `1px solid ${COLORS_RGBA.PRIMARY_BLUE_30}`,
                    color: COLORS.TEXT_SECONDARY,
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="Overall"
                  stroke={COLORS.PRIMARY_BLUE}
                  strokeWidth={2}
                  dot={false}
                  name="Overall"
                />
                {styleOrEffectorInfo.map((item, index) => {
                  // Check if this is a primary style
                  const isPrimary = weaponConfig.primary_effect_styles?.some(
                    (style: any) => (style.name || style.subtype) === item.id
                  );
                  return (
                    <Line
                      key={item.id}
                      type="monotone"
                      dataKey={item.id}
                      stroke={item.color}
                      strokeWidth={2}
                      strokeDasharray={isPrimary ? "5 5" : "0"}
                      dot={false}
                      name={item.name}
                    />
                  );
                })}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Distribution Chart */}
          <div className="chart-container">
            <h4 className="chart-title">Damage Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS_RGBA.PRIMARY_BLUE_20} />
                <XAxis
                  dataKey="range"
                  stroke="#c4c4c4"
                  style={{ fontSize: '0.75rem' }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis stroke="#c4c4c4" style={{ fontSize: '0.85rem' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: COLORS.OVERLAY_DARK,
                    border: `1px solid ${COLORS_RGBA.PRIMARY_BLUE_30}`,
                    color: COLORS.TEXT_SECONDARY,
                  }}
                />
                <Legend />
                <Bar dataKey="count" fill={COLORS.PRIMARY_BLUE} name="Frequency" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
