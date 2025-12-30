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
import './AnalysisTools.css';

interface AnalysisToolsProps {
  weaponConfig: any;
}

interface AnalysisData {
  strikes: number[];
  cumulative_damage: number[];
  damage_values: number[];
  damage_per_strike: number[];
  effector_breakdown: Record<string, number[]>;
  effector_cumulative: Record<string, number[]>;
  min_damage: number;
  max_damage: number;
}

// Color mapping for effectors
const ELEMENT_COLORS: Record<string, string> = {
  Earth: '#8B4513', // Brown
  Water: '#1E90FF', // Blue
  Air: '#87CEEB',   // Sky blue
  Fire: '#FF4500',  // Orange red
};

const DAMAGE_COLOR = '#808080'; // Grey for physical damage

function getEffectorColor(effector: any): string {
  if (effector.effector_type === 'damage') {
    if (effector.damage_subtype === 'elemental' && effector.element_type) {
      return ELEMENT_COLORS[effector.element_type] || '#e94560';
    }
    return DAMAGE_COLOR;
  }
  return '#e94560'; // Default color
}

export default function AnalysisTools({ weaponConfig }: AnalysisToolsProps) {
  const [numStrikes, setNumStrikes] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);

  const runAnalysis = async () => {
    if (!weaponConfig.name || !weaponConfig.effectors || weaponConfig.effectors.length === 0) {
      setError('Please configure the weapon with at least one effector before running analysis.');
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

  // Prepare cumulative data with per-effector breakdown
  const cumulativeData = useMemo(() => {
    if (!analysisData) return [];

    const data = analysisData.strikes.map((strike, index) => {
      const point: any = {
        strike,
        Overall: analysisData.cumulative_damage[index],
      };

      // Add per-effector cumulative damage
      Object.keys(analysisData.effector_cumulative).forEach((effectorId) => {
        point[effectorId] = analysisData.effector_cumulative[effectorId][index];
      });

      return point;
    });

    return data;
  }, [analysisData]);

  // Prepare damage vs call data with per-effector breakdown
  const damageVsCallData = useMemo(() => {
    if (!analysisData) return [];

    const data = analysisData.strikes.map((strike, index) => {
      const point: any = {
        strike,
        Overall: analysisData.damage_per_strike[index],
      };

      // Add per-effector damage per strike
      Object.keys(analysisData.effector_breakdown).forEach((effectorId) => {
        point[effectorId] = analysisData.effector_breakdown[effectorId][index];
      });

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

  // Get effector info for legend
  const effectorInfo = useMemo(() => {
    if (!weaponConfig.effectors) return [];
    return weaponConfig.effectors.map((effector: any, idx: number) => ({
      id: effector.effector_name || `effector_${idx}`,
      name: effector.effector_name || `Effector ${idx + 1}`,
      color: getEffectorColor(effector),
      type: effector.effector_type,
      element: effector.element_type,
    }));
  }, [weaponConfig.effectors]);

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
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(233, 69, 96, 0.2)" />
                <XAxis
                  dataKey="strike"
                  stroke="#c4c4c4"
                  style={{ fontSize: '0.85rem' }}
                />
                <YAxis stroke="#c4c4c4" style={{ fontSize: '0.85rem' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    border: '1px solid rgba(233, 69, 96, 0.3)',
                    color: '#c4c4c4',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="Overall"
                  stroke="#e94560"
                  strokeWidth={2}
                  dot={false}
                  name="Overall"
                />
                {effectorInfo.map((effector) => (
                  <Line
                    key={effector.id}
                    type="monotone"
                    dataKey={effector.id}
                    stroke={effector.color}
                    strokeWidth={2}
                    dot={false}
                    name={effector.name}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Damage vs Call Chart */}
          <div className="chart-container">
            <h4 className="chart-title">Damage vs Call (Per Strike)</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={damageVsCallData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(233, 69, 96, 0.2)" />
                <XAxis
                  dataKey="strike"
                  stroke="#c4c4c4"
                  style={{ fontSize: '0.85rem' }}
                />
                <YAxis stroke="#c4c4c4" style={{ fontSize: '0.85rem' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    border: '1px solid rgba(233, 69, 96, 0.3)',
                    color: '#c4c4c4',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="Overall"
                  stroke="#e94560"
                  strokeWidth={2}
                  dot={false}
                  name="Overall"
                />
                {effectorInfo.map((effector) => (
                  <Line
                    key={effector.id}
                    type="monotone"
                    dataKey={effector.id}
                    stroke={effector.color}
                    strokeWidth={2}
                    dot={false}
                    name={effector.name}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Distribution Chart */}
          <div className="chart-container">
            <h4 className="chart-title">Damage Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(233, 69, 96, 0.2)" />
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
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    border: '1px solid rgba(233, 69, 96, 0.3)',
                    color: '#c4c4c4',
                  }}
                />
                <Legend />
                <Bar dataKey="count" fill="#e94560" name="Frequency" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
