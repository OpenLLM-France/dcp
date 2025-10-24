// Utilities
import { useContext } from "react";

// Contexts
import { VotesContext } from "@/lib/contexts/VotesProvider";

// Icons
import Equal from "@/lib/icons/Equal";
import ThumbsUp from "@/lib/icons/ThumbsUp";
import QuestionMark from "@/lib/icons/QuestionMark";

// Types
import { Criterion, VoteOption } from "@/lib/types";

interface LikeButtonProps {
    criterion: Criterion;
    option: VoteOption;
    showLabel?: boolean;
}

const texts = {
    1: "Un peu meilleure",
    2: "Meilleure",
    3: "Bien meilleure",
};

export default function VoteButton({ criterion, option, showLabel = true }: LikeButtonProps) {
    const votes = useContext(VotesContext);
    const currentVote =
        criterion.id === "main" ? votes.main : votes.additional.find((c) => c.criterion === criterion.id)?.vote || null;

    const amount = parseInt(option.split("-")[1]) as 1 | 2 | 3;
    const facingLeft = option.includes("left");
    const isSelected = currentVote === option;

    function vote() {
        // Calculate vote value
        let value;
        switch (option) {
            case "equal":
                value = 0;
                break;
            case "dislike":
                value = -100;
                break;
            case "hard":
                value = -400;
                break;
            case "left-3":
            case "left-2":
            case "left-1":
                value = -amount;
                break;
            case "right-1":
            case "right-2":
            case "right-3":
                value = amount;
                break;
        }

        votes.updateVote(criterion.id, option, !isSelected, value);
    }

    // Red button for dislike
    if (option === "dislike")
        return (
            <button
                onClick={vote}
                className={`flex flex-col items-center justify-center space-y-1 px-2 py-2 border border-t-0 cursor-pointer
                    ${showLabel ? "w-42 rounded-bl-xl" : "rounded-b-xl"}              
                    ${
                        isSelected
                            ? "bg-red-500 border-red-500 text-white fill-white"
                            : "text-red-400 fill-red-400 border-red-200 hover:bg-red-50 hover:text-red-500 hover:fill-red-500"
                    }`}
            >
                <div className="flex">
                    <ThumbsUp className="fill-inherit rotate-180 size-4" />
                    <ThumbsUp className="fill-inherit rotate-180 rotate-y-180 size-4" />
                </div>
                {showLabel && (
                    <span className={`text-[0.65rem] ${isSelected ? "font-semibold" : "font-medium"}`}>
                        Les deux sont mauvaises
                    </span>
                )}
            </button>
        );

    // orange button for hard to answer
    if (option === "hard")
        return (
            <button
                onClick={vote}
                className={`flex flex-col items-center justify-center space-y-1 px-2 py-2 border border-l-0 border-t-0 cursor-pointer
                    ${showLabel ? "w-42 rounded-br-xl" : "rounded-b-xl"}             
                    ${
                        isSelected
                            ? "bg-orange-500 border-orange-500 text-white stroke-white"
                            : "text-orange-400 stroke-orange-400 border-orange-200 hover:bg-orange-50 hover:text-orange-500 hover:stroke-orange-500"
                    }`}
            >
                <div className="flex">
                    <QuestionMark className="fill-transparent stroke-inherit size-4" />
                </div>
                {showLabel && (
                    <span className={`text-[0.65rem] ${isSelected ? "font-semibold" : "font-medium"}`}>
                        Difficile à dire
                    </span>
                )}
            </button>
        );

    // Normal button otherwise
    return (
        <button
            className={`flex flex-col items-center justify-center space-y-1 px-2 py-2 cursor-pointer
                ${
                    isSelected
                        ? "bg-blue-500 text-white fill-white "
                        : "text-gray-500 fill-gray-400 hover:bg-gray-50 hover:text-gray-700 hover:fill-gray-500"
                }`}
            onClick={vote}
        >
            <div className="flex">
                {option === "equal" ? (
                    <Equal className="fill-inherit size-4" />
                ) : (
                    Array.from({ length: amount }).map((_, i) => (
                        <ThumbsUp key={i} className={`${facingLeft ? "rotate-y-180" : ""} fill-inherit size-4`} />
                    ))
                )}
            </div>
            {showLabel && (
                <span className={`text-[0.65rem] ${isSelected ? "font-semibold" : "font-medium"}`}>
                    {option === "equal" ? "Égales" : texts[amount]}
                </span>
            )}
        </button>
    );
}
