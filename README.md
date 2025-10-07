# Prompt Service (Technical Test)

## Stack
- Python 3.12, Django, DRF, JWT (SimpleJWT)
- Channels + Redis (WebSocket)
- FAISS + Sentence-Transformers (similaridad)
- Postgres (persistencia)
- Prometheus (metrics `/metrics`)
- Throttling: 1 req/s y 10 req/min en `POST /prompts`
- Logging JSON

## Correr con Docker
```bash
docker-compose up --build
```

## Endpoints

- Autenticación (JWT):
  - POST `/api/auth/register/` { username, email, password }
  - POST `/api/auth/login/` { username, password } → { access, refresh }
  - POST `/api/auth/refresh/` { refresh } → { access }

- Prompts:
  - POST `/api/prompts` { prompt: string, websocket?: bool }
    - Autenticado con `Authorization: Bearer <token>`
    - Throttling: 1 req/s y 10 req/min
    - Si `websocket=true`, se envía un evento al grupo del usuario `user_<id>`
  - GET `/api/prompts/similar?q=<texto>&k=<n>`
    - Autenticado
    - Busca similares en FAISS

- Observabilidad:
  - GET `/metrics` (Prometheus)
  - GET `/docs` (Swagger UI), `/redoc` (Redoc), `/schema` (OpenAPI JSON)

## Ejemplos (curl)

```bash
# registrar usuario
curl -X POST http://localhost:8000/api/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","email":"a@b.c","password":"secret123"}'

# login
ACCESS=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"secret123"}' | jq -r .access)

# crear prompt
curl -X POST http://localhost:8000/api/prompts \
  -H "Authorization: Bearer $ACCESS" -H 'Content-Type: application/json' \
  -d '{"prompt":"hola mundo","websocket":false}'

# similares
curl -H "Authorization: Bearer $ACCESS" \
  'http://localhost:8000/api/prompts/similar?q=hola&k=3'
```

## WebSocket

- URL: `ws://localhost:8000/ws/prompts/`
- Autenticación: usa sesión de Django si el cliente comparte cookies. Para JWT, añade el token como query string `?token=` y agrega un middleware de Channels que valide JWT (no incluido por simplicidad). Actualmente, si estás autenticado por sesión, el servidor te unirá al grupo `user_<id>` y recibirás eventos `prompt.message`.

Probar con wscat:
```bash
wscat -c ws://localhost:8000/ws/prompts/
```

## Variables de entorno

- `OPENAI_API_KEY` (opcional): si está presente y el SDK disponible, se usa OpenAI real; de lo contrario, respuestas mock.

## Tests

```bash
pytest -q
```

## Despliegue AWS (opcional - plan)

- ECS Fargate (tarea con `daphne`), detrás de ALB
- RDS Postgres, ElastiCache Redis
- Secrets Manager para credenciales
- CloudWatch Logs y métricas/alarms
- ECR para imágenes y GitHub Actions para CI/CD (build, push, deploy)