import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { setupApi } from '@/lib/api';
import { Product } from '@/lib/types';

interface CampaignFormData {
  product_id: string;
  name: string;
  description: string;
  channel: 'facebook' | 'email' | 'google_seo';
  customer_segment: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  budget: number;
}

interface Props {
  initialData?: Partial<CampaignFormData>;
  onSubmit: (data: CampaignFormData) => void;
  onCancel: () => void;
}

export default function CreateCampaignForm({ initialData, onSubmit, onCancel }: Props) {
  const [products, setProducts] = useState<Product[]>([]);
  const [currentSetup, setCurrentSetup] = useState<any>(null);
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<CampaignFormData>({
    defaultValues: initialData || {
      channel: 'facebook',
      frequency: 'weekly',
      budget: 1000,
    },
  });

  const selectedChannel = watch('channel');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [productsData, setupData] = await Promise.all([
        setupApi.getProducts(),
        setupApi.getCurrent(),
      ]);
      setProducts(productsData);
      setCurrentSetup(setupData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const getChannelDescription = (channel: string) => {
    switch (channel) {
      case 'facebook':
        return 'Create engaging social media posts with images and videos';
      case 'email':
        return 'Design email campaigns with personalized content';
      case 'google_seo':
        return 'Optimize for search with targeted keywords and ad copy';
      default:
        return '';
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="card">
      <h2 className="text-xl font-semibold mb-6">Campaign Details</h2>

      <div className="space-y-6">
        {/* Product Selection */}
        <div>
          <label className="label">Product</label>
          <select
            {...register('product_id', { required: 'Product is required' })}
            className="input-field"
            defaultValue={currentSetup?.product_id || ''}
          >
            <option value="">Select a product</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.product_name}
              </option>
            ))}
          </select>
          {errors.product_id && (
            <p className="text-red-500 text-sm mt-1">{errors.product_id.message}</p>
          )}
        </div>

        {/* Campaign Name */}
        <div>
          <label className="label">Campaign Name</label>
          <input
            type="text"
            {...register('name', { required: 'Campaign name is required' })}
            className="input-field"
            placeholder="Summer Glow Campaign"
          />
          {errors.name && (
            <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="label">Description</label>
          <textarea
            {...register('description')}
            className="input-field h-24"
            placeholder="Describe the campaign objectives and key messages..."
          />
        </div>

        {/* Channel Selection */}
        <div>
          <label className="label">Channel</label>
          <div className="grid grid-cols-3 gap-4">
            {(['facebook', 'email', 'google_seo'] as const).map((channel) => (
              <label
                key={channel}
                className={`
                  border rounded-lg p-4 cursor-pointer transition-all
                  ${selectedChannel === channel
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-gray-400'
                  }
                `}
              >
                <input
                  type="radio"
                  {...register('channel')}
                  value={channel}
                  className="sr-only"
                />
                <div className="text-center">
                  <div className="text-2xl mb-2">
                    {channel === 'facebook' && '📱'}
                    {channel === 'email' && '✉️'}
                    {channel === 'google_seo' && '🔍'}
                  </div>
                  <p className="font-medium capitalize">{channel.replace('_', ' ')}</p>
                </div>
              </label>
            ))}
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {getChannelDescription(selectedChannel)}
          </p>
        </div>

        {/* Customer Segment */}
        <div>
          <label className="label">Customer Segment</label>
          <input
            type="text"
            {...register('customer_segment')}
            className="input-field"
            placeholder="e.g., Young Professionals, Eco-Conscious Consumers"
          />
        </div>

        {/* Frequency */}
        <div>
          <label className="label">Campaign Frequency</label>
          <select
            {...register('frequency')}
            className="input-field"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>

        {/* Budget */}
        <div>
          <label className="label">Monthly Budget (USD)</label>
          <input
            type="number"
            {...register('budget', {
              required: 'Budget is required',
              min: { value: 100, message: 'Minimum budget is $100' },
            })}
            className="input-field"
            placeholder="1000"
            step="100"
          />
          {errors.budget && (
            <p className="text-red-500 text-sm mt-1">{errors.budget.message}</p>
          )}
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex gap-4 mt-8">
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary flex-1"
        >
          {isSubmitting ? 'Creating...' : 'Create Campaign'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="btn-outline flex-1"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}