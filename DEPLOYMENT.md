# 🚀 Netlify 배포 가이드 (WebP 최적화 포함)

## 📋 배포 전 체크리스트

### 1단계: 이미지 WebP 변환 ✅

```bash
# Python 환경 활성화 (필요시)
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 필요한 패키지 설치
pip install -r scripts/requirements.txt

# WebP 변환 실행 (10-15분 소요)
python scripts/convert_to_webp.py
```

**결과**:
- ✅ 모든 PNG/JPG → WebP 변환
- ✅ 파일 크기 30-80% 감소
- ✅ 메타데이터 자동 업데이트
- ✅ `public/` 폴더에 최적화된 이미지 생성

---

### 2단계: 프로덕션 빌드

```bash
# 기존 dist 폴더 삭제 (선택사항)
Remove-Item -Recurse -Force dist  # Windows
# rm -rf dist  # Mac/Linux

# 새로 빌드
npm run build
```

**예상 결과**:
```
✓ 610 modules transformed
✓ Built in 1-2분

dist/
  ├── index.html (0.56 kB)
  ├── assets/
  │   ├── index.css (22.90 kB)
  │   └── index.js (1,039 kB → 289 kB gzipped)
  ├── data/ (메타데이터)
  └── Midjourney 1-8/ (WebP 이미지들)
```

---

### 3단계: Netlify 배포

## 🌐 배포 방법 1: 드래그 앤 드롭 (가장 쉬움)

1. [Netlify Drop](https://app.netlify.com/drop) 접속
2. **`dist` 폴더 전체**를 드래그
3. 완료! 🎉

**소요 시간**: 1-2분 (업로드 시간 포함)

---

## 🔄 배포 방법 2: Git 연결 (자동 배포)

### GitHub 저장소 생성 및 푸시

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: 3D Architecture Reference Site"

# GitHub 저장소 연결
git remote add origin https://github.com/your-username/architecture-reference.git
git branch -M main
git push -u origin main
```

### Netlify 설정

1. [Netlify](https://app.netlify.com) → "Add new site"
2. "Import an existing project" 선택
3. GitHub 연결 및 저장소 선택
4. **빌드 설정** (자동 감지되지만 확인 필요):
   ```
   Build command: npm run build
   Publish directory: dist
   ```
5. "Deploy site" 클릭

**장점**: 
- 이후 `git push`만 하면 자동 배포
- 롤백 기능
- 미리보기 배포 (Pull Request)

---

## 💻 배포 방법 3: Netlify CLI

```bash
# CLI 설치 (1회만)
npm install -g netlify-cli

# 로그인
netlify login

# 배포
netlify deploy --prod

# 프롬프트에서:
# - Publish directory: dist
```

---

## 📊 배포 후 성능 확인

### PageSpeed Insights 테스트
1. [PageSpeed Insights](https://pagespeed.web.dev/) 접속
2. 배포된 URL 입력
3. 점수 확인

**예상 점수**:
- Performance: 85-95 (WebP 덕분)
- Accessibility: 90+
- Best Practices: 90+
- SEO: 90+

### 개선된 로딩 속도
```
개선 전 (PNG):
- 이미지 총 크기: ~500 MB
- 첫 로딩: 15-30초

개선 후 (WebP):
- 이미지 총 크기: ~150 MB (70% 감소!)
- 첫 로딩: 3-8초
```

---

## 🔧 문제 해결

### 문제 1: 이미지가 로드되지 않음

**확인 사항**:
1. `dist/` 폴더에 WebP 이미지가 있는지 확인
2. `dist/data/image_metadata.json`에서 경로가 `.webp`로 끝나는지 확인
3. 브라우저 콘솔에서 404 에러 확인

**해결**:
```bash
# WebP 변환 다시 실행
python scripts/convert_to_webp.py

# 빌드 다시 실행
npm run build
```

---

### 문제 2: 3D 유니버스가 작동하지 않음

**원인**: Three.js 라이브러리 로딩 문제

**해결**:
1. 브라우저 콘솔 확인
2. Netlify 빌드 로그 확인
3. 로컬에서 `npm run build && npm run preview` 테스트

---

### 문제 3: 빌드 실패

**일반적인 원인**:
- Node.js 버전 불일치
- 메모리 부족

**해결**:
```bash
# Netlify 환경 변수 설정 (대시보드에서)
NODE_VERSION = 18
NODE_OPTIONS = --max-old-space-size=4096
```

---

## 🎯 최적화 팁

### 1. CDN 캐싱 활용
`netlify.toml`에 이미 설정되어 있습니다:
- `.js`, `.css` → 1년 캐싱
- 이미지 → 1시간 캐싱

### 2. 환경별 분기
```javascript
// vite.config.js에 추가 가능
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'three': ['three'],
          'react': ['react', 'react-dom']
        }
      }
    }
  }
})
```

### 3. 이미지 Lazy Loading
이미 구현되어 있습니다 (Three.js 텍스처 로딩)

---

## 📱 모바일 최적화 확인

배포 후 다음 기기에서 테스트 권장:
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] iPad
- [ ] Desktop (Chrome, Firefox, Safari)

---

## 🌟 배포 완료 후

### 1. 성능 모니터링
- [Netlify Analytics](https://docs.netlify.com/monitor-sites/analytics/) 활성화
- [Google Analytics](https://analytics.google.com) 연결 (선택)

### 2. 커스텀 도메인 (선택)
1. 도메인 구매 (예: architecture-ref.com)
2. Netlify 대시보드 → Domain settings
3. DNS 설정 업데이트

### 3. SSL 인증서
- Netlify가 자동으로 Let's Encrypt SSL 제공
- HTTPS 자동 활성화 ✅

---

## 📈 예상 배포 시간

| 단계 | 시간 |
|------|------|
| WebP 변환 | 10-15분 |
| npm build | 1-2분 |
| Netlify 업로드 | 2-5분 (크기에 따라) |
| **총 소요 시간** | **~20분** |

---

## ✅ 최종 체크리스트

배포 전:
- [x] WebP 변환 완료
- [x] `npm run build` 성공
- [x] `dist` 폴더 생성 확인
- [x] 로컬에서 `npm run preview` 테스트
- [ ] Netlify에 배포

배포 후:
- [ ] URL 접속 테스트
- [ ] 모든 이미지 로딩 확인
- [ ] 3D 유니버스 작동 확인
- [ ] 필터 기능 테스트
- [ ] 모바일 테스트

---

**축하합니다! 🎉**  
**WebP 최적화가 완료된 고성능 3D 건축 레퍼런스 사이트가 준비되었습니다!**
