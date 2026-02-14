import google.generativeai as genai

genai.configure(api_key="AIzaSyCahrdW3NG8MC-YUFkRTn0i8v4p3N40H-I")

print("사용 가능한 모델:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
