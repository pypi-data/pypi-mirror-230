from ..singleton import Singleton
from ..test_case import LLMTestCase
from ..run_test import assert_test
from .metric import Metric


class AnswerRelevancyModel(metaclass=Singleton):
    def __init__(self):
        from sentence_transformers import SentenceTransformer

        # Load the model
        self.model = SentenceTransformer(
            "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
        )

    def encode(self, text):
        return self.model.encode(text)


class AnswerRelevancyMetric(Metric):
    def __init__(self, minimum_score: bool = 0.5):
        self.minimum_score = minimum_score
        self.model = AnswerRelevancyModel()

    def __call__(self, test_case: LLMTestCase):
        score = self.measure(test_case.query, test_case.output)
        self.success = score > self.minimum_score
        return score

    def measure(self, test_case: LLMTestCase) -> float:
        from sentence_transformers import util

        if test_case.query is None or test_case.output is None:
            raise ValueError("query and output cannot be None")

        docs = [test_case.output]

        # Encode query and documents
        query_emb = self.model.encode(test_case.query)
        doc_emb = self.model.encode(docs)

        # Compute dot score between query and all document embeddings
        scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()
        score = scores[0]
        self.success = score > self.minimum_score
        # Log answer relevancy
        return score

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "Answer Relevancy"


def assert_answer_relevancy(
    query: str, output: str, minimum_score: float = 0.5
):
    metric = AnswerRelevancyMetric(minimum_score=minimum_score)
    test_case = LLMTestCase(query=query, output=output)
    assert_test(test_case, metrics=[metric])
