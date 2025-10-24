// Import utilities
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import "katex/dist/katex.min.css";

// Configure marked options
marked.use(
    markedKatex({
        throwOnError: false,
        displayMode: true,
    })
);

marked.setOptions({
    breaks: true, // Convert \n to <br>
    gfm: true, // Use GitHub Flavored Markdown
});

/**
 * Interface for Generation Card props
 */
export interface GenerationProps {
    which: "A" | "B";
    content: string;
}

/**
 * Component for displaying a single generation in a card format
 */
export default function Generation({ which, content }: GenerationProps) {
    // Convert markdown content to HTML
    const htmlContent = marked(content || ""); // Ensure content is a string

    return (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <h2 className="text-lg font-semibold text-gray-800">Génération {which}</h2>
                </div>
            </div>
            <div className="mt-6">
                <div className="prose max-w-none text-gray-700" dangerouslySetInnerHTML={{ __html: htmlContent }} />
            </div>
        </div>
    );
}
