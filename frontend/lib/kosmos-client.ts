/**
 * KOSMOS API Client - Full integration with backend services
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============ Types ============

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    agent?: string;
    model?: string;
    tokens_used?: number;
    created_at: string;
}

export interface Conversation {
    conversation_id: string;
    title: string | null;
    message_count: number;
    created_at: string;
    updated_at: string;
}

export interface ConversationDetail {
    conversation_id: string;
    title: string | null;
    messages: Message[];
    created_at: string;
}

export interface ChatRequest {
    content: string;
    conversation_id?: string;
    agent?: string;
    model?: string;
}

export interface ChatResponse {
    conversation_id: string;
    message_id: string;
    content: string;
    role: string;
    agent?: string;
    model?: string;
    tokens_used?: number;
    created_at: string;
}

export interface Agent {
    id: string;
    name: string;
    description: string;
    domain: string;
    capabilities: string[];
    pentarchy: boolean;
    status: string;
}

export interface AgentQueryResponse {
    agent: string;
    response: string;
    tool_calls?: any[];
    processing_time_ms: number;
    timestamp: string;
}

export interface Proposal {
    proposal_id: string;
    title: string;
    description: string;
    cost: number;
    risk_level: string;
    status: string;
    votes: Vote[];
    final_score: number | null;
    threshold: number;
    created_at: string;
    resolved_at: string | null;
}

export interface Vote {
    agent: string;
    vote: string;
    score: number;
    reasoning: string[];
    timestamp: string;
}

export interface ProposalRequest {
    title: string;
    description: string;
    cost: number;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    context?: Record<string, any>;
    auto_execute?: boolean;
}

export interface ProposalSummary {
    proposal_id: string;
    title: string;
    status: string;
    final_score: number | null;
    vote_count: number;
    created_at: string;
}

export interface VotingStats {
    total_proposals: number;
    by_status: Record<string, number>;
    average_score: number;
    total_votes: number;
}

export interface VotingThresholds {
    thresholds: Record<string, number>;
    max_score: number;
    pentarchy_agents: string[];
    description: string;
}

// ============ API Client ============

class KosmosAPI {
    private baseUrl: string;
    private token: string | null = null;

    constructor(baseUrl: string = API_BASE) {
        this.baseUrl = baseUrl;
    }

    setToken(token: string) {
        this.token = token;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...options.headers as Record<string, string>,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || `API Error: ${response.status}`);
        }

        return response.json();
    }

    // ============ Health ============

    async health(): Promise<{ status: string; version: string }> {
        return this.request('/health');
    }

    async ready(): Promise<{ status: string; dependencies: Record<string, any> }> {
        return this.request('/ready');
    }

    // ============ Chat ============

    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        return this.request('/api/v1/chat/message', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async listConversations(limit = 20, offset = 0): Promise<Conversation[]> {
        return this.request(`/api/v1/chat/conversations?limit=${limit}&offset=${offset}`);
    }

    async getConversation(conversationId: string): Promise<ConversationDetail> {
        return this.request(`/api/v1/chat/conversations/${conversationId}`);
    }

    async deleteConversation(conversationId: string): Promise<void> {
        return this.request(`/api/v1/chat/conversations/${conversationId}`, {
            method: 'DELETE',
        });
    }

    async setConversationTitle(conversationId: string, title: string): Promise<void> {
        return this.request(`/api/v1/chat/conversations/${conversationId}/title?title=${encodeURIComponent(title)}`, {
            method: 'POST',
        });
    }

    // ============ Agents ============

    async listAgents(options?: { domain?: string; pentarchyOnly?: boolean }): Promise<Agent[]> {
        const params = new URLSearchParams();
        if (options?.domain) params.set('domain', options.domain);
        if (options?.pentarchyOnly) params.set('pentarchy_only', 'true');
        const query = params.toString() ? `?${params.toString()}` : '';
        return this.request(`/api/v1/agents${query}`);
    }

    async getAgent(agentId: string): Promise<Agent> {
        return this.request(`/api/v1/agents/${agentId}`);
    }

    async queryAgent(agentId: string, query: string, conversationId?: string): Promise<AgentQueryResponse> {
        return this.request(`/api/v1/agents/${agentId}/query`, {
            method: 'POST',
            body: JSON.stringify({ query, conversation_id: conversationId }),
        });
    }

    async getAgentCapabilities(agentId: string): Promise<{ agent: string; capabilities: string[]; tools: any[] }> {
        return this.request(`/api/v1/agents/${agentId}/capabilities`);
    }

    // ============ Governance / Voting ============

    async createProposal(request: ProposalRequest): Promise<Proposal> {
        return this.request('/api/v1/votes/proposals', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async listProposals(options?: { status?: string; limit?: number; offset?: number }): Promise<ProposalSummary[]> {
        const params = new URLSearchParams();
        if (options?.status) params.set('status', options.status);
        if (options?.limit) params.set('limit', options.limit.toString());
        if (options?.offset) params.set('offset', options.offset.toString());
        const query = params.toString() ? `?${params.toString()}` : '';
        return this.request(`/api/v1/votes/proposals${query}`);
    }

    async getProposal(proposalId: string): Promise<Proposal> {
        return this.request(`/api/v1/votes/proposals/${proposalId}`);
    }

    async resolveProposal(proposalId: string): Promise<Proposal> {
        return this.request(`/api/v1/votes/proposals/${proposalId}/resolve`, {
            method: 'POST',
        });
    }

    async getVotingThresholds(): Promise<VotingThresholds> {
        return this.request('/api/v1/votes/thresholds');
    }

    async getVotingStats(): Promise<VotingStats> {
        return this.request('/api/v1/votes/stats');
    }

    // ============ WebSocket Chat ============

    connectWebSocket(conversationId: string, onMessage: (msg: any) => void): WebSocket {
        const wsUrl = this.baseUrl.replace('http', 'ws');
        const ws = new WebSocket(`${wsUrl}/api/v1/chat/ws/${conversationId}`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);
        };

        return ws;
    }
}

// Export singleton instance
export const api = new KosmosAPI();

// Legacy exports for backward compatibility
export async function sendChatMessage(message: string, conversationId: string = "default"): Promise<any> {
    const response = await api.sendMessage({ content: message, conversation_id: conversationId });
    return {
        response: response.content,
        agents_used: response.agent ? [response.agent] : ['zeus'],
        confidence: 0.95,
        follow_up_suggestions: [],
        metadata: {
            processing_time_ms: 0,
            token_usage: { total_tokens: response.tokens_used || 0 },
            trace_id: response.message_id,
            conversation_turn: 1,
        },
    };
}

export async function triggerVote(proposalId: string, cost: number, description: string): Promise<any> {
    const proposal = await api.createProposal({
        title: proposalId,
        description,
        cost,
        risk_level: cost > 1000 ? 'high' : cost > 100 ? 'medium' : 'low',
    });

    // Poll for voting to complete
    const maxAttempts = 10;
    const interval = 1000; // 1 second
    let result = proposal;

    for (let i = 0; i < maxAttempts; i++) {
        result = await api.getProposal(proposal.proposal_id);
        if (result.status !== 'pending') {
            break;
        }
        await new Promise(resolve => setTimeout(resolve, interval));
    }

    return {
        proposal_id: result.proposal_id,
        outcome: result.status,
        votes: Object.fromEntries(result.votes.map(v => [v.agent, v.vote])),
        reasoning: result.votes.flatMap(v => v.reasoning),
    };
}
