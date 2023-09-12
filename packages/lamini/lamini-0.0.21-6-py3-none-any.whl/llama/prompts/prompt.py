from abc import ABCMeta, abstractmethod
from typing import List
from llama import Type
import re

from llama.types.type import Type


class BasePrompt(object, metaclass=ABCMeta):
    prompt_template = ""

    def construct_prompt(
        self,
        input: Type,
        output_type: type,
    ) -> str:
        # Validate that input type matches prompt template
        # Validate that output type matches output prompt template
        # Validate that cue type batches output prompt template

        # Substitute input into prompt template
        hydrated_prompt = self.prompt_template
        x = re.search(r"{#input\((\w+)\)}", hydrated_prompt)
        if x is not None:
            entire_match = x.group(0)
            group_match = x.group(1)
            input_string = self.input_to_str(input)
            hydrated_prompt = hydrated_prompt.replace(entire_match, f"{input_string}")
        # Substitute output into output prompt template
        x = re.search(r"{#output\((\w+)\)}", hydrated_prompt)
        if x is not None:
            entire_match = x.group(0)
            group_match = x.group(1)
            output_string = self.output_to_str(output_type)
            hydrated_prompt = hydrated_prompt.replace(entire_match, f"{output_string}")

        return hydrated_prompt
