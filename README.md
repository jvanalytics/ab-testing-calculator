# CRO Portugal - Calculadora de Testes A/B

Uma aplicação web Python totalmente funcional e pronta para produção, construída com Flask, que fornece uma suíte completa de calculadoras estatísticas para testes A/B. A aplicação está totalmente containerizada para fácil implantação e focada no mercado português.

## Features

### 1. Conversion Rate Significance Test
- **Two-Proportion Z-Test** for comparing conversion rates between control and variant groups
- Calculates conversion rates, absolute & relative lift, Z-score, P-value
- Provides significance decision and interpretation

### 2. Average Value Significance Test
- **Welch's t-test** (parametric) for comparing means with unequal variances
- **Mann-Whitney U test** (non-parametric) alternative
- Calculates mean difference, test statistics, P-value, confidence intervals
- Provides interpretation of results

### 3. A/B Test Planner - Proportion Test
- Calculates required sample size for proportion/conversion rate tests
- Supports both absolute and relative Minimum Detectable Effect (MDE)
- Configurable power and alpha levels
- Estimates test duration based on daily traffic

### 4. A/B Test Planner - Average Value
- Calculates required sample size for continuous variable tests
- Uses t-test methodology
- Estimates test duration based on daily sample volume
- Calculates Cohen's d effect size

### Idioma
- Interface totalmente em Português
- Focado no mercado português

## Technology Stack

- **Backend**: Flask 3.0.0
- **Statistics**: SciPy, NumPy
- **Frontend**: Bootstrap 5.3.0
- **WSGI Server**: Gunicorn
- **Containerization**: Docker

## Project Structure

```
ab-testing-calculator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Production Docker image
├── docker-compose.yml    # Docker Compose configuration
├── utils/
│   ├── __init__.py
│   └── statistics.py     # Statistical functions
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── conversion_rate.html
│   ├── average_value.html
│   ├── planner_proportion.html
│   └── planner_average.html
└── tests/
    ├── __init__.py
    └── test_statistics.py  # Unit tests
```

## Local Development Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd ab-testing-calculator
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables (optional):**
   ```bash
   # Windows
   set SECRET_KEY=your-secret-key-here
   set FLASK_DEBUG=True
   
   # Linux/Mac
   export SECRET_KEY=your-secret-key-here
   export FLASK_DEBUG=True
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

1. **Build the Docker image:**
   ```bash
   docker build -t ab-testing-calculator .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 \
     -e SECRET_KEY=your-secret-key-here \
     --name ab-testing-calculator \
     ab-testing-calculator
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Railway Deployment

Railway is a modern platform for deploying applications. Follow these steps to deploy:

### Prerequisites
- A Railway account (sign up at [railway.app](https://railway.app))
- Railway CLI installed (optional, but recommended)

### Deployment Steps

#### Option 1: Using Railway Dashboard (Easiest)

1. **Create a new project:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo" (if your code is on GitHub) or "Empty Project"

2. **Configure the project:**
   - If deploying from GitHub, select your repository
   - Railway will automatically detect the Dockerfile

3. **Set environment variables:**
   - Go to your project settings
   - Add environment variable:
     - `SECRET_KEY`: Generate a secure random string (e.g., use `openssl rand -hex 32`)
     - `PORT`: Railway sets this automatically, but you can verify it's set to `5000`

4. **Deploy:**
   - Railway will automatically build and deploy when you push to your repository
   - Or click "Deploy" in the dashboard

5. **Access your application:**
   - Railway will provide a public URL (e.g., `https://your-app.railway.app`)
   - The application will be accessible at this URL

#### Option 2: Using Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize and link project:**
   ```bash
   railway init
   railway link
   ```

4. **Set environment variables:**
   ```bash
   railway variables set SECRET_KEY=your-secret-key-here
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

### Railway-Specific Configuration

The Dockerfile is already configured for Railway:
- Uses port 5000 (Railway's default)
- Runs Gunicorn with 4 workers
- Includes health checks
- Uses non-root user for security

### Post-Deployment

1. **Verify deployment:**
   - Check the Railway dashboard for deployment status
   - View logs to ensure the application started correctly

2. **Custom domain (optional):**
   - In Railway dashboard, go to Settings → Domains
   - Add your custom domain

3. **Environment variables:**
   - Ensure `SECRET_KEY` is set to a secure value
   - Railway automatically sets `PORT`, but verify it's `5000`

## Running Tests

Run the unit tests to verify statistical functions:

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest tests.test_statistics
```

## Exemplos de Uso

### Teste de Taxa de Conversão
1. Navegue para "Teste de Taxa de Conversão"
2. Insira:
   - Visitantes do controle: 1000
   - Conversões do controle: 50
   - Visitantes da variante: 1000
   - Conversões da variante: 60
3. Clique em "Calcular"
4. Revise os resultados incluindo Z-score, valor P e significância

### Teste de Valor Médio
1. Navegue para "Teste de Valor Médio"
2. Selecione o tipo de teste (teste t de Welch ou U de Mann-Whitney)
3. Insira média, desvio padrão e tamanho da amostra para ambos os grupos
4. Clique em "Calcular"
5. Revise os resultados incluindo intervalos de confiança

### Planejador de Teste
1. Navegue para "Planejador de Proporção" ou "Planejador de Média"
2. Insira métricas de linha de base e tamanho de efeito desejado
3. Defina níveis de poder e alpha
4. Opcionalmente, insira tráfego diário/volume de amostra
5. Clique em "Calcular"
6. Revise o tamanho de amostra necessário e duração estimada

## Statistical Methods

### Two-Proportion Z-Test
- Formula: `z = (p1 - p2) / sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))`
- Used for comparing conversion rates between two groups
- Assumes normal approximation (large sample sizes)

### Welch's t-Test
- Formula: `t = (mean_a - mean_b) / sqrt(sd_a²/n_a + sd_b²/n_b)`
- Used for comparing means with unequal variances
- More robust than standard t-test when variances differ

### Mann-Whitney U Test
- Non-parametric alternative to t-test
- Does not assume normal distribution
- Based on rank ordering of data

### Sample Size Calculations
- Based on power analysis methodology
- Accounts for desired effect size, power, and alpha level
- Provides conservative estimates for real-world scenarios

## Security Considerations

- **Secret Key**: Always set a strong `SECRET_KEY` in production
- **HTTPS**: Use HTTPS in production (Railway provides this automatically)
- **Input Validation**: All inputs are validated on the server side
- **Non-root User**: Docker container runs as non-root user

## Troubleshooting

### Application won't start
- Check that port 5000 is not already in use
- Verify all dependencies are installed
- Check logs for error messages

### Docker build fails
- Ensure Docker is running
- Check that Dockerfile syntax is correct
- Verify all files are in the correct locations

### Railway deployment issues
- Check Railway logs in the dashboard
- Verify environment variables are set correctly
- Ensure Dockerfile is in the root directory
- Check that PORT environment variable is set to 5000

## Contributing

This is a production-ready application. To extend it:

1. Add new statistical tests in `utils/statistics.py`
2. Add corresponding routes in `app.py`
3. Create templates in `templates/`
4. Write tests in `tests/`

## License

This project is provided as-is for educational and professional use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments in `utils/statistics.py` for formula details
3. Consult statistical references for methodology validation

---

**CRO Portugal - Otimização de Taxa de Conversão e Testes A/B em Portugal**

**Construído com Flask | Implantado com Docker | Pronto para Railway**

