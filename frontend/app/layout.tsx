import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
	title: 'RAG Banking & Health Assistant',
	description:
		'Ask questions about Nigerian banking regulations and health insurance documents. Powered by semantic search and AI generation.',
};

export default function RootLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<html lang='en' suppressHydrationWarning>
			<head>
				<script
					dangerouslySetInnerHTML={{
						__html: `
              try {
                const theme = localStorage.getItem('theme');
                if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                  document.documentElement.classList.add('dark');
                }
              } catch(e) {}
            `,
					}}
				/>
			</head>
			<body>{children}</body>
		</html>
	);
}
