"use client";

// Import utilities
import { useMemo } from "react";

// Import components
import Link from "next/link";

// Import icons
import ChevronRight from "@/lib/icons/ChevronRight";
import CheckCircle from "@/lib/icons/CheckCircle";
import Hourglass from "@/lib/icons/Hourglass";

// Import types
import { Task } from "@/lib/types";

interface TasksProps {
    tasks: Task[];
    isEnabled: boolean;
}

/**
 * Component for displaying available tasks
 */
export default function Tasks({ tasks, isEnabled }: TasksProps) {
    /**
     * Check if a task is completed
     * @param task the task
     * @returns true if the task is completed, else false
     */
    function isCompleted(task: Task): boolean {
        return task.done >= task.total;
    }

    /**
     * Sort tasks by completion, putting completed tasks at the end of the list
     */
    const sortedTasks = useMemo(() => {
        return [...tasks].sort((a, b) => {
            const aCompleted = isCompleted(a);
            const bCompleted = isCompleted(b);

            if (aCompleted && !bCompleted) return 1; // a is completed, b is not -> a comes after b
            if (!aCompleted && bCompleted) return -1; // a is not completed, b is -> a comes before b
            return 0; // same completion status -> maintain original order
        });
    }, [tasks]);

    return (
        <div className="relative group">
            {/* Task list */}
            <ul className="divide-y divide-gray-100 overflow-hidden border-t border-gray-200 cursor-not-allowed">
                {sortedTasks.map((task) => {
                    const completed = isCompleted(task);
                    return (
                        <li key={task.id}>
                            <Link
                                href={isEnabled ? `/task?id=${task.id}` : ``}
                                className={`w-full p-4 pr-6 text-left flex items-center justify-between cursor-pointer hover:bg-gray-50  
                                    ${isEnabled ? "" : "opacity-50 pointer-events-none select-none"}`}
                            >
                                <div className="flex items-center space-x-3">
                                    {completed ? (
                                        <CheckCircle className="size-8 fill-blue-600" />
                                    ) : (
                                        <Hourglass className="p-1 size-8 fill-gray-400" />
                                    )}
                                    <div>
                                        <span className="text-gray-800 font-medium">{task.name}</span>
                                        {task.done !== undefined && task.total !== undefined && (
                                            <span
                                                className={`ml-2 text-sm font-medium inline-flex items-center ${
                                                    completed ? "text-blue-600" : "text-gray-500"
                                                }`}
                                            >
                                                ({task.done} / {task.total} effectuées)
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <ChevronRight className="w-5 h-5 text-gray-400" />
                            </Link>
                        </li>
                    );
                })}
            </ul>

            {/* Tooltip for disabled state */}
            {!isEnabled && (
                <div
                    className="absolute opacity-0 group-hover:opacity-100 transition-opacity z-10 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 
                    px-4 py-3 rounded-2xl backdrop-blur-md bg-black/70 text-white/90 text-sm font-medium"
                >
                    Veuillez accepter toutes les conditions d&apos;utilisation pour accéder aux tâches
                </div>
            )}
        </div>
    );
}
