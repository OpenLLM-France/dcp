// Import utilities
import React, { createContext, useState, useEffect, useContext, useCallback } from "react";
import * as api from "@/lib/api";

// Import contexts
import { UserAgreementContext } from "@/lib/contexts/UserAgreementProvider";

// Import types
import { Task, TaskInstance, TaskInstruction } from "@/lib/types";

/**
 * Type definition for the tasks context
 */
interface TasksContextType {
    tasks: Task[];
    currentTask: TaskInstance | null;
    currentTaskInstructions: TaskInstruction | null;
    isTaskLoading: boolean;
    fetchTaskInstance: (taskID: string) => void;
}

/**
 * Context for managing tasks
 */
export const TasksContext = createContext<TasksContextType>({
    tasks: [],
    currentTask: null,
    currentTaskInstructions: null,
    isTaskLoading: false,
    fetchTaskInstance: () => {},
});

/**
 * TasksProvider component that fetches and provides tasks to its children
 */
export const TasksProvider = ({ children }: { children: React.ReactNode }) => {
    const user = useContext(UserAgreementContext).user;

    const [tasks, setTasks] = useState<Task[]>([]);
    const [currentTask, setCurrentTask] = useState<TaskInstance | null>(null);
    const [currentTaskInstructions, setCurrentTaskInstructions] = useState<TaskInstruction | null>(null);
    const [isTaskLoading, setIsTaskLoading] = useState(false);

    /**
     * Fetch tasks from the API and update state
     */
    async function fetchTasks() {
        console.log("Fetching tasks...");
        const tasks = await api.getTasks();
        setTasks(tasks);
        console.log("Tasks fetched:", tasks);
    }

    const fetchTaskInstance = useCallback(async (taskID: string) => {
        setIsTaskLoading(true);
        console.log("Fetching task...");
        const task = await api.getTaskInstance(taskID);
        setCurrentTask(task);
        const instructions = await api.getTaskInstruction(taskID);
        setCurrentTaskInstructions(instructions);
        console.log("Task fetched:", task, instructions);
        setIsTaskLoading(false);
    }, []);

    /**
     * Fetch tasks when the user is available
     */
    useEffect(() => {
        if (user !== null) fetchTasks();
    }, [user]);

    return (
        <TasksContext.Provider
            value={{ tasks, currentTask, currentTaskInstructions, isTaskLoading, fetchTaskInstance }}
        >
            {children}
        </TasksContext.Provider>
    );
};
