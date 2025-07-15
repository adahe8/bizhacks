import { useState } from 'react';

interface Props {
  onComplete: (data: string) => void;
}

export default function StrategicGoalsModal({ onComplete }: Props) {
  const [goals, setGoals] = useState('');
  const [examples] = useState([
    'Increase market share by 15% in the next 12 months',
    'Launch into 3 new customer segments',
    'Build brand awareness among Gen Z consumers',
    'Achieve 25% year-over-year revenue growth',
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onComplete(goals);
  };

  return (
    <div className="modal-backdrop">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full animate-fade-up">
        <div className="mb-6">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary-600 h-2 rounded-full" style={{ width: '60%' }}></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">Step 4 of 6</p>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">Strategic Goals</h2>
        <p className="text-gray-600 mb-6">What do you want to achieve with your marketing campaigns?</p>

        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Example Goals:</h3>
          <div className="space-y-2">
            {examples.map((example, index) => (
              <div
                key={index}
                className="flex items-start space-x-2 text-sm text-gray-600"
              >
                <span className="text-primary-500 mt-0.5">•</span>
                <span>{example}</span>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div>
            <label className="label">Your Strategic Goals</label>
            <textarea
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
              className="input-field h-32"
              placeholder="Describe your marketing objectives and what success looks like for your product..."
              required
            />
            <p className="text-sm text-gray-500 mt-2">
              Be specific about metrics, timelines, and target outcomes.
            </p>
          </div>

          <button
            type="submit"
            disabled={!goals.trim()}
            className="btn-primary w-full mt-8"
          >
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}