"""
전체 파이프라인 실행 스크립트
1. 중복 검사
2. 이미지 분류
3. 썸네일 생성
"""

import sys
from pathlib import Path
import argparse

def run_duplicate_checker():
    """중복 검사 실행"""
    print("\n" + "="*60)
    print("STEP 1: 중복 이미지 검사")
    print("="*60 + "\n")
    
    from duplicate_checker import DuplicateChecker
    config_path = Path(__file__).parent.parent / "config.json"
    checker = DuplicateChecker(config_path)
    checker.run()

def run_classifier(test_mode=False, sample_size=None):
    """이미지 분류 실행"""
    print("\n" + "="*60)
    print("STEP 2: 이미지 분류 (Gemini Vision API)")
    print("="*60 + "\n")
    
    from image_classifier import ImageClassifier
    config_path = Path(__file__).parent.parent / "config.json"
    
    classifier = ImageClassifier(config_path)
    
    if test_mode and sample_size:
        # 테스트 모드: 샘플만 처리
        all_images = classifier.find_all_images()
        sample_images = all_images[:sample_size]
        print(f"🧪 테스트 모드: {len(sample_images)}개 샘플 이미지만 처리")
        classifier.process_images(sample_images)
        classifier.save_metadata()
        stats, _ = classifier.generate_statistics()
        print(f"\n📊 테스트 결과: {stats['architecture_images']}/{stats['total_images']} 건축 이미지")
    else:
        classifier.run()

def run_thumbnail_generator():
    """썸네일 생성 실행"""
    print("\n" + "="*60)
    print("STEP 3: 썸네일 생성")
    print("="*60 + "\n")
    
    from generate_thumbnails import ThumbnailGenerator
    config_path = Path(__file__).parent.parent / "config.json"
    generator = ThumbnailGenerator(config_path)
    generator.run()

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='건축 레퍼런스 이미지 처리 파이프라인')
    parser.add_argument('--skip-duplicates', action='store_true', 
                        help='중복 검사 단계 건너뛰기')
    parser.add_argument('--skip-classification', action='store_true',
                        help='이미지 분류 단계 건너뛰기')
    parser.add_argument('--skip-thumbnails', action='store_true',
                        help='썸네일 생성 단계 건너뛰기')
    parser.add_argument('--test', action='store_true',
                        help='테스트 모드 (샘플만 처리)')
    parser.add_argument('--sample-size', type=int, default=10,
                        help='테스트 모드에서 처리할 샘플 크기 (기본: 10)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏛️  건축 레퍼런스 이미지 처리 파이프라인")
    print("=" * 60)
    
    try:
        # 1. 중복 검사
        if not args.skip_duplicates:
            run_duplicate_checker()
        
        # 2. 이미지 분류
        if not args.skip_classification:
            run_classifier(test_mode=args.test, sample_size=args.sample_size if args.test else None)
        
        # 3. 썸네일 생성
        if not args.skip_thumbnails and not args.test:
            run_thumbnail_generator()
        
        print("\n" + "=" * 60)
        print("✅ 모든 단계 완료!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
