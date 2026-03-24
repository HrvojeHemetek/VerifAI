import os
import shutil
import warnings
import pandas as pd
import numpy as np
from datetime import date

def return_dual_list_columns(column_from_set: str, columns_from_pivot: pd.Index) -> list[str]:
    list_of_matching_columns = list()
    for column in columns_from_pivot:
        if set(column_from_set.split("_")).issubset(set(column.split("_"))):
            list_of_matching_columns.append(column)

    if list_of_matching_columns[0].find("man") == -1:
        list_of_matching_columns.sort()
        return list_of_matching_columns
    
    list_of_matching_columns.sort(reverse=True)
    return list_of_matching_columns

def write_to_csv_nonpivot(path: str, combined_data_df: pd.DataFrame) -> None:
    combined_data = combined_data_df.copy()

    for (i, column) in enumerate(combined_data.columns):
        if column.find("men") == -1 and column.find("male") == -1 and column.find("country") == -1:
            if column.find("sex_ratio") != -1:
                males = round((combined_data[column] / (combined_data[column] + 100)) * 100, 2) 
                females = (100 - males)
                males = (males.astype(str) + "%").to_list()
                females = (females.astype(str) + "%").to_list()
                
                combined_data.drop(column, axis=1, inplace=True)

                combined_data.insert(i, "male_population", males)
                combined_data.insert(i + 1, "female_population", females)
            else:
                if column.find("percent") != -1:
                    combined_data = combined_data.astype({column: str})
                    combined_data[column] = combined_data[column] + "%"
                    combined_data[column].replace(to_replace="nan%", value=np.nan, inplace=True)

                if column.find("income") != -1:
                    combined_data = combined_data.astype({column: str})
                    combined_data[column] = combined_data[column] + "$"
                    combined_data[column].replace(to_replace="nan$", value=np.nan, inplace=True)

        else:
            combined_data.drop(column, axis=1, inplace=True)
    combined_data.to_csv(os.path.join(path, "nonpivot.csv"))


def write_to_csv_pivot_gender(path_to_raw: str, path_to_pivot: str, path_to_nonpivot: str) -> None:
    combined_data = pd.read_csv(path_to_nonpivot, index_col=False)

    countries = combined_data["country"]

    changed_combined_list = list()

    genders = list(["M", "F"])

    for country in countries:
        for gender in genders:
            changed_combined_list.append({"country": country, "gender": gender})

    combined_data = pd.DataFrame(changed_combined_list)

    current_year = date.today().year

    for filename in os.listdir(path_to_raw):
        df = pd.read_csv(os.path.join(path_to_raw, filename))

        df = df[["country", df.columns[-1] if int(df.columns[-1]) < current_year else str(current_year)]]
        df.rename(columns={df.columns[-1]: filename.removesuffix(".csv")}, inplace=True)
        combined_data = combined_data.join(df.set_index("country"), on="country")

    pivot_table = combined_data.pivot_table(index=["country", "gender"], values=combined_data.columns[2:])

    columns_set = set()

    for column in pivot_table.columns:
        columns_set.add(column.replace("female_", "").replace("women_", "").replace("male_", "").replace("men_", ""))

    for column in columns_set:
        list_of_matching_columns = return_dual_list_columns(column, pivot_table.columns)
        pivot_table[column] = pivot_table.apply(lambda row: row[list_of_matching_columns[0]] if row.name[1].find("F") != -1 else row[list_of_matching_columns[1]], axis=1)
        pivot_table.drop(list_of_matching_columns, axis=1, inplace=True)
            
    pivot_table.to_csv(os.path.join(path_to_pivot, "pivot_gender.csv"))
    
def write_to_csv_pivot_gender_age(path_to_raw: str, path_to_nonpivot: str, column_to_add: str) -> pd.DataFrame:
    combined_data = pd.read_csv(path_to_nonpivot, index_col=False)

    countries = combined_data["country"]

    changed_combined_list = list()

    genders = list(["M", "F"])
    years = list(["15_24", "25_54", "55_64", "65plus"])

    for country in countries:
        for gender in genders:
            for year in years:
                changed_combined_list.append({"country": country, "gender": gender, "age": year})

    combined_data = pd.DataFrame(changed_combined_list)

    current_year = date.today().year

    for filename in os.listdir(path_to_raw):
        if filename.find(column_to_add) != -1:
            df = pd.read_csv(os.path.join(path_to_raw, filename))

            df = df[["country", df.columns[-1] if int(df.columns[-1]) < current_year else str(current_year)]]
            df.rename(columns={df.columns[-1]: filename.removesuffix(".csv")}, inplace=True)
            combined_data = combined_data.join(df.set_index("country"), on="country")

    pivot_table = combined_data.pivot_table(index=["country", "gender", "age"], values=combined_data.columns[3:])
 
    columns_set = set()

    for column in pivot_table.columns:
        columns_set.add(column.replace("females_", "").replace("women_", "").replace("males_", "").replace("men_", ""))

    def column_joining_function(row, columns_list, pivot_table_columns):
        for column in columns_list:
            list_of_matching_columns = return_dual_list_columns(column, pivot_table_columns)
        
            if row.name[1].find("F") != -1 and list_of_matching_columns[0].find(row.name[2]) != -1:
                return row[list_of_matching_columns[0]]
            
            if row.name[1].find("M") != -1 and list_of_matching_columns[1].find(row.name[2]) != -1:
                return row[list_of_matching_columns[1]]

    pivot_table[column_to_add] = pivot_table.apply(column_joining_function, args=(sorted(columns_set), pivot_table.columns), axis=1)

    for column in sorted(columns_set):
        list_of_matching_columns = return_dual_list_columns(column, pivot_table.columns)
        pivot_table.drop(list_of_matching_columns, axis=1, inplace=True)

    return pivot_table

if __name__ == "__main__":
    warnings.filterwarnings('ignore')

    current_year = date.today().year 

    path_to_raw_data = "./tables/raw_data"
    path_to_cleaned_data = "./tables/combined_data"

    if (not os.path.exists(path_to_raw_data)):
        print("Ne postoje tablice za obradu!")
        exit(1)

    if (os.path.exists(path_to_cleaned_data)):
        print("Brisanje starih počišćenih podataka.")
        shutil.rmtree(path_to_cleaned_data)

    os.mkdir(path_to_cleaned_data)

    combined_list_columns = list()

    combined_data_df = pd.DataFrame()

    for dirnum, (dirpath, dirs, files) in enumerate(os.walk(path_to_raw_data)):
        for filename in files:
            fname = os.path.join(dirpath, filename) 
            df = pd.read_csv(fname)
            df = df[["country", df.columns[-1] if int(df.columns[-1]) < current_year else str(current_year)]]
            df.rename(columns={df.columns[-1]: filename.removesuffix(".csv")}, inplace=True)
            if (dirnum == 0):
                combined_data_df = df.join(combined_data_df, on="country").set_index("country")
            else:
                if (df.shape[0] <= combined_data_df.shape[0]):
                    combined_data_df = combined_data_df.join(df.set_index("country"))
                else:
                    combined_data_df = df.set_index("country").join(combined_data_df)

    combined_data_df.to_csv(os.path.join(path_to_cleaned_data, "combined.csv"))

    write_to_csv_nonpivot(path_to_cleaned_data, combined_data_df)
    write_to_csv_pivot_gender(os.path.join(path_to_raw_data, "Pivot_gender"), path_to_cleaned_data, os.path.join(path_to_cleaned_data, "nonpivot.csv"))
    pivot_gender_age_unemployment = write_to_csv_pivot_gender_age(os.path.join(path_to_raw_data, "Pivot_gender_age"), os.path.join(path_to_cleaned_data, "nonpivot.csv"), "unemployment_rate_percent")
    pivot_gender_age_unemployment.to_csv(os.path.join(path_to_cleaned_data, "pivot_gender_age.csv"))


