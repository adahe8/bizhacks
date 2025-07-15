// frontend/components/SetupInfoDisplay.tsx
import { Company, Product } from '@/lib/types';

interface Props {
  company: Company | null;
  product: Product | null;
}

export default function SetupInfoDisplay({ company, product }: Props) {
  if (!company || !product) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-lg p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-1">Company</h3>
          <p className="text-xl font-bold text-gray-900">{company.company_name}</p>
          <p className="text-sm text-gray-600 mt-1">{company.industry}</p>
          {company.brand_voice && (
            <p className="text-xs text-gray-500 mt-2 italic">"{company.brand_voice}"</p>
          )}
        </div>
        
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-1">Product</h3>
          <p className="text-xl font-bold text-gray-900">{product.product_name}</p>
          {product.description && (
            <p className="text-sm text-gray-600 mt-1">{product.description}</p>
          )}
          {product.target_skin_type && (
            <p className="text-xs text-gray-500 mt-2">Target: {product.target_skin_type}</p>
          )}
        </div>
      </div>
    </div>
  );
}