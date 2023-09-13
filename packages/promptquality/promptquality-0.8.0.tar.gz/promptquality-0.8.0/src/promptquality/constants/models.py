from enum import Enum


class SupportedModels(str, Enum):
    # OpenAI models.
    chat_gpt = "ChatGPT (4K context)"
    chat_gpt_16k = "ChatGPT (16K context)"
    gpt_35_turbo = "ChatGPT (4K context)"
    gpt_35_turbo_16k = "ChatGPT (16K context)"
    gpt_4 = "gpt-4 (8K context)"
    babbage_2 = "babbage-002"
    davinci_2 = "davinci-002"
    text_ada_1 = "text-ada-001"
    text_babbage_1 = "text-babbage-001"
    text_curie_1 = "text-curie-001"
    text_davinci_3 = "text-davinci-003"

    # Azure models.
    azure_chat_gpt = "ChatGPT (4K context) (Azure)"
    azure_chat_gpt_16k = "ChatGPT (16K context) (Azure)"
    azure_gpt_35_turbo = "ChatGPT (4K context) (Azure)"
    azure_gpt_35_turbo_16k = "ChatGPT (16K context) (Azure)"
    azure_gpt_4 = "gpt-4 (8K context) (Azure)"
    azure_text_ada_1 = "text-ada-001 (Azure)"
    azure_text_babbage_1 = "text-babbage-001 (Azure)"
    azure_text_curie_1 = "text-curie-001 (Azure)"
    azure_text_davinci_3 = "text-davinci-003 (Azure)"
