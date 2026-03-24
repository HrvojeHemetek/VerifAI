import json,os, csv
from collections import defaultdict

rel_factors = ['gender', 'age', 'work_sector', 'employment', 'urban_rural_living', 'daily_income', 'number_of_children', 'years_of_schooling']

def load_possible_answers_from_question_file():
    '''
        This function retrieves possible answers for each of the questions from the questions_answers document that the user uploaded.
        The path to the document is defined in SurveyView.py
    '''

    filepath = os.path.join("surveys", "questions.csv")
    possible_answers = {}
    
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        
        next(reader)
        
        for row in reader:
            if len(row) == 2:  
                question = row[0].strip() +","+ row[1].strip() ## Under the rule that answers do not contain a comma
                answers = [answer.strip() for answer in row[1].split(',')]  
                possible_answers[question] = answers

    return possible_answers

def initialize_general_aggregation(possible_answers):
    '''
        Sets the initial values of each factor to 0. Necessary for displaying on graphs.
        In case there are no members of that category, it will still appear on the graph.
    '''
    
    general_aggregation = defaultdict(lambda: defaultdict(int))

    for question, answers in possible_answers.items():
        general_aggregation[question] = {answer: 0 for answer in answers}
    
    return general_aggregation

def aggregate_survey_results(data):
    possible_answers = load_possible_answers_from_question_file()

    general_aggregation = initialize_general_aggregation(possible_answers)

    for record in data:
        for question, answer in record.items():
            if question in general_aggregation:
                if answer in general_aggregation[question]:
                    general_aggregation[question][answer] += 1

    with open('surveys/results/aggregated_survey_results.json', 'w', encoding='utf-8') as f:
        json.dump(general_aggregation, f, indent=4, ensure_ascii=False)

    return general_aggregation


