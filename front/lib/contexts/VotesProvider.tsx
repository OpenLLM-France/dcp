// Utilities
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import * as api from "@/lib/api";

// Contexts
import { TasksContext } from "@/lib/contexts/TasksProvider";

// Types
import { VoteCategory, VoteOption, FeedbackTag } from "@/lib/types";

interface VotesContextType {
    main: VoteOption | null;
    additional: { criterion: string; vote: VoteOption | null }[];
    tags: FeedbackTag[];
    selectedTags: string[];
    updateVote: (which: VoteCategory, option: VoteOption, action: boolean, value: number) => void;
    updateTag: (feedback: string, action: "set" | "clear") => void;
    resetVotesAndTags: () => void;
}

export const VotesContext = createContext<VotesContextType>({
    main: null,
    additional: [],
    tags: [],
    selectedTags: [],
    updateVote: () => {},
    updateTag: () => {},
    resetVotesAndTags: () => {},
});

export const VotesProvider = ({ children }: { children: React.ReactNode }) => {
    const currentTask = useContext(TasksContext).currentTask;

    const [main, setMain] = useState<VoteOption | null>(null);
    const [additional, setAdditional] = useState<{ criterion: string; vote: VoteOption | null }[]>([]);

    const tags = useMemo(() => currentTask?.meta.feedback ?? [], [currentTask]);

    const [selectedTags, setSelectedTags] = useState<string[]>([]);

    async function updateVote(which: VoteCategory, option: VoteOption, action: boolean, value: number) {
        if (!currentTask) return;

        // Either set or unset the vote
        switch (which) {
            case "main":
                if (action) setMain(option);
                else setMain(null);

                break;
            default:
                if (action) {
                    setAdditional((prev) => {
                        // If criterion already has a vote, update it
                        if (prev.find((c) => c.criterion === which)) {
                            return prev.map((c) => (c.criterion === which ? { ...c, vote: option } : c));
                        } else {
                            return [...prev, { criterion: which, vote: option }];
                        }
                    });
                } else {
                    setAdditional((prev) => prev.filter((c) => c.criterion !== which));
                }

                break;
        }

        await api.updateVote({
            task_instance_id: currentTask.task_instance_id,
            generation_a_id: currentTask.generations[0].id,
            generation_b_id: currentTask.generations[1].id,
            criterion: which,
            action,
            value,
        });
        // console.log(which, option);
    }

    async function updateTag(feedback: string, action: "set" | "clear") {
        if (!currentTask) return;

        const [generation, feedbackTagID, valueId] = feedback.split("-");
        const targetGenerationID = generation === "A" ? currentTask.generations[0].id : currentTask.generations[1].id;

        if (action === "set") {
            if (valueId) {
                const parentId = `${generation}-${feedbackTagID}`;
                const parentTag = tags.find((tag) => `${generation}-${tag.id}` === parentId);

                // If parent tag requires single selection, remove other selected values
                if (parentTag?.children?.select === "single") {
                    setSelectedTags((prev) => {
                        return [...prev.filter((id) => !id.startsWith(`${parentId}-`) || id === feedback), feedback];
                    });
                } else {
                    setSelectedTags((prev) => [...prev, feedback]);
                }
            } else {
                setSelectedTags((prev) => [...prev, feedback]);
            }
        } else {
            setSelectedTags((prev) => prev.filter((id) => id !== feedback));
        }

        // Update feedback tag in the API
        await api.updateTag({
            task_instance_id: currentTask.task_instance_id,
            generation_id: targetGenerationID,
            action: action === "set",
            tag: feedbackTagID + (valueId ? `:${valueId}` : ""),
        });
        // console.log(currentTask.task_instance_id, targetGenerationID, feedbackTagID, action, valueId);
    }

    const resetVotesAndTags = useCallback(() => {
        setMain(null);
        setAdditional([]);

        setSelectedTags([]);
    }, []);

    useEffect(() => {
        setMain(null);
        setAdditional([]);
    }, []);

    return (
        <VotesContext.Provider
            value={{
                main,
                additional,
                tags,
                selectedTags,
                updateVote,
                updateTag,
                resetVotesAndTags,
            }}
        >
            {children}
        </VotesContext.Provider>
    );
};
