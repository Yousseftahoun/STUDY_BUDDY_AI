# from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQQuestion,FillBlankQuestion
from src.prompts.templates import mcq_prompt_template, fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class QuestionGenerator:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.llm = get_groq_llm()

    def _retry_and_parse(self,prompt,parser,topic,difficulty):

        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Attempt {attempt + 1} for generating question on topic '{topic}' with difficulty '{difficulty}'")
                response = self.llm.invoke(prompt.format(topic=topic,difficulty=difficulty))

                parsed = parser.parse(response.content)

                self.logger.info(f"Successfully parsed question on attempt {attempt + 1}")

                return parsed
            
            except Exception as e:
                self.logger.error(f"Error on attempt {str(e)}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(f"Failed to generate question after {settings.MAX_RETRIES} attempts", e)



    def generate_mcq(self, topic: str, difficulty: str = 'medium') -> MCQQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)

            question = self._retry_and_parse(mcq_prompt_template,parser,topic,difficulty)
            
            if len(question.options) != 4 or question.correct_answer not in question.options:
                raise ValueError("Invalid MCQ format: There must be exactly 4 options and the correct answer must be one of them.")
            
            self.logger.info("Generated a valid MCQ question.")
            return question
        
        except Exception as e:
            self.logger.error(f"Failed to generate MCQ question: {str(e)}")
            raise CustomException("MCQ Generation Failed", e)
    

    def generate_fill_blank(self, topic: str, difficulty: str = 'medium') -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question = self._retry_and_parse(fill_blank_prompt_template,parser,topic,difficulty)
            
            
            
            self.logger.info("Generated a valid fill in blanks question.")
            return question
        
        except Exception as e:
            self.logger.error(f"Failed to generate fillups question: {str(e)}")
            raise CustomException("fill in blanks Generation Failed", e)
