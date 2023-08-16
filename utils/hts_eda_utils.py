from matplotlib import pyplot as plt
import pandas as pd

def get_zero_columns(df):
    zero_columns_mask = (df == 0).all()
    zero_columns = df.columns[zero_columns_mask]

    return zero_columns

def remove_zero_columns(df):
    zero_columns = get_zero_columns(df)

    print(f"Removing {len(zero_columns)} columns with all zeros")

    df_without_zero_columns = df.drop(columns=zero_columns)

    return df_without_zero_columns


def plot_correlations(corr_df, figsize=(14,14)):
    plt.figure(figsize=figsize)


    plt.imshow(corr_df, cmap='RdYlGn', vmin=-1, vmax=1)

    num_columns = len(corr_df.columns)
    plt.xticks(range(num_columns), corr_df.columns, rotation=45, ha='right')
    plt.yticks(range(num_columns), corr_df.columns)

    plt.colorbar()


def prep_data_for_scikit_hts(df):
    # Beware, chatgpt below :P
    aggregated_df = pd.DataFrame()

    # Split the columns into hierarchical levels by '-'
    columns_split = [col.split(' - ') for col in df.columns]

    # Get the unique top-level classes (regions)
    regions = list(set([col[0] for col in columns_split if len(col) > 1]))

    # AFAIK, HTS needs a 'total' column for each level in the hierarchy. I believe all tree nodes except bottom-most
    # Create a dictionary to represent the hierarchy, starting with 'total'
    hierarchy = {'total': regions}

    # Iterate through regions: Дальневосточный ФО
    for region in regions:
        # Drug Categories - 'ADRIANOL', 'AGALATES', 'ALMAGEL', 'ALMONT', 'AMBROBENE'
        categories = list(set([col[1] for col in columns_split if len(col) > 1 and col[0] == region]))
        region_key = region
        hierarchy[region_key] = [f'{region} - {category}' for category in categories]

        # Aggregate at the region level
        region_columns = [col for col in df.columns if col.startswith(f'{region} - ')]
        aggregated_df[region_key] = df[region_columns].sum(axis=1)

        # Iterate through Drug categories
        for category in categories:
            category_key = f'{region} - {category}'
            products = [col for col in df.columns if col.startswith(f'{region} - {category} - ')]
            hierarchy[category_key] = products

            # Aggregate at the category level
            category_columns = [col for col in df.columns if col.startswith(f'{region} - {category} - ')]
            aggregated_df[category_key] = df[category_columns].sum(axis=1)

    # Concatenate the aggregated columns with the original DataFrame
    df_with_aggregates = pd.concat([df, aggregated_df], axis=1)

    # Add the "total" column across all columns
    df_with_aggregates['total'] = df_with_aggregates.sum(axis=1)

    return df_with_aggregates, hierarchy