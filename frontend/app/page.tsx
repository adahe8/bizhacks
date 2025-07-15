'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { setupApi } from '@/lib/api';
import ProductDetailsModal from '@/components/modals/ProductDetailsModal';
import FirmDetailsModal from '@/components/modals/FirmDetailsModal';
import MarketDetailsModal from '@/components/modals/MarketDetailsModal';
import StrategicGoalsModal from '@/components/modals/StrategicGoalsModal';
import BudgetModal from '@/components/modals/BudgetModal';
import GuardrailsModal from '@/components/modals/GuardrailsModal';

type SetupStep = 
  | 'product'
  | 'firm'
  | 'market'
  | 'strategic'
  | 'budget'
  | 'guardrails'
  | 'complete';

export default function Home() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<SetupStep | null>(null);
  const [setupData, setSetupData] = useState({
    product_id: '',
    company_id: '',
    market_details: {},
    strategic_goals: '',
    monthly_budget: 0,
    guardrails: '',
    rebalancing_frequency: 'weekly',
    campaign_count: 5,
  });

  useEffect(() => {
    checkExistingSetup();
  }, []);

  const checkExistingSetup = async () => {
    try {
      const setup = await setupApi.getCurrent();
      if (setup && setup.is_active) {
        // Setup exists, redirect to dashboard
        router.push('/dashboard');
      } else {
        // No setup, start onboarding
        setCurrentStep('product');
      }
    } catch (error) {
      console.error('Error checking setup:', error);
      setCurrentStep('product');
    }
  };

  const handleStepComplete = (stepData: any) => {
    setSetupData({ ...setupData, ...stepData });
    
    // Move to next step
    const steps: SetupStep[] = ['product', 'firm', 'market', 'strategic', 'budget', 'guardrails'];
    const currentIndex = steps.indexOf(currentStep as SetupStep);
    
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    } else {
      completeSetup();
    }
  };

  const completeSetup = async () => {
    try {
      await setupApi.initialize(setupData);
      setCurrentStep('complete');
      
      // Redirect to dashboard after a brief delay
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (error) {
      console.error('Error completing setup:', error);
    }
  };

  if (currentStep === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (currentStep === 'complete') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">✨</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Setup Complete!</h2>
          <p className="text-gray-600">Redirecting to your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {currentStep === 'product' && (
        <ProductDetailsModal
          onComplete={(data) => handleStepComplete({ product_id: data.product_id })}
        />
      )}
      
      {currentStep === 'firm' && (
        <FirmDetailsModal
          onComplete={(data) => handleStepComplete({ company_id: data.company_id })}
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
            campaign_count: data.campaign_count,
          })}
        />
      )}
      
      {currentStep === 'guardrails' && (
        <GuardrailsModal
          onComplete={(data) => handleStepComplete({ guardrails: data })}
        />
      )}
    </div>
  );
}