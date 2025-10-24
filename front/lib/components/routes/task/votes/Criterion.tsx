import VoteButton from "@/lib/components/routes/task/votes/VoteButton";
import { Criterion as CriterionType } from "@/lib/types";

interface CriterionProps {
    criterion: CriterionType;
}
export default function Criterion({ criterion }: CriterionProps) {
    return (
        <div className="py-4 flex flex-col items-center">
            <span className="mb-1 font-medium text-gray-800 text-sm">
                {criterion.text.charAt(0).toUpperCase() + criterion.text.slice(1)}
            </span>
            {criterion.help && <h3 className="text-xs italic pb-3 text-gray-700">{criterion.help}</h3>}
            <div className=" flex items-center space-x-2 mb-0">
                {/* A label */}
                <span className="w-6 flex items-center justify-start font-medium text-gray-500 text-sm pl-1">A</span>

                {/* Voting buttons in a grid */}
                <div className="w-full grid grid-cols-7 divide-x divide-gray-200 border border-gray-200 rounded-xl overflow-hidden">
                    <VoteButton criterion={criterion} option="left-3" showLabel={false} />
                    <VoteButton criterion={criterion} option="left-2" showLabel={false} />
                    <VoteButton criterion={criterion} option="left-1" showLabel={false} />
                    <VoteButton criterion={criterion} option="equal" showLabel={false} />
                    <VoteButton criterion={criterion} option="right-1" showLabel={false} />
                    <VoteButton criterion={criterion} option="right-2" showLabel={false} />
                    <VoteButton criterion={criterion} option="right-3" showLabel={false} />
                </div>

                {/* B label */}
                <span className="w-6 flex items-center justify-end font-medium text-gray-500 text-sm pr-1">B</span>
            </div>

            {/* Dislike option */}
            <div className="flex justify-center mb-0">
                <VoteButton criterion={criterion} option="dislike" showLabel={false} />
            </div>
        </div>
    );
}
