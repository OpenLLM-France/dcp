export interface Task {
    id: string;
    name: string;
    done: number;
    total: number;
}

export interface TaskInstance {
    task_instance_id: string;
    prompt: string;
    generations: Generation[];
    meta: {
        feedback: FeedbackTag[];
        criteria: Criteria;
    };
}

export interface Generation {
    id: string;
    text: string;
}

export interface FeedbackTag {
    id: string;
    text: string;
    children?: {
        select: "single" | "multi";
        values: Array<string | { id: string; text: string }>;
    };
}

export interface TaskInstruction {
    id: number;
    text: string;
}

export interface Criteria {
    main: Criterion;
    additional: Criterion[];
}

export interface Criterion {
    id: string;
    text: string;
    help?: string;
}
