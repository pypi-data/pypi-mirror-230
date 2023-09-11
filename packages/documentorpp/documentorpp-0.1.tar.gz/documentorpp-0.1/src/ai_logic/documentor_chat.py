import os
from metaclasses.singleton_meta import SingletonMeta
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    PromptTemplate,
)
from snippet_management.code_snippet import CodeSnippet
from ai_logic.doc_example import (
    CLASS_DOCUMENTATION_TEMPLATE,
    METHOD_DOCUMENTATION_TEMPLATE,
    FUNCTION_DOCUMENTATION_TEMPLATE,
)
from typing import ClassVar

class DocumentorChat(metaclass=SingletonMeta):
    instance: ClassVar = None
    chat: ChatOpenAI
    system_message: SystemMessagePromptTemplate
    snippet_to_doc: CodeSnippet
    current_doc_message: HumanMessage
    current_chat_message: ChatPromptTemplate
    current_answer: str = None

    def __init__(self) -> None:
        key = os.environ.get('OPENAI_API_KEY')
        self.chat = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=key)

    @staticmethod
    def set_snippet_to_doc(snippet_to_doc: CodeSnippet):
        DocumentorChat.instance._set_snippet_to_doc(snippet_to_doc)

    @staticmethod
    def ask_documentation():
        DocumentorChat.instance._ask_documentation()
    
    @staticmethod
    def get_documentation_answer() -> str:
        return DocumentorChat.instance.current_answer

    def _set_snippet_to_doc(self, snippet_to_doc: CodeSnippet):
        self.snippet_to_doc = snippet_to_doc
        self._set_correct_templates()

    def _ask_documentation(self):
        self.current_answer = self.chat(self.current_chat_message).content

    def _set_correct_templates(self):
        if self.snippet_to_doc.code_snippet_type == "class_definition":
            self._set_class_documentation()
        elif (
            self.snippet_to_doc.parent_type == "class_definition"
            and self.snippet_to_doc.code_snippet_type == "function_definition"
        ):
            self._set_method_documentation()
        elif (
            self.snippet_to_doc.parent_type == "root node"
            and self.snippet_to_doc == "function_defintion"
        ):
            self._set_function_documentation()

    def _set_function_documentation(self) -> None:
        self._set_function_system_message_template()
        self._set_function_doc_message_template()
        self._set_function_current_chat_message()

    def _set_function_system_message_template(self) -> None:
        template = PromptTemplate(
            template="You are a senior python developer. Given the following function called '{function_identifier}', documentate the  function'{function_identifier}'. Take into consideration that the function belongs to the file '{file_name}' and this file have the following dependencies:{file_dependencies}. The documentation must be outputted in markdown format maintaining the following format: \n {function_format}",
            input_variables=[
                "function_identifier",
                "file_name",
                "file_dependencies",
                "function_format",
            ],
        )
        self.system_message = SystemMessagePromptTemplate(prompt=template)

    def _set_function_doc_message_template(self) -> None:
        template = PromptTemplate(
            template="Here is the implementaton of the function '{function_identifier}':\n'''{function_implementation}'''\n document the function taking your time analyzing the logic of the function, the arguments of the function, the return type, etc. Think about the correct understandment of the documentation. Use only the provided info.",
            input_variables=["function_identifier", "function_implementation"],
        )
        self.current_doc_message = HumanMessagePromptTemplate(prompt=template)

    def _set_function_current_chat_message(self):
        chat_template = ChatPromptTemplate.from_messages(
            [self.system_message, self.current_doc_message]
        )
        prompt_value = chat_template.format_prompt(
            function_identifier=self.snippet_to_doc.code_snippet_identifier,
            file_name=self.snippet_to_doc.file_name,
            file_dependencies=self.snippet_to_doc.dependencies,
            function_implementation=self.snippet_to_doc.implementation,
            function_format=FUNCTION_DOCUMENTATION_TEMPLATE,
        ).to_messages()
        self.current_chat_message = prompt_value

    def _set_class_documentation(self) -> None:
        self._set_class_system_message_template()
        self._set_class_doc_message_template()
        self._set_class_current_chat_message()

    def _set_class_system_message_template(self) -> None:
        template = PromptTemplate(
            template="You are a senior python developer. Given the following class called '{class_identifier}', documentate the clas '{class_identifier}'. Take into consideration that the class belongs to the file '{file_name}' and this file have the following dependencies:{file_dependencies}. The documentation must be outputted in markdown format maintaining the following format: \n {class_format}",
            input_variables=[
                "class_identifier",
                "file_name",
                "file_dependencies",
                "class_format",
            ],
        )
        self.system_message = SystemMessagePromptTemplate(prompt=template)

    def _set_class_doc_message_template(self) -> None:
        template = PromptTemplate(
            template="Here is the implementaton of the class '{class_identifier}':\n'''{class_implementation}'''\n document the class taking your time infering the use of the attributes, or in case of no attributes how the class would work based on the class name. The methods of the class are not relevant now because they will be document later, think about the correct understandment of the documentation. Use only the provided info.",
            input_variables=["class_identifier", "class_implementation"],
        )
        self.current_doc_message = HumanMessagePromptTemplate(prompt=template)

    def _set_class_current_chat_message(self):
        chat_template = ChatPromptTemplate.from_messages(
            [self.system_message, self.current_doc_message]
        )
        prompt_value = chat_template.format_prompt(
            class_identifier=self.snippet_to_doc.code_snippet_identifier,
            file_name=self.snippet_to_doc.file_name,
            file_dependencies=self.snippet_to_doc.dependencies,
            class_implementation=self.snippet_to_doc.implementation,
            class_format=CLASS_DOCUMENTATION_TEMPLATE,
        ).to_messages()
        self.current_chat_message = prompt_value

    def _set_method_documentation(self) -> None:
        self._set_method_system_message_template()
        self._set_method_doc_message_template()
        self._set_method_current_chat_message()

    def _set_method_system_message_template(self) -> None:
        template = PromptTemplate(
            template="You are a senior python developer. Given the following method called '{method_identifier}', that belongs to the class '{class_identifier}', documentate the method '{method_identifier}'. Take into consideration that the method an it's class belongs to the file '{file_name}' and this file have the following dependencies:{file_dependencies}. The documentation must be outputted in markdown format maintaining the following format: \n {method_format}",
            input_variables=[
                "method_identifier",
                "class_identifier",
                "file_name",
                "file_dependencies",
                "method_format",
            ],
        )
        self.system_message = SystemMessagePromptTemplate(prompt=template)

    def _set_method_doc_message_template(self) -> None:
        template = PromptTemplate(
            template="Here is the implementation of the method '{method_identifier}':\n'''{method_implementation}'''\n document the method taking your time to extract the most important things for a correct understandment of the documentation. Use only the provided info.",
            input_variables=["method_identifier", "method_implementation"],
        )
        self.current_doc_message = HumanMessagePromptTemplate(prompt=template)

    def _set_method_current_chat_message(self):
        chat_template = ChatPromptTemplate.from_messages(
            [self.system_message, self.current_doc_message]
        )
        prompt_value = chat_template.format_prompt(
            method_identifier=self.snippet_to_doc.code_snippet_identifier,
            class_identifier=self.snippet_to_doc.parent_identifier,
            file_name=self.snippet_to_doc.file_name,
            file_dependencies=self.snippet_to_doc.dependencies,
            method_implementation=self.snippet_to_doc.implementation,
            method_format=METHOD_DOCUMENTATION_TEMPLATE,
        ).to_messages()
        self.current_chat_message = prompt_value

DocumentorChat()