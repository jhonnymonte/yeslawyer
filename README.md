# Prompt Service (Technical Test)

## Stack
- Python 3.12, Django, DRF, JWT (SimpleJWT)
- Channels + Redis (WebSocket)
- FAISS + Sentence-Transformers (similarity)
- Postgres (persistence)
- Prometheus (metrics `/metrics`)
- Throttling: 1 req/s and 10 req/min on `POST /prompts`
- JSON Logging

## Run with Docker
```bash
docker-compose up --build
```

## Endpoints

- Authentication (JWT):
  - POST `/api/auth/register/` { username, email, password }
  - POST `/api/auth/login/` { username, password } → { access, refresh }
  - POST `/api/auth/refresh/` { refresh } → { access }

- Prompts:
  - POST `/api/prompts` { prompt: string, websocket?: bool }
    - Authenticated with `Authorization: Bearer <token>`
    - Throttling: 1 req/s and 10 req/min
    - If `websocket=true`, an event is sent to the user's group `user_<id>`
  - GET `/api/prompts/similar?q=<text>&k=<n>`
    - Authenticated
    - Searches similar in FAISS

- Observability:
  - GET `/metrics` (Prometheus)
  - GET `/docs` (Swagger UI), `/redoc` (Redoc), `/schema` (OpenAPI JSON)

## Examples (curl)

```bash
# register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"a@b.c","password":"secret123"}'

# login
ACCESS=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"secret123"}' | jq -r .access)

# create prompt
curl -X POST http://localhost:8000/api/prompts \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d '{"prompt":"hello world","websocket":false}'

# similars
curl -H "Authorization: Bearer $ACCESS" \
  'http://localhost:8000/api/prompts/similar?q=hello&k=3'
```

## WebSocket

- URL: `ws://localhost:8000/ws/prompts/`
- Authentication: uses Django session if the client shares cookies. For JWT, add the token as a query string `?token=` and add a Channels middleware that validates JWT (not included for simplicity). Currently, if you are authenticated by session, the server will join you to the group `user_<id>` and you will receive `prompt.message` events.

Test with wscat:
```bash
wscat -c ws://localhost:8000/ws/prompts/
```

## Environment variables

- `OPENAI_API_KEY` (optional): if present and the SDK available, real OpenAI is used; otherwise, mock responses.

## Tests

```bash
pytest -q
```

## AWS Deployment (optional - plan)

- ECS Fargate (task with `daphne`), behind ALB
- RDS Postgres, ElastiCache Redis
- Secrets Manager for credentials
- CloudWatch Logs and metrics/alarms
- ECR for images and GitHub Actions for CI/CD (build, push, deploy)