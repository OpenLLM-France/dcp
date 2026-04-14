// Utilities
import { useContext } from "react";
import * as api from "@/lib/api";
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import "katex/dist/katex.min.css";

// Contexts
import { TasksContext } from "@/lib/contexts/TasksProvider";
import Flag from "@/lib/icons/Flag";

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
            <div className="prose max-w-none mt-3 text-gray-700" dangerouslySetInnerHTML={{ __html: render(text) }} />
        </div>
    );
}
