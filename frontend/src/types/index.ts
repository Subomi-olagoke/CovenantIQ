// TypeScript type definitions

export interface User {
    id: string;
    email: string;
    full_name: string | null;
    company: string | null;
    role: string;
    created_at: string;
}

export interface LoanAgreement {
    id: string;
    user_id: string;
    title: string;
    borrower_name: string | null;
    loan_amount: number | null;
    currency: string;
    origination_date: string | null;
    maturity_date: string | null;
    status: string;
    ai_extraction_status: string;
    created_at: string;
    covenant_count?: number;
}

export interface Covenant {
    id: string;
    loan_agreement_id: string;
    covenant_type: string;
    covenant_name: string;
    description: string | null;
    threshold_value: number | null;
    threshold_operator: string | null;
    frequency: string | null;
    next_test_date: string | null;
    is_active: boolean;
    latest_status?: string;
    latest_value?: number;
}

export interface CovenantMeasurement {
    id: string;
    covenant_id: string;
    measurement_date: string;
    actual_value: number;
    threshold_value: number | null;
    status: string;
    distance_to_breach: number | null;
    notes: string | null;
    created_at: string;
}

export interface Alert {
    id: string;
    covenant_id: string | null;
    loan_agreement_id: string | null;
    alert_type: string;
    severity: string;
    title: string;
    message: string;
    predicted_breach_date: string | null;
    days_until_breach: number | null;
    is_read: boolean;
    is_resolved: boolean;
    created_at: string;
}

export interface PortfolioSummary {
    total_loans: number;
    active_loans: number;
    total_covenants: number;
    compliant_covenants: number;
    warning_covenants: number;
    breach_covenants: number;
    unread_alerts: number;
    critical_alerts: number;
}

export interface RiskHeatmapItem {
    loan_id: string;
    loan_title: string;
    borrower_name: string | null;
    status: string;
    covenant_count: number;
    critical_count: number;
}

export interface PredictionResult {
    predicted_breach_date: string;
    days_until_breach: number;
    confidence: number;
    current_trajectory: string;
    predicted_value_at_breach: number;
}

export interface PortfolioValueResponse {
    current_value: number;
    previous_value: number;
    change_percentage: number;
    change_amount: number;
}

export interface PortfolioTrendsResponse {
    months: string[];
    current_period: number[];
    previous_period: number[];
}

export interface CovenantTrendsResponse {
    compliant_change: number;
    warning_change: number;
    breach_change: number;
}
