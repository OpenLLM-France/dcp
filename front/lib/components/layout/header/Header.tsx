"use client";

// Utilities
import { useCallback, useContext, useEffect, useState } from "react";
import { usePathname } from "next/navigation";

// Contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";

// Components
import Link from "next/link";
import VoteCounter from "@/lib/components/layout/header/VoteCounter";
import AllAgreementsModal from "@/lib/components/layout/header/AllAgreementsModal";
import HelpModal from "@/lib/components/layout/header/HelpModal";

// Icons
import ChevronLeft from "@/lib/icons/ChevronLeft";
import InfoCircle from "@/lib/icons/InfoCircle";
import QuestionMark from "@/lib/icons/QuestionMark";
import Leaderboard from "@/lib/icons/Leaderboard";

/**
 * Header component for the application
 * Displays the title, back button, and optional buttons for agreements and help
 */
export default function Header() {
    const pathname = usePathname();

    const allAgreementsAccepted = useContext(UserAgreementContext).allAgreementsAccepted;

    // Helper variables to determine the current page
    const isHomePage = pathname === "/";
    const isTaskPage = pathname.includes("/task");
    const isLeaderboardPage = pathname.includes("/leaderboard");

    // Title to display in the header
    const [title, setTitle] = useState("Accueil");

    const [agreementsModalOpened, setAgreementsModalOpened] = useState(false);
    const [helpModalOpened, setHelpModalOpened] = useState(false);

    // State to track if header is at the top
    const [atTop, setAtTop] = useState(true);

    /**
     * Function to determine the title based on the current route
     * @returns The title based on the current route
     */
    const getTitleFromRoute = useCallback((): string => {
        if (isHomePage) return "Accueil";
        if (isTaskPage) return "Tâche";
        if (isLeaderboardPage) return "Meilleur⸱e⸱s contributeur⸱rice⸱s";

        return "Accueil";
    }, [isHomePage, isTaskPage, isLeaderboardPage]);

    function openAllAgreementsModal() {
        setAgreementsModalOpened(true);
    }

    function closeAllAgreementsModal() {
        setAgreementsModalOpened(false);
    }

    function openHelpModal() {
        setHelpModalOpened(true);
    }

    function closeHelpModal() {
        setHelpModalOpened(false);
    }

    /**
     * Effect to update the title based on the current route
     */
    useEffect(() => {
        setTitle(getTitleFromRoute());
    }, [getTitleFromRoute]);

    useEffect(() => {
        function handleScroll() {
            setAtTop(window.scrollY <= 15);
        }
        window.addEventListener("scroll", handleScroll);
        handleScroll(); // initialize on mount
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <>
            {/* Modals */}
            {agreementsModalOpened && <AllAgreementsModal onClose={closeAllAgreementsModal} />}
            {helpModalOpened && <HelpModal onClose={closeHelpModal} />}

            {/* Header */}
            <div className={`sticky w-full bg-white backdrop-blur-md top-0 z-10 ${atTop ? "" : "shadow"}`}>
                <div className="max-w-7xl mx-auto py-4 relative z-10 flex justify-between items-center">
                    {/* Left side buttons */}
                    <div className="w-[90px] flex justify-start">
                        {!isHomePage ? (
                            <Link
                                href="/"
                                className="flex items-center text-blue-600 font-medium cursor-pointer px-3 py-2 rounded-xl hover:bg-blue-50"
                            >
                                <ChevronLeft className="size-5 text-blue-600 mr-1.5" />
                                Retour
                            </Link>
                        ) : (
                            <Link
                                href="/leaderboard"
                                className="flex items-center text-blue-600 font-medium cursor-pointer px-3 py-2 rounded-xl hover:bg-blue-50"
                            >
                                <Leaderboard className="size-5 fill-blue-600 mr-1.5" />
                                Classement
                            </Link>
                        )}
                    </div>

                    {/* Title */}
                    <div className="text-xl font-semibold text-center text-gray-800">{title}</div>

                    {/* Right side buttons */}
                    <div className="w-[90px] flex justify-end">
                        {isTaskPage && (
                            <button
                                onClick={openHelpModal}
                                className="flex items-center text-blue-600 font-medium cursor-pointer px-3 py-2 rounded-xl hover:bg-blue-50"
                                aria-label="Instructions d'aide"
                            >
                                <QuestionMark className="size-5 text-blue-600 mr-1.5" />
                                Aide
                            </button>
                        )}
                        {isHomePage && allAgreementsAccepted && (
                            <button
                                onClick={openAllAgreementsModal}
                                className="flex items-center text-blue-600 font-medium cursor-pointer px-3 py-2 rounded-xl hover:bg-blue-50"
                                aria-label="Conditions d'utilisation"
                            >
                                <InfoCircle className="size-5 fill-blue-600 mr-1.5" />
                                Conditions
                            </button>
                        )}
                    </div>
                </div>

                {/* Vote counter - Only show on home page */}
                {isHomePage && <VoteCounter />}
            </div>
        </>
    );
}
