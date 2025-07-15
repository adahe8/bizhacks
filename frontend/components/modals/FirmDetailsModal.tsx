import { useState, useEffect } from 'react';
import { setupApi } from '@/lib/api';
import { Company } from '@/lib/types';

interface Props {
  onComplete: (data: { company_id: string }) => void;
}

export default function FirmDetailsModal({ onComplete }: Props) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const data = await setupApi.getCompanies();
      setCompanies(data);
    } catch (error) {
      console.error('Error loading companies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedCompanyId) {
      onComplete({ company_id: selectedCompanyId });
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="bg-white rounded-lg p-8 max-w-md w-full animate-fade-up">
        <div className="mb-6">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-primary-600 h-2 rounded-full" style={{ width: '20%' }}></div>
          </div>
          <p className="text-sm text-gray-500 mt-2">Step 1 of 6</p>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">Select Your Company</h2>
        <p className="text-gray-600 mb-6">Let's start by choosing your company.</p>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label className="label">Company</label>
              <select
                value={selectedCompanyId}
                onChange={(e) => setSelectedCompanyId(e.target.value)}
                className="input-field"
                required
              >
                <option value="">Choose a company...</option>
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.company_name || company.company_name || 'Unknown Company'}
                  </option>
                ))}
              </select>
              
              {selectedCompanyId && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  {(() => {
                    const company = companies.find(c => c.id === selectedCompanyId);
                    return company ? (
                      <>
                        <p className="text-sm font-medium text-gray-700">
                          Industry: {company.industry}
                        </p>
                        {company.brand_voice && (
                          <p className="text-sm text-gray-600 mt-2">
                            Brand Voice: {company.brand_voice}
                          </p>
                        )}
                      </>
                    ) : null;
                  })()}
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={!selectedCompanyId}
              className="btn-primary w-full"
            >
              Continue
            </button>
          </form>
        )}
      </div>
    </div>
  );
}