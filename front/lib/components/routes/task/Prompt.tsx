// Utilities
import { useContext, useState } from "react";
import * as api from "@/lib/api";
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import "katex/dist/katex.min.css";

// Contexts
import { TasksContext } from "@/lib/contexts/TasksProvider";
import Flag from "@/lib/icons/Flag";
import ChevronDown from "@/lib/icons/ChevronDown";
import ChevronUp from "@/lib/icons/ChevronUp";

// Configure marked options
marked.use(
    markedKatex({
        throwOnError: false,
        displayMode: true,
    })
);

marked.setOptions({
    breaks: true,
    gfm: true,
});

/**
 * Convert LaTeX line breaks `\\` into Markdown paragraph breaks, but only
 * outside of `$...$` and `$$...$$` math regions (where `\\` is a legitimate
 * LaTeX newline inside `aligned`, arrays, etc.).
 */
function preprocessLatexNewlines(text: string): string {
    const parts: string[] = [];
    let i = 0;
    while (i < text.length) {
        if (text.startsWith("$$", i)) {
            const end = text.indexOf("$$", i + 2);
            if (end === -1) {
                parts.push(text.slice(i).replace(/\\\\/g, "\n\n"));
                break;
            }
            parts.push(text.slice(i, end + 2));
            i = end + 2;
        } else if (text[i] === "$") {
            const end = text.indexOf("$", i + 1);
            if (end === -1) {
                parts.push(text.slice(i).replace(/\\\\/g, "\n\n"));
                break;
            }
            parts.push(text.slice(i, end + 1));
            i = end + 1;
        } else {
            const nextDollar = text.indexOf("$", i);
            const next = nextDollar === -1 ? text.length : nextDollar;
            parts.push(text.slice(i, next).replace(/\\\\/g, "\n\n"));
            i = next;
        }
    }
    return parts.join("");
}

function render(text: string): string {
    return marked(preprocessLatexNewlines(text || "")) as string;
}

interface Message {
    role: string;
    content: string;
}

/**
 * Preprocess RAG document chunks so separators render consistently.
 * The raw format uses lines of dashes as separators, which Markdown would
 * otherwise interpret as h2 underlines, making some chunk titles huge.
 */
function preprocessDocuments(content: string): string {
    return content
        .replace(/^`?\[/, "`[")
        .replace(/\n-{5,}\n/g, "\n\n---\n\n");
}

/**
 * Split a system message into its instruction part and its retrieved documents part.
 * Returns `null` for `documents` if the marker is not found.
 */
function splitSystemContent(content: string): { instruction: string; documents: string | null } {
    const marker = "Voici les documents récupérés";
    const idx = content.indexOf(marker);
    if (idx === -1) return { instruction: content, documents: null };

    const afterMarker = content.slice(idx + marker.length).replace(/^\s*:\s*/, "");
    return {
        instruction: content.slice(0, idx).trimEnd(),
        documents: afterMarker.trim(),
    };
}

/**
 * Try to parse a prompt string as a message list.
 */
function parseMessageList(text: string): Message[] | null {
    const trimmed = text.trim();
    if (!trimmed.startsWith("[{") || !trimmed.endsWith("}]")) return null;

    try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed) && parsed.every(m => m && typeof m === "object" && "role" in m && "content" in m)) {
            return parsed;
        }
    } catch {
        // fallthrough
    }
    return null;
}

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
    const [instructionExpanded, setInstructionExpanded] = useState(false);
    const [documentsExpanded, setDocumentsExpanded] = useState(false);

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

    const messages = parseMessageList(text);

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

            {messages ? (
                <div className="mt-3 space-y-3">
                    {messages.map((msg, i) => {
                        if (msg.role === "system") {
                            const { instruction, documents } = splitSystemContent(msg.content || "");
                            return (
                                <div key={i} className="space-y-3">
                                    <div className="border border-gray-200 rounded-lg">
                                        <button
                                            onClick={() => setInstructionExpanded(!instructionExpanded)}
                                            className="flex items-center justify-between w-full px-4 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 rounded-lg cursor-pointer"
                                        >
                                            <span>Instruction système</span>
                                            {instructionExpanded
                                                ? <ChevronUp className="size-4 fill-gray-400" />
                                                : <ChevronDown className="size-4 fill-gray-400" />
                                            }
                                        </button>
                                        {instructionExpanded && (
                                            <div
                                                className="px-4 pb-3 prose max-w-none text-sm text-gray-500"
                                                dangerouslySetInnerHTML={{ __html: render(instruction) }}
                                            />
                                        )}
                                    </div>
                                    {documents !== null && (
                                        <div className="border border-gray-200 rounded-lg">
                                            <button
                                                onClick={() => setDocumentsExpanded(!documentsExpanded)}
                                                className="flex items-center justify-between w-full px-4 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 rounded-lg cursor-pointer"
                                            >
                                                <span>Documents récupérés</span>
                                                {documentsExpanded
                                                    ? <ChevronUp className="size-4 fill-gray-400" />
                                                    : <ChevronDown className="size-4 fill-gray-400" />
                                                }
                                            </button>
                                            {documentsExpanded && (
                                                <div
                                                    className="px-4 pb-3 prose max-w-none text-sm text-gray-500"
                                                    dangerouslySetInnerHTML={{ __html: render(preprocessDocuments(documents)) }}
                                                />
                                            )}
                                        </div>
                                    )}
                                </div>
                            );
                        }

                        return (
                            <div
                                key={i}
                                className="prose max-w-none text-gray-700"
                                dangerouslySetInnerHTML={{ __html: render(msg.content) }}
                            />
                        );
                    })}
                </div>
            ) : (
                <div className="prose max-w-none mt-3 text-gray-700" dangerouslySetInnerHTML={{ __html: render(text) }} />
            )}
        </div>
    );
}
