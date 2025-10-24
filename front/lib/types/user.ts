/**
 * Represents a user session with a unique identifier
 */
export interface User {
    session_id: string;
}

/**
 * Represents a user agreement that needs to be accepted
 */
export interface Agreement {
    agreement_id: number;
    agreement_name: string;
    description: string;
    signed_timestamp: string | null;
}

/**
 * Modal content structure for agreements display
 */
export interface AgreementDetails {
    name: string;
    description: string;
    text: string;
}
