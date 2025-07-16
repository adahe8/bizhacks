import { useState } from 'react';

interface Props {
  onComplete: (data: any) => void;
}

export default function MarketDetailsModal({ onComplete }: Props) {
  const [marketDetails, setMarketDetails] = useState({
    target_demographics: '',
    market_size: '',
    competition_level: 'medium',
    key_trends: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onComplete(marketDetails);
  };

  const handleChange = (field: string, value: string) => {
    setMarketDetails({ ...marketDetails, [field]: value });
  };

  return (
    <div className="modal-backdrop">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full animate-fade-up max-h-[90vh] overflow-y-auto">
        <div className="mb-6">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary-600 h-2 rounded-full" style={{ width: '40%' }}></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">Step 3 of 6</p>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">Market Details</h2>
        <p className="text-gray-600 mb-6">Help us understand your market landscape.</p>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            <div>
              <label className="label">Target Demographics</label>
              <textarea
                value={marketDetails.target_demographics}
                onChange={(e) => handleChange('target_demographics', e.target.value)}
                className="input-field h-24"
                placeholder="Describe your target audience (age, gender, income, lifestyle, etc.)"
                required
              />
            </div>

            <div>
              <label className="label">Market Size</label>
              <input
                type="text"
                value={marketDetails.market_size}
                onChange={(e) => handleChange('market_size', e.target.value)}
                className="input-field"
                placeholder="e.g., $2.5B US skincare market"
                required
              />
            </div>

            <div>
              <label className="label">Competition Level</label>
              <select
                value={marketDetails.competition_level}
                onChange={(e) => handleChange('competition_level', e.target.value)}
                className="input-field"
              >
                <option value="low">Low - Few competitors</option>
                <option value="medium">Medium - Moderate competition</option>
                <option value="high">High - Saturated market</option>
              </select>
            </div>

            <div>
              <label className="label">Key Market Trends</label>
              <textarea
                value={marketDetails.key_trends}
                onChange={(e) => handleChange('key_trends', e.target.value)}
                className="input-field h-24"
                placeholder="What are the current trends in your market? (e.g., sustainability, personalization, etc.)"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn-primary w-full mt-8"
          >
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}