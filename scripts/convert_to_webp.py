"""
배포용 이미지 WebP 변환 스크립트
- 원본 이미지를 WebP로 변환하여 public 폴더에 복사
- 파일 크기 30-80% 감소
- 메타데이터도 새로운 경로로 업데이트
"""

import os
import json
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class WebPConverter:
    def __init__(self, config_path):
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.source_folders = self.config['source_folders']
        self.output_dir = Path(self.config['output_dir']) / 'public'
        self.extensions = ['.png', '.jpg', '.jpeg']  # WebP로 변환할 확장자
        
        self.processed_count = 0
        self.error_count = 0
        self.total_original_size = 0
        self.total_webp_size = 0
    
    def find_all_images(self):
        """모든 이미지 파일 찾기"""
        image_files = []
        for folder in self.source_folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                print(f"⚠️  폴더가 존재하지 않습니다: {folder}")
                continue
            
            for ext in self.extensions:
                for img in folder_path.rglob(f"*{ext}"):
                    # macOS 시스템 파일 제외
                    if not img.name.startswith('._'):
                        image_files.append(img)
        
        return sorted(image_files)
    
    def convert_to_webp(self, image_path):
        """단일 이미지를 WebP로 변환"""
        try:
            # 원본 파일 크기
            original_size = image_path.stat().st_size
            
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
                
                # 출력 경로 생성
                # E:\4. Midjourney\Midjourney 1\image.png 
                # -> public/Midjourney 1/image.webp
                relative_path = image_path.relative_to(Path(self.source_folders[0]).parent)
                output_path = self.output_dir / relative_path.parent / (image_path.stem + '.webp')
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # WebP로 저장 (quality=85는 좋은 품질과 압축의 균형)
                img.save(output_path, 'WEBP', quality=85, method=6)
                
                # 변환 후 파일 크기
                webp_size = output_path.stat().st_size
                
                return True, output_path, original_size, webp_size
                
        except Exception as e:
            return False, str(e), 0, 0
    
    def process_all_images(self, image_files, max_workers=4):
        """모든 이미지를 병렬 처리"""
        total = len(image_files)
        print(f"\n🔄 {total}개 이미지를 WebP로 변환 중...\n")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.convert_to_webp, img): img for img in image_files}
            
            with tqdm(total=total, desc="변환 진행", unit="장") as pbar:
                for future in as_completed(futures):
                    image_path = futures[future]
                    success, result, original_size, webp_size = future.result()
                    
                    if success:
                        self.processed_count += 1
                        self.total_original_size += original_size
                        self.total_webp_size += webp_size
                        
                        reduction = ((original_size - webp_size) / original_size * 100) if original_size > 0 else 0
                        pbar.set_postfix({
                            '파일': image_path.name[:20],
                            '압축률': f"{reduction:.1f}%"
                        })
                    else:
                        self.error_count += 1
                        tqdm.write(f"❌ 오류: {image_path.name} - {result}")
                    
                    pbar.update(1)
    
    def update_metadata(self):
        """메타데이터 파일의 경로를 .webp로 업데이트"""
        metadata_path = self.output_dir / 'data' / 'image_metadata.json'
        
        if not metadata_path.exists():
            print("⚠️  메타데이터 파일이 없습니다.")
            return
        
        print("\n📝 메타데이터 경로 업데이트 중...")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 경로를 .webp로 변경
        for item in metadata:
            if 'path' in item:
                path = Path(item['path'])
                # 확장자를 .webp로 변경
                new_path = path.with_suffix('.webp')
                item['path'] = str(new_path).replace('\\', '/')
        
        # 업데이트된 메타데이터 저장
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(metadata)}개 항목 업데이트 완료")
    
    def run(self):
        """전체 변환 프로세스 실행"""
        print("=" * 60)
        print("🖼️  WebP 변환 시작 (배포용)")
        print("=" * 60)
        
        # 1. 이미지 파일 찾기
        image_files = self.find_all_images()
        print(f"\n✓ 총 {len(image_files)}개 이미지 발견")
        
        if len(image_files) == 0:
            print("❌ 처리할 이미지가 없습니다.")
            return
        
        # 2. WebP 변환
        self.process_all_images(image_files)
        
        # 3. 메타데이터 업데이트
        self.update_metadata()
        
        # 4. 결과 출력
        print(f"\n📊 변환 결과:")
        print(f"   • 성공: {self.processed_count}개")
        print(f"   • 실패: {self.error_count}개")
        
        if self.total_original_size > 0:
            original_mb = self.total_original_size / (1024 * 1024)
            webp_mb = self.total_webp_size / (1024 * 1024)
            reduction = ((self.total_original_size - self.total_webp_size) / self.total_original_size * 100)
            
            print(f"\n💾 파일 크기:")
            print(f"   • 원본: {original_mb:.2f} MB")
            print(f"   • WebP: {webp_mb:.2f} MB")
            print(f"   • 절감: {original_mb - webp_mb:.2f} MB ({reduction:.1f}%)")
        
        print(f"\n   • 저장 위치: {self.output_dir}")
        
        print("\n" + "=" * 60)
        print("✅ WebP 변환 완료!")
        print("=" * 60)
        print("\n💡 다음 단계:")
        print("   1. npm run build 실행")
        print("   2. dist 폴더를 Netlify에 배포")

def main():
    """메인 함수"""
    import sys
    
    # 설정 파일 경로
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print(f"❌ 설정 파일을 찾을 수 없습니다: {config_path}")
        sys.exit(1)
    
    # WebP 변환 실행
    converter = WebPConverter(config_path)
    converter.run()

if __name__ == "__main__":
    main()
