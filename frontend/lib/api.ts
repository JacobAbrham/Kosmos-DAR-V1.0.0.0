export interface ChatResponse {
    response: string;
    agents_used: string[];
    confidence: number;
    follow_up_suggestions: string[];
    metadata: {
        processing_time_ms: number;
        token_usage: {
            prompt_tokens: number;
            completion_tokens: number;
            total_tokens: number;
        };
        trace_id: string;
        conversation_turn: number;
    };
}

export interface VoteResponse {
    proposal_id: string;
    outcome: string;
    votes: Record<string, string>;
    reasoning: string[];
}

export async function sendChatMessage(message: string, conversationId: string = "default"): Promise<ChatResponse> {
    const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message,
            conversation_id: conversationId,
            user_id: "frontend-user"
        })
    });
    
    if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
    }
    
    return res.json();
}

export async function triggerVote(proposalId: string, cost: number, description: string): Promise<VoteResponse> {
    const res = await fetch('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            proposal_id: proposalId,
            cost,
            description
        })
    });

    if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
    }

    return res.json();
}
