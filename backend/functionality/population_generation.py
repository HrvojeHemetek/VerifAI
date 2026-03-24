import random
import numpy as np
import json, csv, os
import pandas as pd
from .aggregate_sample import aggregate_sample_data, input_files, output_files

filename = "surveys/results/test_country.csv"

def generate_sample(sample_size:int, relevant_factors:list[str], country:str):
    '''
        This function generates a sample of N individuals based on an algorithm that uses demographic, unemployment, and employment data for the specified country.
    '''
    # Filtering data for the specified country
    country_data = fetch_country(country)
    remove_file_if_exists(filename)
    
    data = generate_sample_algorithm(sample_size, country_data[0][0], country_data[1], country_data[2])

    # Writing sample data to CSV                
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=relevant_factors)
        writer.writeheader() 
        writer.writerows(data)

    agg_data = aggregate_sample_data(data)

    # Writing aggregated data to the document
    with open("surveys/results/formated_agg_sample_data.json",mode = "w") as file:
        json.dump(agg_data, file, indent = 4)

    return agg_data,data   

def generate_sample_algorithm(N: int, demographics: dict, unemployment_data: list[dict], employment_data: list[dict]) -> list[dict]:
    sample = []
    # Extracting necessary data
    male_population = float(demographics['male_population'].strip('%')) / 100
    female_population = float(demographics['female_population'].strip('%')) / 100
    urban_population_percent = float(demographics['urban_population_percent_of_total'].strip('%')) / 100
    avg_daily_income = float(demographics['daily_income'].strip('$'))
    avg_years_schooling = {
        "M": employment_data[1]['mean_years_in_school_25_years_and_older'],
        "F": employment_data[0]['mean_years_in_school_25_years_and_older']
    }
    for i in range(N):
        # Gender
        gender = 'M' if random.random() < male_population else 'F'
        # Age
        age_group = random.choices(
            population=[d['age'] for d in unemployment_data if d['gender'] == gender],
            weights=[100-d['unemployment_rate_percent'] for d in unemployment_data if d['gender'] == gender],
            k=1
        )[0]
        # Employment
        unemployment_rate = (next(d['unemployment_rate_percent'] for d in unemployment_data if d['gender'] == gender and d['age'] == age_group) / 100)
        employment = random.random() > unemployment_rate
        # Urban/Rural Living
        urban_rural_living = 'urban' if random.random() < urban_population_percent else 'rural'
        # Daily Income
        daily_income = np.random.normal(loc=avg_daily_income, scale=float(avg_daily_income / 4.0)) * (1 + unemployment_rate) if employment else 0
        if daily_income < 0:
            daily_income = 0
        # Work Sector
        sector_data = next(d for d in employment_data if d['gender'] == gender)
        work_sector = random.choices(
            population=['industry_workers', 'service_workers', 'agriculture_workers'],
            weights=[sector_data['industry_workers_percent_of_employment'],
                     sector_data['service_workers_percent_of_employment'],
                     sector_data['agriculture_workers_percent_of_employment']],
            k=1
        )[0] if employment else None
        # Number of Children
        number_of_children = round(np.random.normal(loc=demographics["children_per_woman_total_fertility"], scale=float(demographics["children_per_woman_total_fertility"] / 3.0)))  # assuming an arbitrary distribution
        if number_of_children < 0:
            number_of_children = 0
        # Years of Schooling
        years_of_schooling = round(np.random.normal(loc=avg_years_schooling[gender], scale=float(avg_years_schooling[gender] / 4.0)))
        if years_of_schooling < 0:
            years_of_schooling = 0
        sample.append({
            "gender": gender,
            "age": age_group,
            "work_sector": work_sector,
            "employment": employment,
            "urban_rural_living": urban_rural_living,
            "daily_income": daily_income,
            "number_of_children": number_of_children,
            "years_of_schooling": years_of_schooling
        })
    return sample

def remove_file_if_exists(filename):
    if os.path.isfile(filename):
        os.remove(filename)
    
def fetch_country(country: str):
    '''
        This function iterates through 3 tables in the folder tables/combined to filter data for the country where the survey is being conducted.
    '''
    fetched_data = []
    for i in range(len(output_files)):
        df = pd.read_csv(input_files[i])

        filtered_df = df[df['country'] == country]
        result = filtered_df.to_dict(orient='records')
        fetched_data.append(result)
        with open(output_files[i], 'w') as f:
            json.dump(result, f, indent=4)
    
    return fetched_data