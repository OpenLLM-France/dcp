"use client";

// Utilities
import { Suspense, useContext, useEffect, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";

// Contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";
import { TasksContext } from "@/lib/contexts/TasksProvider";
import { VotesContext } from "@/lib/contexts/VotesProvider";

// Components
import Prompt from "@/lib/components/routes/task/Prompt";
import Generation from "@/lib/components/routes/task/Generation";
import VoteSection from "@/lib/components/routes/task/votes/VoteSection";
import FeedbackSection from "@/lib/components/routes/task/feedback/FeedbackSection";
import ScrollButton from "@/lib/components/routes/task/ScrollButton";
import ActionBar from "@/lib/components/routes/task/ActionBar";
import LoadingIndicator from "@/lib/components/layout/LoadingIndicator";

/**
 * TaskPage component that serves as the main entry point for the task page.
 * Uses Suspense for loading state management and checks if terms are accepted.
 */
function TaskPageContent() {
    const router = useRouter();

    const allAgreementsAccepted = useContext(UserAgreementContext).allAgreementsAccepted;
    const fetchTaskInstance = useContext(TasksContext).fetchTaskInstance;
    const currentTask = useContext(TasksContext).currentTask;
    const isTaskLoading = useContext(TasksContext).isTaskLoading;
    const resetVotesAndTags = useContext(VotesContext).resetVotesAndTags;

    // Router and search params
    const searchParams = useSearchParams();
    const urlTaskId = searchParams.get("id");

    /**
     * Redirect the user to the home page if all the agreements are not accepted
     */
    useEffect(() => {
        if (!allAgreementsAccepted) router.replace("/");
    }, [allAgreementsAccepted, router]);

    const getNewInstance = useCallback(() => {
        window.scrollTo(0, 0);
        resetVotesAndTags();

        if (urlTaskId) fetchTaskInstance(urlTaskId);
    }, [fetchTaskInstance, resetVotesAndTags, urlTaskId]);

    useEffect(() => {
        getNewInstance();
    }, [getNewInstance]);

    // Add refs for each category
    const voteSectionRef = useRef<HTMLDivElement | null>(null);

    if (isTaskLoading) return <LoadingIndicator text="Loading task..." className="absolute top-1/2 -translate-y-1/2" />;

    if (currentTask && urlTaskId) {
        return (
            <>
                <Prompt text={currentTask.prompt} getNewInstance={getNewInstance} />

                <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                    <Generation which="A" content={currentTask.generations[0].text} />
                    <Generation which="B" content={currentTask.generations[1].text} />
                </div>

                <VoteSection ref={voteSectionRef} criteria={currentTask.meta.criteria} />

                <FeedbackSection />

                {/* Floating elements */}
                <ScrollButton voteSectionRef={voteSectionRef} />
                <ActionBar getNewInstance={getNewInstance} />
            </>
        );
    }
}

export default function TaskPage() {
    return (
        <Suspense>
            <TaskPageContent></TaskPageContent>
        </Suspense>
    );
}
