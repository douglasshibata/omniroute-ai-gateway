# 📘 Tutorial de Uso do OmniRoute AI Gateway

Este guia demonstra como inicializar, testar e integrar o gateway OmniRoute às suas aplicações em Python, TypeScript e cURL.

---

## 1. Pré-requisitos e Instalação

```bash
cd omniroute-ai-gateway
pip install -r requirements.txt
```

---

## 2. Inicializando o Gateway

```bash
uvicorn src.main:app --host 0.0.0.0 --port 20128
```

---

## 3. Exemplos de Chamadas

### Verificando a Saúde do Gateway
```bash
curl -s http://localhost:20128/health
```

### Listando Modelos Homologados
```bash
curl -s http://localhost:20128/v1/models \
  -H "Authorization: Bearer omniroute-local-secret"
```

### Completando Chat com Auto-Routing Dinâmico
```bash
curl -s http://localhost:20128/v1/chat/completions \
  -H "Authorization: Bearer omniroute-local-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Explique padrões de resiliência em microsserviços."}
    ]
  }'
```

---

## 4. Executando os Testes Automatizados

```bash
PYTHONPATH=omniroute-ai-gateway pytest omniroute-ai-gateway/tests/ -v
```
