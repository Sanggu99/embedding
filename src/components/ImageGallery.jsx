import { useState } from 'react'
import Masonry from 'react-masonry-css'
import Lightbox from 'yet-another-react-lightbox'
import Captions from 'yet-another-react-lightbox/plugins/captions'
import 'yet-another-react-lightbox/styles.css'
import 'yet-another-react-lightbox/plugins/captions.css'

export default function ImageGallery({ images, language }) {
    const [lightboxOpen, setLightboxOpen] = useState(false)
    const [lightboxIndex, setLightboxIndex] = useState(0)

    const breakpointColumns = {
        default: 4,
        1536: 4,
        1280: 3,
        1024: 3,
        768: 2,
        640: 1
    }

    const handleImageClick = (index) => {
        setLightboxIndex(index)
        setLightboxOpen(true)
    }

    const typeLabels = {
        kr: {
            exterior: '익스테리어',
            interior: '인테리어',
            urban: '도시',
            concept: '컨셉',
            other: '기타'
        },
        en: {
            exterior: 'Exterior',
            interior: 'Interior',
            urban: 'Urban',
            concept: 'Concept',
            other: 'Other'
        }
    }

    // Lightbox용 슬라이드 생성 (프롬프트와 태그 포함)
    const slides = images.map(img => {
        const typeLabel = typeLabels[language][img.type] || img.type
        const tagsText = img.tags.join(', ')

        return {
            src: `/${img.path}`,
            title: img.description,
            description: `${language === 'kr' ? '카테고리' : 'Category'}: ${typeLabel}\n${language === 'kr' ? '태그' : 'Tags'}: ${tagsText}`
        }
    })

    if (images.length === 0) {
        return (
            <div className="text-center py-16">
                <p className="text-xl text-gray-500">
                    {language === 'kr' ? '검색 결과가 없습니다.' : 'No results found.'}
                </p>
                <p className="text-sm text-gray-400 mt-2">
                    {language === 'kr' ? '다른 필터를 시도해보세요.' : 'Try different filters.'}
                </p>
            </div>
        )
    }

    return (
        <>
            <Masonry
                breakpointCols={breakpointColumns}
                className="masonry-grid"
                columnClassName="masonry-grid_column"
            >
                {images.map((image, index) => (
                    <div
                        key={image.id}
                        className="image-card mb-4"
                        onClick={() => handleImageClick(index)}
                    >
                        <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 cursor-pointer">
                            <img
                                src={`/${image.path}`}
                                alt={image.description}
                                className="w-full h-auto"
                                loading="lazy"
                                style={{ display: 'block' }}
                            />
                        </div>
                    </div>
                ))}
            </Masonry>

            {/* Lightbox with Captions */}
            <Lightbox
                open={lightboxOpen}
                close={() => setLightboxOpen(false)}
                index={lightboxIndex}
                slides={slides}
                plugins={[Captions]}
                captions={{
                    showToggle: true,
                    descriptionTextAlign: 'start',
                    descriptionMaxLines: 10
                }}
                styles={{
                    container: { backgroundColor: 'rgba(0, 0, 0, 0.95)' },
                    captionsTitle: {
                        fontSize: '18px',
                        fontWeight: '600',
                        marginBottom: '12px',
                        color: '#fff'
                    },
                    captionsDescription: {
                        fontSize: '14px',
                        lineHeight: '1.6',
                        whiteSpace: 'pre-line',
                        color: '#ddd'
                    }
                }}
            />
        </>
    )
}
