// Import utilities
import { useContext } from "react";

// Import contexts
import { RatingsContext } from "@/lib/contexts/RatingsProvider";

/**
 * A table that shows the users with the most contributions.
 */
export default function Leaderboard() {
    const userRating = useContext(RatingsContext).userRating;
    const leaderboardEntries = useContext(RatingsContext).leaderboardEntries;

    return (
        <table className="w-full divide-y divide-gray-200 table-fixed">
            {/* Header row */}
            <thead className="bg-gray-50 uppercase py-3 tracking-wider text-center text-xs font-medium text-gray-500">
                <tr>
                    <th scope="col" className="py-3 w-24">
                        Rang
                    </th>
                    <th scope="col" className="py-3 px-4 text-left">
                        Utilisateur&middot;rice
                    </th>
                    <th scope="col" className="py-3 w-24">
                        Score
                    </th>
                    <th scope="col" className="py-3 w-24">
                        Votes
                    </th>
                </tr>
            </thead>

            {/* Table body */}
            <tbody className="divide-y divide-gray-200">
                {/* Add a row for the user if he's better than everyone on the current page */}
                {userRating &&
                    userRating.num !== "⌛" &&
                    leaderboardEntries[0] &&
                    leaderboardEntries[0].num !== "⌛" &&
                    userRating.num < leaderboardEntries[0].num && (
                        <tr className="text-center bg-blue-50 text-gray-500 text-sm ">
                            <td className="py-4 font-medium">{userRating.num}</td>
                            <td className="py-4 px-4 text-left">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    Vous
                                </span>
                            </td>
                            <td className="py-4 ">
                                {typeof userRating.score === "number" ? userRating.score.toFixed(2) : userRating.score}
                            </td>
                            <td className="py-4">{userRating.count}</td>
                        </tr>
                    )}

                {/* Add a row for the user if he's better than everyone on the current page */}
                {/* Separate the user from the leaderboard with a ... row if he's not right next to the first of the page */}
                {userRating &&
                    userRating.num !== "⌛" &&
                    leaderboardEntries[0] &&
                    leaderboardEntries[0].num !== "⌛" &&
                    userRating.num < leaderboardEntries[0].num - 1 && (
                        <tr>
                            <td colSpan={4} className="text-center py-1 bg-gray-50 text-gray-500">
                                &middot;&middot;&middot;
                            </td>
                        </tr>
                    )}

                {/* Display the current page of the leaderboard */}
                {leaderboardEntries.map((entry, index) => {
                    const isUser = entry.id === "moi";
                    const rank = typeof entry.num === "number" ? entry.num + 1 : entry.num;
                    return (
                        <tr
                            key={index}
                            className={`text-sm text-gray-500 text-center ${isUser ? "bg-blue-50" : ""}`}
                        >
                            <td className="py-4 font-medium">
                                {rank === 1 ? "🥇" : rank === 2 ? "🥈" : rank === 3 ? "🥉" : rank}
                            </td>
                            <td className="py-4 px-4 text-left">
                                {isUser ? (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        Vous
                                    </span>
                                ) : (
                                    entry.id
                                )}
                            </td>
                            <td className="py-4">
                                {typeof entry.score === "number" ? entry.score.toFixed(2) : entry.score}
                            </td>
                            <td className="py-4">{entry.count}</td>
                        </tr>
                    );
                })}

                {/* Add a row for the user if he's worse than everyone on the current page, or if he's undefined */}
                {/* Separate the user from the leaderboard with a ... row if he's not right next to the last of the page */}
                {userRating &&
                    (userRating.num === "⌛" ||
                        (leaderboardEntries[10] && leaderboardEntries[10].num !== "⌛" && userRating.num > leaderboardEntries[10].num + 1)) && (
                        <tr>
                            <td colSpan={4} className="text-center py-1 bg-gray-50 text-gray-500">
                                &middot;&middot;&middot;
                            </td>
                        </tr>
                    )}
                {userRating &&
                    (userRating.num === "⌛" ||
                        (leaderboardEntries[10] && leaderboardEntries[10].num !== "⌛" && userRating.num > leaderboardEntries[10].num)) && (
                        <tr className="text-center bg-blue-50 text-gray-500 text-sm ">
                            <td className="py-4 font-medium">{userRating.num}</td>
                            <td className="py-4 px-4 text-left">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    Vous
                                </span>
                            </td>
                            <td className="py-4 ">
                                {typeof userRating.score === "number" ? userRating.score.toFixed(2) : userRating.score}
                            </td>
                            <td className="py-4">{userRating.count}</td>
                        </tr>
                    )}
            </tbody>
        </table>
    );
}
