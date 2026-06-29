'use client';
import { useState, useRef, useEffect } from 'react';
import { Send, FileSearch, Loader, Moon, Sun } from 'lucide-react';
import { queryDocuments } from '@/lib/api';
import ChatMessage, { Message } from '@/components/ChatMessage';
import UploadPanel from '@/components/UploadPanel';
import ThemeToggle from '@/components/ThemeToggle';

const SUGGESTED = [
	'What are the consumer protection rights of bank customers in Nigeria?',
	'What are the data localisation requirements for Nigerian payment systems?',
	'What actions should banks take regarding OFAC designations?',
];

export default function Home() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [input, setInput] = useState('');
	const [loading, setLoading] = useState(false);
	const [sidebarOpen, setSidebarOpen] = useState(true);
	const bottomRef = useRef<HTMLDivElement>(null);
	const textareaRef = useRef<HTMLTextAreaElement>(null);

	useEffect(() => {
		bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
	}, [messages]);

	const handleAutoResize = () => {
		const el = textareaRef.current;
		if (!el) return;
		el.style.height = 'auto';
		el.style.height = Math.min(el.scrollHeight, 160) + 'px';
	};

	const sendMessage = async (question?: string) => {
		const q = (question ?? input).trim();
		if (!q || loading) return;

		const userMsg: Message = { role: 'user', content: q };
		setMessages((prev) => [...prev, userMsg]);
		setInput('');
		if (textareaRef.current) textareaRef.current.style.height = 'auto';
		setLoading(true);

		try {
			const res = await queryDocuments(q);
			setMessages((prev) => [
				...prev,
				{ role: 'assistant', content: res.answer, response: res },
			]);
		} catch (e: unknown) {
			const msg = e instanceof Error ? e.message : 'Something went wrong';
			setMessages((prev) => [
				...prev,
				{ role: 'assistant', content: msg, error: true },
			]);
		} finally {
			setLoading(false);
		}
	};

	const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	};

	return (
		<div className='h-screen flex flex-col bg-primary overflow-hidden'>
			{/* Header */}
			<header className='shrink-0 flex items-center justify-between px-4 py-3 border-b border-theme bg-surface'>
				<div className='flex items-center gap-3'>
					<div className='w-8 h-8 rounded-lg bg-[var(--accent)]/10 border border-[var(--accent)]/20 flex items-center justify-center'>
						<FileSearch size={16} className='accent' />
					</div>
					<div>
						<h1 className='text-sm font-semibold text-primary leading-none'>
							RAG Document Assistant
						</h1>
						<p className='text-xs text-muted leading-none mt-0.5'>
							CBN Banking & Health Documents
						</p>
					</div>
				</div>
				<div className='flex items-center gap-2'>
					<button
						onClick={() => setSidebarOpen(!sidebarOpen)}
						className='hidden md:flex text-xs text-muted hover:text-secondary transition-colors px-2 py-1 rounded border border-theme'>
						{sidebarOpen ? 'Hide' : 'Show'} uploads
					</button>
					<ThemeToggle />
				</div>
			</header>

			{/* Body */}
			<div className='flex-1 flex overflow-hidden'>
				{/* Chat area */}
				<main className='flex-1 flex flex-col overflow-hidden'>
					{/* Messages */}
					<div className='flex-1 overflow-y-auto px-4 py-6'>
						{messages.length === 0 ? (
							<div className='h-full flex flex-col items-center justify-center gap-6 animate-fade-in'>
								<div className='text-center'>
									<div className='w-14 h-14 rounded-2xl bg-[var(--accent)]/10 border border-[var(--accent)]/20 flex items-center justify-center mx-auto mb-4'>
										<FileSearch size={24} className='accent' />
									</div>
									<h2 className='text-lg font-semibold text-primary mb-1'>
										Ask about your documents
									</h2>
									<p className='text-sm text-muted max-w-sm'>
										Query CBN regulations, consumer protection rules, banking
										circulars, and health insurance guidelines.
									</p>
								</div>
								<div className='flex flex-col gap-2 w-full max-w-md'>
									{SUGGESTED.map((q, i) => (
										<button
											key={i}
											onClick={() => sendMessage(q)}
											className='text-left text-sm text-secondary px-4 py-3 rounded-xl border border-theme bg-surface hover:border-[var(--accent)]/40 hover:text-primary transition-all duration-150'>
											{q}
										</button>
									))}
								</div>
							</div>
						) : (
							<div className='max-w-3xl mx-auto flex flex-col gap-6'>
								{messages.map((msg, i) => (
									<ChatMessage key={i} message={msg} />
								))}
								{loading && (
									<div className='flex gap-3 animate-fade-in'>
										<div className='w-7 h-7 rounded-full bg-[var(--accent)]/10 border border-[var(--accent)]/20 flex items-center justify-center shrink-0 mt-1'>
											<Loader size={14} className='accent animate-spin' />
										</div>
										<div className='px-4 py-3 rounded-2xl rounded-tl-sm bg-surface border border-theme'>
											<div className='flex gap-1 items-center h-5'>
												<span className='w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-bounce [animation-delay:0ms]' />
												<span className='w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-bounce [animation-delay:150ms]' />
												<span className='w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-bounce [animation-delay:300ms]' />
											</div>
										</div>
									</div>
								)}
								<div ref={bottomRef} />
							</div>
						)}
					</div>

					{/* Input */}
					<div className='shrink-0 px-4 pb-4 pt-2 border-t border-theme bg-surface'>
						<div className='max-w-3xl mx-auto'>
							<div className='flex items-end gap-2 p-2 rounded-xl border border-theme bg-elevated focus-within:border-[var(--accent)]/50 transition-colors'>
								<textarea
									ref={textareaRef}
									value={input}
									onChange={(e) => {
										setInput(e.target.value);
										handleAutoResize();
									}}
									onKeyDown={handleKeyDown}
									placeholder='Ask a question about the documents... (Enter to send, Shift+Enter for new line)'
									rows={1}
									className='flex-1 bg-transparent text-sm text-primary placeholder:text-muted resize-none outline-none px-2 py-1.5 max-h-40'
								/>
								<button
									onClick={() => sendMessage()}
									disabled={!input.trim() || loading}
									className='shrink-0 w-8 h-8 rounded-lg bg-[var(--accent)] flex items-center justify-center hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity'>
									<Send size={14} className='text-white' />
								</button>
							</div>
							<p className='text-[10px] text-muted text-center mt-2'>
								Answers are grounded in ingested documents only — not general AI
								knowledge.
							</p>
						</div>
					</div>
				</main>

				{/* Sidebar */}
				{sidebarOpen && (
					<aside className='hidden md:flex w-72 shrink-0 flex-col border-l border-theme bg-surface overflow-y-auto'>
						<div className='p-4 border-b border-theme'>
							<h2 className='text-xs font-semibold text-primary uppercase tracking-wider'>
								Document Upload
							</h2>
							<p className='text-xs text-muted mt-1'>
								Add PDFs to expand the knowledge base
							</p>
						</div>
						<div className='p-4 flex-1'>
							<UploadPanel />
						</div>
					</aside>
				)}
			</div>
		</div>
	);
}
