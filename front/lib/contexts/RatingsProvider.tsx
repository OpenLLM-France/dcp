// Import utilities
import React, { createContext, useState, useEffect, useContext, useMemo, useCallback } from "react";
import * as api from "@/lib/api";

// Import contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";

// Import types
import { Rating } from "@/lib/types";

/**
 * Type definition for the ratings context
 */
interface RatingsContextType {
    totalVotes: number;
    currentGoal: number;
    progress: number;
    userRating: Rating | null;
    leaderboardEntries: Rating[];
    currentPage: number;
    hasMore: boolean;
    nextPage: () => void;
    prevPage: () => void;
}

/**
 * Context for managing ratings
 */
export const RatingsContext = createContext<RatingsContextType>({
    totalVotes: 0,
    currentGoal: 0,
    progress: 0,
    userRating: { id: "moi", num: "⌛", score: "⌛", count: 0 },
    leaderboardEntries: [],
    currentPage: 1,
    hasMore: true,
    nextPage: () => {},
    prevPage: () => {},
});

/**
 * RatingsProvider component that fetches and provides ratings to its children
 */
export const RatingsProvider = ({ children }: { children: React.ReactNode }) => {
    const user = useContext(UserAgreementContext).user;

    const [totalVotes, setTotalVotes] = useState(0);
    const [userRating, setUserRating] = useState<Rating | null>(null);
    const [leaderboardEntries, setLeaderboardEntries] = useState<Rating[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    const entriesPerPage = 10;

    /**
     * Fetch total votes from the API and update state
     */
    async function fetchTotalVotes() {
        console.log("Fetching total votes...");
        const votes = await api.getTotalVotes();
        setTotalVotes(votes);
        console.log("Votes fetched:", votes);
    }

    /**
     * Fetch user rating from the API and update state
     */
    async function fetchUserRating() {
        console.log("Fetching user rating...");
        const rating = (await api.getRating(undefined, 0)).user;
        setUserRating(rating);
        console.log("User rating:", rating);
    }

    /**
     * Fetch leaderboard entries from the API based on the current page
     * and update state with the entries and user data
     * Handles pagination and checks if there are more entries to load
     */
    const fetchLeaderboard = useCallback(async () => {
        console.log("Fetching leaderboard entries...");
        const start = (currentPage - 1) * entriesPerPage;

        const response = await api.getRating(start);

        // Get the list of entries and user data from the response
        const pageEntries = response.list;
        const userEntry = response.user;

        setLeaderboardEntries(pageEntries);
        setUserRating(userEntry);
        setHasMore(pageEntries.length === entriesPerPage);
        console.log("Entries fetched:", pageEntries);
    }, [currentPage, entriesPerPage]);

    /**
     * Get the current vote goal based on the number of votes collected
     */
    const currentGoal = useMemo((): number => {
        // Predefined milestones (small to large)
        const predefinedMilestones = [
            100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000,
        ];

        // Check predefined milestones first
        for (const goal of predefinedMilestones) {
            if (totalVotes < 0.9 * goal) {
                return goal;
            }
        }

        // Dynamically generate larger milestones if needed
        let currentGoal = predefinedMilestones[predefinedMilestones.length - 1];
        let multiplier = 2.5; // Start with 2.5x after last predefined milestone

        while (totalVotes >= 0.9 * currentGoal) {
            const nextGoal = Math.floor(currentGoal * multiplier);
            multiplier = multiplier === 2.5 ? 2 : 2.5; // Alternate multipliers
            currentGoal = nextGoal;
        }

        return currentGoal;
    }, [totalVotes]);

    /**
     * Calculate progress percentage based on total votes and current goal
     * Ensures progress does not exceed 100%
     */
    const progress = useMemo(
        () => (totalVotes && currentGoal ? Math.min(Math.round((totalVotes / currentGoal) * 100), 100) : 0),
        [totalVotes, currentGoal]
    );

    /**
     * Function to go to the next page of leaderboard entries
     */
    const nextPage = useCallback(() => {
        if (hasMore) setCurrentPage((prev) => prev + 1);
    }, [hasMore]);

    /**
     * Function to go to the previous page of leaderboard entries
     */
    const prevPage = useCallback(() => {
        if (currentPage > 1) setCurrentPage((prev) => prev - 1);
    }, [currentPage]);

    /**
     * Fetch votes & ratings when the user is available
     */
    useEffect(() => {
        if (user !== null) {
            fetchTotalVotes();
            fetchUserRating();
        }
    }, [user]);

    /**
     * Effect to fetch leaderboard entries when the current page changes
     */
    useEffect(() => {
        if (user !== null) {
            fetchLeaderboard();
        }
    }, [currentPage, fetchLeaderboard, user]);

    return (
        <RatingsContext.Provider
            value={{
                totalVotes,
                currentGoal,
                progress,
                userRating,
                leaderboardEntries,
                currentPage,
                hasMore,
                nextPage,
                prevPage,
            }}
        >
            {children}
        </RatingsContext.Provider>
    );
};
