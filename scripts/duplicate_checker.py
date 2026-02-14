"""
이미지 중복 검사 스크립트
- SHA-256 해시로 완전 동일한 이미지 탐지
- Perceptual hash (pHash)로 시각적으로 유사한 이미지 탐지
- 중복 이미지를 백업 폴더로 이동
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from PIL import Image
import imagehash

class DuplicateChecker:
    def __init__(self, config_path):
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.source_folders = self.config['source_folders']
        self.backup_dir = Path(self.config['backup_dir'])
        self.output_dir = Path(self.config['output_dir'])
        self.extensions = self.config['image_extensions']
        self.phash_threshold = self.config.get('perceptual_hash_threshold', 10)
        
        # 백업 디렉토리 생성
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 결과 저장용
        self.exact_duplicates = defaultdict(list)
        self.similar_duplicates = defaultdict(list)
        self.sha256_map = {}
        self.phash_map = {}
    
    def calculate_sha256(self, file_path):
        """파일의 SHA-256 해시 계산"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def calculate_phash(self, file_path):
        """이미지의 perceptual hash 계산"""
        try:
            img = Image.open(file_path)
            return str(imagehash.phash(img))
        except Exception as e:
            print(f"⚠️  pHash 계산 실패: {file_path} - {e}")
            return None
    
    def find_all_images(self):
        """모든 소스 폴더에서 이미지 파일 찾기"""
        image_files = []
        for folder in self.source_folders:
            folder_path = Path(folder)
            if not folder_path.exists():
                print(f"⚠️  폴더가 존재하지 않습니다: {folder}")
                continue
            
            for ext in self.extensions:
                image_files.extend(folder_path.rglob(f"*{ext}"))
        
        return image_files
    
    def check_duplicates(self, image_files):
        """중복 이미지 검사"""
        print(f"\n🔍 {len(image_files)}개 이미지 검사 중...")
        
        for idx, file_path in enumerate(image_files, 1):
            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(image_files)}")
            
            # SHA-256 해시 계산 (완전 중복)
            sha256 = self.calculate_sha256(file_path)
            
            if sha256 in self.sha256_map:
                # 완전 중복 발견
                self.exact_duplicates[sha256].append(str(file_path))
            else:
                self.sha256_map[sha256] = str(file_path)
            
            # Perceptual hash 계산 (시각적 유사성)
            phash = self.calculate_phash(file_path)
            if phash:
                # 유사한 해시 찾기
                found_similar = False
                for existing_phash in self.phash_map.keys():
                    # Hamming distance 계산
                    distance = imagehash.hex_to_hash(phash) - imagehash.hex_to_hash(existing_phash)
                    if distance <= self.phash_threshold:
                        self.similar_duplicates[existing_phash].append(str(file_path))
                        found_similar = True
                        break
                
                if not found_similar:
                    self.phash_map[phash] = str(file_path)
    
    def backup_and_remove_duplicates(self):
        """중복 이미지를 백업 폴더로 이동"""
        moved_count = 0
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / f"duplicates_{timestamp}"
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📦 중복 이미지를 백업 폴더로 이동 중...")
        
        # 완전 중복 처리
        for sha256, duplicate_files in self.exact_duplicates.items():
            # 첫 번째 파일은 유지, 나머지는 백업
            for dup_file in duplicate_files:
                source = Path(dup_file)
                if source.exists():
                    # 백업 디렉토리에 원본 폴더 구조 유지
                    relative_path = source.relative_to(Path(self.source_folders[0]).parent)
                    dest = backup_subdir / relative_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.move(str(source), str(dest))
                    moved_count += 1
                    print(f"   ✓ 이동: {source.name}")
        
        return moved_count, backup_subdir
    
    def generate_report(self):
        """중복 검사 리포트 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_images_scanned": len(self.sha256_map) + sum(len(v) for v in self.exact_duplicates.values()),
            "exact_duplicates_count": sum(len(v) for v in self.exact_duplicates.values()),
            "similar_duplicates_count": sum(len(v) for v in self.similar_duplicates.values()),
            "exact_duplicates": {
                sha256: {
                    "original": self.sha256_map.get(sha256, "Unknown"),
                    "duplicates": files
                }
                for sha256, files in self.exact_duplicates.items()
            },
            "similar_duplicates": {
                phash: {
                    "original": self.phash_map.get(phash, "Unknown"),
                    "similar_images": files
                }
                for phash, files in self.similar_duplicates.items()
            }
        }
        
        report_path = self.output_dir / "duplicate_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_path
    
    def run(self):
        """전체 중복 검사 프로세스 실행"""
        print("=" * 60)
        print("🔍 이미지 중복 검사 시작")
        print("=" * 60)
        
        # 1. 모든 이미지 찾기
        image_files = self.find_all_images()
        print(f"\n✓ 총 {len(image_files)}개 이미지 발견")
        
        # 2. 중복 검사
        self.check_duplicates(image_files)
        
        # 3. 결과 출력
        exact_count = sum(len(v) for v in self.exact_duplicates.values())
        similar_count = sum(len(v) for v in self.similar_duplicates.values())
        
        print(f"\n📊 검사 결과:")
        print(f"   • 완전 중복: {exact_count}개")
        print(f"   • 시각적 유사: {similar_count}개")
        
        # 4. 중복 파일 백업 및 삭제
        if exact_count > 0:
            moved_count, backup_dir = self.backup_and_remove_duplicates()
            print(f"\n✓ {moved_count}개 파일을 백업으로 이동")
            print(f"   백업 위치: {backup_dir}")
        
        # 5. 리포트 생성
        report_path = self.generate_report()
        print(f"\n✓ 리포트 생성 완료: {report_path}")
        
        print("\n" + "=" * 60)
        print("✅ 중복 검사 완료!")
        print("=" * 60)

def main():
    """메인 함수"""
    import sys
    
    # 설정 파일 경로
    config_path = Path(__file__).parent.parent / "config.json"
    
    if not config_path.exists():
        print(f"❌ 설정 파일을 찾을 수 없습니다: {config_path}")
        print("config.json 파일을 먼저 생성해주세요.")
        sys.exit(1)
    
    # 중복 검사 실행
    checker = DuplicateChecker(config_path)
    checker.run()

if __name__ == "__main__":
    main()
