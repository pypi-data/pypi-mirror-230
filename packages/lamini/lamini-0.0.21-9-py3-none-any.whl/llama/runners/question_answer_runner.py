from typing import List
from llama import Type, Context, LLMEngine
import jsonlines
import pandas as pd


# Input
class Question(Type):
    question: str = Context("a question")


# Output
class Answer(Type):
    answer: str = Context("the response to the question")


class QuestionAnswerModel:
    """A class for running and training a question answering model"""

    def __init__(
        self,
        model_name: str = "EleutherAI/pythia-410m-deduped",
        task_name: str = "question_answer_runner_data",
        config={},
        enable_peft=False,
    ):
        self.model_name = model_name
        self.task_name = task_name
        self.config = config
        self.llm = LLMEngine(id=self.task_name, model_name=self.model_name, config=self.config)
        
        self.question_answer = []
        self.job_id = None
        self.enable_peft = enable_peft
        
        self.evaluation_results = None

    def get_answer(
        self,
        question: str,
    ) -> str:
        """Get answer to a single question"""
        question_object = Question(question=question)
        answer_object = self.llm(
            input=question_object,
            output_type=Answer,
            model_name=self.model_name,
            task="question_answer",  # this maps onto a prompt template, not to be confused with task_name
            enable_peft=self.enable_peft,
        )
        return answer_object.answer

    def get_answers(self, questions: List[str]) -> List[str]:
        """Get answers to a batch of questions"""
        print("Asking %d questions" % len(questions))
        question_objects = [Question(question=q) for q in questions]
        answer_objects = self.llm(
            input=question_objects,
            output_type=Answer,
            model_name=self.model_name,
            task="question_answer", # this maps onto a prompt template, not to be confused with task_name
            enable_peft=self.enable_peft,
        )
        answers = [a.answer for a in answer_objects]
        return [{"question": q, "answer": a} for q, a in zip(questions, answers)]

    def load_question_answer(self, data, question_key="question", answer_key="answer"):
        """
        Load a list of json objects with question answer keys into the LLM
        Each object must have 'question' and 'answer' as keys.
        """
        try:
            question_answer_objects = [
                [Question(question=d[question_key]), Answer(answer=d[answer_key])]
                for d in data
            ]
        except KeyError:
            raise ValueError("Each object must have 'question' and 'answer' as keys")
        self.question_answer.extend(question_answer_objects)

    def load_question_answer_from_jsonlines(self, file_path: str, question_key="question", answer_key="answer"):
        """
        Load a jsonlines file with question answer keys into the LLM.
        Each line must be a json object with 'question' and 'answer' as keys.
        """
        data = []
        with open(file_path) as dataset_file:
            reader = jsonlines.Reader(dataset_file)
            data = list(reader)
        self.load_question_answer(data, question_key, answer_key)

    def load_question_answer_from_dataframe(self, df: pd.DataFrame, question_key="question", answer_key="answer"):
        """
        Load a pandas dataframe with question answer keys into the LLM.
        Each row must have 'question' as a key.
        """
        try:
            for _, row in df.iterrows():
                self.question_answer.append(
                    [Question(question=row[question_key]), Answer(answer=row[answer_key])]
                )
        except KeyError:
            raise ValueError("Each object must have 'question' and 'answer' as keys")

    def load_question_answer_from_csv(self, file_path: str, question_key="question", answer_key="answer"):
        """
        Load a csv file with question answer keys into the LLM.
        Each row must have 'question' and 'answer' as keys.
        """
        df = pd.read_csv(file_path)
        self.load_question_answer_from_dataframe(df, question_key=question_key, answer_key=answer_key)

    def clear_data(self):
        """Clear the data from the LLM"""
        self.llm.clear_data()
        self.question_answer = []

    def train(
        self,
        verbose: bool = False,
        limit=500,
        is_public=False,
        **kwargs,
    ):
        """
        Train the LLM on added data. This function blocks until training is complete.
        """
        if len(self.question_answer) < 2:
            raise Exception("Submit at least 2 question answer pairs to train to allow validation")
        if limit is None:
            qa_pairs = self.question_answer
        elif len(self.question_answer) > limit:
            qa_pairs = self.question_answer[:limit]
        else:
            qa_pairs = self.question_answer

        final_status = self.llm.train(
            qa_pairs,
            task="question_answer", # this maps onto a prompt template, not to be confused with task_name
            **kwargs,
        )
        try:
            self.model_name = final_status["model_name"]
            self.job_id = final_status["job_id"]
            self.llm.clear_data()
        except KeyError:
            raise Exception("Training failed")

        return final_status

    def evaluate(self) -> List:
        """Get evaluation results"""
        self.evaluation_results = self.llm.evaluate()
        return self.evaluation_results

    def get_eval_results(self) -> List:
        if self.job_id is None:
            raise Exception("Must train before getting results (no job id))")
        return self.llm.eval(self.job_id)
