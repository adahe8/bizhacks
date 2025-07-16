import { useState } from 'react';

interface Props {
  onComplete: (data: string) => void;
}

export default function GuardrailsModal({ onComplete }: Props) {
  const [guardrails, setGuardrails] = useState('');
  const [guidelines] = useState([
    { category: 'Tone & Voice', examples: ['Professional but approachable', 'No slang or informal language', 'Empowering and positive messaging'] },
    { category: 'Content Restrictions', examples: ['No medical claims without FDA approval', 'Avoid competitor comparisons', 'No before/after photos'] },
    { category: 'Brand Standards', examples: ['Always use registered trademark symbol', 'Include sustainability messaging', 'Emphasize cruelty-free status'] },
    { category: 'Legal Requirements', examples: ['Include disclaimer for results', 'Follow FTC guidelines for testimonials', 'Comply with GDPR for email marketing'] },
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onComplete(guardrails);
  };

  return (
    <div className="modal-backdrop">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full animate-fade-up max-h-[90vh] overflow-y-auto">
        <div className="mb-6">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary-600 h-2 rounded-full" style={{ width: '100%' }}></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">Step 6 of 6</p>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">Brand Guardrails</h2>
        <p className="text-gray-600 mb-6">Define the rules and guidelines for your marketing content.</p>

        <div className="mb-6 space-y-4">
          {guidelines.map((guide) => (
            <div key={guide.category} className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">{guide.category}</h3>
              <ul className="space-y-1">
                {guide.examples.map((example, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start">
                    <span className="text-gray-400 mr-2">•</span>
                    {example}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
          <div>
            <label className="label">Your Brand Guardrails</label>
            <textarea
              value={guardrails}
              onChange={(e) => setGuardrails(e.target.value)}
              className="input-field h-32"
              placeholder="List your brand guidelines, content restrictions, legal requirements, and any other rules that all marketing content must follow..."
              required
            />
            <p className="text-sm text-gray-500 mt-2">
              These rules will be enforced by AI before any content is published.
            </p>
          </div>

          <button
            type="submit"
            disabled={!guardrails.trim()}
            className="btn-primary w-full mt-8"
          >
            Complete Setup
          </button>
        </form>
      </div>
    </div>
  );
}