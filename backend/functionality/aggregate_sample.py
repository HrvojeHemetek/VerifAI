from collections import defaultdict
import os
import json

input_files = [os.path.join("tables", "combined_data", "nonpivot.csv"),os.path.join("tables", "combined_data", "pivot_gender_age.csv"),os.path.join("tables", "combined_data", "pivot_gender.csv")]
output_files = [os.path.join("surveys", "country_info", "nonpivot.json"),os.path.join("surveys", "country_info", f"pivot_gender_age.json"),os.path.join("surveys", "country_info", f"pivot_gender.json")]

def categorize_age(age):
    '''
        This function categorizes age into age groups relevant for analysis and is used if the AI generates age.
    '''
    #return age
    if age > 15 and age < 25:
        return '15_24'
    elif 25 <= age < 54:
        return '25_54'
    elif 55 <= age < 64:
        return '55_64'
    else:
        return '65plus'

# Data standardization
def standardize_record(record):
    standardized = {}
    
    standardized['age'] = record.get('age')
    standardized['gender'] = record.get('gender', record.get('sex'))
    standardized['daily_income'] = record.get('daily_income')
    standardized['work_sector'] = record.get('work_sector')
    standardized['years_of_schooling'] = record.get('years_of_schooling')
    standardized['employment'] = record.get('employment')
    standardized['urban_rural_living'] = record.get('urban_rural_living')
    standardized['number_of_children'] = record.get('number_of_children')
    return standardized

# Aggregation of generated sample data
def aggregate_sample_data(data):
    '''
        This function takes the generated sample and aggregates it into a selected format (visible in the return section) so that data can be compared with the real population and displayed graphically.
    '''

    ## Initialization of initial values for all demographic data elements
    age_distribution = {'15_24':0, '25_54': 0, '55_64':0,'65plus':0}
    gender_distribution = {'F':0, 'M':0 }
    work_sector_distribution = {"F": {
            "service_workers": 0,
            "industry_workers": 0,
            "agriculture_workers": 0
        },
        "M": {
            "service_workers": 0,
            "industry_workers": 0,
            "agriculture_workers": 0
        }}
    urban_rural_distribution = defaultdict(int)
    unemployment_rate ={
        "F": {"15_24": {"employed":0,"unemployed":0}, "25_54": {"employed":0,"unemployed":0},"55_64": {"employed":0,"unemployed":0},"65plus": {"employed":0,"unemployed":0}},
        "M": {"15_24": {"employed":0,"unemployed":0},"25_54": {"employed":0,"unemployed":0},"55_64": {"employed":0,"unemployed":0},"65plus": {"employed":0,"unemployed":0}}}
    total_schooling_years = 0
    total_children = 0
    total_income = 0
    income_count = 0
    schooling_count = 0
    children_count = 0
    total_urban = 0
    total_rural = 0
    
    for record in data:
        ## loops through "each person" in the sample and aggregates data into appropriate variables
        ## to understand these instructions, it is necessary to understand the structure of the tables in tables/combined_data/...
        standardized_record = standardize_record(record)
        
        if standardized_record['age'] is not None:
            age_category = standardized_record['age']
            age_distribution[age_category] += 1


        if standardized_record['gender'] is not None:
            gender_distribution[standardized_record['gender']] += 1
        
        if standardized_record['work_sector'] is not None and standardized_record['gender'] is not None:
            gender = standardized_record['gender']
            work_sector_distribution[gender][standardized_record['work_sector']] += 1
        
        if standardized_record['urban_rural_living'] is not None:
            urban_rural_distribution[standardized_record['urban_rural_living']] += 1
            if standardized_record['urban_rural_living'] == 'urban':
                total_urban += 1
            elif standardized_record['urban_rural_living'] == 'rural':
                total_rural += 1
        
        if standardized_record['employment'] is not None:

            if standardized_record['age'] is not None and standardized_record['gender'] is not None:
                age_category = standardized_record['age']
                gender = standardized_record['gender']
                if standardized_record['employment']:
                    unemployment_rate[gender][age_category]['employed'] += 1
                else:
                    unemployment_rate[gender][age_category]['unemployed'] += 1

        if standardized_record['years_of_schooling'] is not None:
            total_schooling_years += standardized_record['years_of_schooling']
            schooling_count += 1
        

        if standardized_record['number_of_children'] is not None:
            total_children += standardized_record['number_of_children']
            children_count += 1

        if standardized_record['daily_income'] is not None:
            total_income += standardized_record['daily_income']
            income_count += 1
    
    # Average calculation
    average_schooling_years = total_schooling_years / schooling_count if schooling_count > 0 else None
    average_number_of_children = total_children / children_count if children_count > 0 else None
    average_daily_income = total_income / income_count if income_count > 0 else None
    
    # Unemployment rate calculation
    unemployment_rate_percent = {}
    for gender, age_groups in unemployment_rate.items():
        unemployment_rate_percent[gender] = {}
        for age_group, counts in age_groups.items():
            total_people = counts['employed'] + counts['unemployed']
            if total_people > 0:
                unemployment_rate_percent[gender][age_group] = (counts['unemployed'] / total_people) * 100
            else:
                unemployment_rate_percent[gender][age_group] = None
    
    # Calculation of the urban ratio in the total
    total_population = total_urban + total_rural
    urban_ratio_percent = (total_urban / total_population) * 100 if total_population > 0 else None

    # Calculation of employment by sectors
    work_sector_percent_distribution = {}
    for gender, sectors in work_sector_distribution.items():
        total_employed = sum(sectors.values())
        if total_employed > 0:
            work_sector_percent_distribution[gender] = {
                sector: (count / total_employed) * 100 for sector, count in sectors.items()
            }

    # Calculation of age and gender ratio
    age_percent_distribution = {
        category: (count / sum(age_distribution.values())) * 100 if sum(age_distribution.values()) != 0 else 0 for category, count in age_distribution.items()
    }
    gender_percent_distribution = {
        gender: (count / sum(gender_distribution.values())) * 100 if sum(gender_distribution.values()) != 0 else 0  for gender, count in gender_distribution.items()
    }

    final_data = {
        'age': age_percent_distribution,
        'gender': gender_percent_distribution,
        'work_sector': work_sector_percent_distribution,
        'urban_rural_living': urban_ratio_percent,
        'employment': unemployment_rate_percent,
        'years_of_schooling': average_schooling_years,
        'number_of_children': average_number_of_children,
        'daily_income': average_daily_income
    }

    return final_data

def format_population_data():
    '''
        Formatting of real population data
    '''

    # Initialize variables for data collection
    age_data = None
    gender_data = {'F': 0.0, 'M': 0.0}
    work_sector_data = {'F': {}, 'M': {}}
    urban_rural_living = None
    employment_data = {'F': {}, 'M': {}}
    years_of_schooling = None
    number_of_children = None
    daily_income = None

    # Read and process each JSON document
    for file in output_files:
        with open(file, 'r') as f:
            data = json.load(f)

            # Process data from the first JSON
            if 'population' in data[0]:
                urban_rural_living = float(data[0]['urban_population_percent_of_total'].replace('%', ''))
                number_of_children = float(data[0]['children_per_woman_total_fertility'])
                daily_income = float(data[0]['daily_income'].replace('$', ''))
                gender_data['F']= float(data[0]['female_population'].replace('%', ''))
                gender_data['M']= float(data[0]['male_population'].replace('%', ''))

            # Process data from the second JSON
            if 'unemployment_rate_percent' in data[0]:
                for entry in data:
                    gender = entry['gender']
                    age_group = entry['age']
                    unemployment_rate = entry['unemployment_rate_percent']
                    employment_data[gender][age_group] = unemployment_rate


            # Process data from the third JSON
            if 'industry_workers_percent_of_employment' in data[0]:
                for entry in data:
                    gender = entry['gender']
                    work_sector_data[gender]['service_workers'] = entry['service_workers_percent_of_employment']
                    work_sector_data[gender]['industry_workers'] = entry['industry_workers_percent_of_employment']
                    work_sector_data[gender]['agriculture_workers'] = entry['agriculture_workers_percent_of_employment']
                    years_of_schooling = entry['mean_years_in_school_25_years_and_older']

    # Converting obtained data into the desired format
    formatted_data = {
        'age': age_data,
        'gender': gender_data,
        'work_sector': work_sector_data,
        'urban_rural_living': urban_rural_living,
        'employment': employment_data,
        'years_of_schooling': years_of_schooling,
        'number_of_children': number_of_children,
        'daily_income': daily_income
    }

    output_path = 'surveys/results/formated_population_data.json'
    with open(output_path, 'w') as f:
        json.dump(formatted_data, f, indent=4)
    return formatted_data


