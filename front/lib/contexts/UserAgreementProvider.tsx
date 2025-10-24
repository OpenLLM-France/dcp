// Utilities
import React, { createContext, useState, useEffect, useMemo, useCallback } from "react";
import * as api from "@/lib/api";

// Types
import { Agreement, AgreementDetails, User } from "@/lib/types";

/**
 * Type definition for the user context
 */
interface UserAgreementsContextType {
    user: User | null;
    agreements: Agreement[];
    allAgreementsAccepted: boolean;
    allAgreementsDetails: AgreementDetails[];
    refreshAgreements: () => Promise<void>;
}

/**
 * Context for managing user data and agreements
 */
export const UserAgreementContext = createContext<UserAgreementsContextType>({
    user: null,
    agreements: [],
    allAgreementsAccepted: true,
    allAgreementsDetails: [],
    refreshAgreements: async () => {},
});

/**
 * UserProvider component that fetches and provides user data and agreements to its children
 */
export const UserAgreementProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [agreements, setAgreements] = useState<Agreement[]>([]);
    const [allAgreementsDetails, setAllAgreementsDetails] = useState<AgreementDetails[]>([]);

    /**
     * Fetch the user data from the API and set it in state
     * This function will create a new user if one does not exist
     */
    const fetchUser = useCallback(async () => {
        console.log("Fetching user...");
        const user = await api.getOrCreateUser();
        setUser(user);
        console.log("User fetched:", user);
    }, []);

    /**
     * Fetch user agreements from the API and set them in state
     */
    const fetchAgreements = useCallback(async () => {
        console.log("Fetching agreements...");
        const agreements = await api.getUserAgreements();
        setAgreements(agreements);
        console.log("Agreements fetched:", agreements);
    }, []);

    /**
     * Check if all agreements have been accepted
     * This checks if the signed_timestamp for each agreement is not null
     */
    const allAgreementsAccepted = useMemo(
        () => agreements.every((agreement) => agreement.signed_timestamp !== null),
        [agreements]
    );

    /**
     * Function to refresh agreements by fetching them again
     */
    const refreshAgreements = useCallback(async () => {
        await fetchAgreements();
    }, [fetchAgreements]);

    /**
     * Effect to fetch user and agreements data when the component mounts
     */
    useEffect(() => {
        async function fetchData() {
            await fetchUser();
            await fetchAgreements();
        }
        fetchData();
    }, [fetchUser, fetchAgreements]);

    /**
     * Refresh agreements details when agreements change
     */
    useEffect(() => {
        const fetchAgreementsDetails = async () => {
            const details = await Promise.all(
                agreements.map((agreement) => api.getAgreementText(agreement.agreement_id))
            );
            setAllAgreementsDetails(details);
        };

        fetchAgreementsDetails();
    }, [agreements]);

    return (
        <UserAgreementContext.Provider
            value={{
                user,
                agreements,
                allAgreementsAccepted,
                allAgreementsDetails,
                refreshAgreements,
            }}
        >
            {children}
        </UserAgreementContext.Provider>
    );
};
