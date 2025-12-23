/**
 * React hooks for KOSMOS API integration
 */
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import {
    api,
    Agent,
    Conversation,
    ConversationDetail,
    Proposal,
    ProposalSummary,
    ChatResponse,
    VotingStats,
    VotingThresholds,
} from './kosmos-client';

// ============ useChat Hook ============

interface UseChatOptions {
    conversationId?: string;
    agent?: string;
    onError?: (error: Error) => void;
}

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    agent?: string;
    tokens?: number;
    timestamp: Date;
}

export function useChat(options: UseChatOptions = {}) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [conversationId, setConversationId] = useState(options.conversationId);

    const sendMessage = useCallback(async (content: string) => {
        setIsLoading(true);
        setError(null);

        // Add user message
        const userMsg: ChatMessage = {
            id: `user-${Date.now()}`,
            role: 'user',
            content,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMsg]);

        try {
            const response = await api.sendMessage({
                content,
                conversation_id: conversationId,
                agent: options.agent,
            });

            setConversationId(response.conversation_id);

            const assistantMsg: ChatMessage = {
                id: response.message_id,
                role: 'assistant',
                content: response.content,
                agent: response.agent,
                tokens: response.tokens_used,
                timestamp: new Date(response.created_at),
            };
            setMessages(prev => [...prev, assistantMsg]);

            return response;
        } catch (err) {
            const error = err instanceof Error ? err : new Error('Unknown error');
            setError(error);
            options.onError?.(error);
            throw error;
        } finally {
            setIsLoading(false);
        }
    }, [conversationId, options.agent, options.onError]);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setConversationId(undefined);
    }, []);

    return {
        messages,
        sendMessage,
        isLoading,
        error,
        conversationId,
        clearMessages,
    };
}

// ============ useAgents Hook ============

interface UseAgentsOptions {
    domain?: string;
    pentarchyOnly?: boolean;
}

export function useAgents(options: UseAgentsOptions = {}) {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let mounted = true;

        async function fetchAgents() {
            try {
                const data = await api.listAgents(options);
                if (mounted) {
                    setAgents(data);
                    setError(null);
                }
            } catch (err) {
                if (mounted) {
                    setError(err instanceof Error ? err : new Error('Failed to fetch agents'));
                }
            } finally {
                if (mounted) {
                    setIsLoading(false);
                }
            }
        }

        fetchAgents();

        return () => {
            mounted = false;
        };
    }, [options.domain, options.pentarchyOnly]);

    const queryAgent = useCallback(async (agentId: string, query: string) => {
        return api.queryAgent(agentId, query);
    }, []);

    return { agents, isLoading, error, queryAgent };
}

// ============ useProposals Hook ============

interface UseProposalsOptions {
    status?: string;
    autoRefresh?: boolean;
    refreshInterval?: number;
}

export function useProposals(options: UseProposalsOptions = {}) {
    const [proposals, setProposals] = useState<ProposalSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchProposals = useCallback(async () => {
        try {
            const data = await api.listProposals({ status: options.status });
            setProposals(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to fetch proposals'));
        } finally {
            setIsLoading(false);
        }
    }, [options.status]);

    useEffect(() => {
        fetchProposals();

        if (options.autoRefresh) {
            const interval = setInterval(fetchProposals, options.refreshInterval || 5000);
            return () => clearInterval(interval);
        }
    }, [fetchProposals, options.autoRefresh, options.refreshInterval]);

    const createProposal = useCallback(async (
        title: string,
        description: string,
        cost: number,
        riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'medium'
    ) => {
        const proposal = await api.createProposal({
            title,
            description,
            cost,
            risk_level: riskLevel,
        });
        await fetchProposals();
        return proposal;
    }, [fetchProposals]);

    return { proposals, isLoading, error, createProposal, refresh: fetchProposals };
}

// ============ useConversations Hook ============

export function useConversations() {
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const fetchConversations = useCallback(async () => {
        try {
            const data = await api.listConversations();
            setConversations(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to fetch conversations'));
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchConversations();
    }, [fetchConversations]);

    const deleteConversation = useCallback(async (id: string) => {
        await api.deleteConversation(id);
        await fetchConversations();
    }, [fetchConversations]);

    return { conversations, isLoading, error, refresh: fetchConversations, deleteConversation };
}

// ============ useVotingStats Hook ============

export function useVotingStats() {
    const [stats, setStats] = useState<VotingStats | null>(null);
    const [thresholds, setThresholds] = useState<VotingThresholds | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [statsData, thresholdsData] = await Promise.all([
                    api.getVotingStats(),
                    api.getVotingThresholds(),
                ]);
                setStats(statsData);
                setThresholds(thresholdsData);
            } catch (err) {
                console.error('Failed to fetch voting stats:', err);
            } finally {
                setIsLoading(false);
            }
        }

        fetchData();
    }, []);

    return { stats, thresholds, isLoading };
}

// ============ useActiveProposal Hook ============

export function useActiveProposal(proposalId: string | null) {
    const [proposal, setProposal] = useState<Proposal | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    const fetchProposal = useCallback(async () => {
        if (!proposalId) {
            setProposal(null);
            return;
        }

        try {
            const data = await api.getProposal(proposalId);
            setProposal(data);
            
            // Stop polling if resolved
            if (data.status !== 'pending' && intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        } catch (err) {
            console.error('Failed to fetch proposal:', err);
        } finally {
            setIsLoading(false);
        }
    }, [proposalId]);

    useEffect(() => {
        if (!proposalId) {
            setProposal(null);
            return;
        }

        setIsLoading(true);
        fetchProposal();

        // Poll every 2 seconds while pending
        intervalRef.current = setInterval(fetchProposal, 2000);

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [proposalId, fetchProposal]);

    return { proposal, isLoading, refresh: fetchProposal };
}

// ============ useWebSocketChat Hook ============

export function useWebSocketChat(conversationId: string) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const ws = api.connectWebSocket(conversationId, (data) => {
            if (data.type === 'message') {
                setMessages(prev => [...prev, {
                    id: data.id,
                    role: data.role,
                    content: data.content,
                    agent: data.agent,
                    timestamp: new Date(data.timestamp),
                }]);
            } else if (data.type === 'stream') {
                setMessages(prev => {
                    const last = prev[prev.length - 1];
                    if (last && last.id === data.id) {
                        return [...prev.slice(0, -1), { ...last, content: last.content + data.chunk }];
                    }
                    return prev;
                });
            }
        });

        ws.onopen = () => setIsConnected(true);
        ws.onclose = () => setIsConnected(false);
        wsRef.current = ws;

        return () => {
            ws.close();
        };
    }, [conversationId]);

    const sendMessage = useCallback((content: string) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'message', content }));
            setMessages(prev => [...prev, {
                id: `user-${Date.now()}`,
                role: 'user',
                content,
                timestamp: new Date(),
            }]);
        }
    }, []);

    return { messages, sendMessage, isConnected };
}
