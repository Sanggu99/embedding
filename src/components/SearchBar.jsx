import { useState } from 'react'

export default function SearchBar({ searchQuery, onSearchChange, language }) {
    const placeholder = language === 'kr'
        ? '태그 또는 설명으로 검색... (예: modern, glass, concrete)'
        : 'Search by tags or description... (e.g., modern, glass, concrete)'
    return (
        <div className="mb-6">
            <div className="relative max-w-2xl mx-auto">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => onSearchChange(e.target.value)}
                    placeholder={placeholder}
                    className="w-full px-6 py-4 text-lg border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
                />
                <svg
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                </svg>
            </div>
        </div>
    )
}
