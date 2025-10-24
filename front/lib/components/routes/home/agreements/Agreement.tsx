"use client";

// Utilities
import { useContext, useState } from "react";
import * as api from "@/lib/api";

// Contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";

// Components
import AgreementModal from "@/lib/components/routes/home/agreements/AgreementModal";

// Icons
import InfoCircle from "@/lib/icons/InfoCircle";

// Types
import { AgreementDetails, Agreement as AgreementType } from "@/lib/types";

/**
 * Component properties
 */
interface AgreementProps {
    agreement: AgreementType;
}

/**
 * Component for displaying a single condition with title, description, and an info button
 */
export default function Agreement({ agreement }: AgreementProps) {
    const refreshAgreements = useContext(UserAgreementContext).refreshAgreements;
    const [agreementDetails, setAgreementDetails] = useState<AgreementDetails | null>(null);

    const checked = agreement.signed_timestamp !== null;

    async function openAgreementModal() {
        setAgreementDetails(await api.getAgreementText(agreement.agreement_id));
    }

    async function closeAgreementModal(accept?: boolean) {
        // If the user accepted the agreement, call the API to sign it, then refresh agreements
        if (accept) {
            const res = await api.signAgreement(agreement.agreement_id);
            console.log("Agreement signed:", res);
            refreshAgreements();
        }

        // Close the modal and reset content
        setAgreementDetails(null);
    }

    return (
        <>
            {agreementDetails && (
                <AgreementModal agreement={agreementDetails} onClose={closeAgreementModal} isAccepted={checked} />
            )}

            <div className="px-6 py-4 flex items-center justify-between">
                <div className="grow">
                    <div className="flex items-center space-x-2">
                        <h3 className="text-base font-medium text-gray-900">{agreement.agreement_name}</h3>
                        <button
                            onClick={openAgreementModal}
                            className="group cursor-pointer"
                            aria-label="Plus d'informations"
                        >
                            <InfoCircle className="h-5 w-5 fill-gray-400 group-hover:fill-blue-500" />
                        </button>
                    </div>
                    <p className="mt-1 text-sm text-gray-500">{agreement.description}</p>
                </div>
                <button
                    onClick={openAgreementModal}
                    disabled={checked}
                    className="px-4 py-2 rounded-lg text-sm font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 cursor-pointer
                        disabled:bg-green-50 disabled:text-green-600 disabled:cursor-default"
                >
                    {checked ? "Acceptée" : "Lire"}
                </button>
            </div>
        </>
    );
}
