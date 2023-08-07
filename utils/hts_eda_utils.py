from matplotlib import pyplot as plt

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