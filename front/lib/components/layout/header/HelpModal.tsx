"use client";

import { TasksContext } from "@/lib/contexts/TasksProvider";
import Cross from "@/lib/icons/Cross";
import { marked } from "marked";
import { useContext } from "react";

interface HelpModalProps {
    onClose: () => void;
}

/**
 * Modal component for displaying help instructions
 */
export default function HelpModal({ onClose }: HelpModalProps) {
    const content = useContext(TasksContext).currentTaskInstructions?.text ?? "";

    // Convert markdown content to HTML using marked
    const htmlContent = marked(content);

    return (
        <div
            className="fixed inset-0 bg-gray-500/30 backdrop-blur-sm flex items-center justify-center z-50 px-4"
            onClick={() => onClose()}
        >
            <div
                className="bg-white rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="p-8 pb-0 flex justify-between items-center">
                    <h3 className="text-xl font-semibold text-gray-900">Instructions</h3>
                    <button
                        onClick={() => onClose()}
                        className="cursor-pointer p-2 rounded-xl hover:bg-gray-50"
                        aria-label="Fermer"
                    >
                        <Cross className="h-5 w-5 stroke-blue-500" />
                    </button>
                </div>

                {/* Content */}
                <div
                    className="overflow-y-auto p-8 pt-4 prose max-w-none"
                    dangerouslySetInnerHTML={{
                        __html: htmlContent,
                    }}
                ></div>

                {/* Footer */}
                <div className="p-8 pt-4 w-full flex justify-end">
                    <button
                        onClick={() => onClose()}
                        className="py-2 px-6 rounded-xl bg-blue-500 text-white font-medium border border-blue-500
                         hover:bg-blue-600 hover:border-blue-600 cursor-pointer"
                    >
                        Fermer
                    </button>
                </div>
            </div>
        </div>
    );
}
