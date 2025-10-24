"use client";

// Utilities
import { useContext, useEffect, useState } from "react";
import { marked } from "marked";

// Contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";

// Icons
import Cross from "@/lib/icons/Cross";
import ChevronRight from "@/lib/icons/ChevronRight";

/**
 * Component properties
 */
interface AllAgreementsModalProps {
    onClose: () => void;
}

/**
 * Modal component for displaying agreement details and accepting them
 */
export default function AllAgreementsModal({ onClose }: AllAgreementsModalProps) {
    const agreements = useContext(UserAgreementContext).allAgreementsDetails;
    const [openedAgreements, setOpenedAgreements] = useState<string[]>([]);

    /**
     * Toggles the visibility of an agreement section
     * @param agreementName The name of the agreement to toggle
     */
    function toggleAgreement(agreementName: string) {
        setOpenedAgreements((prev) =>
            prev.includes(agreementName) ? prev.filter((name) => name !== agreementName) : [...prev, agreementName]
        );
    }

    /**
     * Effect to initialize the modal with the first agreement opened
     */
    useEffect(() => {
        if (agreements.length > 0) {
            setOpenedAgreements([agreements[0].name]);
        }
    }, [agreements]);

    return (
        <div
            className="fixed inset-0 bg-gray-500/30 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => onClose()}
        >
            <div
                className="bg-white rounded-2xl w-full max-w-3xl min-h-[85vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="px-8 pt-6 pb-4 flex justify-between items-center">
                    <h3 className="text-xl font-semibold text-gray-900">Conditions d&apos;utilisation</h3>
                    <button
                        onClick={() => onClose()}
                        className="flex items-center text-blue-600 font-medium cursor-pointer p-2 rounded-xl hover:bg-gray-50"
                        aria-label="Fermer"
                    >
                        <Cross className="h-5 w-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="grow overflow-y-auto space-y-4">
                    {agreements.map((agreement) => {
                        const isOpened = openedAgreements.includes(agreement.name);
                        return (
                            <div key={agreement.name} className="mx-8">
                                <button
                                    onClick={() => toggleAgreement(agreement.name)}
                                    className={`flex items-center justify-between w-full p-4 backdrop-blur-sm 
                                 text-lg font-semibold text-gray-800 border rounded-t-xl border-gray-200
                                 cursor-pointer hover:bg-gray-50 ${isOpened ? "" : "rounded-b-xl"}`}
                                >
                                    {agreement.name}
                                    <ChevronRight
                                        className={`inline-block size-5 stroke-gray-500 transition-transform ${
                                            isOpened ? "rotate-90" : ""
                                        }`}
                                    />
                                </button>
                                {isOpened && (
                                    <div
                                        className="prose max-w-none p-4 max-h-[60vh] overflow-y-auto border border-t-0 rounded-b-xl border-gray-200"
                                        dangerouslySetInnerHTML={{ __html: marked(agreement.text || "") }}
                                    />
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Footer */}
                <div className="p-8 pt-4 w-full flex justify-end">
                    <button
                        onClick={() => onClose()}
                        className="py-2 px-6 rounded-xl bg-blue-500 text-white font-medium hover:bg-blue-600 cursor-pointer"
                    >
                        Fermer
                    </button>
                </div>
            </div>
        </div>
    );
}
