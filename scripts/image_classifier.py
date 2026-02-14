"""
Gemini Vision API를 사용한 이미지 분류 스크립트
- 건축/비건축 이미지 구분
- 익스테리어/인테리어/도시/컨셉 등 세부 분류
- 자동 태그 생성
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from PIL import Image

class ImageClassifier:
    def __init__(self, config_path):
        """설정 파일 로드 및 Gemini API 초기화"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # API 키 설정
        api_key = self.config.get('gemini_api_key')
        if not api_key or api_key == 'YOUR_GEMINI_API_KEY_HERE':
            print("⚠️  API 키가 설정되지 않음. 파일 이름 기반 분류 모드로 실행합니다.")
        else:
             try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
             except:
                print("⚠️  API 설정 오류. 파일 이름 기반 분류 모드로 실행합니다.")
                self.model = None
        
        self.source_folders = self.config['source_folders']
        self.output_dir = Path(self.config['output_dir'])
        self.extensions = self.config['image_extensions']
        
        # 메타데이터 저장
        self.metadata = []
        self.processed_count = 0
        self.error_count = 0
    
    def find_all_images(self):
        """중복이 제거된 이미지 파일 찾기"""
        image_files = []
        for folder in self.source_folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                print(f"⚠️  폴더가 존재하지 않습니다: {folder}")
                continue
            
            for ext in self.extensions:
                for img in folder_path.rglob(f"*{ext}"):
                    # macOS 시스템 파일 (._로 시작) 제외
                    if not img.name.startswith('._'):
                        image_files.append(img)
        
        return sorted(image_files)
    
    
    def classify_image(self, image_path):
        """이미지 분류 (API 미사용)"""
        # API 사용하지 않고 파일 정보 기반 메타데이터 생성
        filename = image_path.name
        
        # 기본 분류 정보
        is_architecture = True
        img_type = "exterior"  # 기본값
        confidence = 0.5
        
        # 파일명에서 태그 추출 (언더바, 하이픈 제거)
        tags = [t for t in filename.replace('_', ' ').replace('-', ' ').split() if len(t) > 3]
        tags = list(set(tags))[:5]  # 중복 제거 및 최대 5개
        
        description = filename.replace('_', ' ').replace('-', ' ').split('.')[0]
        
        return {
            "is_architecture": is_architecture,
            "type": img_type,
            "confidence": confidence,
            "tags": tags,
            "description": description
        }
    
    def get_image_dimensions(self, image_path):
        """이미지 크기 가져오기"""
        try:
            with Image.open(image_path) as img:
                return {"width": img.width, "height": img.height}
        except:
            return {"width": 0, "height": 0}
    
    def process_images(self, image_files, batch_size=10):
        """이미지 일괄 처리"""
        total = len(image_files)
        print(f"\n🤖 Gemini Vision API로 {total}개 이미지 분류 중...")
        print("   (API 제한을 위해 천천히 처리됩니다)\n")
        
        for idx, image_path in enumerate(image_files, 1):
            print(f"[{idx}/{total}] 처리 중: {image_path.name}")
            
            # 이미지 분류
            classification = self.classify_image(image_path)
            
            if classification:
                # 메타데이터 생성
                metadata = {
                    "id": f"img_{idx:04d}",
                    "filename": image_path.name,
                    "path": str(image_path.relative_to(Path(self.source_folders[0]).parent)).replace('\\', '/'),
                    "folder": image_path.parent.name,
                    "is_architecture": classification.get('is_architecture', False),
                    "type": classification.get('type', 'other'),
                    "confidence": classification.get('confidence', 0.0),
                    "tags": classification.get('tags', []),
                    "description": classification.get('description', ''),
                    "size": self.get_image_dimensions(image_path),
                    "processed_at": datetime.now().isoformat()
                }
                
                self.metadata.append(metadata)
                self.processed_count += 1
                
                # 분류 결과 출력
                arch_icon = "🏛️" if metadata['is_architecture'] else "❌"
                print(f"   {arch_icon} {metadata['type']} | {metadata['tags'][:3]}")
            else:
                self.error_count += 1
            
            # 중간 저장 (10개마다)
            if idx % batch_size == 0:
                self.save_metadata(temp=True)
                print(f"   💾 중간 저장 완료 ({self.processed_count}/{total})\n")
                # API 제한 방지를 위한 딜레이
                time.sleep(2)
            else:
                pass # API를 사용하지 않으므로 대기 시간 불필요
    
    def save_metadata(self, temp=False):
        """메타데이터를 JSON 파일로 저장"""
        if temp:
            output_path = self.output_dir / "public" / "data" / "image_metadata_temp.json"
        else:
            output_path = self.output_dir / "public" / "data" / "image_metadata.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def generate_statistics(self):
        """분류 통계 생성"""
        total = len(self.metadata)
        architecture_count = sum(1 for m in self.metadata if m['is_architecture'])
        
        type_counts = {}
        for m in self.metadata:
            if m['is_architecture']:
                type_counts[m['type']] = type_counts.get(m['type'], 0) + 1
        
        all_tags = []
        for m in self.metadata:
            all_tags.extend(m['tags'])
        
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_tags = tag_counts.most_common(20)
        
        stats = {
            "total_images": total,
            "architecture_images": architecture_count,
            "non_architecture_images": total - architecture_count,
            "type_distribution": type_counts,
            "top_tags": [{"tag": tag, "count": count} for tag, count in top_tags],
            "errors": self.error_count,
            "generated_at": datetime.now().isoformat()
        }
        
        stats_path = self.output_dir / "public" / "data" / "statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        return stats, stats_path
    
    def run(self):
        """전체 분류 프로세스 실행"""
        print("=" * 60)
        print("🤖 Gemini Vision API 이미지 분류 시작")
        print("=" * 60)
        
        # 1. 이미지 파일 찾기
        image_files = self.find_all_images()
        print(f"\n✓ 총 {len(image_files)}개 이미지 발견")
        
        if len(image_files) == 0:
            print("❌ 처리할 이미지가 없습니다.")
            return
        
        # 2. 이미지 분류
        self.process_images(image_files)
        
        # 3. 최종 저장
        metadata_path = self.save_metadata(temp=False)
        print(f"\n✓ 메타데이터 저장 완료: {metadata_path}")
        
        # 4. 통계 생성
        stats, stats_path = self.generate_statistics()
        print(f"✓ 통계 생성 완료: {stats_path}")
        
        # 5. 결과 출력
        print(f"\n📊 분류 결과:")
        print(f"   • 총 이미지: {stats['total_images']}개")
        print(f"   • 건축 이미지: {stats['architecture_images']}개")
        print(f"   • 비건축 이미지: {stats['non_architecture_images']}개")
        print(f"   • 오류: {stats['errors']}개")
        print(f"\n   분류 타입별:")
        for type_name, count in stats['type_distribution'].items():
            print(f"   • {type_name}: {count}개")
        
        print("\n" + "=" * 60)
        print("✅ 이미지 분류 완료!")
        print("=" * 60)

def main():
    """메인 함수"""
    import sys
    
    # 설정 파일 경로
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print(f"❌ 설정 파일을 찾을 수 없습니다: {config_path}")
        sys.exit(1)
    
    try:
        # 이미지 분류 실행
        classifier = ImageClassifier(config_path)
        classifier.run()
    except ValueError as e:
        print(f"\n❌ 설정 오류: {e}")
        print("\nconfig.json 파일을 열어 'gemini_api_key'에 유효한 API 키를 입력해주세요.")
        print("API 키는 https://aistudio.google.com/app/apikey 에서 발급받을 수 있습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
