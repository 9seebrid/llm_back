import os # 파일 경로 설정 등에 사용
import io # 입출력을 위한 모듈
import sys # 파이썬 인터프리터가 제공하는 변수와 함수를 직접 제어할 수 있게 해주는 모듈
import openai
from dotenv import load_dotenv
from langchain import hub
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from collections import Counter
from langchain_core.prompts import PromptTemplate

load_dotenv()
client = openai.Client(api_key = os.getenv("OPENAI_API_KEY")) # 환경변수에 저장된 API_KEY를 사용

# 경로 추적을 위한 설정
os.environ["PWD"] = os.getcwd() # 현재 작업 디렉토리를 설정
# print("Current working directory:", os.getcwd())

#출력의 인코딩을 utf-8로 설정한다
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# 문서 로드
loader = DirectoryLoader('./data', glob="*.txt", loader_cls=TextLoader) # 경로, 타입, 사용 함수
documents = loader.load()
# print(len(documents))

# 문서 분할
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap =200 ) # 분할 토큰수(chunk), 오버랩 정도
texts = text_splitter.split_documents(documents)
# print(f"분할된 텍스트 뭉치의 개수: {len(texts)}")

# source_list = []
# for i in range(0, len(texts)):
#   source_list.append(texts[i].metadata["source"])


# element_counts = Counter(source_list)
# filtered_counts = {key: value for key, value in element_counts.items() if value >= 2}

# print("2개 이상으로 분할된 문서: ", filtered_counts)
# print("분할된 텍스트의 개수: ", len(documents) + len(filtered_counts))

# 임베딩을 사용하여 문서를 벡터화
embeddings = OpenAIEmbeddings()
vectordb =FAISS.from_documents(documents=texts, embedding=embeddings) # 벡터화할 문서, 임베팅 메서드
retriever = vectordb.as_retriever() # 검색기 생성
# print(texts[0])

# retriever = vectordb.as_retriever() # 검색기 생성
# docs = retriever.get_relevant_documents("신혼부부를 위한 정책을 알려주세요") # 검색 결과

# print(f"유사도 높은 텍스트 개수 : {len(docs)}")
# print("-" * 50)
# print(f"유사도 높은 텍스트 중 첫번째 텍스트 출력 : {docs[0]}")
# print("-" * 50)
# print("출처: ")
# for doc in docs:
#     print(doc.metadata['source'])

# qa_chain = RetrievalQA.from_chain_type(
#     llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0), # llm 모델 버전, 온도(0 이상인 값. 0 - FM대로 말한다. 수치가 높아지면 창의적으로 답한다.)
#     chain_type="stuff",
#     retriever=retriever,
#     return_source_documents=True
# ) # llm 모델 호출 메서드, 체인 타입, 검색문서(벡터), 반환문서(True)

# OpenAI Chat API를 사용하여 질문-답변을 수행하는 체인을 생성, 대화 모델 생성, 사전 주문 및 생성
prompt = PromptTemplate.from_template(
    """당신은 질문-답변(Question-Answering)을 수행하는 친절한 AI 어시스턴트입니다. 당신의 임무는 주어진 문맥(context) 에서 주어진 질문(question) 에 답하는 것입니다.
검색된 다음 문맥(context) 을 사용하여 질문(question) 에 답하세요. 만약, 주어진 문맥(context) 에서 답을 찾을 수 없다면, 답을 모른다면 `주어진 정보에서 질문에 대한 정보를 찾을 수 없습니다` 라고 답하세요.
한글로 답변해 주세요. 단, 기술적인 용어나 이름은 번역하지 않고 그대로 사용해 주세요. 답변은 3줄 이내로 요약해 주세요.

#Question:
{question}

#Context:
{context}

#Answer:"""
)

llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0) # llm 모델 버전, 온도(0 이상인 값. 0 - FM대로 말한다. 수치가 높아지면 창의적으로 답한다.)

# 체인을 생성합니다.
# RunnablesPassThrough는 입력값을 그대로 전달하는 역할. invoke 메서드를 사용하여 질문을 전달하면, 질문을 그대로 반환
# StrOputputParser() : LLM이나 ChatModel에서 나오는 언어 모델의 출력을 문자열 형식으로 변환

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

from langchain_teddynote.messages import stream_response

recieved_question = sys.argv[1]
# print("질문: ", recieved_question)

answer = rag_chain.stream(recieved_question) # 질문을 전달
stream_response(answer)

# print(answer)


