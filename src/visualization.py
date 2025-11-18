import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def setup_dark_theme(fig, ax):
    """Apply dark theme styling to matplotlib figure"""
    fig.patch.set_facecolor('#2d2d2d')
    ax.set_facecolor('#1a1a1a')
    ax.spines['bottom'].set_color('#666')
    ax.spines['top'].set_color('#666')
    ax.spines['left'].set_color('#666')
    ax.spines['right'].set_color('#666')
    ax.tick_params(colors='#e0e0e0')
    ax.xaxis.label.set_color('#e0e0e0')
    ax.yaxis.label.set_color('#e0e0e0')
    ax.title.set_color('#ffffff')


def create_chart(df, chart_type, x_col, y_col):
    """Generate chart based on type and columns"""
    fig, ax = plt.subplots(figsize=(10, 6))
    setup_dark_theme(fig, ax)
    
    if chart_type == "Scatter":
        ax.scatter(df[x_col], df[y_col], alpha=0.6, color='#ff6b35')
    elif chart_type == "Line":
        ax.plot(df[x_col], df[y_col], color='#ff6b35', linewidth=2)
    elif chart_type == "Bar":
        df_grouped = df.groupby(x_col)[y_col].mean()
        df_grouped.plot(kind='bar', ax=ax, color='#ff6b35')
    elif chart_type == "Histogram":
        ax.hist(df[y_col].dropna(), bins=30, color='#ff6b35', edgecolor='#1a1a1a')
    elif chart_type == "Box Plot":
        df[[x_col, y_col]].boxplot(ax=ax)
    
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f"{chart_type}: {x_col} vs {y_col}")
    plt.tight_layout()
    
    return fig


def create_missing_values_chart(missing_df):
    """Create bar chart for missing values"""
    fig, ax = plt.subplots(figsize=(10, 6))
    setup_dark_theme(fig, ax)
    ax.barh(missing_df['Column'], missing_df['Missing %'], color='#ff6b35')
    ax.set_xlabel('Missing %', color='#e0e0e0')
    ax.set_title('Missing Values by Column', color='#ffffff')
    plt.tight_layout()
    return fig


def create_correlation_heatmap(numeric_df):
    """Create correlation heatmap"""
    corr_matrix = numeric_df.corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#2d2d2d')
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn', 
               center=0, ax=ax, cbar_kws={'label': 'Correlation'})
    ax.set_title('Correlation Heatmap', color='#ffffff', pad=20)
    plt.tight_layout()
    
    return fig, corr_matrix


def create_distribution_plots(numeric_df, column):
    """Create histogram and box plot for a column"""
    # Histogram
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    setup_dark_theme(fig1, ax1)
    ax1.hist(numeric_df[column].dropna(), bins=30, color='#ff6b35', 
           edgecolor='#1a1a1a', alpha=0.7)
    ax1.set_title(f'Distribution of {column}', color='#ffffff')
    ax1.set_xlabel(column, color='#e0e0e0')
    ax1.set_ylabel('Frequency', color='#e0e0e0')
    plt.tight_layout()
    
    # Box plot
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    setup_dark_theme(fig2, ax2)
    ax2.boxplot(numeric_df[column].dropna(), vert=True, patch_artist=True,
              boxprops=dict(facecolor='#ff6b35', alpha=0.7),
              medianprops=dict(color='#1a1a1a', linewidth=2),
              whiskerprops=dict(color='#a0a0a0'),
              capprops=dict(color='#a0a0a0'))
    ax2.set_title(f'Box Plot of {column}', color='#ffffff')
    ax2.set_ylabel(column, color='#e0e0e0')
    plt.tight_layout()
    
    return fig1, fig2


def get_column_statistics(numeric_df, column):
    """Calculate statistics for a column"""
    return pd.DataFrame({
        'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Q1', 'Q3'],
        'Value': [
            numeric_df[column].mean(),
            numeric_df[column].median(),
            numeric_df[column].std(),
            numeric_df[column].min(),
            numeric_df[column].max(),
            numeric_df[column].quantile(0.25),
            numeric_df[column].quantile(0.75)
        ]
    }).round(2)


def get_top_correlations(corr_matrix, top_n=10):
    """Get top N correlations from correlation matrix"""
    corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_pairs.append({
                'Variable 1': corr_matrix.columns[i],
                'Variable 2': corr_matrix.columns[j],
                'Correlation': corr_matrix.iloc[i, j]
            })
    
    return pd.DataFrame(corr_pairs).sort_values('Correlation', key=abs, ascending=False).head(top_n)