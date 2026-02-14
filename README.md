# 건축 레퍼런스 웹사이트

Midjourney로 생성된 건축 이미지들을 효율적으로 관리하고 탐색할 수 있는 AI 기반 레퍼런스 갤러리입니다.

## 주요 기능

- 🔍 **AI 자동 분류**: Gemini Vision API를 활용한 이미지 자동 분류
- 🏗️ **스마트 필터링**: 건축/비건축, 익스테리어/인테리어 등 세밀한 필터링
- 🔎 **강력한 검색**: 태그 기반 실시간 검색
- 📱 **반응형 디자인**: 모든 기기에서 최적화된 경험
- 🖼️ **Masonry 레이아웃**: Pinterest 스타일의 아름다운 그리드

## 설치 및 실행

### 1. Python 패키지 설치

```powershell
cd scripts
pip install -r requirements.txt
```

### 2. Gemini API 키 설정

`config.json` 파일을 열어 API 키를 입력하세요:

```json
{
  "gemini_api_key": "YOUR_API_KEY_HERE"
}
```

API 키는 https://aistudio.google.com/app/apikey 에서 발급받을 수 있습니다.

### 3. 이미지 처리 파이프라인 실행

```powershell
cd scripts

# 테스트 모드로 먼저 실행해보기 (10개 샘플)
python run_pipeline.py --test --sample-size 10

# 전체 실행
python run_pipeline.py
```

이 과정은 다음을 수행합니다:
- 중복 이미지 검사 및 백업
- Gemini Vision API로 이미지 분류
- 썸네일 생성 (WebP)

### 4. Node.js 패키지 설치

```powershell
npm install
```

### 5. 웹사이트 실행

```powershell
npm run dev
```

브라우저에서 http://localhost:5173 을 열어 확인하세요.

## 프로젝트 구조

```
architecture-reference-site/
├── scripts/                    # Python 이미지 처리 스크립트
│   ├── duplicate_checker.py  # 중복 검사
│   ├── image_classifier.py   # AI 분류
│   ├── generate_thumbnails.py # 썸네일 생성
│   └── run_pipeline.py       # 전체 파이프라인
├── src/                       # React 소스 코드
│   ├── components/           # React 컴포넌트
│   │   ├── ImageGallery.jsx
│   │   ├── FilterPanel.jsx
│   │   └── SearchBar.jsx
│   ├── App.jsx
│   └── main.jsx
├── public/
│   └── data/                 # 이미지 메타데이터
│       ├── image_metadata.json
│       └── statistics.json
├── thumbnails/                # 생성된 썸네일
├── backup/                   # 백업된 중복 이미지
└── config.json               # 설정 파일
```

## 사용 방법

1. **필터링**: 좌측 패널에서 원하는 카테고리를 선택하세요
2. **검색**: 상단 검색창에 태그나 키워드를 입력하세요
3. **이미지 보기**: 이미지를 클릭하면 큰 화면으로 볼 수 있습니다
4. **필터 초기화**: 우측 상단의 "초기화" 버튼을 클릭하세요

## 기술 스택

### Backend
- Python 3.x
- Gemini Vision API
- PIL (이미지 처리)
- ImageHash (중복 검사)

### Frontend
- React 18
- Vite
- TailwindCSS
- React Masonry CSS
- Yet Another React Lightbox

## 라이센스

MIT

