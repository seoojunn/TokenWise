# 🪙 Tokenwise (토큰와이즈)

Tokenwise는 OpenAI, Gemini, Groq 등 다양한 대형 언어 모델(LLM)을 효율적으로 관리하고, 상황에 맞는 최적의 모델로 요청을 동적으로 분기하는 Intelligent LLM Routing 시스템입니다.

## 🚀 Features (주요 기능)
* **Multi-LLM Routing**: 입력 쿼리의 특성에 따라 OpenAI, Gemini, Groq 등 가장 적합한 API 모델로 동적 라우팅 (`router.py`)
* **Cost & Token Optimization**: 토큰 사용량 및 비용을 고려한 최적의 추론 모델 선택
* **Secure Key Management**: `.env` 파일과 가상환경을 통한 안전한 API 키 및 환경 변수 관리

## 🛠️ Tech Stack (기술 스택)
* **Language**: Python 3.9+
* **APIs**: OpenAI API, Google Gemini API, Groq API
* **Libraries**: python-dotenv, openai, google-generativeai, groq

---

## ⚙️ Installation & Setup (설치 및 실행 방법)

이 프로젝트를 로컬 환경에서 설치하고 실행하기 위한 순서입니다. 안정적인 의존성 관리를 위해 가상환경(venv) 사용을 권장합니다.

### 1. 사전 준비 (Prerequisites)
프로젝트 실행을 위해 아래 플랫폼에서 각각 API 키를 발급받아야 합니다.
* [OpenAI API Key](https://platform.openai.com/)
* [Gemini API Key](https://aistudio.google.com/)
* [Groq API Key](https://console.groq.com/)

### 2. 프로젝트 다운로드 및 이동
터미널을 열고 저장소를 클론한 뒤 프로젝트 디렉토리로 이동합니다.

```bash
# 저장소 복제
git clone [https://github.com/username/tokenwise.git](https://github.com/username/tokenwise.git)

# 프로젝트 폴더로 이동
cd tokenwise
```

### 3. 가상환경 생성 및 활성화 (권장)
다른 프로젝트와의 라이브러리 충돌을 방지하기 위해 가상환경을 생성합니다.

* **Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

* **Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. 필수 패키지 설치
프로젝트 구동 및 각종 LLM API 연동에 필요한 라이브러리를 설치합니다.

```bash
# 패키지 개별 설치 시
pip install python-dotenv openai google-generativeai groq

# 또는 requirements.txt 파일이 있는 경우 일괄 설치
pip install -r requirements.txt
```

### 5. 환경 변수 및 보안 설정 (`.env`)
프로젝트 최상위(루트) 디렉토리에 `.env` 파일을 생성하고 발급받은 API 키를 입력합니다.

> 🚨 **보안 주의:** `.env` 파일에는 개인 비밀키가 포함되므로 절대 GitHub 등 원격 저장소에 업로드하지 마세요. 소스 제어에서 제외하기 위해 `.gitignore` 파일에 반드시 `.env`가 추가되어 있는지 확인하세요.

```env
# .env
OPENAI_API_KEY="your_actual_openai_api_key_here"
GEMINI_API_KEY="your_actual_gemini_api_key_here"
GROQ_API_KEY="your_actual_groq_api_key_here"
```

### 6. 실행 확인
환경 설정이 완료되면 메인 스크립트를 실행하여 라우팅 시스템이 정상 작동하는지 확인합니다.

```bash
python main.py
```

---

## 💻 Usage (사용 방법)

```python
# main.py 또는 실행 예시 코드
from router import TokenRouter

# 라우터 초기화
router = TokenRouter()

# 쿼리에 따른 대형 언어 모델 호출 예시
response = router.generate_response(prompt="Hello, world!", model="gemini")
print(response)
```

## 🤝 Contributing (기여 방법)
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License (라이선스)
Distributed under the MIT License. See `LICENSE` for more information.
