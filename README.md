# AutoML No-Code Platform

A fully autonomous machine learning platform that accepts natural language problem descriptions and automatically executes the complete ML pipeline from data acquisition to model deployment.

## Features

- 🤖 **Natural Language Interface**: Describe your ML problem in plain English
- 📊 **Automatic Data Acquisition**: Fetches datasets from Kaggle, HuggingFace, UCI, or generates synthetic data
- 🔧 **Smart Preprocessing**: LLM-guided data cleaning, encoding, and feature engineering
- 🎯 **Multi-Model Training**: Trains XGBoost, LightGBM, CatBoost, Random Forest, and more
- 📈 **Comprehensive Evaluation**: Generates metrics, visualizations, and model cards
- 🚀 **One-Click Deployment**: Automatic FastAPI + Docker deployment configs
- 💻 **Interactive Dashboard**: Real-time progress tracking and results visualization

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Docker (optional, for deployment)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd automl-agent
```

2. **Install Python dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Initialize the system**
```bash
python -c "from app.storage import ensure_dirs; ensure_dirs()"
python -c "from app.main import init_db; init_db()"
```

5. **Start the backend**
```bash
uvicorn app.main:app --reload --port 8000
```

6. **Access the dashboard**
Open your browser to: `http://localhost:8000/dashboard`

## Configuration

### LLM Providers

The system supports multiple LLM providers. Configure in `.env`:

**OpenAI (Recommended)**
```env
LLM_MODE=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

**Anthropic Claude**
```env
LLM_MODE=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Google Gemini**
```env
LLM_MODE=gemini
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Ollama (Local)**
```env
LLM_MODE=ollama
OLLAMA_MODEL=mistral:latest
OLLAMA_URL=http://localhost:11434/api/generate
```

### Data Sources

**Kaggle**
```env
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

**HuggingFace**
```env
HF_DATASETS_CACHE=path_to_cache
```

## Usage

### Via Dashboard

1. Navigate to `http://localhost:8000/dashboard`
2. Enter your problem statement (e.g., "Predict customer churn")
3. Optionally upload a dataset or let the system find one
4. Click "Start Run" and monitor progress
5. View results, download model, and get deployment configs

### Via API

**Start a new run:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Predict house prices",
    "preferences": {
      "training_budget_minutes": 5,
      "primary_metric": "r2"
    }
  }'
```

**Check run status:**
```bash
curl http://localhost:8000/status/{run_id}
```

**List all runs:**
```bash
curl http://localhost:8000/runs
```

## Architecture

```
┌─────────────────────────────────────────┐
│           Orchestrator                   │
│      (FastAPI + Background Worker)       │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼───┐         ┌───▼───┐
│  PS   │         │ Data  │
│ Agent │         │ Agent │
└───┬───┘         └───┬───┘
    │                 │
┌───▼───┐         ┌───▼───┐
│ Prep  │         │AutoML │
│ Agent │         │ Agent │
└───┬───┘         └───┬───┘
    │                 │
┌───▼───┐         ┌───▼───┐
│ Eval  │         │Deploy │
│ Agent │         │ Agent │
└───────┘         └───────┘
```

## Supported Models

### Classification
- XGBoost
- LightGBM
- CatBoost
- Random Forest
- Extra Trees
- Gradient Boosting
- Logistic Regression
- SVM
- K-Nearest Neighbors

### Regression
- XGBoost
- LightGBM
- Random Forest
- Extra Trees
- Gradient Boosting
- Linear Regression
- SGD Regressor

## API Endpoints

- `POST /run` - Start a new ML pipeline run
- `GET /status/{run_id}` - Get run status and logs
- `GET /runs` - List all runs
- `POST /ps` - Interactive problem statement parsing
- `GET /dashboard` - Web dashboard UI
- `GET /artifacts/{filename}` - Download artifact files
- `GET /health` - Health check endpoint

## Development

### Project Structure

```
automl-agent/
├── app/
│   ├── agents/           # Specialized ML agents
│   │   ├── ps_agent.py
│   │   ├── data_agent.py
│   │   ├── prep_agent.py
│   │   ├── automl_agent.py
│   │   ├── eval_agent.py
│   │   └── deploy_agent.py
│   ├── utils/            # Utility modules
│   │   ├── llm_clients.py
│   │   └── run_logger.py
│   ├── main.py           # FastAPI application
│   └── storage.py        # Artifact management
├── artifacts/            # Generated artifacts
├── data/                 # Dataset storage
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov hypothesis

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_ps_agent.py
```

### Adding a New Agent

1. Create agent file in `app/agents/`
2. Implement main function with signature: `def agent_function(run_id, ...)`
3. Add logging with `agent_log(run_id, message, agent="agent_name")`
4. Handle errors and return structured results
5. Integrate in `orchestrate_run()` in `main.py`

## Deployment

### Docker

```bash
# Build image
docker build -t automl-platform .

# Run container
docker run -p 8000:8000 --env-file .env automl-platform
```

### Render

1. Create `render.yaml` (generated by deployment agent)
2. Connect GitHub repository to Render
3. Deploy with one click

### Railway

1. Create `railway.json` (generated by deployment agent)
2. Connect GitHub repository to Railway
3. Deploy with one click

## Troubleshooting

### LLM Connection Issues

**Problem**: "LLM call failed" errors

**Solution**:
- Check API keys in `.env`
- Verify internet connection
- Check API rate limits
- Try fallback provider

### Dataset Download Fails

**Problem**: Cannot download datasets

**Solution**:
- Check Kaggle credentials
- Verify HuggingFace access
- System will auto-generate synthetic data as fallback

### Out of Memory During Training

**Problem**: Training crashes with OOM error

**Solution**:
- Reduce `training_budget_minutes` in preferences
- Use smaller dataset
- Increase system RAM
- Use models with lower memory footprint (LightGBM, Linear models)

### Model Training Takes Too Long

**Problem**: Training exceeds time budget

**Solution**:
- Increase `training_budget_minutes`
- Reduce number of models in estimator list
- Use faster HPO strategy (Random Search instead of Bayesian)

## Performance Tips

- **Small datasets (<1k rows)**: Use Grid Search, train all models
- **Medium datasets (1k-100k rows)**: Use Random Search, focus on tree-based models
- **Large datasets (>100k rows)**: Use Bayesian Optimization, use LightGBM/XGBoost only
- **High cardinality categoricals**: Use Ordinal encoding instead of OneHot
- **Imbalanced classes**: Enable SMOTE in preferences

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [repository-url]/docs

## Acknowledgments

- FLAML for AutoML framework
- FastAPI for web framework
- scikit-learn for ML algorithms
- All LLM providers (OpenAI, Anthropic, Google)
