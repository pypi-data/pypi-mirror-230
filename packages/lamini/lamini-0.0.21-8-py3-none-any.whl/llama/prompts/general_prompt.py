import logging
from llama.prompts.prompt import BasePrompt

logger = logging.getLogger(__name__)


class GeneralPrompt(BasePrompt):
    prompt_template = """Given:
{input:question.field} ({input:question.context}): {input:question}
Generate:
{output:answer.field} ({output:answer.context}), after "{output:answer.field}:"
{output:answer.field}: """
