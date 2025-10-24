// Import utilities
import { useContext } from "react";

// Import contexts
import { RatingsContext } from "@/lib/contexts/RatingsProvider";

/**
 * Pagination controls for the leaderboard (prev / next)
 */
export default function PageControls() {
    const currentPage = useContext(RatingsContext).currentPage;
    const hasMore = useContext(RatingsContext).hasMore;
    const nextPage = useContext(RatingsContext).nextPage;
    const prevPage = useContext(RatingsContext).prevPage;

    return (
        <div className="fixed bottom-0 left-0 right-0 flex items-center justify-center space-x-4 py-4 bg-white backdrop-blur-md border-t border-gray-200 shadow-lg">
            <button
                onClick={prevPage}
                disabled={currentPage === 1}
                className={`px-4 py-2 text-sm rounded-md ${
                    currentPage === 1
                        ? "text-gray-400 cursor-not-allowed"
                        : "text-blue-600 hover:bg-blue-50 cursor-pointer"
                }`}
            >
                Précédente
            </button>
            <span className="text-gray-600 text-sm">Page {currentPage}</span>
            <button
                onClick={nextPage}
                disabled={!hasMore}
                className={`px-4 py-2 text-sm rounded-md ${
                    !hasMore ? "text-gray-400 cursor-not-allowed" : "text-blue-600 hover:bg-blue-50 cursor-pointer"
                }`}
            >
                Suivante
            </button>
        </div>
    );
}
