import json
from pathlib import Path

# 메타데이터 파일 로드
metadata_path = Path("public/data/image_metadata.json")
with open(metadata_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 경로 수정 (백슬래시 -> 슬래시)
for item in data:
    item['path'] = item['path'].replace('\\', '/')

# 저장
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ 메타데이터 경로 수정 완료: {len(data)}개 항목")
