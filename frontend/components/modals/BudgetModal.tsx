import { useState } from 'react';

interface Props {
  onComplete: (data: {
    budget: number;
    frequency: string;
    campaign_count: number;
  }) => void;
}

export default function BudgetModal({ onComplete }: Props) {
  const [budget, setBudget] = useState('');
  const [frequency, setFrequency] = useState('weekly');
  const [campaignCount, setCampaignCount] = useState('5');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onComplete({
      budget: parseFloat(budget),
      frequency,
      campaign_count: parseInt(campaignCount),
    });
  };

  const formatBudget = (value: string) => {
    const num = parseFloat(value);
    if (isNaN(num)) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  return (
    <div className="modal-backdrop">
      <div className="bg-white rounded-lg p-8 max-w-md w-full animate-fade-up">
        <div className="mb-6">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary-600 h-2 rounded-full" style={{ width: '80%' }}></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">Step 5 of 6</p>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">Budget & Optimization</h2>
        <p className="text-gray-600 mb-6">Set your marketing budget and optimization preferences.</p>

        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            <div>
              <label className="label">Monthly Marketing Budget (USD)</label>
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="input-field"
                placeholder="10000"
                min="100"
                step="100"
                required
              />
              {budget && (
                <p className="text-sm text-gray-600 mt-2">
                  Budget: {formatBudget(budget)} per month
                </p>
              )}
            </div>

            <div>
              <label className="label">Budget Rebalancing Frequency</label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
                className="input-field"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
              <p className="text-sm text-gray-500 mt-2">
                How often should AI optimize budget allocation across campaigns
              </p>
            </div>

            <div>
              <label className="label">Number of Campaigns to Generate</label>
              <input
                type="number"
                value={campaignCount}
                onChange={(e) => setCampaignCount(e.target.value)}
                className="input-field"
                min="1"
                max="20"
                required
              />
              <p className="text-sm text-gray-500 mt-2">
                AI will generate this many campaign ideas for you to review
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={!budget || parseFloat(budget) < 100}
            className="btn-primary w-full mt-8"
          >
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}