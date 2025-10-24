// Utilities
import { useContext } from "react";

// Contexts
import { VotesContext } from "@/lib/contexts/VotesProvider";

// Components
import FeedbackTags from "@/lib/components/routes/task/feedback/FeedbackTags";

export default function FeedbackSection() {
    const main = useContext(VotesContext).main;

    if (main)
        return (
            <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                {(main.startsWith("right") || main === "dislike" || main === "hard") && (
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">
                            Quels sont les problèmes de la Génération A ?
                        </h2>
                        <FeedbackTags generation="A" />
                    </div>
                )}

                {main.startsWith("left") && (
                    <div /> // Empty div to push feedback to right column
                )}

                {(main.startsWith("left") || main === "dislike" || main === "hard") && (
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">
                            Quels sont les problèmes de la Génération B ?
                        </h2>
                        <FeedbackTags generation="B" />
                    </div>
                )}
            </div>
        );
}
