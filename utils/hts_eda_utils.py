from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

def get_zero_columns(df, any_or_all='all'):
    if any_or_all == 'any':
        zero_columns_mask = (df == 0).any()
    elif any_or_all == 'all':
        zero_columns_mask = (df == 0).all()
    else:
        raise ValueError(f"any_or_all must be either 'any' or 'all', got {any_or_all}")
    
    zero_columns = df.columns[zero_columns_mask]

    return zero_columns

def remove_zero_columns(df, any_or_all='all'):
    zero_columns = get_zero_columns(df, any_or_all)

    print(f"Removing {len(zero_columns)} columns with {any_or_all} zeros")

    df_without_zero_columns = df.drop(columns=zero_columns)

    return df_without_zero_columns


def plot_correlations(corr_df, figsize=(14,14)):
    plt.figure(figsize=figsize)


    plt.imshow(corr_df, cmap='RdYlGn', vmin=-1, vmax=1)

    num_columns = len(corr_df.columns)
    plt.xticks(range(num_columns), corr_df.columns, rotation=45, ha='right')
    plt.yticks(range(num_columns), corr_df.columns)

    plt.colorbar()


def prep_data_for_scikit_hts(df, HIERARCHY_DELIMITER='_'):
    # Beware, chatgpt below :P
    aggregated_df = pd.DataFrame()

    # Split the columns into hierarchical levels by '-'
    columns_split = [col.split(HIERARCHY_DELIMITER) for col in df.columns]

    # Get the unique top-level classes (regions)
    regions = list(set([col[0] for col in columns_split if len(col) > 1]))

    # AFAIK, HTS needs a 'Total' column for each level in the hierarchy. I believe all tree nodes except bottom-most
    # Create a dictionary to represent the hierarchy, starting with 'Total'
    hierarchy = {'Total': regions}

    # Iterate through regions: Дальневосточный ФО
    for region in regions:
        # Drug Categories - 'ADRIANOL', 'AGALATES', 'ALMAGEL', 'ALMONT', 'AMBROBENE'
        categories = list(set([col[1] for col in columns_split if len(col) > 1 and col[0] == region]))
        region_key = region
        hierarchy[region_key] = [f'{region}{HIERARCHY_DELIMITER}{category}' for category in categories]

        # Aggregate at the region level
        region_columns = [col for col in df.columns if col.startswith(f'{region}{HIERARCHY_DELIMITER}')]
        aggregated_df[region_key] = df[region_columns].sum(axis=1)

        # Iterate through Drug categories
        for category in categories:
            category_key = f'{region}{HIERARCHY_DELIMITER}{category}'
            products = [col for col in df.columns if col.startswith(f'{region}{HIERARCHY_DELIMITER}{category}{HIERARCHY_DELIMITER}')]
            hierarchy[category_key] = products

            # Aggregate at the category level
            category_columns = [col for col in df.columns if col.startswith(f'{region}{HIERARCHY_DELIMITER}{category}{HIERARCHY_DELIMITER}')]
            aggregated_df[category_key] = df[category_columns].sum(axis=1)

    # Concatenate the aggregated columns with the original DataFrame
    df_with_aggregates = pd.concat([df, aggregated_df], axis=1)

    # Add the "total" column across all columns
    df_with_aggregates['Total'] = df_with_aggregates.sum(axis=1)

    return df_with_aggregates, hierarchy


def add_1_to_all_df_cells(df):
    for c in df.columns[1:]: # adding 1 unit everywhere
        df[c] = df[c]+1
    
    return df


def select_top_n_brands(df, n=10, HIERARCHY_DELIMITER='_'):
    selected_brands = pd.Series([c.split(HIERARCHY_DELIMITER)[1] for c in df.columns[1:]]).value_counts()[0:n].keys()
    toremove = [c for c in df.columns[1:] if c.split(HIERARCHY_DELIMITER)[1] not in selected_brands]
    print("Keeping only these brands: ", selected_brands)
    print("Removing ", len(toremove), ' brands')

    return df.drop(columns = toremove)


def create_S_df(df, HIERARCHY_DELIMITER='_'):
    """
    This is the matrix that represents hierarchical structure of the data.
    """

    columns = df.columns

    # Extract unique components from column names
    components = set()
    for col in columns:
        parts = col.split(HIERARCHY_DELIMITER)
        for i in range(1, len(parts) + 1):
            components.add(HIERARCHY_DELIMITER.join(parts[:i]))

    # Convert to sorted list
    index = ['Total'] + sorted(components)

    # Create DataFrame
    S_df = pd.DataFrame(0, index=index, columns=columns)

    # Populate DataFrame
    for col in columns:
        parts = col.split(HIERARCHY_DELIMITER)
        for i in range(1, len(parts) + 1):
            S_df.at[HIERARCHY_DELIMITER.join(parts[:i]), col] = 1
        S_df.at['Total', col] = 1

    return S_df


def mean_absolute_percentage_error(y_true, y_pred): 
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def symmetric_mean_absolute_percentage_error(y_true, y_pred):
    return 100/len(y_true) * np.sum(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))