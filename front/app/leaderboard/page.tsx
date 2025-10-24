"use client";

// Import components
import Leaderboard from "@/lib/components/routes/leaderboard/Leaderboard";
import PageControls from "@/lib/components/routes/leaderboard/PageControls";

/**
 * This page displays the leaderboard of users with the most contributions.
 */
export default function LeaderboardPage() {
    return (
        <>
            <div className="w-full max-w-7xl bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="w-full px-6 py-4 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-800">
                        Classement des contributeur&middot;rice&middot;s
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">
                        Découvrez les meilleur&middot;e&middot;s contributeur&middot;rice&middot;s et leurs scores
                    </p>
                </div>

                <Leaderboard />
            </div>
            <PageControls />
        </>
    );
}
