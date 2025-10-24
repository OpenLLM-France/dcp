"use client";

// Import utilities
import { marked } from "marked";
import { useState, useRef, useEffect } from "react";

// Import icons
import Cross from "@/lib/icons/Cross";

// Import types
import { AgreementDetails } from "@/lib/types";

/**
 * Component properties
 */
interface AgreementModalProps {
    agreement: AgreementDetails;
    onClose: (accept?: boolean) => void;
    isAccepted?: boolean;
}

/**
 * Modal component for displaying agreement details and accepting them
 */
export default function AgreementModal({ agreement, onClose, isAccepted = false }: AgreementModalProps) {
    // State to track if the user has scrolled to the bottom of the content
    // This is used to enable the accept button only after reading the agreement
    const [hasScrolledToBottom, setHasScrolledToBottom] = useState(false);
    const contentRef = useRef<HTMLDivElement>(null);

    // Convert markdown content to HTML using marked
    const htmlContent = marked(agreement.text || "");

    /**
     * Check if the content is scrollable
     * This is used to determine if the user needs to scroll to read the entire agreement
     * If the content is not scrollable, we assume the user has read it
     * and set hasScrolledToBottom to true automatically
     */
    function checkIfScrollable() {
        if (contentRef.current) {
            const { scrollHeight, clientHeight } = contentRef.current;
            const isScrollable = scrollHeight > clientHeight;
            if (!isScrollable) {
                setHasScrolledToBottom(true);
            }
        }
    }

    /**
     * This function checks if the user has scrolled to the bottom of the content
     * and updates the hasScrolledToBottom state accordingly.
     * @param e The scroll event from the content div
     */
    function handleScroll(e: React.UIEvent<HTMLDivElement>) {
        const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;

        // Use a more tolerant threshold (10 pixels) for detecting bottom scroll
        const isAtBottom = Math.abs(scrollHeight - scrollTop - clientHeight) <= 10;
        setHasScrolledToBottom(isAtBottom);
    }

    /**
     * Effect to check if the content is scrollable when the modal opens
     * and to add a resize listener to check when the window size changes.
     */
    useEffect(() => {
        checkIfScrollable();

        window.addEventListener("resize", checkIfScrollable);
        return () => window.removeEventListener("resize", checkIfScrollable);
    }, [agreement.text]);

    return (
        <div
            className="fixed inset-0 bg-gray-500/30 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => onClose()}
        >
            <div
                className="bg-white rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="px-8 pt-6 pb-4 flex justify-between items-center">
                    <h3 className="text-xl font-semibold text-gray-900">{agreement.name}</h3>
                    <button
                        onClick={() => onClose()}
                        className="flex items-center text-blue-600 font-medium cursor-pointer p-2 rounded-xl hover:bg-gray-50"
                        aria-label="Fermer"
                    >
                        <Cross className="h-5 w-5" />
                    </button>
                </div>

                {/* Content */}
                <div
                    ref={contentRef}
                    onScroll={handleScroll}
                    className="grow overflow-y-auto py-4 px-8 text-base prose max-w-none"
                    dangerouslySetInnerHTML={{
                        __html: htmlContent,
                    }}
                />

                {/* Footer */}
                <div className="p-8 pt-4 w-full flex justify-end">
                    {!isAccepted ? (
                        <button
                            onClick={() => onClose(true)}
                            disabled={!hasScrolledToBottom}
                            className="py-2 px-6 rounded-xl font-medium cursor-pointer bg-blue-500 text-white
                              hover:bg-blue-600
                              disabled:bg-transparent disabled:text-gray-400 disabled:cursor-not-allowed"
                            title={!hasScrolledToBottom ? "Veuillez lire les conditions avant de les accepter." : ""}
                        >
                            Accepter
                        </button>
                    ) : (
                        <button
                            onClick={() => onClose()}
                            className="py-2 px-6 rounded-xl bg-blue-500 text-white font-medium hover:bg-blue-600 cursor-pointer"
                        >
                            Fermer
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
