import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

class Visualizer:
    """Handle all visualization and chart generation"""
    
    def __init__(self, df):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def _setup_dark_plot(self, figsize=(10, 6)):
        """Setup plot with dark theme"""
        fig, ax = plt.subplots(figsize=figsize)
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
        return fig, ax
    
    def render_chart_builder(self):
        """Render interactive chart builder"""
        cols = self.df.columns.tolist()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            chart_type = st.selectbox("Chart Type", ["Scatter", "Line", "Bar", "Histogram", "Box Plot"])
        with col2:
            x_col = st.selectbox("X-axis", cols, index=0)
        with col3:
            y_col = st.selectbox("Y-axis", cols, index=1 if len(cols) > 1 else 0)
        
        if st.button("Generate Chart", type="primary"):
            try:
                fig, ax = self._setup_dark_plot()
                
                if chart_type == "Scatter":
                    ax.scatter(self.df[x_col], self.df[y_col], alpha=0.6, color='#ff6b35')
                elif chart_type == "Line":
                    ax.plot(self.df[x_col], self.df[y_col], color='#ff6b35', linewidth=2)
                elif chart_type == "Bar":
                    df_grouped = self.df.groupby(x_col)[y_col].mean()
                    df_grouped.plot(kind='bar', ax=ax, color='#ff6b35')
                elif chart_type == "Histogram":
                    ax.hist(self.df[y_col].dropna(), bins=30, color='#ff6b35', edgecolor='#1a1a1a')
                elif chart_type == "Box Plot":
                    self.df[[x_col, y_col]].boxplot(ax=ax)
                
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{chart_type}: {x_col} vs {y_col}")
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
    
    def render_missing_values_analysis(self):
        """Render missing values analysis"""
        missing_df = pd.DataFrame({
            'Column': self.df.columns,
            'Missing Count': self.df.isnull().sum().values,
            'Missing %': (self.df.isnull().sum().values / len(self.df) * 100).round(2)
        })
        missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
        
        if len(missing_df) > 0:
            st.dataframe(missing_df, use_container_width=True)
            
            fig, ax = self._setup_dark_plot()
            ax.barh(missing_df['Column'], missing_df['Missing %'], color='#ff6b35')
            ax.set_xlabel('Missing %', color='#e0e0e0')
            ax.set_title('Missing Values by Column', color='#ffffff')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.success("No missing values found")
    
    def render_correlation_analysis(self):
        """Render correlation heatmap and top correlations"""
        numeric_df = self.df.select_dtypes(include=['number'])
        
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            
            fig, ax = self._setup_dark_plot(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn', 
                       center=0, ax=ax, cbar_kws={'label': 'Correlation'})
            ax.set_title('Correlation Heatmap', color='#ffffff', pad=20)
            plt.tight_layout()
            st.pyplot(fig)
            
            st.markdown("#### Strongest Correlations")
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_pairs.append({
                        'Variable 1': corr_matrix.columns[i],
                        'Variable 2': corr_matrix.columns[j],
                        'Correlation': corr_matrix.iloc[i, j]
                    })
            
            corr_df = pd.DataFrame(corr_pairs).sort_values('Correlation', key=abs, ascending=False).head(10)
            st.dataframe(corr_df, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for correlation analysis")
    
    def render_distribution_analysis(self):
        """Render distribution analysis with histogram and box plot"""
        if len(self.numeric_cols) > 0:
            selected_col = st.selectbox("Select column to analyze", self.numeric_cols)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig, ax = self._setup_dark_plot(figsize=(8, 6))
                ax.hist(self.df[selected_col].dropna(), bins=30, color='#ff6b35', 
                       edgecolor='#1a1a1a', alpha=0.7)
                ax.set_title(f'Distribution of {selected_col}', color='#ffffff')
                ax.set_xlabel(selected_col, color='#e0e0e0')
                ax.set_ylabel('Frequency', color='#e0e0e0')
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                fig, ax = self._setup_dark_plot(figsize=(8, 6))
                ax.boxplot(self.df[selected_col].dropna(), vert=True, patch_artist=True,
                          boxprops=dict(facecolor='#ff6b35', alpha=0.7),
                          medianprops=dict(color='#1a1a1a', linewidth=2),
                          whiskerprops=dict(color='#a0a0a0'),
                          capprops=dict(color='#a0a0a0'))
                ax.set_title(f'Box Plot of {selected_col}', color='#ffffff')
                ax.set_ylabel(selected_col, color='#e0e0e0')
                plt.tight_layout()
                st.pyplot(fig)
            
            st.markdown("#### Statistics")
            stats_df = pd.DataFrame({
                'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Q1', 'Q3'],
                'Value': [
                    self.df[selected_col].mean(),
                    self.df[selected_col].median(),
                    self.df[selected_col].std(),
                    self.df[selected_col].min(),
                    self.df[selected_col].max(),
                    self.df[selected_col].quantile(0.25),
                    self.df[selected_col].quantile(0.75)
                ]
            })
            stats_df['Value'] = stats_df['Value'].round(2)
            st.dataframe(stats_df, use_container_width=True)
        else:
            st.info("No numeric columns available for distribution analysis")