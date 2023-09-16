import openai as OpenAIApi


class CustomPromptActionBuilder:
    def __init__(self):
        self._instance = None

    def set_api_key(self, api_key):
        self._get_instance().api_key = api_key
        return self

    def set_model(self, model):
        self._get_instance().model = model
        return self

    def set_prompt(self, prompt):
        self._get_instance().prompt = prompt
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = CustomPromptAction()
        return self._instance


class CustomPromptAction:
    def __init__(self):
        self.api_key = None
        self.model = None
        self.prompt = None

    def execute(self, input_text: str):
        if not (self.api_key and self.prompt):
            raise Exception("Incomplete setup: Make sure to set api_key and prompt.")

        OpenAIApi.api_key = self.api_key
        chat_completion = OpenAIApi.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"{self.prompt}. input_text: `{input_text}`",
                }
            ],
        )

        return chat_completion.choices[0].message.content

    @staticmethod
    def prepare(data):
        builder = CustomPromptActionBuilder()
        return (
            builder.set_api_key(data["api_key"])
            .set_model(data["model"])
            .set_prompt(data["prompt"])
            .build()
        )


class SummarizeTextActionBuilder:
    def __init__(self):
        self._instance = None

    def set_api_key(self, api_key):
        self._get_instance().api_key = api_key
        return self

    def set_model(self, model):
        self._get_instance().model = model
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = SummarizeTextAction()
        return self._instance


class SummarizeTextAction:
    def __init__(self):
        self.api_key = None
        self.model = None

    def execute(self, input_text: str):
        if not self.api_key:
            raise Exception("Incomplete setup: Make sure to set api_key.")

        OpenAIApi.api_key = self.api_key

        # We specify a prompt that instructs the model to summarize the input text.
        chat_completion = OpenAIApi.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Please summarize the following text: `{input_text}`",
                }
            ],
        )

        return chat_completion.choices[0].message.content

    @staticmethod
    def prepare(data):
        builder = SummarizeTextActionBuilder()
        return builder.set_api_key(data["api_key"]).set_model(data["model"]).build()


class SentimentAnalysisActionBuilder:
    def __init__(self):
        self._instance = None

    def set_api_key(self, api_key):
        self._get_instance().api_key = api_key
        return self

    def set_model(self, model):
        self._get_instance().model = model
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = SentimentAnalysisAction()
        return self._instance


class SentimentAnalysisAction:
    def __init__(self):
        self.api_key = None
        self.model = None

    def execute(self, input_text: str):
        if not self.api_key:
            raise Exception("Incomplete setup: Make sure to set api_key.")

        OpenAIApi.api_key = self.api_key

        # Prompt instructs the model to classify the sentiment of the input text.
        chat_completion = OpenAIApi.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Classify the sentiment of the following text as either positive or negative: `{input_text}`",
                }
            ],
        )

        response_content = chat_completion.choices[0].message.content.lower()

        if "positive" in response_content:
            return "positive"
        elif "negative" in response_content:
            return "negative"
        else:
            return "neutral"

    @staticmethod
    def prepare(data):
        builder = SentimentAnalysisActionBuilder()
        return builder.set_api_key(data["api_key"]).set_model(data["model"]).build()


import openai


class ClassifyTextActionBuilder:
    def __init__(self):
        self._instance = None

    def set_api_key(self, api_key):
        self._get_instance().api_key = api_key
        return self

    def set_model(self, model):
        self._get_instance().model = model
        return self

    def set_labels(self, labels):
        self._get_instance().labels = labels
        return self

    def build(self):
        return self._get_instance()

    def _get_instance(self):
        if self._instance is None:
            self._instance = ClassifyTextAction()
        return self._instance


class ClassifyTextAction:
    def __init__(self):
        self.api_key = None
        self.model = None
        self.labels = []

    def execute(self, input_text: str):
        if not (self.api_key and self.labels):
            raise Exception("Incomplete setup: Make sure to set api_key and labels.")

        OpenAIApi.api_key = self.api_key

        labels_str = ", ".join(self.labels)
        # Prompt instructs the model to classify the input_text into one of the given labels.
        chat_completion = OpenAIApi.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Classify the following text into one of these categories: {labels_str}. Text: `{input_text}`",
                }
            ],
        )

        response_content = chat_completion.choices[0].message.content.lower()

        for label in self.labels:
            if label.lower() in response_content:
                return label

        return "Unable to classify"

    @staticmethod
    def prepare(data):
        builder = ClassifyTextActionBuilder()
        return (
            builder.set_api_key(data["api_key"])
            .set_model(data["model"])
            .set_labels(data["labels"])
            .build()
        )


prepare_date = {
    "api_key": "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",
    "model": "gpt-3.5-turbo",
    "labels": ["Happy Customer", "Angry Customer"],
}

REPLACE_SLUG_NAME = ClassifyTextAction.prepare(prepare_date)
result = REPLACE_SLUG_NAME.execute("Your input text here.")

print(result)
