import { useState, useEffect } from 'react'
import UniverseView from './components/UniverseView'

function App() {
    const [filters, setFilters] = useState({
        architectureOnly: false,
        types: {
            exterior: false,
            interior: false,
            aerial: false,
            nature: false,
            other: false
        },
        searchQuery: ''
    })
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [language, setLanguage] = useState('kr')

    // 통계 데이터 로드 (필요한 경우)
    useEffect(() => {
        const loadStats = async () => {
            try {
                const statsResponse = await fetch(`${import.meta.env.BASE_URL}data/statistics.json`)
                const statsData = await statsResponse.json()
                setStats(statsData)
                setLoading(false)
            } catch (error) {
                console.error('통계 로드 실패:', error)
                setLoading(false)
            }
        }

        loadStats()
    }, [])

    if (loading) {
        return (
            <div className="fixed inset-0 z-50 bg-black flex items-center justify-center">
                <div className="text-center space-y-4 animate-pulse">
                    <div className="text-6xl mb-4">🌌</div>
                    <div className="text-white font-mono tracking-[0.5em] text-sm opacity-50">INITIALIZING...</div>
                </div>
            </div>
        )
    }

    return (
        <div className="fixed inset-0">
            <UniverseView
                filters={filters}
                onFiltersChange={setFilters}
                stats={stats}
                language={language}
                onLanguageChange={setLanguage}
            />
        </div>
    )
}

export default App

