import json

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from core.summarizer import get_llm


class MindMapNode(BaseModel):
    topic: str
    children: list["MindMapNode"] = Field(default_factory=list)


class MindMap(BaseModel):
    title: str
    branches: list[MindMapNode]


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str
    explanation: str


class Quiz(BaseModel):
    questions: list[QuizQuestion]


def _generate_structured(transcript: str, instructions: str, output_model):
    if not transcript.strip():
        raise ValueError("Transcript is empty.")

    parser = PydanticOutputParser(pydantic_object=output_model)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{instructions}\n\n"
                "Use only facts supported by the transcript. "
                "Do not invent information.\n\n"
                "{format_instructions}",
            ),
            ("human", "Transcript:\n{transcript}"),
        ]
    )

    chain = prompt | get_llm() | parser

    return chain.invoke(
        {
            "instructions": instructions,
            "format_instructions": parser.get_format_instructions(),
            "transcript": transcript,
        }
    )


def generate_mindmap(transcript: str) -> dict:
    mindmap = _generate_structured(
        transcript,
        (
            "Create a clear educational mind map for this video. "
            "Return one central title and 4 to 7 main branches. "
            "Each branch may have nested subtopics. "
            "Keep topics short and make the hierarchy easy to study."
        ),
        MindMap,
    )

    if not mindmap.branches:
        raise ValueError("The model returned a mind map without branches.")

    return json.loads(mindmap.json())


def generate_quiz(transcript: str) -> dict:
    quiz = _generate_structured(
        transcript,
        (
            "Create exactly 5 multiple-choice questions about the video. "
            "Each question must have exactly 4 answer options. "
            "The correct_answer must exactly match one of its options. "
            "Include a short explanation for the correct answer. "
            "Mix basic recall and understanding questions."
        ),
        Quiz,
    )

    if len(quiz.questions) != 5:
        raise ValueError("The model did not return exactly 5 quiz questions.")

    for question in quiz.questions:
        if len(question.options) != 4:
            raise ValueError("A quiz question did not have exactly 4 options.")
        if question.correct_answer not in question.options:
            raise ValueError("A quiz answer did not match one of its options.")

    return json.loads(quiz.json())