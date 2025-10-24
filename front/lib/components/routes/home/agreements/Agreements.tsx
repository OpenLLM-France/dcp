"use client";
// Import utilities
import { useContext } from "react";

// Import components
import Agreement from "@/lib/components/routes/home/agreements/Agreement";

// Import contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";

/**
 * Section component specifically for displaying and managing agreements
 */
export default function Agreements() {
    const agreements = useContext(UserAgreementContext).agreements;

    const acceptedCount = agreements.filter((a) => a.signed_timestamp !== null).length;
    const totalCount = agreements.length;

    return (
        <div className="w-full bg-white rounded-xl border border-gray-200 mb-6">
            <div className="flex items-center space-x-3 p-6">
                <h2 className="text-lg font-semibold text-gray-800">Conditions d&apos;utilisation</h2>
                <span className="text-sm translate-y-0.25 font-medium text-gray-500">
                    ({acceptedCount} / {totalCount} acceptées)
                </span>
            </div>

            <div className="divide-y divide-gray-100 border-t border-gray-200">
                {agreements.map((agreement) => (
                    <Agreement
                        key={agreement.agreement_id}
                        agreement={agreement}
                    />
                ))}
            </div>
        </div>
    );
}
