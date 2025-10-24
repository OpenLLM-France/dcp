"use client";

// Global styles
import "@/lib/globals.css";

// Utilities
import React, { StrictMode } from "react";

// Components
import Header from "@/lib/components/layout/header/Header";

// Contexts
import { UserAgreementProvider } from "@/lib/contexts/UserAgreementProvider";
import { TasksProvider } from "@/lib/contexts/TasksProvider";
import { RatingsProvider } from "@/lib/contexts/RatingsProvider";
import { VotesProvider } from "@/lib/contexts/VotesProvider";

/**
 * Root layout component for the application
 * Handles global navigation, layout, and custom events
 */
export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <StrictMode>
            <UserAgreementProvider>
                <RatingsProvider>
                    <TasksProvider>
                        <VotesProvider>
                            <html lang="fr">
                                <head>
                                    <title>OpenLLM-France - Crowdsourcing platform</title>
                                    <meta name="description" content="Help develop open LLMs with your feedback !" />
                                    <link
                                        rel="icon"
                                        href="https://static.tildacdn.net/tild3134-6163-4630-a137-376439333662/avatar-logo.svg"
                                    />
                                </head>
                                <body>
                                    <Header />
                                    <div className="pt-6 pb-24 flex flex-col items-center max-w-7xl mx-auto">
                                        {children}
                                    </div>
                                </body>
                            </html>
                        </VotesProvider>
                    </TasksProvider>
                </RatingsProvider>
            </UserAgreementProvider>
        </StrictMode>
    );
}
