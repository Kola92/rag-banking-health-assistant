const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChunkResult {
	text: string;
	source: string;
	score: number;
}

export interface QueryResponse {
	answer: string;
	sources: string[];
	chunks: ChunkResult[];
	model: string;
}

export interface IngestResponse {
	filename: string;
	chunks_stored: number;
	message: string;
}

export interface ApiError {
	detail: string;
}

export async function queryDocuments(
	question: string,
	top_k: number = 5,
): Promise<QueryResponse> {
	const res = await fetch(`${API_BASE}/api/v1/query`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ question, top_k }),
	});

	if (!res.ok) {
		const err: ApiError = await res.json();
		throw new Error(err.detail || 'Query failed');
	}

	return res.json();
}

export async function ingestDocument(file: File): Promise<IngestResponse> {
	const formData = new FormData();
	formData.append('file', file);

	const res = await fetch(`${API_BASE}/api/v1/ingest`, {
		method: 'POST',
		body: formData,
	});

	if (!res.ok) {
		const err: ApiError = await res.json();
		throw new Error(err.detail || 'Ingestion failed');
	}

	return res.json();
}
