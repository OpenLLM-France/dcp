// Utilities
import React, { useContext } from "react";

// Contexts
import { VotesContext } from "@/lib/contexts/VotesProvider";

// Types
import { FeedbackTag } from "@/lib/types";

interface FeedbackTagsProps {
    generation: "A" | "B";
}

/**
 * Renders a list of feedback tags
 */
export default function FeedbackTags({ generation }: FeedbackTagsProps) {
    const feedbackTags = useContext(VotesContext).tags;
    const selectedTags = useContext(VotesContext).selectedTags;
    const selectTag = useContext(VotesContext).updateTag;

    /**
     * Handles selecting a feedback tag
     * Works for both normal and child tags, with support for multi or single selection for child tags
     * @param feedbackTagID a tag or child tag ID
     */
    function handleSelection(feedbackTagID: string) {
        if (selectedTags.includes(feedbackTagID)) {
            selectTag(feedbackTagID, "clear");
        } else {
            // Check if this is a child option
            const parentId = feedbackTagID.split("-").slice(0, 2).join("-");
            const parentTag = feedbackTags.find((tag) => `${generation}-${tag.id}` === parentId);

            // If this is a child option and parent has single selection
            if (parentTag?.children?.select === "single") {
                // Find currently selected child to clear it
                const currentlySelectedChild = selectedTags.find(
                    (id) => id.startsWith(`${parentId}-`) && id !== feedbackTagID
                );

                if (currentlySelectedChild) {
                    // Fire clear event for the previously selected child
                    selectTag(currentlySelectedChild, "clear");
                }
            }

            selectTag(feedbackTagID, "set");
        }
    }

    /**
     * Renders a feedback tag
     */
    function renderFeedbackTag(feedbackTag: FeedbackTag) {
        const feedbackTagID = `${generation}-${feedbackTag.id}`;
        const isSelected = selectedTags.includes(feedbackTagID);

        return (
            <div
                key={feedbackTagID}
                className={`flex flex-col 
                    ${isSelected ? "bg-blue-500  hover:bg-blue-600" : "hover:bg-gray-50 text-gray-600"}`}
            >
                <button
                    className={`px-3 py-2 text-left text-sm cursor-pointer 
                        ${isSelected ? "text-white font-semibold" : ""}`}
                    onClick={() => handleSelection(feedbackTagID)}
                >
                    {feedbackTag.text.charAt(0).toUpperCase() + feedbackTag.text.slice(1)}
                </button>

                {isSelected && feedbackTag.children && (
                    <div className="flex flex-col mb-3 mx-3 rounded border border-gray-200 divide-y divide-gray-200 overflow-hidden">
                        {feedbackTag.children.values.map((value) => {
                            // Handle both string values and object values
                            const valueId = typeof value === "string" ? value : value.id;
                            const valueText = typeof value === "string" ? value : value.text;

                            const childId = `${feedbackTagID}-${valueId}`;
                            const isChildSelected = selectedTags.includes(childId);

                            return (
                                <button
                                    key={childId}
                                    onClick={() => handleSelection(childId)}
                                    className={`text-xs py-1 px-2 text-left cursor-pointer
                                        ${
                                            isChildSelected
                                                ? "font-semibold bg-blue-400 text-white hover:bg-blue-500"
                                                : "font-normal bg-white text-gray-600 hover:bg-blue-50"
                                        }`}
                                >
                                    {valueText.charAt(0).toUpperCase() + valueText.slice(1)}
                                </button>
                            );
                        })}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="flex flex-col border border-gray-200 rounded-lg divide-y divide-gray-200 overflow-hidden">
            {feedbackTags.map(renderFeedbackTag)}
        </div>
    );
}
