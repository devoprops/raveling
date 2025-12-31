import { ELEMENTS } from '../../utils/constants';
import './ElementAffinitiesWidget.css';

export interface ElementAffinitiesData {
  elemental: Record<string, number>;
  race?: Record<string, number>;
}

export interface ElementDetrimentsData {
  elemental: Record<string, number>;
  race?: Record<string, number>;
}

interface ElementAffinitiesWidgetProps {
  affinities: ElementAffinitiesData;
  detriments: ElementDetrimentsData;
  onAffinityChange: (element: string, value: number) => void;
  onDetrimentChange: (element: string, value: number) => void;
  showRace?: boolean; // Optional race affinities/detriments (for future use)
}

export default function ElementAffinitiesWidget({
  affinities,
  detriments,
  onAffinityChange,
  onDetrimentChange,
  showRace = false,
}: ElementAffinitiesWidgetProps) {
  return (
    <div className="element-affinities-widget">
      <h3 className="section-title">Elemental Affinities & Detriments</h3>
      <div className="element-affinities-table">
        <div className="element-affinities-header">
          <div className="element-column">Element</div>
          <div className="value-column">Affinity</div>
          <div className="value-column">Detriment</div>
        </div>
        <div className="element-affinities-body">
          {ELEMENTS.map((element) => (
            <div key={element} className="element-affinities-row">
              <div className="element-column">
                <label>{element}</label>
              </div>
              <div className="value-column">
                <input
                  type="number"
                  step="0.1"
                  value={affinities.elemental[element] ?? 1.0}
                  onChange={(e) => onAffinityChange(element, parseFloat(e.target.value) || 1.0)}
                />
              </div>
              <div className="value-column">
                <input
                  type="number"
                  step="0.1"
                  value={detriments.elemental[element] ?? 1.0}
                  onChange={(e) => onDetrimentChange(element, parseFloat(e.target.value) || 1.0)}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
