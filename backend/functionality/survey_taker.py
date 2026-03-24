import threading
from openai import OpenAI
import time
from dotenv import load_dotenv, find_dotenv
import pandas as pd

from .aggregate_results import aggregate_survey_results


load_dotenv(find_dotenv())

class SurveyAssistant():
    def __init__(self, respondent,country, questions):
        super().__init__()
        self.respondent = respondent   # data for an individual person with relevant factors {'age':..,'gender':...}
        self.country = country         
        self.questions = questions

        self.client = OpenAI()
        self.assistant = self.generate_assistant()
        self.thread = self.client.beta.threads.create()

    def run(self):
        '''
            The function iterates through each of the survey questions and calls the function that will generate a response.
        '''

        for question in self.questions:
            self.generate_response(question)
            # Added delay due to rate limits (requests per minute)
            time.sleep(2)

    def generate_assistant(self):
        template = f"""You are an {self.country} citizen and you are taking a survey. Based on information about yourself,
                    imagine you are that person and respond to given question as such person would respond. This is some basic
                    information about yourself: {self.respondent}"""
        assistant = self.client.beta.assistants.create(
            name="Survey taker",
            instructions=template,
            model="gpt-4o-mini",
        )
        return assistant

    def generate_response(self, question):
        '''
            The function generates a response for a given question and stores it in self.respondent.
        '''

        try:
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=question + " Use information known about yourself."
            )

            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=f"""You are a helpful citizen of {self.country} and you have extensive knowledge about 
                    the culture, people, mentality, customs and habits of people from  {self.country}.
                    You are taking a survey. Based on demographic information about yourself,
                    imagine you are that person and respond to given question as such person would respond. 
                    
                    Demographic information about yourself: {self.respondent}.

                    Remeber to not answer in general sense, but as a representative person from {self.country} and specified demographic.
                    Take all your previous questions into consideration when answering a question.
                    Please reply with value only! I do NOT want any additional characters! Do not add a fullstop."""
            )
            time.sleep(2)

            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
                data = messages.data[0].content[0].text.value
                print(f"Response: {data}")
                self.respondent[question] = data
            else:
                print(f"Run not completed for respondent {self.respondent}: {run.status}")
        except Exception as e:
            print(f"Error for respondent {self.respondent}: {e}")

def generate_response(data,questions,country):
    survey_group = []
    num_respondents = len(data)
    for i in range(num_respondents):
        assistant = SurveyAssistant(data[i],country, questions)
        survey_group.append(assistant)
        assistant.run()

    # User data has been updated with survey responses, updated data for everyone is retrieved
    new_data= []
    for person in survey_group:
        new_data.append(person.respondent)

    df = pd.DataFrame(new_data)
    excel_filename = 'surveys/results/answers.xlsx'

    df.to_excel(excel_filename, index=False)
    print("All responses have been processed.")

    # Aggregating data for all responses -> survey results
    aggregated = aggregate_survey_results(new_data)
    return aggregated

