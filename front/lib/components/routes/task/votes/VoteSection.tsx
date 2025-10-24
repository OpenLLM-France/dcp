// Components
import VoteButton from "@/lib/components/routes/task/votes/VoteButton";
import Criteria from "@/lib/components/routes/task/votes/CriteriaSection";

// Types
import { RefObject } from "react";
import { Criteria as CriteriaType } from "@/lib/types";

interface VoteSectionProps {
    ref: RefObject<HTMLDivElement | null>;
    criteria: CriteriaType;
}

/**
 * VoteSection component that displays voting options for comparing two generations.
 * It includes main voting options, and additional detailed criteria.
 */
export default function VoteSection({ ref, criteria }: VoteSectionProps) {
    return (
        <div ref={ref} className="w-full bg-white rounded-xl border border-gray-200 mb-3 overflow-hidden">
            <h2 className="text-lg font-semibold text-gray-800 p-6 pb-3">{criteria.main.text}</h2>
            {criteria.main.help && <h3 className="text-xs italic px-6 pb-6 text-gray-700">{criteria.main.help}</h3>}
            <div className="p-6 pt-0">
                <div className="flex items-center space-x-2 mb-0">
                    <span className="w-6 flex items-center justify-start font-medium text-gray-500 text-sm pl-1">
                        A
                    </span>

                    <div className="w-full grid grid-cols-7 divide-x divide-gray-200 border border-gray-200 rounded-xl overflow-hidden">
                        <VoteButton criterion={criteria.main} option="left-3" />
                        <VoteButton criterion={criteria.main} option="left-2" />
                        <VoteButton criterion={criteria.main} option="left-1" />
                        <VoteButton criterion={criteria.main} option="equal" />
                        <VoteButton criterion={criteria.main} option="right-1" />
                        <VoteButton criterion={criteria.main} option="right-2" />
                        <VoteButton criterion={criteria.main} option="right-3" />
                    </div>

                    <span className="w-6 flex items-center justify-end font-medium text-gray-500 text-sm pr-1">B</span>
                </div>

                <div className="flex justify-center mb-0">
                    <VoteButton criterion={criteria.main} option="dislike" />
                    <VoteButton criterion={criteria.main} option="hard" />
                </div>
            </div>

            {criteria.additional.length > 0 && <Criteria criteria={criteria.additional} />}
        </div>
    );
}
