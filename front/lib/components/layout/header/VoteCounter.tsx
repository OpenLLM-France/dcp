// Utilities
import { useContext } from "react";

// Import contexts
import { RatingsContext } from "@/lib/contexts/RatingsProvider";

/**
 * Displays a progress bar toward the next vote goal
 * Designed to be used in the header
 */
export default function VoteCounter() {
    const totalVotes = useContext(RatingsContext).totalVotes;
    const currentGoal = useContext(RatingsContext).currentGoal;
    const progress = useContext(RatingsContext).progress;

    return (
        <div className="w-full bg-blue-50 py-2 flex flex-col space-y-2 relative z-0">
            <div className="max-w-7xl mx-auto px-6 flex items-center justify-center">
                <span className="text-xs text-gray-700 whitespace-nowrap mr-3">Nombre total de votes</span>
                <div className="w-100 flex items-center">
                    <div className="flex-grow h-5 rounded bg-white overflow-hidden">
                        <div className="h-full bg-blue-500 flex items-center" style={{ width: `${progress}%` }}>
                            <span
                                className={`px-2 text-xs font-semibold ${
                                    progress < 7.5 ? "text-blue-500" : "text-white"
                                }`}
                            >
                                {totalVotes}
                            </span>
                        </div>
                    </div>
                    <div className="ml-2 text-xs text-gray-700 whitespace-nowrap">Objectif : {currentGoal}</div>
                </div>
            </div>
        </div>
    );
}
