// components/SetupModals.tsx
import { useState, useRef } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import { FaUpload, FaArrowRight, FaArrowLeft, FaCheck } from 'react-icons/fa';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SetupModalsProps {
  onComplete: () => void;
}

interface SetupData {
  product_name: string;
  product_description: string;
  firm_name: string;
  firm_details: string;
  market_details: string;
  strategic_goals: string;
  monthly_budget: number;
  guardrails: string;
  rebalancing_frequency_days: number;
  max_campaigns_to_generate: number;
}

const STEPS = [
  'Product Details',
  'Firm Details',
  'Market Details',
  'Strategic Goals',
  'Budget & Settings',
  'Upload Data'
];

export default function SetupModals({ onComplete }: SetupModalsProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [setupData, setSetupData] = useState<SetupData>({
    product_name: '',
    product_description: '',
    firm_name: '',
    firm_details: '',
    market_details: '',
    strategic_goals: '',
    monthly_budget: 5000,
    guardrails: '',
    rebalancing_frequency_days: 7,
    max_campaigns_to_generate: 10
  });
  const [loading, setLoading] = useState(false);
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateData = (field: keyof SetupData, value: any) => {
    setSetupData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    // Validation based on current step
    switch(currentStep) {
      case 0: // Product Details
        if (!setupData.product_name || !setupData.product_description) {
          toast.error('Please fill in all product details');
          return;
        }
        break;
      case 1: // Firm Details
        if (!setupData.firm_name || !setupData.firm_details) {
          toast.error('Please provide firm details');
          return;
        }
        break;
      case 2: // Market Details
        if (!setupData.market_details) {
          toast.error('Please describe your market');
          return;
        }
        break;
      case 3: // Strategic Goals
        if (!setupData.strategic_goals || !setupData.guardrails) {
          toast.error('Please define your goals and brand guidelines');
          return;
        }
        break;
      case 4: // Budget
        if (setupData.monthly_budget < 100) {
          toast.error('Monthly budget must be at least $100');
          return;
        }
        break;
    }

    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handlePdfUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/api/campaigns/upload-firm-pdf`, formData);
      
      // Update firm details with extracted text
      updateData('firm_details', response.data.extracted_text);
      setPdfUploaded(true);
      toast.success('PDF uploaded and processed successfully');
    } catch (error) {
      console.error('Error uploading PDF:', error);
      toast.error('Failed to process PDF');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    try {
      setLoading(true);
      
      // Submit setup data
      await axios.post(`${API_BASE}/api/campaigns/setup`, setupData);
      
      // TODO: Upload customer and transaction data files
      
      toast.success('Setup completed successfully!');
      onComplete();
    } catch (error) {
      console.error('Error completing setup:', error);
      toast.error('Failed to complete setup');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch(currentStep) {
      case 0: // Product Details
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Name
              </label>
              <input
                type="text"
                value={setupData.product_name}
                onChange={(e) => updateData('product_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g., Premium Coffee Beans"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Description
              </label>
              <textarea
                value={setupData.product_description}
                onChange={(e) => updateData('product_description', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows={4}
                placeholder="Describe your product, its key features, and unique value proposition..."
              />
            </div>
          </div>
        );

      case 1: // Firm Details
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Name
              </label>
              <input
                type="text"
                value={setupData.firm_name}
                onChange={(e) => updateData('firm_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Your company name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Details
              </label>
              <div className="mb-2">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  <FaUpload className="mr-2" />
                  {pdfUploaded ? 'Upload Another PDF' : 'Upload Company PDF'}
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handlePdfUpload}
                  className="hidden"
                />
              </div>
              <textarea
                value={setupData.firm_details}
                onChange={(e) => updateData('firm_details', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows={4}
                placeholder="Or manually enter company background, history, values, and culture..."
              />
            </div>
          </div>
        );

      case 2: // Market Details
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Market Details
              </label>
              <textarea
                value={setupData.market_details}
                onChange={(e) => updateData('market_details', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows={6}
                placeholder="Describe your target market, competition, market size, trends, and opportunities..."
              />
            </div>
          </div>
        );

      case 3: // Strategic Goals
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Strategic Goals
              </label>
              <textarea
                value={setupData.strategic_goals}
                onChange={(e) => updateData('strategic_goals', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows={4}
                placeholder="What do you want to achieve? (e.g., increase market share, reach new segments, boost brand awareness...)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Brand Guidelines & Guardrails
              </label>
              <textarea
                value={setupData.guardrails}
                onChange={(e) => updateData('guardrails', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows={4}
                placeholder="Define your brand voice, tone, values, and any content restrictions..."
              />
            </div>
          </div>
        );

      case 4: // Budget & Settings
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Monthly Marketing Budget ($)
              </label>
              <input
                type="number"
                value={setupData.monthly_budget}
                onChange={(e) => updateData('monthly_budget', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                min="100"
                step="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Budget Rebalancing Frequency (days)
              </label>
              <input
                type="number"
                value={setupData.rebalancing_frequency_days}
                onChange={(e) => updateData('rebalancing_frequency_days', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                min="1"
                max="30"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Campaigns to Generate
              </label>
              <input
                type="number"
                value={setupData.max_campaigns_to_generate}
                onChange={(e) => updateData('max_campaigns_to_generate', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                min="1"
                max="50"
              />
            </div>
          </div>
        );

      case 5: // Upload Data
        return (
          <div className="space-y-4">
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                Upload your customer and transaction data to enable AI-powered segmentation
              </p>
              <div className="space-y-4">
                <button className="w-full px-4 py-3 bg-white border-2 border-dashed border-gray-300 rounded-lg hover:border-indigo-500 transition-colors">
                  <FaUpload className="mx-auto mb-2 text-gray-400" size={24} />
                  <span className="text-gray-600">Upload Customer Data (CSV)</span>
                </button>
                <button className="w-full px-4 py-3 bg-white border-2 border-dashed border-gray-300 rounded-lg hover:border-indigo-500 transition-colors">
                  <FaUpload className="mx-auto mb-2 text-gray-400" size={24} />
                  <span className="text-gray-600">Upload Transaction Data (CSV)</span>
                </button>
                <button className="w-full px-4 py-3 bg-white border-2 border-dashed border-gray-300 rounded-lg hover:border-indigo-500 transition-colors">
                  <FaUpload className="mx-auto mb-2 text-gray-400" size={24} />
                  <span className="text-gray-600">Upload Previous Marketing Materials (PDF)</span>
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                You can skip this step and upload data later
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4">
        {/* Header */}
        <div className="px-6 py-4 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Welcome to BizHacks Campaign Manager</h2>
          <p className="text-sm text-gray-600 mt-1">Let's set up your marketing campaigns</p>
        </div>

        {/* Progress */}
        <div className="px-6 py-4 border-b">
          <div className="flex items-center justify-between">
            {STEPS.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  index < currentStep ? 'bg-green-500 text-white' :
                  index === currentStep ? 'bg-indigo-600 text-white' :
                  'bg-gray-200 text-gray-600'
                }`}>
                  {index < currentStep ? <FaCheck /> : index + 1}
                </div>
                {index < STEPS.length - 1 && (
                  <div className={`w-12 h-1 mx-2 ${
                    index < currentStep ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="mt-2 text-center">
            <p className="text-sm font-medium text-gray-900">{STEPS[currentStep]}</p>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6" style={{ minHeight: '300px' }}>
          {renderStepContent()}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t flex justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className={`inline-flex items-center px-4 py-2 rounded-md ${
              currentStep === 0
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <FaArrowLeft className="mr-2" />
            Back
          </button>

          {currentStep < STEPS.length - 1 ? (
            <button
              onClick={handleNext}
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Next
              <FaArrowRight className="ml-2" />
            </button>
          ) : (
            <button
              onClick={handleComplete}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Setting up...' : 'Complete Setup'}
              <FaCheck className="ml-2" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}