import { useState, useEffect } from 'react';
import { setupApi } from '@/lib/api';
import { Product } from '@/lib/types';

interface Props {
  onComplete: (data: { product_id: string }) => void;
}

export default function ProductDetailsModal({ onComplete }: Props) {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const data = await setupApi.getProducts();
      setProducts(data);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedProductId) {
      onComplete({ product_id: selectedProductId });
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="bg-white rounded-lg p-8 max-w-md w-full animate-fade-up">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to BizHacks!</h2>
        <p className="text-gray-600 mb-6">Let's start by selecting your product.</p>

        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label className="label">Select Product</label>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="input-field"
                required
              >
                <option value="">Choose a product...</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.product_name}
                  </option>
                ))}
              </select>
              
              {selectedProductId && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  {(() => {
                    const product = products.find(p => p.id === selectedProductId);
                    return product ? (
                      <>
                        <p className="text-sm text-gray-600">{product.description}</p>
                        {product.target_skin_type && (
                          <p className="text-xs text-gray-500 mt-2">
                            Target: {product.target_skin_type}
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
              disabled={!selectedProductId}
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