# LangGraph 기반 운동 추천 멀티 에이전트 실습

## 프로젝트 소개

이 프로젝트는 `LangGraph`를 활용하여 사용자의 질문을 단계별로 처리하는 멀티 에이전트 워크플로우 실습 프로젝트입니다.

사용자가 자신의 상태나 고민을 입력하면, 시스템은 다음과 같은 흐름으로 답변을 생성합니다.

1. 사용자의 질문에서 증상 또는 문제점 추출
2. 추출된 증상을 바탕으로 운동 리스트 추천
3. 증상 요약과 추천 운동을 개조식으로 정리한 최종 답변 생성

이 프로젝트는 OpenAI API가 아닌 로컬 환경의 `Ollama`와 `llama3.2` 모델을 사용하여 실행되도록 구성되어 있습니다.

---

## 사용 기술

- Python
- LangGraph
- LangChain
- Ollama
- llama3.2

---

## 프로젝트 구조


주요 코드는 하나의 Python 파일로 구성되어 있으며, LangGraph의 StateGraph를 이용해 에이전트 간의 실행 흐름을 정의합니다.

---

## 사용자 질문
   ↓
[추출 에이전트]
   ↓
[후보 에이전트]
   ↓
[답변 생성 에이전트]
   ↓
최종 답변


---

## 주요 기능
1. 증상 추출 에이전트

사용자의 질문에서 현재 겪고 있는 증상이나 문제점을 추출합니다.

예시 입력: 체력이 안좋고, 살이 계속 찌는데 어떤 운동을 할까?

추출 대상: 체력 저하, 체중 증가



2. 운동 추천 에이전트

추출된 증상을 바탕으로 도움이 될 수 있는 운동 리스트를 추천합니다.

예상 추천 운동:
- 걷기
- 가벼운 조깅
- 스쿼트
- 홈트레이닝
- 근력 운동

3. 최종 답변 생성 에이전트
사용자의 증상과 추천 운동을 바탕으로 최종 답변을 생성합니다.

최종 답변은 다음 형식으로 작성됩니다.

- 증상 요약
- 추천 운동

---

## 코드 설명
State 정의
```python
class AgentState(TypedDict):
    query: str
    symptoms: str
    exercises: str
    final_answer: str
```

AgentState는 각 에이전트가 주고받는 데이터의 구조를 정의합니다.


| 필드명            | 설명         |
| -------------- | ---------- |
| `query`        | 사용자의 초기 질문 |
| `symptoms`     | 추출된 증상     |
| `exercises`    | 추천된 운동 리스트 |
| `final_answer` | 최종 답변      |


## 에이전트 구성
1. Extractor Agent
```python
def extract_symptoms(state: AgentState):
```
사용자의 질문에서 증상이나 문제점을 추출하는 역할을 합니다.

2. Recommender Agent
```python
def recommend_exercises(state: AgentState):
```
추출된 증상을 바탕으로 적절한 운동 리스트를 추천합니다.


3. Generator Agent
```python
def generate_response(state: AgentState):
```

증상 요약과 추천 운동을 바탕으로 사용자에게 보여줄 최종 답변을 생성합니다.


---

## 그래프 구성
```python
workflow = StateGraph(AgentState)

workflow.add_node("extractor", extract_symptoms)
workflow.add_node("recommender", recommend_exercises)
workflow.add_node("generator", generate_response)

workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "recommender")
workflow.add_edge("recommender", "generator")
workflow.add_edge("generator", END)

app = workflow.compile()
```
LangGraph의 StateGraph를 사용하여 각 에이전트를 노드로 추가하고, 순차적인 실행 흐름을 정의합니다.


---

## 실행 예시
```python
user_query = "체력이 안좋고, 살이 계속 찌는데 어떤 운동을 할까?"

initial_state = {"query": user_query}
result = app.invoke(initial_state)

print(result["final_answer"])
```

## 실행 결과 예시
```python
[사용자 질문] 체력이 안좋고, 살이 계속 찌는데 어떤 운동을 할까?

--------------------------------------------------
▶ [추출 에이전트] 증상 추출 중...
▶ [후보 에이전트] 운동 리스트 추천 중...
▶ [답변 생성 에이전트] 최종 답변 작성 중...
--------------------------------------------------

[최종 답변]

- 증상 요약
  - 체력이 부족함
  - 체중이 계속 증가하고 있음

- 추천 운동
  - 가벼운 걷기부터 시작하기
  - 유산소 운동으로 체지방 감량하기
  - 스쿼트, 런지 등 하체 근력 운동 병행하기
  - 주 3~4회 꾸준히 운동하기
```

---

## 실행 방법
1. Ollama 설치

먼저 로컬 환경에 Ollama를 설치합니다.

2. llama3.2 모델 다운로드

터미널에서 다음 명령어를 실행합니다.
ollama pull llama3.2

3. 필요한 라이브러리 설치
pip install langgraph langchain langchain-community

4. Python 파일 실행
python langgraph_practice.py


---

## 프로젝트 특징
- OpenAI API Key 없이 로컬 LLM으로 실행 가능
- LangGraph의 기본 구조를 이해하기 쉬운 예제
- State, Node, Edge 개념을 실습할 수 있음
- 여러 에이전트가 순차적으로 협업하는 구조 구현
- 증상 분석과 운동 추천이라는 직관적인 예제로 구성

## 향후 개선 방향
- 사용자 입력을 직접 받을 수 있도록 input() 기능 추가
- 운동 추천 결과를 더 구체적인 루틴 형태로 개선
- 사용자의 운동 목적에 따라 분기 처리 추가
- 다이어트
- 근력 향상
- 체력 증진
- 재활 운동
- 조건부 Edge를 활용한 LangGraph 고급 워크플로우 구현
- Streamlit을 활용한 웹 애플리케이션 제작





