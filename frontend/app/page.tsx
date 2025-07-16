// frontend/app/page.tsx

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { setupApi, agentApi } from '@/lib/api';
import ProductDetailsModal from '@/components/modals/ProductDetailsModal';
import FirmDetailsModal from '@/components/modals/FirmDetailsModal';
import MarketDetailsModal from '@/components/modals/MarketDetailsModal';
import StrategicGoalsModal from '@/components/modals/StrategicGoalsModal';
import BudgetModal from '@/components/modals/BudgetModal';
import GuardrailsModal from '@/components/modals/GuardrailsModal';
import AICampaignGenerationModal from '../components/modals/AICampaignGenerationModal';

type SetupStep = 
  | 'firm'
  | 'product'
  | 'market'
  | 'strategic'
  | 'budget'
  | 'guardrails'
  | 'generating-segments'
  | 'ai-campaigns'
  | 'complete';

export default function Home() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<SetupStep | null>(null);
  const [isExistingSetup, setIsExistingSetup] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const [generatedSegments, setGeneratedSegments] = useState<any[]>([]);
  const [completedSetup, setCompletedSetup] = useState<any>(null); // ✅ Store completed setup
  const [setupData, setSetupData] = useState({
    company_id: '',
    product_id: '',
    market_details: {},
    strategic_goals: '',
    monthly_budget: 0,
    guardrails: '',
    rebalancing_frequency: 'weekly' as const,
    campaign_count: 5,
  });

  useEffect(() => {
    checkExistingSetup();
  }, []);

  const checkExistingSetup = async () => {
    try {
      const setup = await setupApi.getCurrent();
      
      if (setup && setup.is_active) {
        // Setup exists and is active
        setIsExistingSetup(true);
        setShowWelcome(true);
        
        // Check if all required fields are present
        if (setup.company_id && setup.product_id && setup.monthly_budget > 0) {
          // Complete setup exists, show welcome with options
          setShowWelcome(true);
        } else {
          // Incomplete setup, restart wizard
          setCurrentStep('firm');
          setShowWelcome(false);
        }
      } else {
        // No setup or inactive, start fresh
        setCurrentStep('firm');
        setShowWelcome(false);
      }
    } catch (error) {
      console.error('Error checking setup:', error);
      // On error, start fresh setup
      setCurrentStep('firm');
      setShowWelcome(false);
    }
  };

  const handleStepComplete = async (stepData: any) => {
    setSetupData(prev => ({ ...prev, ...stepData }));
    
    // Move to next step
    const steps: SetupStep[] = ['firm', 'product', 'market', 'strategic', 'budget', 'guardrails'];
    const currentIndex = steps.indexOf(currentStep as SetupStep);
    
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    } else {
      // After guardrails, complete setup and generate segments
      await completeSetup();
    }
  };

  const completeSetup = async () => {
    try {
      // Initialize setup
      const setupResponse = await setupApi.initialize(setupData);
      
      // ✅ Store the completed setup for passing to AICampaignGenerationModal
      setCompletedSetup({
        ...setupData,
        id: setupResponse.id,
        is_active: true
      });
      
      // Show segment generation loading
      setCurrentStep('generating-segments');
      
      // Generate customer segments
      try {
        const segmentResponse = await agentApi.generateSegments();
        const segments = segmentResponse.segments || [];
        setGeneratedSegments(segments);
        
        // After segments are generated, automatically go to AI campaign generation
        setTimeout(() => {
          setCurrentStep('ai-campaigns');
        }, 1500);
        
      } catch (error) {
        console.error('Error generating segments:', error);
        // Continue to campaign generation even if segments fail
        setCurrentStep('ai-campaigns');
      }
      
    } catch (error) {
      console.error('Error completing setup:', error);
      alert('Error completing setup. Please try again.');
    }
  };

  const handleCampaignsGenerated = () => {
    setCurrentStep('complete');
    
    // Redirect to dashboard after a brief delay
    setTimeout(() => {
      router.push('/dashboard');
    }, 2000);
  };

  const startNewSetup = () => {
    setShowWelcome(false);
    setCurrentStep('firm');
    setGeneratedSegments([]);
    setCompletedSetup(null);
    setSetupData({
      company_id: '',
      product_id: '',
      market_details: {},
      strategic_goals: '',
      monthly_budget: 0,
      guardrails: '',
      rebalancing_frequency: 'weekly',
      campaign_count: 5,
    });
  };

  if (currentStep === null && !showWelcome) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (showWelcome && isExistingSetup) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="bg-white rounded-lg p-8 max-w-md w-full animate-fade-up shadow-lg">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Welcome Back!</h1>
            <p className="text-gray-600 mb-8">
              You have an existing setup. What would you like to do?
            </p>
            <div className="space-y-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="btn-primary w-full"
              >
                Go to Dashboard
              </button>
              <button
                onClick={startNewSetup}
                className="btn-outline w-full"
              >
                Run Setup Wizard Again
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-6">
              Running the setup wizard will update your existing configuration.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'generating-segments') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="text-center bg-white rounded-lg p-8 shadow-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Analyzing Customer Data...</h2>
          <p className="text-gray-600">Creating customer segments using AI</p>
        </div>
      </div>
    );
  }

  if (currentStep === 'complete') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
        <div className="text-center bg-white rounded-lg p-8 shadow-lg">
          <div className="text-6xl mb-4">✨</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Setup Complete!</h2>
          <p className="text-gray-600 mb-4">Your campaigns are ready!</p>
          <div className="animate-pulse text-sm text-gray-500">
            Redirecting to dashboard...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Progress Indicator */}
      {currentStep && currentStep !== 'ai-campaigns' && (
        <div className="fixed top-0 left-0 right-0 bg-white shadow-sm z-50">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold text-primary-600">BizHacks Setup Wizard</h1>
              <button
                onClick={() => {
                  if (confirm('Are you sure you want to exit the setup wizard?')) {
                    if (isExistingSetup) {
                      router.push('/dashboard');
                    } else {
                      setShowWelcome(true);
                    }
                  }
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}
      
      <div className={currentStep && currentStep !== 'ai-campaigns' ? "pt-16" : ""}>
        {currentStep === 'firm' && (
          <FirmDetailsModal
            onComplete={(data) => handleStepComplete({ company_id: data.company_id })}
          />
        )}
        
        {currentStep === 'product' && (
          <ProductDetailsModal
            companyId={setupData.company_id}
            onComplete={(data) => handleStepComplete({ product_id: data.product_id })}
          />
        )}
        
        {currentStep === 'market' && (
          <MarketDetailsModal
            onComplete={(data) => handleStepComplete({ market_details: data })}
          />
        )}
        
        {currentStep === 'strategic' && (
          <StrategicGoalsModal
            onComplete={(data) => handleStepComplete({ strategic_goals: data })}
          />
        )}
        
        {currentStep === 'budget' && (
          <BudgetModal
            onComplete={(data) => handleStepComplete({
              monthly_budget: data.budget,
              rebalancing_frequency: data.frequency,
              campaign_count: data.campaign_count, // ✅ Ensure campaign_count is saved
            })}
          />
        )}
        
        {currentStep === 'guardrails' && (
          <GuardrailsModal
            onComplete={(data) => handleStepComplete({ guardrails: data })}
          />
        )}
        
        {currentStep === 'ai-campaigns' && completedSetup && ( // ✅ Pass completedSetup
          <AICampaignGenerationModal
            segments={generatedSegments}
            channels={['facebook', 'email', 'google_seo']}
            setup={completedSetup} // ✅ Pass setup as prop
            onComplete={handleCampaignsGenerated}
          />
        )}
      </div>
    </div>
  );
}