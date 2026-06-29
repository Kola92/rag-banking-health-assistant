'use client';
import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText } from 'lucide-react';
import { ChunkResult } from '@/lib/api';

interface SourceCardProps {
	chunk: ChunkResult;
	index: number;
}

export default function SourceCard({ chunk, index }: SourceCardProps) {
	const [expanded, setExpanded] = useState(false);
	const scorePercent = Math.round(chunk.score * 100);
	const scoreColor =
		chunk.score >= 0.7
			? 'text-emerald-400 bg-emerald-400/10'
			: chunk.score >= 0.5
				? 'text-yellow-400 bg-yellow-400/10'
				: 'text-slate-400 bg-slate-400/10';

	return (
		<div className='rounded-lg border border-theme bg-elevated overflow-hidden animate-slide-up'>
			<button
				onClick={() => setExpanded(!expanded)}
				className='w-full flex items-center gap-3 p-3 hover:bg-[var(--bg-border)]/40 transition-colors text-left'>
				<FileText size={13} className='text-muted shrink-0' />
				<div className='flex-1 min-w-0'>
					<p className='text-xs font-medium text-secondary truncate'>
						{chunk.source}
					</p>
					<p className='text-xs text-muted'>Chunk {index + 1}</p>
				</div>
				<span
					className={`text-xs font-mono px-2 py-0.5 rounded-full shrink-0 ${scoreColor}`}>
					{scorePercent}%
				</span>
				{expanded ? (
					<ChevronUp size={12} className='text-muted shrink-0' />
				) : (
					<ChevronDown size={12} className='text-muted shrink-0' />
				)}
			</button>

			{expanded && (
				<div className='px-3 pb-3 border-t border-theme'>
					<p className='text-xs font-mono text-secondary leading-relaxed pt-3 whitespace-pre-wrap'>
						{chunk.text}
					</p>
				</div>
			)}
		</div>
	);
}
