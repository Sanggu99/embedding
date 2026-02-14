"""
썸네일 생성 스크립트
- 웹 최적화를 위한 다양한 크기의 썸네일 생성
- WebP 포맷으로 변환하여 파일 크기 최소화
"""

import os
import json
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

class ThumbnailGenerator:
    def __init__(self, config_path):
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.source_folders = self.config['source_folders']
        self.thumbnails_dir = Path(self.config['thumbnails_dir'])
        self.extensions = self.config['image_extensions']
        self.sizes = self.config['thumbnail_sizes']
        
        # 썸네일 디렉토리 생성
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        
        self.processed_count = 0
        self.error_count = 0
    
    def find_all_images(self):
        """모든 이미지 파일 찾기"""
        image_files = []
        for folder in self.source_folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                continue
            
            for ext in self.extensions:
                image_files.extend(folder_path.rglob(f"*{ext}"))
        
        return sorted(image_files)
    
    def generate_thumbnail(self, image_path, size_name, max_size):
        """단일 썸네일 생성"""
        try:
            with Image.open(image_path) as img:
                # RGBA를 RGB로 변환 (WebP 호환성)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 비율 유지하며 리사이즈
                img.thumbnail((max_size, max_size), Image.Lanczos)
                
                # 썸네일 저장 경로
                relative_path = image_path.relative_to(Path(self.source_folders[0]).parent)
                thumb_dir = self.thumbnails_dir / relative_path.parent / size_name
                thumb_dir.mkdir(parents=True, exist_ok=True)
                
                # WebP로 저장
                thumb_name = image_path.stem + '.webp'
                thumb_path = thumb_dir / thumb_name
                
                img.save(thumb_path, 'WEBP', quality=85, method=6)
                
                return True, thumb_path
                
        except Exception as e:
            return False, str(e)
    
    def process_image(self, image_path):
        """한 이미지의 모든 크기 썸네일 생성"""
        results = {}
        for size_name, max_size in self.sizes.items():
            success, result = self.generate_thumbnail(image_path, size_name, max_size)
            results[size_name] = {'success': success, 'path': result}
        
        all_success = all(r['success'] for r in results.values())
        return image_path, all_success, results
    
    def process_all_images(self, image_files, max_workers=4):
        """모든 이미지를 병렬 처리"""
        total = len(image_files)
        print(f"\n🖼️  {total}개 이미지의 썸네일 생성 중...")
        print(f"   크기: {list(self.sizes.keys())}\n")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.process_image, img): img for img in image_files}
            
            for idx, future in enumerate(as_completed(futures), 1):
                image_path, success, results = future.result()
                
                if success:
                    self.processed_count += 1
                    print(f"[{idx}/{total}] ✓ {image_path.name}")
                else:
                    self.error_count += 1
                    print(f"[{idx}/{total}] ✗ {image_path.name}")
                    for size_name, result in results.items():
                        if not result['success']:
                            print(f"   오류 ({size_name}): {result['path']}")
    
    def run(self):
        """전체 썸네일 생성 프로세스 실행"""
        print("=" * 60)
        print("🖼️  썸네일 생성 시작")
        print("=" * 60)
        
        # 1. 이미지 파일 찾기
        image_files = self.find_all_images()
        print(f"\n✓ 총 {len(image_files)}개 이미지 발견")
        
        if len(image_files) == 0:
            print("❌ 처리할 이미지가 없습니다.")
            return
        
        # 2. 썸네일 생성
        self.process_all_images(image_files)
        
        # 3. 결과 출력
        print(f"\n📊 생성 결과:")
        print(f"   • 성공: {self.processed_count}개")
        print(f"   • 실패: {self.error_count}개")
        print(f"   • 저장 위치: {self.thumbnails_dir}")
        
        print("\n" + "=" * 60)
        print("✅ 썸네일 생성 완료!")
        print("=" * 60)

def main():
    """메인 함수"""
    import sys
    
    # 설정 파일 경로
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print(f"❌ 설정 파일을 찾을 수 없습니다: {config_path}")
        sys.exit(1)
    
    # 썸네일 생성 실행
    generator = ThumbnailGenerator(config_path)
    generator.run()

if __name__ == "__main__":
    main()
