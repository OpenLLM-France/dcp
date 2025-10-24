// Utilities
import { useContext } from "react";
import * as api from "@/lib/api";

// Contexts
import { TasksContext } from "@/lib/contexts/TasksProvider";
import { VotesContext } from "@/lib/contexts/VotesProvider";

/**
 * Component properties
 */
export interface ActionBarProps {
    getNewInstance: () => void;
}

/**
 * Action bar component with skip/submit buttons
 * Fixed to bottom of viewport
 */
export default function ActionBar({ getNewInstance }: ActionBarProps) {
    const main = useContext(VotesContext).main;
    const additional = useContext(VotesContext).additional;

    const currentTask = useContext(TasksContext).currentTask;

    function submit() {
        getNewInstance();
    }

    async function skip() {
        if (currentTask)
            await api.updateVote({
                task_instance_id: currentTask.task_instance_id,
                generation_a_id: currentTask.generations[0].id,
                generation_b_id: currentTask.generations[1].id,
                value: -200,
                action: true,
                criterion: "",
            });

        getNewInstance();
    }

    const showSubmit = main !== null || additional.filter((vote) => vote !== null).length >= 2;

    return (
        <div className="fixed w-screen shadow backdrop-blur-md bottom-0 bg-white border-t border-gray-200 px-6 py-4">
            <div className="flex justify-between max-w-7xl mx-auto">
                <button
                    onClick={skip}
                    className="px-5 py-2 rounded-full text-gray-500 font-medium border border-gray-200 cursor-pointer 
                    hover:bg-gray-50 hover:text-gray-600"
                >
                    Sauter
                </button>

                {showSubmit && (
                    <button
                        onClick={submit}
                        className="px-5 py-2 rounded-full bg-blue-500 text-white font-medium border border-blue-500  cursor-pointer 
                        hover:bg-blue-600 hover:border-blue-600 "
                    >
                        Valider
                    </button>
                )}
            </div>
        </div>
    );
}
