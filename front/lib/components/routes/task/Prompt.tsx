// Utilities
import { useContext } from "react";
import * as api from "@/lib/api";

// Contexts
import { TasksContext } from "@/lib/contexts/TasksProvider";
import Flag from "@/lib/icons/Flag";

/**
 * Component properties
 */
interface PromptProps {
    text: string;
    getNewInstance: () => void;
}

/**
 * Prompt component that displays a prompt message.
 */
export default function Prompt({ text, getNewInstance }: PromptProps) {
    const currentTask = useContext(TasksContext).currentTask;

    async function report() {
        if (!confirm("Voulez-vous vraiment signaler ce prompt ?\n\nVous passerez ensuite au prompt suivant.")) return;

        if (currentTask)
            await api.updateVote({
                task_instance_id: currentTask.task_instance_id,
                generation_a_id: currentTask.generations[0].id,
                generation_b_id: currentTask.generations[1].id,
                value: -300,
                action: true,
                criterion: "",
            });

        getNewInstance();
    }

    return (
        <div className="bg-white w-full rounded-xl border border-gray-200 p-6 mb-3">
            <div className="flex justify-between">
                <h2 className="text-lg font-semibold text-gray-800">Prompt</h2>

                <button
                    onClick={report}
                    className="group p-1 rounded-full cursor-pointer hover:bg-orange-100"
                    title="Signaler ce prompt"
                >
                    <Flag className="fill-orange-400 group-hover:fill-orange-500 size-5" />
                </button>
            </div>
            <p className="mt-3 text-gray-700">{text}</p>
        </div>
    );
}
