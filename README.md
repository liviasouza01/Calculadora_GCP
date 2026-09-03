# Calculadora de Custos GCP — Projetos de Dados

Calculadora simples para estimar custos de infraestrutura de dados no Google
Cloud (Cloud Storage, BigQuery on-demand/Enterprise, Looker, Datastream, Pub/Sub, Data
Transfer Service, Dataflow, Cloud Composer), com base em preços oficiais
publicados pelo Google Cloud (região US), cada um citado com sua fonte.

## Arquitetura

- **Backend (FastAPI)**: cada serviço GCP é um `Calculator` (em
  `backend/app/domain/calculators/`) que implementa uma interface comum
  (`BaseCalculator`). Os preços oficiais ficam centralizados e citados em
  `backend/app/data/pricing.py`. A API é genérica: `GET /api/services` lista
  todos os serviços com seus campos de entrada e preços; `POST
  /api/services/{id}/calculate` calcula um serviço; `POST
  /api/calculate/project` calcula vários serviços de uma vez (o "projeto").
  Adicionar um novo serviço GCP não exige mudanças na API.
- **Frontend (React + TypeScript)**: um único componente genérico
  (`ServiceForm`) renderiza o formulário de qualquer serviço a partir do
  schema retornado pela API — não há formulário hardcoded por serviço.

## Rodando com Docker (recomendado)

Requer Docker e Docker Compose.

```bash
make up       # builda as imagens e sobe backend + frontend em background
make logs     # acompanha os logs dos dois serviços
make down     # para e remove os containers
make restart  # down + up
make clean    # para os containers e remove imagens/volumes locais
make ps       # lista os containers em execução
```

- Frontend: ://localhost:http3000 (Nginx servindo o build estático, faz proxy de `/api` para o backend)
- Backend: http://localhost:8000 (FastAPI, acessível também diretamente)

## Rodando sem Docker (desenvolvimento)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173 (o Vite já faz proxy de `/api` para `http://localhost:8000`).

## Aviso sobre os preços

Os valores usados são preços públicos on-demand (sem desconto por
compromisso de uso, sem SUDs, sem impostos) da região `us`/`us-central1`,
coletados das páginas oficiais de pricing do Google Cloud em setembro de
2026. Cada preço no app tem um link "fonte oficial" e uma data de
verificação. Preços do Google Cloud mudam com frequência — confirme sempre
na página oficial antes de usar os números para uma decisão de compra.
