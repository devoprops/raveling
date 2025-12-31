import { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { COLORS, COLORS_RGBA } from '../../constants/colors';
import './DistributionParameterWidget.css';

export interface DistributionParameters {
  type: string;
  params: Record<string, number | string>;
}

interface DistributionParameterWidgetProps {
  distributionType: string;
  parameters: Record<string, number | string>;
  onParametersChange: (params: DistributionParameters) => void;
}

const DISTRIBUTION_TYPES = ['uniform', 'gaussian', 'skewnorm', 'bimodal', 'die_roll'];

// Helper function to calculate Gaussian PDF
function gaussianPDF(x: number, mean: number, std: number): number {
  const variance = std * std;
  const coefficient = 1 / (std * Math.sqrt(2 * Math.PI));
  const exponent = -0.5 * Math.pow((x - mean) / std, 2);
  return coefficient * Math.exp(exponent);
}

// Helper function to calculate skewed normal PDF (simplified approximation)
function skewnormPDF(x: number, loc: number, scale: number, skew: number): number {
  // Simplified approximation - for exact calculation would need scipy
  const z = (x - loc) / scale;
  const normal = gaussianPDF(x, loc, scale);
  // Apply skew transformation (simplified)
  if (skew === 0) {
    return normal;
  }
  // Simple skew approximation
  const skewFactor = 1 + (skew * z) / (1 + Math.abs(z));
  return normal * skewFactor;
}

// Helper function to parse die notation (e.g., "2d6")
function parseDieNotation(notation: string): { numDice: number; numSides: number } | null {
  const parts = notation.toLowerCase().split('d');
  if (parts.length !== 2) return null;
  const numDice = parseInt(parts[0]);
  const numSides = parseInt(parts[1]);
  if (isNaN(numDice) || isNaN(numSides) || numDice < 1 || numSides < 1) return null;
  return { numDice, numSides };
}

// Calculate dice probabilities
function calculateDiceProbabilities(numDice: number, numSides: number): Map<number, number> {
  const probabilities = new Map<number, number>();
  const totalOutcomes = Math.pow(numSides, numDice);
  
  // Use dynamic programming to calculate probabilities
  let ways: Map<number, number> = new Map();
  ways.set(0, 1);
  
  for (let die = 0; die < numDice; die++) {
    const nextWays = new Map<number, number>();
    for (const [sum, count] of ways.entries()) {
      for (let side = 1; side <= numSides; side++) {
        const newSum = sum + side;
        nextWays.set(newSum, (nextWays.get(newSum) || 0) + count);
      }
    }
    ways = nextWays;
  }
  
  for (const [sum, count] of ways.entries()) {
    probabilities.set(sum, count / totalOutcomes);
  }
  
  return probabilities;
}

export default function DistributionParameterWidget({
  distributionType,
  parameters,
  onParametersChange,
}: DistributionParameterWidgetProps) {
  const [localParams, setLocalParams] = useState<Record<string, number | string>>(parameters);

  useEffect(() => {
    setLocalParams(parameters);
  }, [parameters]);

  const updateParam = (key: string, value: number | string) => {
    const newParams = { ...localParams, [key]: value };
    setLocalParams(newParams);
    onParametersChange({
      type: distributionType,
      params: newParams,
    });
  };

  // Calculate PDF data for preview
  const pdfData = useMemo(() => {
    try {
      if (distributionType === 'uniform') {
        const min = Number(localParams.min_val ?? localParams.min ?? 0);
        const max = Number(localParams.max_val ?? localParams.max ?? 10);
        const range = max - min;
        const step = range / 100;
        const data = [];
        
        for (let x = min - range * 0.1; x <= max + range * 0.1; x += step) {
          const y = (x >= min && x <= max) ? (range > 0 ? 1 / range : 1) : 0;
          data.push({ x: Number(x.toFixed(2)), y });
        }
        return data;
      } else if (distributionType === 'gaussian') {
        const mean = Number(localParams.mean ?? 10);
        const std = Number(localParams.std_dev ?? 2);
        const data = [];
        
        for (let x = mean - 4 * std; x <= mean + 4 * std; x += std / 10) {
          const y = gaussianPDF(x, mean, std);
          data.push({ x: Number(x.toFixed(2)), y });
        }
        return data;
      } else if (distributionType === 'skewnorm') {
        const loc = Number(localParams.mean ?? 10);
        const scale = Number(localParams.std_dev ?? 2);
        const skew = Number(localParams.skew ?? 0);
        const data = [];
        
        // Approximate range
        const range = 4 * scale;
        for (let x = loc - range; x <= loc + range; x += scale / 10) {
          const y = skewnormPDF(x, loc, scale, skew);
          data.push({ x: Number(x.toFixed(2)), y });
        }
        return data;
      } else if (distributionType === 'bimodal') {
        const mean1 = Number(localParams.mean1 ?? 5);
        const std1 = Number(localParams.std1 ?? 1);
        const mean2 = Number(localParams.mean2 ?? 15);
        const std2 = Number(localParams.std2 ?? 1);
        const weight = Number(localParams.weight ?? 0.5);
        const data = [];
        
        const xMin = Math.min(mean1 - 4 * std1, mean2 - 4 * std2);
        const xMax = Math.max(mean1 + 4 * std1, mean2 + 4 * std2);
        const step = (xMax - xMin) / 200;
        
        for (let x = xMin; x <= xMax; x += step) {
          const y1 = weight * gaussianPDF(x, mean1, std1);
          const y2 = (1 - weight) * gaussianPDF(x, mean2, std2);
          data.push({ x: Number(x.toFixed(2)), y: y1 + y2 });
        }
        return data;
      } else if (distributionType === 'die_roll') {
        const notation = String(localParams.notation ?? '1d6');
        const parsed = parseDieNotation(notation);
        if (!parsed) return [];
        
        const probs = calculateDiceProbabilities(parsed.numDice, parsed.numSides);
        const data = Array.from(probs.entries())
          .sort((a, b) => a[0] - b[0])
          .map(([x, y]) => ({ x, y }));
        return data;
      }
    } catch (error) {
      console.error('Error calculating PDF:', error);
    }
    return [];
  }, [distributionType, localParams]);

  return (
    <div className="distribution-parameter-widget">
      <div className="distribution-controls">
        <div className="distribution-type-selector">
          <label>
            Distribution Type:
            <select
              value={distributionType}
              onChange={(e) => {
                const newType = e.target.value;
                // Reset parameters based on type
                let defaultParams: Record<string, number | string> = {};
                if (newType === 'uniform') {
                  defaultParams = { min_val: 0, max_val: 10 };
                } else if (newType === 'gaussian') {
                  defaultParams = { mean: 10, std_dev: 2 };
                } else if (newType === 'skewnorm') {
                  defaultParams = { mean: 10, std_dev: 2, skew: 0 };
                } else if (newType === 'bimodal') {
                  defaultParams = { mean1: 5, std1: 1, mean2: 15, std2: 1, weight: 0.5 };
                } else if (newType === 'die_roll') {
                  defaultParams = { notation: '1d6' };
                }
                setLocalParams(defaultParams);
                onParametersChange({ type: newType, params: defaultParams });
              }}
            >
              {DISTRIBUTION_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="distribution-parameters">
          {distributionType === 'uniform' && (
            <>
              <label>
                Min:
                <input
                  type="number"
                  step="0.1"
                  value={localParams.min_val ?? localParams.min ?? 0}
                  onChange={(e) => updateParam('min_val', parseFloat(e.target.value) || 0)}
                />
              </label>
              <label>
                Max:
                <input
                  type="number"
                  step="0.1"
                  value={localParams.max_val ?? localParams.max ?? 10}
                  onChange={(e) => updateParam('max_val', parseFloat(e.target.value) || 10)}
                />
              </label>
            </>
          )}

          {distributionType === 'gaussian' && (
            <>
              <label>
                Mean:
                <input
                  type="number"
                  step="0.1"
                  value={localParams.mean ?? 10}
                  onChange={(e) => updateParam('mean', parseFloat(e.target.value) || 0)}
                />
              </label>
              <label>
                Std Dev:
                <input
                  type="number"
                  step="0.1"
                  min="0.01"
                  value={localParams.std_dev ?? 2}
                  onChange={(e) => updateParam('std_dev', parseFloat(e.target.value) || 1)}
                />
              </label>
            </>
          )}

          {distributionType === 'skewnorm' && (
            <>
              <label>
                Mean:
                <input
                  type="number"
                  step="0.1"
                  value={localParams.mean ?? 10}
                  onChange={(e) => updateParam('mean', parseFloat(e.target.value) || 0)}
                />
              </label>
              <label>
                Std Dev:
                <input
                  type="number"
                  step="0.1"
                  min="0.01"
                  value={localParams.std_dev ?? 2}
                  onChange={(e) => updateParam('std_dev', parseFloat(e.target.value) || 1)}
                />
              </label>
              <label>
                Skew:
                <input
                  type="number"
                  step="0.1"
                  value={localParams.skew ?? 0}
                  onChange={(e) => updateParam('skew', parseFloat(e.target.value) || 0)}
                />
              </label>
            </>
          )}

          {distributionType === 'bimodal' && (
            <>
              <label>
                Mean 1:
                <input
                  type="number"
                  step="0.1"
                  value={localParams.mean1 ?? 5}
                  onChange={(e) => updateParam('mean1', parseFloat(e.target.value) || 0)}
                />
              </label>
              <label>
                Std 1:
                <input
                  type="number"
                  step="0.1"
                  min="0.01"
                  value={localParams.std1 ?? 1}
                  onChange={(e) => updateParam('std1', parseFloat(e.target.value) || 1)}
                />
              </label>
              <label>
                Mean 2:
                <input
                  type="number"
                  step="0.1"
                  value={localParams.mean2 ?? 15}
                  onChange={(e) => updateParam('mean2', parseFloat(e.target.value) || 0)}
                />
              </label>
              <label>
                Std 2:
                <input
                  type="number"
                  step="0.1"
                  min="0.01"
                  value={localParams.std2 ?? 1}
                  onChange={(e) => updateParam('std2', parseFloat(e.target.value) || 1)}
                />
              </label>
              <label>
                Weight:
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={localParams.weight ?? 0.5}
                  onChange={(e) => updateParam('weight', parseFloat(e.target.value) || 0.5)}
                />
              </label>
            </>
          )}

          {distributionType === 'die_roll' && (
            <label>
              Notation (e.g., 2d6):
              <input
                type="text"
                value={localParams.notation ?? '1d6'}
                onChange={(e) => updateParam('notation', e.target.value)}
                placeholder="1d6"
              />
            </label>
          )}
        </div>
      </div>

      <div className="distribution-preview">
        <h4>PDF Preview</h4>
        {distributionType === 'die_roll' ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={pdfData}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS_RGBA.PRIMARY_BLUE_20} />
              <XAxis dataKey="x" stroke={COLORS.TEXT_SECONDARY} />
              <YAxis stroke={COLORS.TEXT_SECONDARY} />
              <Tooltip
                contentStyle={{
                  backgroundColor: COLORS.OVERLAY_DARK,
                  border: `1px solid ${COLORS_RGBA.PRIMARY_BLUE_30}`,
                  color: COLORS.TEXT_SECONDARY,
                }}
              />
              <Bar dataKey="y" fill={COLORS.PRIMARY_BLUE} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={pdfData}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS_RGBA.PRIMARY_BLUE_20} />
              <XAxis dataKey="x" stroke={COLORS.TEXT_SECONDARY} />
              <YAxis stroke={COLORS.TEXT_SECONDARY} />
              <Tooltip
                contentStyle={{
                  backgroundColor: COLORS.OVERLAY_DARK,
                  border: `1px solid ${COLORS_RGBA.PRIMARY_BLUE_30}`,
                  color: COLORS.TEXT_SECONDARY,
                }}
              />
              <Line type="monotone" dataKey="y" stroke={COLORS.PRIMARY_BLUE} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

