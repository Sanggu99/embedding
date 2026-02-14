import json
import os
import sys
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel
import umap
from sklearn.preprocessing import MinMaxScaler

# 설정 로드
def load_config():
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("🚀 3D 유니버스 모드 데이터 생성 스크립트 시작")
    
    # 1. 설정 및 모델 로드
    config = load_config()
    source_folders = config['source_folders']
    output_dir = Path(config['output_dir'])
    extensions = config['image_extensions']

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"DEVICE: {device}")

    try:
        model_id = "openai/clip-vit-base-patch32"
        print(f"📦 CLIP 모델 로드 중 ({model_id})...")
        model = CLIPModel.from_pretrained(model_id).to(device)
        processor = CLIPProcessor.from_pretrained(model_id)
    except Exception as e:
        print(f"❌ 모델 로드 실패: {e}")
        print("pip install transformers torch pillow umap-learn scikit-learn tqdm 명령어를 실행했는지 확인하세요.")
        return

    # 2. 이미지 파일 찾기
    print("📂 이미지 파일 검색 중...")
    image_paths = []
    for folder in source_folders:
        folder_path = Path(folder)
        for ext in extensions:
            image_paths.extend(list(folder_path.rglob(f"*{ext}")))
    
    # 중복 및 시스템 파일 제거
    image_paths = sorted(list(set([p for p in image_paths if not p.name.startswith('._')])))
    print(f"✓ 총 {len(image_paths)}개 이미지 발견")

    if not image_paths:
        print("❌ 처리할 이미지가 없습니다.")
        return

    # 2.5 메타데이터 미리 로드
    metadata_path = output_dir / "public" / "data" / "image_metadata.json"
    metadata_map = {}
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            meta_json = json.load(f)
            for item in meta_json:
                metadata_map[item['filename']] = item
    else:
        print("⚠️ image_metadata.json 파일을 찾을 수 없습니다. 타입 분류가 정확하지 않을 수 있습니다.")

    # 3. 특징 추출 (Feature Extraction) & Zero-shot Classification 준비
    print("🧠 특징 추출 및 Zero-shot Classification 중...")
    
    # 클래스 정의 (Zero-shot) - 클러스터링 확장
    class_names = ["exterior", "interior", "aerial", "nature"]
    class_prompts = [
        "exterior architecture photo", 
        "interior design photo", 
        "aerial view of city or building plan", 
        "nature landscape, forest, or mountains"
    ]
    
    # 텍스트 특징 미리 계산
    try:
        text_inputs = processor(text=class_prompts, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            text_outputs = model.get_text_features(**text_inputs)
            
            # 텍스트 출력 처리
            if not isinstance(text_outputs, torch.Tensor):
                if hasattr(text_outputs, 'text_embeds'):
                    text_features = text_outputs.text_embeds
                elif hasattr(text_outputs, 'pooler_output'):
                    text_features = text_outputs.pooler_output
                else:
                    text_features = text_outputs
            else:
                text_features = text_outputs

            # 정규화
            import torch.nn.functional as F
            text_features = F.normalize(text_features, p=2, dim=-1)
            print("✓ 텍스트 특징 추출 완료")
            
    except Exception as e:
        print(f"⚠️ 텍스트 특징 추출 실패: {e}")
        import traceback
        traceback.print_exc()
        text_features = None

    features_list = []
    valid_images = []
    classified_types = [] # 새로 분류된 타입 저장
    
    batch_size = 32
    
    for i in tqdm(range(0, len(image_paths), batch_size)):
        batch_paths = image_paths[i:i + batch_size]
        batch_images = []
        current_batch_indices = []
        
        for idx, path in enumerate(batch_paths):
            try:
                image = Image.open(path).convert('RGB')
                batch_images.append(image)
                current_batch_indices.append(idx)
            except Exception as e:
                print(f"⚠️ 이미지 로드 실패 ({path.name}): {e}")
        
        if not batch_images:
            continue

        try:
            inputs = processor(images=batch_images, return_tensors="pt", padding=True).to(device)
            with torch.no_grad():
                outputs = model.get_image_features(**inputs)
            
            # If outputs is not a tensor, try to extract the tensor
            if not isinstance(outputs, torch.Tensor):
                if hasattr(outputs, 'image_embeds'):
                    outputs = outputs.image_embeds
                elif hasattr(outputs, 'pooler_output'):
                    outputs = outputs.pooler_output
            
            # 정규화
            import torch.nn.functional as F
            image_features = F.normalize(outputs, p=2, dim=-1)
            
            features_list.append(image_features.cpu().numpy())
            
            # Zero-shot Classification 수행
            if text_features is not None:
                # Similarity: (Batch, Feature) @ (Feature, Classes).T = (Batch, Classes)
                similarity = (image_features @ text_features.T).softmax(dim=-1)
                top_class_indices = similarity.argmax(dim=-1)
                
                for class_idx in top_class_indices:
                    classified_types.append(class_names[class_idx.item()])
            else:
                # 텍스트 특징 없으면 기본값
                for _ in range(image_features.shape[0]):
                    classified_types.append("other")

            # 유효한 이미지 정보 저장
            for idx in current_batch_indices:
                valid_images.append(batch_paths[idx])
                
        except Exception as e:
            print(f"⚠️ 배치 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    if not features_list:
        print("❌ 추출된 특징이 없습니다.")
        return

    all_features = np.concatenate(features_list, axis=0)
    print(f"✓ 특징 추출 완료: {all_features.shape}")

    # 4. 차원 축소 (UMAP)
    print("📉 UMAP으로 3차원 차원 축소 중...")
    try:
        reducer = umap.UMAP(n_components=3, random_state=42, n_neighbors=15, min_dist=0.1)
        embedding = reducer.fit_transform(all_features)
    except Exception as e:
        print(f"❌ UMAP 오류: {e}")
        return

    # 5. 좌표 정규화 (-50 ~ 50 범위로 조정)
    scaler = MinMaxScaler(feature_range=(-50, 50))
    embedding_scaled = scaler.fit_transform(embedding)

    # 6. 결과 저장 (JSON)
    print("💾 데이터 저장 중...")
    output_data = []

    for i, path in enumerate(valid_images):
        filename = path.name
        
        # 메타데이터 매칭 - 파일명 기준 (기존 정보)
        meta = metadata_map.get(filename, {})
        
        # ⚠️ 중요: Zero-shot Classification 결과 우선 사용
        # 기존 메타데이터가 'exterior' (기본값) 이거나 'other' 인 경우, 새로 분류된 결과를 사용
        old_type = meta.get('type', 'other')
        new_type = classified_types[i]
        
        if old_type in ['exterior', 'other'] and new_type != 'other':
            img_type = new_type
            # 덮어쓰기 로깅 (선택사항)
            # if i < 5: print(f"Update: {filename[:20]}... {old_type} -> {new_type}")
        else:
            img_type = old_type

        is_architecture = meta.get('is_architecture', True)
        description = meta.get('description', '')
        
        # 썸네일 경로 결정 우선순위:
        # 1. 메타데이터에 있는 path (가장 정확)
        # 2. config의 source_folder 기준 상대 경로
        if 'path' in meta:
            rel_path = meta['path']
        else:
            try:
                # E:\4. Midjourney\Midjourney 8\... -> Midjourney 8\...
                # source_folders[0]의 부모 디렉토리를 기준으로 상대 경로 계산
                rel_path = str(path.relative_to(Path(source_folders[0]).parent)).replace('\\', '/')
            except:
                rel_path = str(path).replace('\\', '/')

        output_data.append({
            "id": i,
            "x": float(embedding_scaled[i, 0]),
            "y": float(embedding_scaled[i, 1]),
            "z": float(embedding_scaled[i, 2]),
            "filename": filename,
            "path": rel_path,
            "type": img_type,
            "is_architecture": is_architecture,
            "description": description
        })

        output_data.append({
            "id": i,
            "x": float(embedding_scaled[i, 0]),
            "y": float(embedding_scaled[i, 1]),
            "z": float(embedding_scaled[i, 2]),
            "filename": filename,
            "path": rel_path,
            "type": img_type,
            "is_architecture": is_architecture,
            "description": description
        })

    output_file = output_dir / "public" / "data" / "coordinates.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 완료! 파일 저장됨: {output_file}")

if __name__ == "__main__":
    main()
