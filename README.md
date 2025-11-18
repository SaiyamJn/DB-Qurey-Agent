# DataSense

An AI-powered data analysis tool that lets you query CSV files using natural language. Built with Streamlit and powered by Google's Gemini API.

## Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Interactive Chat Interface**: Conversational data exploration
- **Visual Dashboard**: Charts, statistics, and data previews
- **Advanced Analytics**: Correlation analysis, distribution plots, and AI-generated insights
- **Dark Theme**: Modern, minimal UI optimized for readability

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-based-query-support-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   
   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

1. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

2. **Upload your CSV file** using the sidebar

3. **Start asking questions** like:
   - "Show me the first 10 rows"
   - "What's the average sales by category?"
   - "Filter rows where revenue > 5000"
   - "Group by region and count customers"

## Project Structure

```
src/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration settings
├── data_handler.py       # CSV loading and processing
├── gemini_api.py         # Gemini API integration
├── query_processor.py    # Natural language query processing
├── ui_components.py      # UI styling and components
└── visualization.py      # Chart generation
```

## Requirements

- Python 3.8+
- Streamlit
- pandas
- numpy
- matplotlib
- seaborn
- requests
- python-dotenv

## How It Works

1. **Upload Data**: Load your CSV file through the sidebar
2. **Ask Questions**: Type natural language queries in the chat interface
3. **AI Processing**: Gemini API interprets your query and generates pandas/SQL code
4. **View Results**: Get instant results with explanations and visualizations

## Examples

**Basic queries:**
```
- Show me the data
- What columns are available?
- How many rows are there?
```

**Filtering:**
```
- Filter where price > 100
- Show rows with status = 'active'
```

**Aggregation:**
```
- Average price by category
- Sum of sales grouped by region
- Count unique customers
```

**Analysis:**
```
- Show correlation between price and sales
- Distribution of age column
- Top 10 products by revenue
```

## Features by Tab

### Chat
- Interactive conversation with your data
- Natural language query processing
- Code explanation for each query
- Chat history with delete functionality

### Dashboard
- Data overview with key metrics
- Interactive chart builder
- Data preview with adjustable rows
- CSV export functionality

### Analytics
- Statistical summaries
- Missing value analysis
- Correlation heatmaps
- Distribution plots
- AI-generated insights

## License
MIT License