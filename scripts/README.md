# 건축 레퍼런스 이미지 처리 스크립트

이 폴더에는 Midjourney 이미지를 처리하기 위한 Python 스크립트들이 포함되어 있습니다.

## 설치

```powershell
pip install -r requirements.txt
```

## 사용법

### 1. config.json 설정

먼저 프로젝트 루트의 `config.json` 파일을 열어 Gemini API 키를 입력하세요:

```json
{
  "gemini_api_key": "YOUR_ACTUAL_API_KEY_HERE"
}
```

API 키는 https://aistudio.google.com/app/apikey 에서 발급받을 수 있습니다.

### 2. 전체 파이프라인 실행

```powershell
python run_pipeline.py
```

### 3. 개별 스크립트 실행

#### 중복 검사만 실행
```powershell
python duplicate_checker.py
```

#### 이미지 분류만 실행
```powershell
python image_classifier.py
```

#### 썸네일 생성만 실행
```powershell
python generate_thumbnails.py
```

### 4. 테스트 모드

10개 샘플 이미지로만 테스트:
```powershell
python run_pipeline.py --test --sample-size 10
```

## 출력 파일

- `duplicate_report.json`: 중복 이미지 리포트
- `public/data/image_metadata.json`: 이미지 분류 메타데이터
- `public/data/statistics.json`: 분류 통계
- `thumbnails/`: 생성된 썸네일 이미지들
- `backup/`: 백업된 중복 이미지들
