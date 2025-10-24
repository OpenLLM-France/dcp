const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";
//const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

import {
    User,
    Agreement,
    AgreementDetails,
    Leaderboard,
    Task,
    TaskInstance,
    TaskInstruction,
    VotePayload,
    TagPayload,
} from "@/lib/types";

// ENDPOINTS RELATED TO USER AND AGREEMENTS

export async function getOrCreateUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/home`, {
        method: "GET",
        credentials: "include",
    });
    return await response.json();
}

export async function getUserAgreements(): Promise<Agreement[]> {
    const response = await fetch(`${API_BASE_URL}/user/agreements`, {
        method: "GET",
        credentials: "include",
    });
    return await response.json();
}

export async function signAgreement(agreementID: number) {
    await fetch(`${API_BASE_URL}/user/sign?agreement_id=${agreementID}`, {
        method: "POST",
        credentials: "include",
    });
}

export async function getAgreementText(agreementID: number): Promise<AgreementDetails> {
    const response = await fetch(`${API_BASE_URL}/agreement?agreement_id=${agreementID}`, {
        method: "GET",
        credentials: "include",
    });
    return await response.json();
}

// ENDPOINTS RELATED TO LEADERBOARD AND RATINGS

export async function getTotalVotes(): Promise<number> {
    const response = await fetch(`${API_BASE_URL}/stat/votes/total`, {
        method: "GET",
        credentials: "include",
    });
    const votes = (await response.json()).count;
    return votes;
}

export async function getRating(start?: number, count?: number): Promise<Leaderboard> {
    const params = new URLSearchParams();
    if (start !== undefined) params.append("start", start.toString());
    if (count !== undefined) params.append("count", count.toString());

    const response = await fetch(`${API_BASE_URL}/stat/rating?${params.toString()}`, {
        method: "GET",
        credentials: "include",
    });
    return response.json();
}

// ENDPOINTS RELATED TO TASKS

export async function getTasks(): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: "GET",
        credentials: "include",
    });
    return (await response.json()).tasks;
}

export async function getTaskInstance(taskID: string): Promise<TaskInstance> {
    const response = await fetch(`${API_BASE_URL}/task/${taskID}/next`, {
        method: "POST",
        credentials: "include",
    });
    const data = await response.json();
    data.meta = JSON.parse(data.meta);
    return data;
}

export async function getTaskInstruction(taskID: string): Promise<TaskInstruction> {
    const response = await fetch(`${API_BASE_URL}/task/${taskID}/instruction`, {
        method: "GET",
        credentials: "include",
    });
    return response.json();
}

// ENDPOINTS RELATED TO VOTES AND TAGS

export async function updateVote(vote: VotePayload) {
    await fetch(`${API_BASE_URL}/task/vote`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(vote),
    });
}

export async function updateTag(tag: TagPayload) {
    await fetch(`${API_BASE_URL}/task/tag`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(tag),
    });
}
