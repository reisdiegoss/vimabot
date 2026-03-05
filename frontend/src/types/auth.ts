export interface User {
    tenant_id: string;
    email: string;
    company_name: string;
    is_superadmin: boolean;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    tenant_id: string;
    email: string;
    company_name: string;
    is_superadmin: boolean;
}

export interface Tenant {
    id: string;
    company_name: string;
    owner_email: string;
    plan_type: 'free' | 'basic' | 'pro' | 'enterprise';
    status: 'active' | 'inactive' | 'suspended';
    subscription_due_date?: string;
    is_superadmin: boolean;
    created_at: string;
}
