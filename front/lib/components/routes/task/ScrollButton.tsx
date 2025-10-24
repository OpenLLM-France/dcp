// Import utilities
import { useCallback, useEffect, useState } from "react";

// Import icons
import ChevronDown from "@/lib/icons/ChevronDown";
import ChevronUp from "@/lib/icons/ChevronUp";

// Component properties
interface ScrollButtonProps {
    voteSectionRef: React.RefObject<HTMLDivElement | null>;
}

/**
 * ScrollButton component that toggles between "Go to Vote" and "Back to Prompt" actions.
 */
export default function ScrollButton({ voteSectionRef }: ScrollButtonProps) {
    // State for scroll direction
    const [scrollDirection, setScrollDirection] = useState("down");

    /**
     * Handles click events to scroll to the top or to the vote section.
     */
    function handleClick() {
        if (scrollDirection === "up") {
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else {
            const headerHeight = 72 + 12 - 1; // Header is 72px tall, spacing for the page is 12px, border is 1px
            const voteSectionPosition = voteSectionRef.current?.getBoundingClientRect().top ?? 0;

            // Calculate the offset position
            const offsetPosition = voteSectionPosition + window.scrollY - headerHeight;

            window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
    }

    /**
     * Handles scroll events to determine if the vote section is visible,
     * and to update the scroll direction state.
     */
    const handleScroll = useCallback(() => {
        if (!voteSectionRef.current) return;
        const voteRect = voteSectionRef.current.getBoundingClientRect();

        const isVoteVisible = voteRect.top < window.innerHeight && voteRect.bottom > 0;
        setScrollDirection(isVoteVisible ? "up" : "down");
    }, [voteSectionRef]);

    /**
     * Effect to add scroll event listener and handle initial scroll state.
     */
    useEffect(() => {
        window.addEventListener("scroll", handleScroll, { passive: true });
        handleScroll();

        return () => window.removeEventListener("scroll", handleScroll);
    }, [handleScroll, voteSectionRef]);

    return (
        <button
            onClick={handleClick}
            className="fixed z-40 bottom-24 right-8 bg-white hover:bg-gray-50 text-gray-600 rounded-full border border-gray-200 cursor-pointer flex items-center justify-center size-16"
            aria-label={scrollDirection === "up" ? "Retour au prompt" : "Aller au vote"}
        >
            {scrollDirection === "up" ? (
                <ChevronUp className="size-6 text-gray-600" />
            ) : (
                <ChevronDown className="size-6 text-gray-600" />
            )}
        </button>
    );
}
