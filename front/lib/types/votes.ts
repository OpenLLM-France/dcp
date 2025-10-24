/**
 * Type for a vote selection
 * 'left-1' to 'left-3' = Generation A preference (increasing strength)
 * 'right-1' to 'right-3' = Generation B preference (increasing strength)
 * 'equal' = Both generations are of equal quality
 * 'dislike' = Both generations are of poor quality
 */
export type VoteOption =
    | "left-3"
    | "left-2"
    | "left-1"
    | "equal"
    | "right-1"
    | "right-2"
    | "right-3"
    | "dislike"
    | "hard";

export type VoteCategory = "main" | string;

export interface VotePayload {
    task_instance_id: string;
    generation_a_id: string;
    generation_b_id: string;
    criterion: string;
    value: number;
    action: boolean; // true for set, false for clear
}

export interface TagPayload {
    task_instance_id: string;
    generation_id: string;
    action: boolean; // true for set, false for clear
    tag: string;
}
