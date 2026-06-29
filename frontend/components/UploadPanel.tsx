'use client';
import { useState, useRef } from 'react';
import {
	Upload,
	FileText,
	CheckCircle,
	AlertCircle,
	Loader,
} from 'lucide-react';
import { ingestDocument, IngestResponse } from '@/lib/api';

interface UploadedDoc {
	filename: string;
	chunks: number;
	status: 'success' | 'error';
	message?: string;
}

export default function UploadPanel() {
	const [dragging, setDragging] = useState(false);
	const [uploading, setUploading] = useState(false);
	const [docs, setDocs] = useState<UploadedDoc[]>([]);
	const [error, setError] = useState<string | null>(null);
	const inputRef = useRef<HTMLInputElement>(null);

	const handleFile = async (file: File) => {
		if (!file.name.endsWith('.pdf')) {
			setError('Only PDF files are supported.');
			return;
		}
		if (file.size > 10 * 1024 * 1024) {
			setError('File must be under 10MB.');
			return;
		}

		setError(null);
		setUploading(true);

		try {
			const res: IngestResponse = await ingestDocument(file);
			setDocs((prev) => [
				{
					filename: res.filename,
					chunks: res.chunks_stored,
					status: 'success',
				},
				...prev,
			]);
		} catch (e: unknown) {
			const msg = e instanceof Error ? e.message : 'Upload failed';
			setDocs((prev) => [
				{ filename: file.name, chunks: 0, status: 'error', message: msg },
				...prev,
			]);
		} finally {
			setUploading(false);
		}
	};

	const onDrop = (e: React.DragEvent) => {
		e.preventDefault();
		setDragging(false);
		const file = e.dataTransfer.files[0];
		if (file) handleFile(file);
	};

	return (
		<div className='flex flex-col gap-4'>
			<div
				onDragOver={(e) => {
					e.preventDefault();
					setDragging(true);
				}}
				onDragLeave={() => setDragging(false)}
				onDrop={onDrop}
				onClick={() => inputRef.current?.click()}
				className={`
          border-2 border-dashed rounded-xl p-6 text-center cursor-pointer
          transition-all duration-200 select-none
          ${
						dragging
							? 'border-[var(--accent)] bg-[var(--accent)]/5'
							: 'border-theme hover:border-[var(--accent)]/50 bg-elevated'
					}
          ${uploading ? 'pointer-events-none opacity-60' : ''}
        `}>
				<input
					ref={inputRef}
					type='file'
					accept='.pdf'
					className='hidden'
					onChange={(e) => {
						const file = e.target.files?.[0];
						if (file) handleFile(file);
						e.target.value = '';
					}}
				/>
				{uploading ? (
					<div className='flex flex-col items-center gap-2'>
						<Loader size={24} className='accent animate-spin' />
						<p className='text-sm text-secondary'>Processing document...</p>
					</div>
				) : (
					<div className='flex flex-col items-center gap-2'>
						<Upload size={24} className='text-muted' />
						<p className='text-sm font-medium text-secondary'>
							Drop a PDF here or click to browse
						</p>
						<p className='text-xs text-muted'>PDF only · Max 10MB</p>
					</div>
				)}
			</div>

			{error && (
				<div className='flex items-start gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 animate-fade-in'>
					<AlertCircle size={14} className='text-red-400 mt-0.5 shrink-0' />
					<p className='text-xs text-red-400'>{error}</p>
				</div>
			)}

			{docs.length > 0 && (
				<div className='flex flex-col gap-2'>
					<p className='text-xs font-medium text-muted uppercase tracking-wider'>
						Ingested Documents
					</p>
					{docs.map((doc, i) => (
						<div
							key={i}
							className='flex items-start gap-3 p-3 rounded-lg bg-elevated border border-theme animate-slide-up'>
							{doc.status === 'success' ? (
								<CheckCircle
									size={14}
									className='text-emerald-400 mt-0.5 shrink-0'
								/>
							) : (
								<AlertCircle
									size={14}
									className='text-red-400 mt-0.5 shrink-0'
								/>
							)}
							<div className='min-w-0 flex-1'>
								<p className='text-xs font-medium text-primary truncate'>
									{doc.filename}
								</p>
								<p className='text-xs text-muted'>
									{doc.status === 'success'
										? `${doc.chunks} chunks stored`
										: doc.message}
								</p>
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
}
