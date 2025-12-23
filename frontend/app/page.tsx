"use client";

import { useState, useRef, useEffect } from 'react';
import { useChat, useAgents, useVotingStats, useActiveProposal } from '@/lib/hooks';
import { api, Agent } from '@/lib/kosmos-client';
import { Send, Bot, User, Activity, Vote, Zap } from 'lucide-react';
import VotingPanel from '@/lib/components/VotingPanel';

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    agent?: string;
    metadata?: any;
    proposalId?: string;
}

export default function Home() {
    const [input, setInput] = useState('');
    const [selectedAgent, setSelectedAgent] = useState<string | undefined>();
    const [activeProposalId, setActiveProposalId] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Use custom hooks
    const { messages: chatMessages, sendMessage, isLoading, conversationId } = useChat({
        onError: (err) => console.error('Chat error:', err),
    });
    const { agents } = useAgents({ pentarchyOnly: false });
    const { stats } = useVotingStats();
    const { proposal: activeProposal } = useActiveProposal(activeProposalId);

    const [systemMessages, setSystemMessages] = useState<Message[]>([
        { role: 'system', content: 'System initialized. Connected to KOSMOS API.' }
    ]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatMessages, systemMessages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = input;
        setInput('');

        try {
            // Check for special commands
            if (userMsg.startsWith('/vote')) {
                const parts = userMsg.split(' ');
                const title = parts.slice(1, 4).join(' ') || 'Manual Proposal';
                const cost = parseFloat(parts[4]) || 100;

                setSystemMessages(prev => [...prev, {
                    role: 'system',
                    content: `Initiating Pentarchy Vote: "${title}" ($${cost})...`
                }]);

                const result = await api.createProposal({
                    title,
                    description: userMsg,
                    cost,
                    risk_level: 'medium',
                });

                // Set active proposal to show voting panel
                setActiveProposalId(result.proposal_id);

                setSystemMessages(prev => [...prev, {
                    role: 'assistant',
                    content: `✅ Proposal created: ${result.proposal_id}\nStatus: ${result.status}\nScore: ${result.final_score?.toFixed(2) || 'pending'}`,
                    proposalId: result.proposal_id,
                }]);
            } else if (userMsg.startsWith('/agent')) {
                // Query specific agent
                const parts = userMsg.split(' ');
                const agentId = parts[1] || 'zeus';
                const query = parts.slice(2).join(' ') || 'Hello';

                setSystemMessages(prev => [...prev, {
                    role: 'system',
                    content: `Querying agent: ${agentId}...`
                }]);

                const response = await api.queryAgent(agentId, query);

                setSystemMessages(prev => [...prev, {
                    role: 'assistant',
                    agent: agentId,
                    content: response.response,
                }]);
            } else {
                // Normal Chat via hook
                await sendMessage(userMsg);
            }
        } catch (error) {
            setSystemMessages(prev => [...prev, {
                role: 'system',
                content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
            }]);
        }
    };

    // Combine all messages for display
    const allMessages: Message[] = [
        ...systemMessages,
        ...chatMessages.map(m => ({
            role: m.role,
            content: m.content,
            agent: m.agent,
            metadata: { tokens: m.tokens },
        })),
    ].sort((a, b) => 0); // Keep insertion order

    return (
        <div className="flex flex-col h-full max-w-4xl mx-auto w-full p-4">
            {/* Stats bar */}
            {stats && (
                <div className="mb-4 p-2 bg-slate-800/50 rounded-lg flex gap-4 text-sm text-slate-400">
                    <span className="flex items-center gap-1">
                        <Vote size={14} /> {stats.total_proposals} proposals
                    </span>
                    <span className="text-emerald-400">{stats.by_status['approved'] || 0} approved</span>
                    <span className="text-red-400">{stats.by_status['rejected'] || 0} rejected</span>
                    <span className="text-yellow-400">{stats.by_status['pending'] || 0} pending</span>
                </div>
            )}

            {/* Active Voting Panel */}
            {activeProposal && (
                <VotingPanel 
                    proposal={activeProposal} 
                    className="mb-4"
                    onClose={() => setActiveProposalId(null)}
                />
            )}

            {/* Agent selector */}
            <div className="mb-4 flex gap-2 overflow-x-auto pb-2">
                <button
                    onClick={() => setSelectedAgent(undefined)}
                    className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${!selectedAgent
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                        }`}
                >
                    <Zap size={14} className="inline mr-1" />
                    Auto
                </button>
                {agents.slice(0, 6).map((agent) => (
                    <button
                        key={agent.id}
                        onClick={() => setSelectedAgent(agent.id)}
                        className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${selectedAgent === agent.id
                            ? 'bg-emerald-600 text-white'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                            }`}
                    >
                        {agent.name}
                    </button>
                ))}
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800">
                {allMessages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex items-start max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`p-2 rounded-full mx-2 ${msg.role === 'user' ? 'bg-blue-600' :
                                msg.role === 'system' ? 'bg-slate-700' : 'bg-emerald-600'
                                }`}>
                                {msg.role === 'user' ? <User size={16} /> :
                                    msg.role === 'system' ? <Activity size={16} /> : <Bot size={16} />}
                            </div>
                            <div className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600/20 border border-blue-500/30' :
                                msg.role === 'system' ? 'text-slate-400 text-sm italic' :
                                    'bg-slate-800 border border-slate-700'
                                }`}>
                                {msg.agent && (
                                    <div className="text-xs text-emerald-400 mb-1 font-medium">
                                        {msg.agent.toUpperCase()}
                                    </div>
                                )}
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                                {msg.metadata?.tokens && (
                                    <div className="mt-2 pt-2 border-t border-slate-700/50 text-xs text-slate-500">
                                        {msg.metadata.tokens} tokens
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="flex items-center gap-2 p-3 bg-slate-800 rounded-lg text-slate-400">
                            <div className="animate-pulse">●</div>
                            <div className="animate-pulse delay-100">●</div>
                            <div className="animate-pulse delay-200">●</div>
                        </div>
                    </div>
                )}
            </div>

            <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={selectedAgent
                        ? `Ask ${selectedAgent}... or /vote, /agent`
                        : "Message KOSMOS or /vote, /agent..."
                    }
                    className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50 transition-colors"
                >
                    <Send size={20} />
                </button>
            </form>

            {conversationId && (
                <div className="mt-2 text-xs text-slate-500 text-center">
                    Conversation: {conversationId.slice(0, 8)}...
                </div>
            )}
        </div>
    );
}
