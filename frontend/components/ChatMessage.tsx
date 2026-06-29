'use client';
import { useState } from 'react';
import { Bot, User, ChevronDown, ChevronUp } from 'lucide-react';
import { QueryResponse } from '@/lib/api';
import SourceCard from './SourceCard';

export interface Message {
	role: 'user' | 'assistant';
	content: string;
	response?: QueryResponse;
	error?: boolean;
}

export default function ChatMessage({ message }: { message: Message }) {
	const [showSources, setShowSources] = useState(false);
	const isUser = message.role === 'user';

	return (
		<div
			className={`flex gap-3 animate-slide-up ${isUser ? 'justify-end' : 'justify-start'}`}>
			{!isUser && (
				<div className='w-7 h-7 rounded-full bg-[var(--accent)]/10 border border-[var(--accent)]/20 flex items-center justify-center shrink-0 mt-1'>
					<Bot size={14} className='accent' />
				</div>
			)}

			<div
				className={`max-w-[80%] flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
				<div
					className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
						isUser
							? 'bg-[var(--accent)] text-white rounded-tr-sm'
							: message.error
								? 'bg-red-500/10 border border-red-500/20 text-red-400 rounded-tl-sm'
								: 'bg-surface border border-theme text-primary rounded-tl-sm'
					}`}>
					{message.content}
				</div>

				{message.response && message.response.chunks.length > 0 && (
					<div className='w-full'>
						<button
							onClick={() => setShowSources(!showSources)}
							className='flex items-center gap-1.5 text-xs text-muted hover:text-secondary transition-colors'>
							{showSources ? (
								<ChevronUp size={12} />
							) : (
								<ChevronDown size={12} />
							)}
							{showSources ? 'Hide' : 'Show'} {message.response.chunks.length}{' '}
							source
							{message.response.chunks.length !== 1 ? 's' : ''}
							<span className='font-mono text-[10px] opacity-60 ml-1'>
								· {message.response.model}
							</span>
						</button>

						{showSources && (
							<div className='flex flex-col gap-2 mt-2'>
								{message.response.chunks.map((chunk, i) => (
									<SourceCard key={i} chunk={chunk} index={i} />
								))}
							</div>
						)}
					</div>
				)}
			</div>

			{isUser && (
				<div className='w-7 h-7 rounded-full bg-elevated border border-theme flex items-center justify-center shrink-0 mt-1'>
					<User size={14} className='text-muted' />
				</div>
			)}
		</div>
	);
}
