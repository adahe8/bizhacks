// frontend/app/create/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { campaignApi, setupApi } from "@/lib/api";
import CreateCampaignForm from "@/components/CreateCampaignForm";
import { SetupConfig } from "@/lib/types";

export default function CreateCampaignPage() {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);
  const [setup, setSetup] = useState<SetupConfig | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSetup();
  }, []);

  const loadSetup = async () => {
    try {
      const currentSetup = await setupApi.getCurrent();
      if (!currentSetup || !currentSetup.product_id) {
        alert("No product selected. Please complete the setup wizard first.");
        router.push("/");
        return;
      }
      setSetup(currentSetup);
    } catch (error) {
      console.error("Error loading setup:", error);
      alert("Failed to load setup. Please try again.");
      router.push("/");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCampaign = async (campaignData: any) => {
    if (!setup || !setup.product_id) {
      alert("No product selected. Please complete the setup wizard.");
      return;
    }

    setIsCreating(true);

    try {
      // Ensure product_id is included
      const dataWithProduct = {
        ...campaignData,
        product_id: setup.product_id,
      };

      const campaign = await campaignApi.create(dataWithProduct);

      // Redirect to campaigns page
      router.push("/campaigns");
    } catch (error) {
      console.error("Error creating campaign:", error);
      alert("Failed to create campaign. Please try again.");
    } finally {
      setIsCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!setup) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Setup Required
          </h2>
          <p className="text-gray-600 mb-4">
            Please complete the setup wizard before creating campaigns.
          </p>
          <button onClick={() => router.push("/")} className="btn-primary">
            Go to Setup
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Create New Campaign
        </h1>
        <p className="text-gray-600 mt-2">
          Design and launch a new marketing campaign
        </p>
      </div>

      <CreateCampaignForm
        onSubmit={handleCreateCampaign}
        onCancel={() => router.push("/campaigns")}
      />

      {isCreating && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Creating campaign...</p>
          </div>
        </div>
      )}
    </div>
  );
}
