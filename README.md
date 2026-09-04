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

### Agente (preencher a partir de briefing)

Na interface, anexe uma ou várias transcrições (PDF, TXT ou Word) e, se quiser, um ou vários PNG/JPG da arquitetura. O backend usa o [Agent Development Kit](https://google.github.io/adk-docs/get-started/python/) da Google (`Agent` + `FunctionTool` + `Runner`).

Defina a chave do Gemini no ambiente do backend:

```bash
export GOOGLE_API_KEY="sua-chave"
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

No Docker Compose, as mesmas variáveis são lidas do ambiente da máquina (ou de um `.env` na raiz). No Cloud Run, configure `GOOGLE_API_KEY` como variável/secret do serviço.

## Deploy em produção

O projeto está publicado no Google Cloud, projeto `calculadora-gcp`:

- **Frontend**: Firebase Hosting — https://calculadora-gcp.web.app
- **Backend**: Cloud Run — serviço `calculadora-gcp-backend`, região `us-central1`

O Firebase Hosting redireciona toda rota `/api/**` para o serviço do Cloud
Run (configurado em `firebase.json`), então o frontend chama a API por
caminho relativo (`/api/...`) sem problema de CORS.

### Pré-requisitos (uma vez só)

```bash
npm install -g firebase-tools
firebase login
gcloud auth login
gcloud config set project calculadora-gcp
```

### Atualizar o backend (Cloud Run)

Sempre que mudar algo em `backend/`:

```bash
cd backend
gcloud run deploy calculadora-gcp-backend \
  --source . \
  --region us-central1 \
  --project calculadora-gcp \
  --allow-unauthenticated \
  --port 8000
```

Isso builda a imagem via Cloud Build e atualiza o serviço em produção. Não
precisa mexer no `firebase.json` — o `serviceId`/`region` já apontam para
esse serviço.

### Atualizar o frontend (Firebase Hosting)

Sempre que mudar algo em `frontend/`:

```bash
cd frontend
npm run build      # gera frontend/dist
cd ..
firebase deploy --only hosting
```

**Atenção**: nunca rode `firebase init hosting` de novo neste projeto sem
cuidado — ele sobrescreve o `firebase.json` e apaga o rewrite `/api/**` para
o Cloud Run, deixando a API inacessível (o site carrega mas mostra erro de
conexão). Se isso acontecer, o `firebase.json` deve conter, nessa ordem:

```json
{
  "hosting": {
    "public": "frontend/dist",
    "rewrites": [
      {
        "source": "/api/**",
        "run": { "serviceId": "calculadora-gcp-backend", "region": "us-central1" }
      },
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

A regra do `/api/**` tem que vir **antes** da regra genérica `**`, senão o
catch-all do SPA intercepta as chamadas de API primeiro.

### Deploy completo (backend + frontend)

```bash
cd backend && gcloud run deploy calculadora-gcp-backend --source . --region us-central1 --project calculadora-gcp --allow-unauthenticated --port 8000 && cd ..
cd frontend && npm run build && cd ..
firebase deploy --only hosting
```

## Aviso sobre os preços

Os valores usados são preços públicos on-demand (sem desconto por
compromisso de uso, sem SUDs, sem impostos) da região `us`/`us-central1`,
coletados das páginas oficiais de pricing do Google Cloud em setembro de
2026. Cada preço no app tem um link "fonte oficial" e uma data de
verificação. Preços do Google Cloud mudam com frequência — confirme sempre
na página oficial antes de usar os números para uma decisão de compra.
