import os
import math
from fastapi import FastAPI
from pydantic import BaseModel
from litellm import completion, embedding
from pypdf import PdfReader

# ==========================================
# 🔑 API 키 셋업
# ==========================================
os.environ["GROQ_API_KEY"] = "발급받은 api키는 여기에"
os.environ["GEMINI_API_KEY"] = "발급받은 api키는 여기에"

app = FastAPI(title="Tokenwise 지능형 라우터 API")

class QueryRequest(BaseModel):
    user_query: str

# ==========================================
# 🏫 [RAG 시스템] 학칙 PDF 추출 및 벡터화
# ==========================================
def extract_and_chunk_pdf(file_path, chunk_size=500, overlap=100):
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        if page.extract_text():
            full_text += page.extract_text() + "\n"
            
    chunks = []
    for i in range(0, len(full_text), chunk_size - overlap):
        chunk = full_text[i:i + chunk_size].strip()
        if len(chunk) > 50: 
            chunks.append(chunk)
    return chunks

def get_embedding(text: str):
    # 💡 최신 권장 모델명으로 교체!
    response = embedding(model="gemini/gemini-embedding-001", input=[text])
    return response.data[0]['embedding']

def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    return dot_product / (norm_a * norm_b)

# 서버 구동 시 PDF 로드 및 임베딩 (최초 1회)
PDF_FILE_NAME = "school_rules.pdf"
print("📚 [RAG 시스템] 학칙 PDF 벡터화 중... (최초 1회만 실행됩니다)")
try:
    ACADEMIC_DOCS = extract_and_chunk_pdf(PDF_FILE_NAME)
    DOC_EMBEDDINGS = [get_embedding(doc) for doc in ACADEMIC_DOCS]
    print(f"✅ 총 {len(ACADEMIC_DOCS)}개의 학칙 조각이 준비되었습니다!")
except Exception as e:
    print(f"⚠️ 에러: '{PDF_FILE_NAME}' 파일을 찾을 수 없거나 읽을 수 없습니다. 가짜 데이터로 대체합니다.")
    ACADEMIC_DOCS = ["제1조: 수강신청은 개강 2주 전입니다.", "제2조: 졸업은 130학점 필요합니다."]
    DOC_EMBEDDINGS = [get_embedding(doc) for doc in ACADEMIC_DOCS]

def generate_academic_answer(user_query: str):
    query_embedding = get_embedding(user_query)
    similarities = [cosine_similarity(query_embedding, doc_emb) for doc_emb in DOC_EMBEDDINGS]
    best_match_index = similarities.index(max(similarities))
    retrieved_text = ACADEMIC_DOCS[best_match_index]
    
    print(f"📄 [RAG 검색 완료] 참조 문서 발췌: {retrieved_text[:50]}...")
    
    system_prompt = f"""
    너는 대학교 학사행정 AI 조수야.
    반드시 아래 제공된 [학칙 문서]의 내용만을 바탕으로 대답해.
    문서에 없는 내용을 묻는다면 "해당 내용은 학칙 규정에서 찾을 수 없습니다"라고만 답해.
    
    [학칙 문서]
    {retrieved_text}
    """
    response = completion(
        model="gemini/gemini-2.5-flash", 
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
        temperature=0.0
    )
    return response.choices[0].message.content

# ==========================================
# 1. 문지기 (의도 분류기 - Groq)
# ==========================================
def analyze_intent(user_query: str):
    small_model = "groq/llama-3.1-8b-instant" 
    router_prompt = """
    너는 질문 의도를 분석하는 라우터야. 오직 아래 카테고리 이름 중 하나로만 대답해. 부가 설명 금지.
    1. ACADEMIC : 학사행정 규정, 수강신청, 장학금
    2. ENGINEERING : 코딩, 알고리즘, 공학 등 복잡한 전공 질문
    3. CHITCHAT : 일상 대화, 잡담, 단순 인사

    출력 예시: ENGINEERING
    """
    response = completion(
        model=small_model,
        messages=[{"role": "system", "content": router_prompt}, {"role": "user", "content": user_query}],
        temperature=0.0
    )
    return response.choices[0].message.content.strip().upper().replace(".", "")

# ==========================================
# 2. 해결사 (엔지니어링 담당 - Gemini Flash)
# ==========================================
def generate_expert_answer(user_query: str):
    # 할당량 초과 에러 방지를 위해 Flash 모델 사용
    large_model = "gemini/gemini-2.5-flash" 
    system_prompt = "너는 Tokenwise 프로젝트의 수석 AI 엔지니어야. 논리적이고 전문적으로 답변해."
    response = completion(
        model=large_model,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
        temperature=0.7
    )
    return response.choices[0].message.content

# ==========================================
# 3. 일상 대화 담당 (가벼운 챗봇 - Groq)
# ==========================================
def generate_friendly_answer(user_query: str):
    small_model = "groq/llama-3.1-8b-instant" 
    system_prompt = "너는 지능형 라우팅 및 효율적인 토큰 관리를 돕는 프로젝트 'Tokenwise'의 친절한 AI 어시스턴트야. 다정하고 밝게 대답해줘."
    response = completion(
        model=small_model,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}],
        temperature=0.7 
    )
    return response.choices[0].message.content

# ==========================================
# 4. FastAPI 엔드포인트 (최종 트래픽 제어소)
# ==========================================
@app.post("/chat")
@app.post("/api/chat")
def chat_endpoint(request: QueryRequest):
    user_query = request.user_query
    print(f"\n🚦 [Tokenwise Router] 트래픽 분석 시작: {user_query}")
    
    intent = analyze_intent(user_query)
    print(f"👉 [판별된 카테고리]: {intent}")
    
    if intent == "ENGINEERING":
        print("🤖 [엔지니어 연결] 복잡한 공학 질문 처리 중...")
        answer = generate_expert_answer(user_query)
        used_model = "gemini/gemini-2.5-flash"
        
    elif intent == "CHITCHAT":
        print("🤖 [일반 대화 모드] 가벼운 챗봇 처리 중...")
        answer = generate_friendly_answer(user_query)
        used_model = "groq/llama-3.1-8b-instant"
        
    elif intent == "ACADEMIC":
        print("🤖 [RAG 모드 가동] 학칙 문서 검색 및 답변 생성 중...")
        answer = generate_academic_answer(user_query)
        used_model = "gemini/gemini-2.5-flash (with RAG)"
        
    else:
        answer = "의도를 정확히 파악하지 못했습니다."
        used_model = "None"

    return {
        "status": "success",
        "routing_info": {
            "label": intent,
            "used_model": used_model
        },
        "answer": answer
    }
