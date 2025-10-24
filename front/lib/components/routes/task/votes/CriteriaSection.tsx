// Utilities
import { useState } from "react";

// Components
import Criterion from "@/lib/components/routes/task/votes/Criterion";

// Icons
import ChevronUp from "@/lib/icons/ChevronUp";
import ChevronDown from "@/lib/icons/ChevronDown";

// Types
import { Criterion as CriterionType } from "@/lib/types";

interface CriteriaSectionProps {
    criteria: CriterionType[];
}

export default function Criteria({ criteria }: CriteriaSectionProps) {
    const [opened, setOpened] = useState(false);

    function toggle() {
        setOpened(!opened);
    }

    return (
        <div className="border-t border-gray-200">
            <button
                onClick={toggle}
                className={`w-full font-medium text-gray-500 py-2 flex justify-center border-gray-200 bg-gray-50 hover:bg-gray-100 items-center space-x-2 cursor-pointer 
                    ${opened ? "border-b" : ""}`}
            >
                <span>Critères supplémentaires</span>{" "}
                {opened ? (
                    <ChevronUp className="size-4 translate-y-0.2" />
                ) : (
                    <ChevronDown className="size-4 translate-y-0.2" />
                )}
            </button>
            {opened && (
                <div className="flex flex-col divide-y divide-gray-100">
                    {criteria.map((criterion) => (
                        <Criterion key={criterion.id} criterion={criterion} />
                    ))}
                    {/* <Criterion criterion="factuality" />
                    <Criterion criterion="format" />
                    <Criterion criterion="precaution" /> */}
                </div>
            )}
        </div>
    );
}
