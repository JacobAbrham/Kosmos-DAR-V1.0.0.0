"use client";

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage, triggerVote, ChatResponse, VoteResponse } from '@/lib/api';
import { Send, Bot, User, Activity, Vote } from 'lucide-react';

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    metadata?: any;
}

export default function Home() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { role: 'system', content: 'System initialized. Connected to Zeus Orchestrator.' }
    ]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setLoading(true);

        try {
            // Check for special commands
            if (userMsg.startsWith('/vote')) {
                // Mock parsing: /vote prop-1 50 "desc"
                const parts = userMsg.split(' ');
                const propId = parts[1] || `prop-${Date.now()}`;
                const cost = parseFloat(parts[2]) || 100;
                const desc = parts.slice(3).join(' ') || "Manual vote trigger";
                
                setMessages(prev => [...prev, { role: 'system', content: `Initiating Pentarchy Vote for ${propId} ($${cost})...` }]);
                
                const result = await triggerVote(propId, cost, desc);
                
                setMessages(prev => [...prev, { 
                    role: 'assistant', 
                    content: `Vote Outcome: **${result.outcome}**\n\nReasoning:\n${result.reasoning.map(r => `- ${r}`).join('\n')}`,
                    metadata: result
                }]);
            } else {
                // Normal Chat
                const response = await sendChatMessage(userMsg);
                setMessages(prev => [...prev, { 
                    role: 'assistant', 
                    content: response.response,
                    metadata: response
                }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, { role: 'system', content: `Error: ${error}` }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full max-w-4xl mx-auto w-full p-4">
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex items-start max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`p-2 rounded-full mx-2 ${
                                msg.role === 'user' ? 'bg-blue-600' : 
                                msg.role === 'system' ? 'bg-slate-700' : 'bg-emerald-600'
                            }`}>
                                {msg.role === 'user' ? <User size={16} /> : 
                                 msg.role === 'system' ? <Activity size={16} /> : <Bot size={16} />}
                            </div>
                            <div className={`p-3 rounded-lg ${
                                msg.role === 'user' ? 'bg-blue-600/20 border border-blue-500/30' : 
                                msg.role === 'system' ? 'text-slate-400 text-sm italic' : 
                                'bg-slate-800 border border-slate-700'
                            }`}>
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                                {msg.metadata && msg.role === 'assistant' && (
                                    <div className="mt-2 pt-2 border-t border-slate-700/50 text-xs text-slate-500 flex gap-2">
                                        <span>Agents: {msg.metadata.agents_used?.join(', ') || 'Zeus'}</span>
                                        <span>•</span>
                                        <span>{msg.metadata.metadata?.processing_time_ms}ms</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Message Zeus or type /vote [id] [cost] [desc]..."
                    className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                />
                <button 
                    type="submit" 
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50 transition-colors"
                >
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
}
