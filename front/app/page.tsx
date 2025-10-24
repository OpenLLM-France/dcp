"use client";

// Import utilities
import { useContext } from "react";

// Import contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";
import { TasksContext } from "@/lib/contexts/TasksProvider";

// Import components
import Tasks from "@/lib/components/routes/home/Tasks";
import Agreements from "@/lib/components/routes/home/agreements/Agreements";

/**
 * Home page component displaying agreements and available tasks
 */
export default function Home() {
    // Load agreements and user data from context
    const allAgreementsAccepted = useContext(UserAgreementContext).allAgreementsAccepted;
    const tasks = useContext(TasksContext).tasks;

    return (
        <div className="flex flex-col items-center w-full max-w-7xl">
            {/* Terms and Conditions Section */}
            {!allAgreementsAccepted && <Agreements />}

            {/* Tasks Section */}
            <div className="w-full bg-white rounded-xl border border-gray-200 mb-6 overflow-hidden">
                <div className="flex items-center justify-between p-6">
                    <div className="flex items-center space-x-3">
                        <h2 className="text-lg font-semibold text-gray-800">Tâches disponibles</h2>
                        <span className="text-sm font-medium text-gray-500">({tasks.length})</span>
                    </div>
                    {!allAgreementsAccepted && (
                        <span className="text-sm font-medium text-gray-500">
                            Acceptez les conditions pour commencer
                        </span>
                    )}
                </div>
                <Tasks tasks={tasks} isEnabled={allAgreementsAccepted} />
            </div>
        </div>
    );
}
