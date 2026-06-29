'use client';
import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
	const [dark, setDark] = useState(false);

	useEffect(() => {
		setDark(document.documentElement.classList.contains('dark'));
	}, []);

	const toggle = () => {
		const isDark = !dark;
		setDark(isDark);
		document.documentElement.classList.toggle('dark', isDark);
		localStorage.setItem('theme', isDark ? 'dark' : 'light');
	};

	return (
		<button
			onClick={toggle}
			className='p-2 rounded-lg bg-elevated border border-theme hover:opacity-80 transition-opacity'
			aria-label='Toggle theme'>
			{dark ? (
				<Sun size={16} className='text-secondary' />
			) : (
				<Moon size={16} className='text-secondary' />
			)}
		</button>
	);
}
