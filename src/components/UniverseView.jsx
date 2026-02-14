import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Points, PointMaterial, Html, Stars } from '@react-three/drei'
import * as THREE from 'three'

// 색상 매핑 - 클러스터링 확장
const COLOR_MAP = {
    'exterior': '#6366f1',    // Indigo-500
    'interior': '#f59e0b',    // Amber-500
    'aerial': '#10b981',      // Emerald-500
    'nature': '#ec4899',      // Pink-500
    'other': '#9ca3af'        // Gray-400
}

const TYPE_ICONS = {
    'exterior': '🏛️',
    'interior': '🛋️',
    'aerial': '✈️',
    'nature': '🌲',
    'other': '📦'
}

// Helper component to update popup position
// REMOVED PopupController because Mouse Follow Strategy handles positioning in UniverseView

// 이미지 경로 헬퍼 함수
const getImagePath = (path) => {
    if (!path) return '';
    // 경로 내의 공백을 언더바로 변경 (폴더명 변경 대응) 및 인코딩
    const normalizedPath = path.replace(/ /g, '_').replace(/\\/g, '/');
    const cleanPath = normalizedPath.startsWith('/') ? normalizedPath.slice(1) : normalizedPath;
    return encodeURI(`${import.meta.env.BASE_URL}${cleanPath}`);
}

function PointCloud({ data, onHover, selectedPointId, onPointClick }) {
    const pointsRef = useRef()
    const [hovered, setHover] = useState(null)
    const { camera } = useThree()
    const previousPositionsRef = useRef(new Float32Array(data.length * 3))
    const currentPositionsRef = useRef(new Float32Array(data.length * 3))
    const animationProgressRef = useRef(0)

    const { positions, colors, sizes } = useMemo(() => {
        const count = data.length
        const positions = new Float32Array(count * 3)
        const colors = new Float32Array(count * 3)
        const sizes = new Float32Array(count)
        const colorObj = new THREE.Color()

        data.forEach((d, i) => {
            positions[i * 3] = d.x
            positions[i * 3 + 1] = d.y
            positions[i * 3 + 2] = d.z

            const colorHex = COLOR_MAP[d.type] || COLOR_MAP['other']
            colorObj.set(colorHex)

            if (selectedPointId !== null && d.id !== selectedPointId) {
                colors[i * 3] = colorObj.r * 0.15
                colors[i * 3 + 1] = colorObj.g * 0.15
                colors[i * 3 + 2] = colorObj.b * 0.15
                sizes[i] = 0.3
            } else {
                colors[i * 3] = colorObj.r * 1.8
                colors[i * 3 + 1] = colorObj.g * 1.8
                colors[i * 3 + 2] = colorObj.b * 1.8
                sizes[i] = selectedPointId === d.id ? 2.5 : 0.8
            }
        })

        return { positions, colors, sizes }
    }, [data, selectedPointId])

    // Compute bounding sphere for raycasting
    useEffect(() => {
        if (pointsRef.current) {
            pointsRef.current.geometry.computeBoundingSphere()
        }
    }, [positions])

    // 위치 변경 감지 및 애니메이션 초기화
    useEffect(() => {
        // 이전 위치 저장
        for (let i = 0; i < currentPositionsRef.current.length; i++) {
            previousPositionsRef.current[i] = currentPositionsRef.current[i]
        }
        // 새 위치 설정
        for (let i = 0; i < positions.length; i++) {
            currentPositionsRef.current[i] = positions[i]
        }
        // 애니메이션 리셋
        animationProgressRef.current = 0
    }, [positions])

    const handlePointerOver = (e) => {
        e.stopPropagation()
        const index = e.index
        setHover(index)
        if (onHover && data[index]) {
            // Pass native client coordinates for tooltip positioning
            onHover(data[index], { x: e.clientX, y: e.clientY })
        }
        document.body.style.cursor = 'pointer'
    }

    const handlePointerOut = (e) => {
        setHover(null)
        if (onHover) onHover(null)
        document.body.style.cursor = 'auto'
    }

    const handleClick = (e) => {
        try {
            e.stopPropagation()
            const index = e.index
            if (onPointClick && data[index]) {
                console.log('🎯 Clicked:', data[index].filename);
                onPointClick(data[index])
            }
        } catch (error) {
            console.error('Click error:', error);
        }
    }

    useFrame(() => {
        // 카메라 애니메이션
        if (selectedPointId !== null) {
            const target = data.find(d => d.id === selectedPointId)
            if (target) {
                const targetPos = new THREE.Vector3(target.x, target.y, target.z + 8)
                camera.position.lerp(targetPos, 0.05)
            }
        }

        // 포인트 위치 애니메이션
        if (pointsRef.current && animationProgressRef.current < 1) {
            animationProgressRef.current = Math.min(animationProgressRef.current + 0.02, 1)
            const progress = animationProgressRef.current
            // easeInOutCubic 이징 함수
            const eased = progress < 0.5
                ? 4 * progress * progress * progress
                : 1 - Math.pow(-2 * progress + 2, 3) / 2

            const geom = pointsRef.current.geometry
            const posAttr = geom.attributes.position

            for (let i = 0; i < posAttr.count; i++) {
                const i3 = i * 3
                posAttr.array[i3] = previousPositionsRef.current[i3] +
                    (currentPositionsRef.current[i3] - previousPositionsRef.current[i3]) * eased
                posAttr.array[i3 + 1] = previousPositionsRef.current[i3 + 1] +
                    (currentPositionsRef.current[i3 + 1] - previousPositionsRef.current[i3 + 1]) * eased
                posAttr.array[i3 + 2] = previousPositionsRef.current[i3 + 2] +
                    (currentPositionsRef.current[i3 + 2] - previousPositionsRef.current[i3 + 2]) * eased
            }
            posAttr.needsUpdate = true
            geom.computeBoundingSphere() // Update bounding sphere during animation
        }
    })

    return (
        <group>
            <points
                ref={pointsRef}
                onPointerOver={handlePointerOver}
                onPointerOut={handlePointerOut}
                onClick={handleClick}
            >
                <bufferGeometry>
                    <bufferAttribute
                        attach="attributes-position"
                        count={positions.length / 3}
                        array={positions}
                        itemSize={3}
                    />
                    <bufferAttribute
                        attach="attributes-color"
                        count={colors.length / 3}
                        array={colors}
                        itemSize={3}
                    />
                    {/* Size attribute for PointMaterial (if supported by vertexColors/size attenuation) */}
                    {/* Note: Standard PointMaterial uses uniform size. Variable sizes require custom shader or attribute injection. */}
                    {/* Since we are using drei's PointMaterial previously, let's stick to it or standard. */}
                    {/* If we use standard with size=0.8, all points are same size. */}
                    {/* The array 'sizes' is computed but standard material ignores it without attribute binding. */}
                </bufferGeometry>
                <PointMaterial
                    transparent
                    vertexColors
                    size={0.8}
                    sizeAttenuation={true}
                    depthWrite={false}
                    opacity={0.95}
                    blending={THREE.AdditiveBlending}
                />
            </points>

            {hovered !== null && data[hovered] && (
                <group position={[data[hovered].x, data[hovered].y, data[hovered].z]}>
                    <mesh>
                        <sphereGeometry args={[0.25, 16, 16]} />
                        <meshBasicMaterial color="#ffffff" />
                    </mesh>

                    <line>
                        <bufferGeometry>
                            <float32BufferAttribute
                                attach="attributes-position"
                                count={2}
                                itemSize={3}
                                array={new Float32Array([0, 0, 0, 0, 2.5, 0])}
                            />
                        </bufferGeometry>
                        <lineBasicMaterial color="white" transparent opacity={0.4} />
                    </line>
                </group>
            )}
        </group>
    )
}

export default function UniverseView({ filters, onFiltersChange, stats, language, onLanguageChange }) {
    const [allData, setAllData] = useState([])
    const [originalData, setOriginalData] = useState([]) // 원본 좌표 저장
    const [visibleData, setVisibleData] = useState([])
    const [loading, setLoading] = useState(true)
    const [hoveredItem, setHoveredItem] = useState(null)
    const [selectedItem, setSelectedItem] = useState(null)
    const [showControls, setShowControls] = useState(true)
    const [searchTerm, setSearchTerm] = useState('')
    const [isShuffled, setIsShuffled] = useState(false)
    const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 })

    useEffect(() => {
        setLoading(true)
        // 캐시 방지를 위해 버전 쿼리 추가
        fetch(`${import.meta.env.BASE_URL}data/coordinates.json?v=${Date.now()}`)
            .then(res => res.json())
            .then(d => {
                console.log(`✅ Loaded ${d.length} coordinates`)
                setAllData(d)
                setOriginalData(d) // 원본 저장
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to load coordinates:", err)
                setLoading(false)
            })
    }, [])

    useEffect(() => {
        if (allData.length > 0) {
            let data = allData

            if (filters) {
                const activeTypes = Object.keys(filters.types).filter(t => filters.types[t])
                if (activeTypes.length > 0) {
                    data = data.filter(d => activeTypes.includes(d.type))
                }
            }

            if (searchTerm) {
                const lower = searchTerm.toLowerCase()
                data = data.filter(d =>
                    d.filename.toLowerCase().includes(lower) ||
                    (d.description && d.description.toLowerCase().includes(lower)) ||
                    d.type.toLowerCase().includes(lower)
                )
            }

            setVisibleData(data)
        }
    }, [allData, filters, searchTerm])

    const toggleTypeFilter = (type) => {
        if (onFiltersChange && filters) {
            const newFilters = {
                ...filters,
                types: {
                    ...filters.types,
                    [type]: !filters.types[type]
                }
            }
            onFiltersChange(newFilters)
        }
    }

    // 랜덤 좌표 생성 함수
    const randomizePositions = () => {
        if (isShuffled) {
            // 원래 배치로 복구
            setAllData(originalData)
            setIsShuffled(false)
        } else {
            // 랜덤 배치
            const shuffled = allData.map(item => ({
                ...item,
                x: (Math.random() - 0.5) * 120,
                y: (Math.random() - 0.5) * 120,
                z: (Math.random() - 0.5) * 120
            }))
            setAllData(shuffled)
            setIsShuffled(true)
        }
    }

    const handlePointClick = (item) => {

        try {
            console.log('Setting selected item:', item);
            if (selectedItem && selectedItem.id === item.id) {
                setSelectedItem(null)
            } else {
                setSelectedItem(item)
            }
        } catch (error) {
            console.error('Error setting selected item:', error);
        }
    }

    if (loading) return (
        <div className="fixed inset-0 z-50 bg-black flex items-center justify-center">
            <div className="text-center space-y-4 animate-pulse">
                <div className="text-6xl mb-4">🌌</div>
                <div className="text-white font-mono tracking-[0.5em] text-sm opacity-50">INITIALIZING...</div>
            </div>
        </div>
    )

    return (
        <div className="fixed inset-0 z-50 bg-black font-sans overflow-hidden">
            {/* Control Panel */}
            <div className={`absolute top-6 left-6 z-10 transition-all duration-500 transform ${showControls ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'}`}>
                <div className="bg-black/30 backdrop-blur-xl p-6 rounded-3xl border border-white/10 text-white w-80 shadow-2xl">
                    <div className="space-y-6">
                        <div>
                            <h2 className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-purple-300 to-pink-300 mb-1">
                                UNIVERSE
                            </h2>
                            <p className="text-[10px] text-indigo-200 tracking-widest uppercase font-bold">
                                {visibleData.length.toLocaleString()} Dimensions
                            </p>
                        </div>

                        <div className="relative">
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                placeholder="Search..."
                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-all"
                            />
                            <div className="absolute right-3 top-3 text-gray-500 text-xs">🔍</div>
                        </div>

                        <div className="space-y-3">
                            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Filters</div>
                            <div className="grid grid-cols-2 gap-2">
                                {Object.keys(COLOR_MAP).map(type => (
                                    <button
                                        key={type}
                                        onClick={() => toggleTypeFilter(type)}
                                        className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs transition-all border ${filters?.types[type]
                                            ? 'bg-white/10 border-white/30 text-white shadow-lg'
                                            : 'bg-transparent border-white/5 text-gray-500 hover:bg-white/5'
                                            }`}
                                    >
                                        <span className="text-base">{TYPE_ICONS[type]}</span>
                                        <span className="capitalize font-medium text-[11px]">{type}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Shuffle Button */}
                        <button
                            onClick={randomizePositions}
                            className={`w-full px-4 py-3 rounded-xl font-bold text-sm transition-all duration-300 transform hover:scale-105 active:scale-95 ${isShuffled
                                ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg shadow-pink-500/50'
                                : 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/50'
                                }`}
                        >
                            <div className="flex items-center justify-center gap-2">
                                <span className="text-xl">{isShuffled ? '🔄' : '🎲'}</span>
                                <span>{isShuffled ? 'Reset Layout' : 'Shuffle Points'}</span>
                            </div>
                        </button>
                    </div>
                </div>
            </div>

            {!showControls && (
                <button
                    onClick={() => setShowControls(true)}
                    className="absolute top-6 left-6 z-10 p-3 bg-black/30 hover:bg-white/10 text-white rounded-full backdrop-blur-md transition-all border border-white/10"
                >
                    <span className="text-xl">🎛️</span>
                </button>
            )}

            <div className="absolute top-6 right-6 z-10 flex gap-3">
                {showControls && (
                    <button
                        onClick={() => setShowControls(false)}
                        className="px-4 py-2 bg-black/40 hover:bg-white/10 text-white/50 hover:text-white rounded-full backdrop-blur-md transition-all text-xs uppercase"
                    >
                        Hide
                    </button>
                )}
                {/* 언어 선택 */}
                <div className="flex bg-black/40 backdrop-blur-md rounded-full p-1 border border-white/10">
                    <button
                        onClick={() => onLanguageChange('kr')}
                        className={`px-4 py-2 rounded-full text-xs font-medium transition-all ${language === 'kr'
                            ? 'bg-white text-black shadow-lg'
                            : 'text-white/50 hover:text-white'
                            }`}
                    >
                        KR
                    </button>
                    <button
                        onClick={() => onLanguageChange('en')}
                        className={`px-4 py-2 rounded-full text-xs font-medium transition-all ${language === 'en'
                            ? 'bg-white text-black shadow-lg'
                            : 'text-white/50 hover:text-white'
                            }`}
                    >
                        EN
                    </button>
                </div>
            </div>

            {/* Selected Item - Simplified */}
            {selectedItem && selectedItem.path && (
                <div className="absolute bottom-10 right-10 z-20">
                    <div className="bg-black/70 backdrop-blur-xl p-6 rounded-3xl border border-white/10 text-white w-96 shadow-2xl relative">
                        <button
                            onClick={() => setSelectedItem(null)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors text-xl"
                        >
                            ✕
                        </button>
                        <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                            Selected
                        </div>
                        <h3 className="text-base font-bold mb-4 pr-6">
                            {selectedItem.filename || 'Unknown'}
                        </h3>
                        <div className="aspect-video rounded-lg overflow-hidden mb-4 bg-gray-900 border border-white/10">
                            <img
                                src={getImagePath(selectedItem.path)}
                                alt="Selected"
                                className="w-full h-full object-cover"
                                onError={(e) => e.target.style.opacity = '0'}
                            />
                        </div>
                        <p className="text-xs text-gray-300 leading-relaxed border-l-2 border-indigo-500 pl-4">
                            {selectedItem.description || 'No description'}
                        </p>
                    </div>
                </div>
            )}

            {/* Canvas */}
            <Canvas camera={{ position: [0, 0, 90], fov: 50 }} dpr={[1, 2]}>
                <color attach="background" args={['#0a0a12']} />
                <fog attach="fog" args={['#0a0a12', 50, 300]} />

                <Stars radius={200} depth={50} count={8000} factor={5} saturation={0.5} fade speed={0.5} />
                <Stars radius={100} depth={20} count={3000} factor={6} saturation={0} fade speed={1} />

                <ambientLight intensity={0.6} />
                <pointLight position={[50, 50, 50]} intensity={2.5} color="#6366f1" distance={200} />
                <pointLight position={[-50, -50, -50]} intensity={2} color="#ec4899" distance={200} />
                <pointLight position={[0, 100, 0]} intensity={1.5} color="#10b981" distance={200} />

                <PointCloud
                    data={visibleData}
                    onHover={(item, pos) => {
                        setHoveredItem(item)
                        if (pos) setTooltipPos(pos)
                    }}
                    selectedPointId={selectedItem?.id}
                    onPointClick={handlePointClick}
                />

                <OrbitControls
                    enablePan={true}
                    enableZoom={true}
                    enableRotate={true}
                    autoRotate={!hoveredItem && !selectedItem}
                    autoRotateSpeed={0.3}
                    zoomSpeed={0.8}
                    rotateSpeed={0.6}
                    maxDistance={200}
                    minDistance={5}
                />
            </Canvas>

            {/* Guide */}
            {!selectedItem && (
                <div className={`absolute bottom-10 left-1/2 transform -translate-x-1/2 transition-all duration-700 ${hoveredItem ? 'opacity-0 translate-y-10' : 'opacity-100'}`}>
                    <div className="flex items-center gap-6 px-6 py-3 rounded-full bg-white/5 backdrop-blur-sm border border-white/10">
                        <div className="flex items-center gap-3 text-white/40 text-[10px] tracking-[0.2em] uppercase font-light">
                            <span className="flex items-center gap-2">
                                <div className="w-1 h-1 bg-indigo-400 rounded-full animate-pulse"></div>Drag
                            </span>
                            <span className="w-px h-3 bg-white/10"></span>
                            <span className="flex items-center gap-2">
                                <div className="w-1 h-1 bg-pink-400 rounded-full animate-pulse"></div>Click
                            </span>
                            <span className="w-px h-3 bg-white/10"></span>
                            <span className="flex items-center gap-2">
                                <div className="w-1 h-1 bg-emerald-400 rounded-full animate-pulse"></div>Explore
                            </span>
                        </div>
                    </div>
                </div>
            )}
            {/* External Popup Overlay - Mouse Follow Position */}
            {hoveredItem && (
                <div
                    className="fixed pointer-events-none z-50"
                    style={{
                        left: tooltipPos.x,
                        top: tooltipPos.y,
                        transform: 'translate(-50%, -110%)' // Center above cursor
                    }}
                >
                    <div className="mb-2 w-64 backdrop-blur-lg border border-white/20 shadow-[0_0_30px_rgba(0,0,0,0.5)] bg-black/80 rounded-xl overflow-hidden">
                        <div className="relative aspect-[4/3] bg-gray-900 w-full h-48">
                            <img
                                src={getImagePath(hoveredItem.path)}
                                alt={hoveredItem.filename}
                                className="absolute inset-0 w-full h-full object-cover"
                                onError={(e) => {
                                    e.target.style.opacity = '0';
                                }}
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent"></div>
                            <div className="absolute bottom-3 left-3 right-3">
                                <span
                                    className="px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider text-white border border-white/30 backdrop-blur-md"
                                    style={{ backgroundColor: `${COLOR_MAP[hoveredItem.type]}cc` }}
                                >
                                    {hoveredItem.type}
                                </span>
                                <div className="text-xs font-bold truncate text-white mt-1 font-mono">
                                    {hoveredItem.filename.substring(0, 30)}...
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
