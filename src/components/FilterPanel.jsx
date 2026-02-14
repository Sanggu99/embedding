export default function FilterPanel({ filters, onFiltersChange, stats, language }) {
    const typeLabels = language === 'kr' ? {
        exterior: '익스테리어',
        interior: '인테리어',
        urban: '도시',
        concept: '컨셉',
        other: '기타'
    } : {
        exterior: 'Exterior',
        interior: 'Interior',
        urban: 'Urban',
        concept: 'Concept',
        other: 'Other'
    }

    const handleArchitectureToggle = () => {
        onFiltersChange(prev => ({
            ...prev,
            architectureOnly: !prev.architectureOnly
        }))
    }

    const handleTypeToggle = (type) => {
        onFiltersChange(prev => ({
            ...prev,
            types: {
                ...prev.types,
                [type]: !prev.types[type]
            }
        }))
    }

    const handleReset = () => {
        onFiltersChange({
            architectureOnly: false,
            types: {
                exterior: false,
                interior: false,
                urban: false,
                concept: false,
                other: false
            },
            searchQuery: ''
        })
    }

    const hasActiveFilters = filters.architectureOnly || Object.values(filters.types).some(v => v) || filters.searchQuery

    return (
        <div className="mb-8 bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                    {language === 'kr' ? '필터' : 'Filters'}
                </h2>
                {hasActiveFilters && (
                    <button
                        onClick={handleReset}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                        {language === 'kr' ? '초기화' : 'Reset'}
                    </button>
                )}
            </div>

            {/* 건축만 보기 토글 */}
            <div className="mb-6 pb-6 border-b border-gray-200">
                <label className="flex items-center cursor-pointer">
                    <input
                        type="checkbox"
                        checked={filters.architectureOnly}
                        onChange={handleArchitectureToggle}
                        className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="ml-3 text-gray-900 font-medium">
                        {language === 'kr' ? '건축 이미지만 보기' : 'Architecture only'}
                        {stats && (
                            <span className="ml-2 text-sm text-gray-500">
                                ({stats.architecture_images}{language === 'kr' ? '개' : ''})
                            </span>
                        )}
                    </span>
                </label>
            </div>

            {/* 타입 필터 */}
            <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">
                    {language === 'kr' ? '카테고리' : 'Categories'}
                </h3>
                <div className="flex flex-wrap gap-2">
                    {Object.entries(typeLabels).map(([type, label]) => {
                        const count = stats?.type_distribution?.[type] || 0
                        return (
                            <button
                                key={type}
                                onClick={() => handleTypeToggle(type)}
                                className={`filter-button ${filters.types[type] ? 'filter-button-active' : 'filter-button-inactive'
                                    }`}
                            >
                                {label}
                                <span className="ml-1.5 text-xs opacity-75">
                                    ({count})
                                </span>
                            </button>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}
