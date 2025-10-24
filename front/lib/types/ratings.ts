export interface Rating {
    id: string | "moi";
    num: number | "⌛";
    score: number | "⌛";
    count: number;
}

export interface Leaderboard {
    user: Rating;
    list: Rating[];
}
