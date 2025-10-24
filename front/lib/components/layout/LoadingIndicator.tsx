"use client";

// Icons
import LoadingCircle from "@/lib/icons/LoadingCircle";

interface LoadingIndicatorProps {
    className?: string;
    text?: string;
}

/**
 * Reusable loading indicator component with animation
 * Can be customized with different text and additional CSS classes
 */
export default function LoadingIndicator({ className = "", text = "Loading..." }: LoadingIndicatorProps) {
    return (
        <div className={`flex flex-col justify-center items-center space-y-2 ${className}`}>
            <LoadingCircle className="animate-spin fill-blue-500" />
            <div className="text-blue-500 font-medium">{text}</div>
        </div>
    );
}
