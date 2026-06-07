
"""
总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model

import jieba
from rank_bm25 import BM25Okapi
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

        self.rerank_model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-base')
        self.rerank_tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-base')
        self.rerank_model.eval() # 推理模式

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    def bm25_retrieve(self, query: str, docs: list[Document], topk:int = 10):
        corpus_tokens = [jieba.lcut(doc.page_content) for doc in docs]
        query_tokens = jieba.lcut(query)
        bm25 = BM25Okapi(corpus_tokens)

        return bm25.get_top_n(query_tokens, docs, n=topk)
    
    def bge_rerank(self, query: str, docs: list[Document], topk: int = 3):
        """
        BGE重排：原生Transformers实现（修复版）
        """
        if not docs:
            return []
        
        # 构造问题-文档对
        pairs = [[query, doc.page_content] for doc in docs]
        # 批量编码
        inputs = self.rerank_tokenizer(pairs, padding=True, truncation=True, return_tensors="pt", max_length=512)
        # 计算相似度分数
        scores = self.rerank_model(**inputs, return_dict=True).logits.view(-1).float().tolist()
        
        # 按分数排序
        ranked_docs = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
        return [doc for score, doc in ranked_docs[:topk]]

    def retriever_docs(self, query: str) -> list[Document]:
        """
        优化版：BM25关键词 + 向量检索 + BGE重排
        """
        # 1. 先拉取候选文档
        candidate_docs = self.retriever.invoke(query)
        
        # 2. 两路召回：BM25(关键词) + 向量(语义)
        bm25_docs = self.bm25_retrieve(query, candidate_docs, topk=10)
        vector_docs = self.retriever.invoke(query)
        
        # 3. 合并去重
        combined_docs = []
        content_set = set()
        for doc in bm25_docs + vector_docs:
            if doc.page_content not in content_set:
                content_set.add(doc.page_content)
                combined_docs.append(doc)
        
        # 4. BGE重排，返回最终结果
        final_docs = self.bge_rerank(query, combined_docs, topk=3)
        
        return final_docs

    def rag_summarize(self, query: str) -> str:

        context_docs = self.retriever_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )


if __name__ == '__main__':
    rag = RagSummarizeService()

    print(rag.rag_summarize("滚刷脏了怎么清理"))
