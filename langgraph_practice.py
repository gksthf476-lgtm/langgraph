import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOllama # (변경됨) OpenAI 대신 Ollama 임포트
from langchain_core.messages import SystemMessage, HumanMessage

# ==========================================
# 0. 환경 변수 및 LLM 설정
# ==========================================
# OpenAI API 키 설정 부분은 아예 지워버려도 돼! (필요 없음)

# LLM 초기화 (네 컴퓨터에 설치된 Ollama와 llama3.2 모델을 연결)
llm = ChatOllama(model="llama3.2", temperature=0)

# ==========================================
# 이하 코드(상태 정의 및 노드 정의 부분)는 이전과 100% 동일하게 진행하면 돼!

# ==========================================
# 1. 상태(State) 정의
# ==========================================
# 에이전트들끼리 주고받을 데이터의 구조를 정의합니다.
class AgentState(TypedDict):
    query: str          # 사용자의 초기 질문
    symptoms: str       # 추출된 증상
    exercises: str      # 추천된 운동 리스트
    final_answer: str   # 최종 개조식 답변

# ==========================================
# 2. 노드(에이전트) 정의
# ==========================================

# 노드 1: 추출 에이전트 (증상 추출)
def extract_symptoms(state: AgentState):
    print("▶ [추출 에이전트] 증상 추출 중...")
    messages = [
        SystemMessage(content="사용자의 질문에서 현재 겪고 있는 증상이나 문제점을 명확하게 추출하세요."),
        HumanMessage(content=state["query"])
    ]
    response = llm.invoke(messages)
    return {"symptoms": response.content}

# 노드 2: 후보 에이전트 (운동 리스트 추천)
def recommend_exercises(state: AgentState):
    print("▶ [후보 에이전트] 운동 리스트 추천 중...")
    messages = [
        SystemMessage(content="주어진 증상을 해결하는 데 도움이 되는 구체적인 운동 리스트를 추천하세요."),
        HumanMessage(content=f"증상: {state['symptoms']}")
    ]
    response = llm.invoke(messages)
    return {"exercises": response.content}

# 노드 3: 답변 생성 에이전트 (최종 답변 포맷팅)
def generate_response(state: AgentState):
    print("▶ [답변 생성 에이전트] 최종 답변 작성 중...")
    messages = [
        SystemMessage(content="""
        당신은 친절한 헬스 트레이너입니다. 
        사용자의 증상과 추천 운동 리스트를 바탕으로 최종 답변을 작성하세요.
        반드시 '증상 요약'과 '추천 운동'을 나누어 **개조식(Bullet points, -, * 등 사용)**으로 간결하게 작성해야 합니다.
        """),
        HumanMessage(content=f"증상:\n{state['symptoms']}\n\n추천 운동:\n{state['exercises']}")
    ]
    response = llm.invoke(messages)
    return {"final_answer": response.content}

# ==========================================
# 3. 그래프(워크플로우) 구성
# ==========================================
workflow = StateGraph(AgentState)

# 그래프에 노드(에이전트) 추가
workflow.add_node("extractor", extract_symptoms)
workflow.add_node("recommender", recommend_exercises)
workflow.add_node("generator", generate_response)

# 노드 간의 연결(Edge) 설정 - 순차적 흐름
workflow.set_entry_point("extractor")          # 시작점
workflow.add_edge("extractor", "recommender")  # 추출 -> 추천
workflow.add_edge("recommender", "generator")  # 추천 -> 생성
workflow.add_edge("generator", END)            # 생성 -> 종료

# 그래프 컴파일 (실행 가능한 앱으로 변환)
app = workflow.compile()

# ==========================================
# 4. 실행 및 결과 확인
# ==========================================
if __name__ == "__main__":
    # 사용자 질문
    user_query = "체력이 안좋고, 살이 계속 찌는데 어떤 운동을 할까?"
    
    print(f"\n[사용자 질문] {user_query}\n")
    print("-" * 50)
    
    # 초기 상태(State) 주입하여 워크플로우 실행
    initial_state = {"query": user_query}
    result = app.invoke(initial_state)
    
    print("-" * 50)
    print("\n✅ [최종 답변]\n")
    print(result["final_answer"])