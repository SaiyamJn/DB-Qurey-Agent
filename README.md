# DataSense

An AI-powered data analysis tool that lets you query CSV files using natural language. Built with Streamlit and powered by Google's Gemini API.

## Features

- **Multiple Data Sources**: Support for CSV files and database connections
  - **SQL**: PostgreSQL, MySQL, SQLite, SQL Server
  - **NoSQL**: MongoDB, Redis, Cassandra
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

2. **Upload your data** using one of two methods:
   - **CSV File**: Upload directly from the sidebar
   - **Database**: Connect to PostgreSQL, MySQL, SQLite, or SQL Server

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

**Optional SQL Database Drivers:**
- `psycopg2-binary` - for PostgreSQL
- `mysql-connector-python` - for MySQL
- `pyodbc` - for SQL Server
- SQLite support is built-in

**Optional NoSQL Database Drivers:**
- `pymongo` - for MongoDB
- `redis` - for Redis
- `cassandra-driver` - for Cassandra

Install database drivers only as needed:
```bash
# SQL Databases
pip install psycopg2-binary  # PostgreSQL
pip install mysql-connector-python  # MySQL
pip install pyodbc  # SQL Server

# NoSQL Databases
pip install pymongo  # MongoDB
pip install redis  # Redis
pip install cassandra-driver  # Cassandra
```

## How It Works

1. **Load Data**: 
   - Upload CSV files through the sidebar, OR
   - Connect to your database and select a table
2. **Ask Questions**: Type natural language queries in the chat interface
3. **AI Processing**: Gemini API interprets your query and generates pandas/SQL code
4. **View Results**: Get instant results with explanations and visualizations

### Database Connection

DataSense supports multiple database types:

**SQL Databases:**

*PostgreSQL:*
```
Host: localhost
Port: 5432
Database: your_database
Username: your_user
Password: your_password
```

*MySQL:*
```
Host: localhost
Port: 3306
Database: your_database
Username: your_user
Password: your_password
```

*SQLite:*
```
Database Path: /path/to/your/database.db
```

*SQL Server:*
```
Host: localhost
Port: 1433
Database: your_database
Username: your_user
Password: your_password
```

**NoSQL Databases:**

*MongoDB:*
```
Host: localhost
Port: 27017
Database: your_database
Username: your_user (optional)
Password: your_password (optional)
```

*Redis:*
```
Host: localhost
Port: 6379
Database Number: 0
Password: your_password (optional)
```

*Cassandra:*
```
Host: localhost
Port: 9042
Keyspace: your_keyspace (optional)
Username: your_user (optional)
Password: your_password (optional)
```

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
