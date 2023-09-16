"""**Prompt** is the input to the model.

Prompt is often constructed
from multiple components. Prompt classes and functions make constructing
 and working with prompts easy.

**Class hierarchy:**

.. code-block::

    BasePromptTemplate --> PipelinePromptTemplate
                           StringPromptTemplate --> PromptTemplate
                                                    FewShotPromptTemplate
                                                    FewShotPromptWithTemplates
                           BaseChatPromptTemplate --> AutoGPTPrompt
                                                      ChatPromptTemplate --> AgentScratchPadChatPromptTemplate



    BaseMessagePromptTemplate --> MessagesPlaceholder
                                  BaseStringMessagePromptTemplate --> ChatMessagePromptTemplate
                                                                      HumanMessagePromptTemplate
                                                                      AIMessagePromptTemplate
                                                                      SystemMessagePromptTemplate

    PromptValue --> StringPromptValue
                    ChatPromptValue

"""  # noqa: E501
from langchainmulti.prompts.base import StringPromptTemplate
from langchainmulti.prompts.chat import (
    AIMessagePromptTemplate,
    BaseChatPromptTemplate,
    ChatMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchainmulti.prompts.example_selector import (
    LengthBasedExampleSelector,
    MaxMarginalRelevanceExampleSelector,
    NGramOverlapExampleSelector,
    SemanticSimilarityExampleSelector,
)
from langchainmulti.prompts.few_shot import (
    FewShotChatMessagePromptTemplate,
    FewShotPromptTemplate,
)
from langchainmulti.prompts.few_shot_with_templates import FewShotPromptWithTemplates
from langchainmulti.prompts.loading import load_prompt
from langchainmulti.prompts.pipeline import PipelinePromptTemplate
from langchainmulti.prompts.prompt import Prompt, PromptTemplate
from langchainmulti.schema.prompt_template import BasePromptTemplate

__all__ = [
    "AIMessagePromptTemplate",
    "BaseChatPromptTemplate",
    "BasePromptTemplate",
    "ChatMessagePromptTemplate",
    "ChatPromptTemplate",
    "FewShotPromptTemplate",
    "FewShotPromptWithTemplates",
    "HumanMessagePromptTemplate",
    "LengthBasedExampleSelector",
    "MaxMarginalRelevanceExampleSelector",
    "MessagesPlaceholder",
    "NGramOverlapExampleSelector",
    "PipelinePromptTemplate",
    "Prompt",
    "PromptTemplate",
    "SemanticSimilarityExampleSelector",
    "StringPromptTemplate",
    "SystemMessagePromptTemplate",
    "load_prompt",
    "FewShotChatMessagePromptTemplate",
]
