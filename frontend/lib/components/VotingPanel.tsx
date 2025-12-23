'use client';

import { useState, useEffect } from 'react';
import { Vote, CheckCircle, XCircle, AlertCircle, Users, Clock } from 'lucide-react';

interface VoteResult {
    agent: string;
    vote: 'APPROVE' | 'REJECT' | 'ABSTAIN';
    score: number;
    reasoning: string[];
    timestamp: string;
}

interface Proposal {
    proposal_id: string;
    title: string;
    description: string;
    cost: number;
    risk_level: string;
    status: 'pending' | 'approved' | 'rejected' | 'escalated';
    votes: VoteResult[];
    final_score: number | null;
    threshold: number;
    created_at: string;
    resolved_at: string | null;
}

interface VotingPanelProps {
    proposal: Proposal;
    onClose?: () => void;
    className?: string;
}

const AGENT_COLORS: Record<string, string> = {
    athena: 'text-purple-400',
    hephaestus: 'text-orange-400',
    hermes: 'text-blue-400',
    nur_prometheus: 'text-yellow-400',
    aegis: 'text-red-400',
};

const AGENT_ICONS: Record<string, string> = {
    athena: '🦉',
    hephaestus: '🔨',
    hermes: '📨',
    nur_prometheus: '📊',
    aegis: '🛡️',
};

export function VotingPanel({ proposal, onClose, className = '' }: VotingPanelProps) {
    const [isExpanded, setIsExpanded] = useState(true);

    const getStatusIcon = () => {
        switch (proposal.status) {
            case 'approved':
                return <CheckCircle className="text-emerald-400" size={20} />;
            case 'rejected':
                return <XCircle className="text-red-400" size={20} />;
            case 'escalated':
                return <AlertCircle className="text-yellow-400" size={20} />;
            default:
                return <Clock className="text-blue-400 animate-pulse" size={20} />;
        }
    };

    const getVoteIcon = (vote: string) => {
        switch (vote) {
            case 'APPROVE':
                return <CheckCircle className="text-emerald-400" size={16} />;
            case 'REJECT':
                return <XCircle className="text-red-400" size={16} />;
            default:
                return <AlertCircle className="text-slate-400" size={16} />;
        }
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'low':
                return 'text-emerald-400 bg-emerald-400/10';
            case 'medium':
                return 'text-yellow-400 bg-yellow-400/10';
            case 'high':
                return 'text-orange-400 bg-orange-400/10';
            case 'critical':
                return 'text-red-400 bg-red-400/10';
            default:
                return 'text-slate-400 bg-slate-400/10';
        }
    };

    const approveCount = proposal.votes.filter(v => v.vote === 'APPROVE').length;
    const rejectCount = proposal.votes.filter(v => v.vote === 'REJECT').length;
    const abstainCount = proposal.votes.filter(v => v.vote === 'ABSTAIN').length;

    return (
        <div className={`bg-slate-800/80 border border-slate-700 rounded-lg overflow-hidden ${className}`}>
            {/* Header */}
            <div 
                className="p-3 flex items-center justify-between cursor-pointer hover:bg-slate-700/50 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-2">
                    <Vote size={18} className="text-emerald-400" />
                    <span className="font-medium text-sm">Pentarchy Vote</span>
                    {getStatusIcon()}
                    <span className={`text-xs px-2 py-0.5 rounded ${getRiskColor(proposal.risk_level)}`}>
                        {proposal.risk_level.toUpperCase()}
                    </span>
                </div>
                <div className="flex items-center gap-3 text-xs">
                    <span className="text-emerald-400">{approveCount} ✓</span>
                    <span className="text-red-400">{rejectCount} ✗</span>
                    <span className="text-slate-400">{abstainCount} −</span>
                    {proposal.final_score !== null && (
                        <span className="text-blue-400">
                            Score: {proposal.final_score.toFixed(2)}/{proposal.threshold.toFixed(1)}
                        </span>
                    )}
                </div>
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="p-3 pt-0 space-y-3">
                    {/* Proposal Info */}
                    <div className="text-xs text-slate-400 border-t border-slate-700 pt-3">
                        <div className="font-medium text-slate-300 mb-1">{proposal.title}</div>
                        <div className="text-slate-500 truncate">{proposal.description}</div>
                        <div className="mt-1 flex gap-4">
                            <span>Cost: <span className="text-emerald-400">${proposal.cost.toFixed(2)}</span></span>
                            <span>ID: <span className="text-slate-500">{proposal.proposal_id.slice(0, 8)}</span></span>
                        </div>
                    </div>

                    {/* Vote Grid */}
                    <div className="grid grid-cols-5 gap-1">
                        {proposal.votes.map((vote) => (
                            <div 
                                key={vote.agent}
                                className="p-2 bg-slate-900/50 rounded text-center"
                                title={vote.reasoning.join('\n')}
                            >
                                <div className="text-lg mb-1">{AGENT_ICONS[vote.agent] || '🤖'}</div>
                                <div className={`text-xs font-medium ${AGENT_COLORS[vote.agent] || 'text-slate-300'}`}>
                                    {vote.agent.split('_')[0]}
                                </div>
                                <div className="flex justify-center mt-1">
                                    {getVoteIcon(vote.vote)}
                                </div>
                                <div className="text-xs text-slate-500 mt-1">
                                    {vote.score.toFixed(1)}
                                </div>
                            </div>
                        ))}
                        
                        {/* Placeholder for pending votes */}
                        {Array.from({ length: Math.max(0, 5 - proposal.votes.length) }).map((_, i) => (
                            <div 
                                key={`pending-${i}`}
                                className="p-2 bg-slate-900/30 rounded text-center opacity-50"
                            >
                                <div className="text-lg mb-1">⏳</div>
                                <div className="text-xs text-slate-500">Pending</div>
                            </div>
                        ))}
                    </div>

                    {/* Status Bar */}
                    <div className="flex items-center justify-between text-xs border-t border-slate-700 pt-2">
                        <div className="flex items-center gap-2">
                            <Users size={14} className="text-slate-400" />
                            <span className="text-slate-400">
                                {proposal.votes.length}/5 votes cast
                            </span>
                        </div>
                        <div className={`px-2 py-1 rounded font-medium ${
                            proposal.status === 'approved' ? 'bg-emerald-400/20 text-emerald-400' :
                            proposal.status === 'rejected' ? 'bg-red-400/20 text-red-400' :
                            proposal.status === 'escalated' ? 'bg-yellow-400/20 text-yellow-400' :
                            'bg-blue-400/20 text-blue-400'
                        }`}>
                            {proposal.status.toUpperCase()}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default VotingPanel;
