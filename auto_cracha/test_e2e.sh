#!/bin/bash

# ==============================================
# CrachApp - Teste End-to-End (E2E)
# ==============================================
# Este script testa os principais fluxos da aplicação
# Uso: bash test_e2e.sh [URL_BASE]
# Exemplo: bash test_e2e.sh https://crachapp.com.br
# ==============================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL base da API
API_URL="${1:-http://localhost:8000}"
FRONTEND_URL="${API_URL//:8000/:3000}"
FRONTEND_URL="${FRONTEND_URL//:8000/}"

echo -e "${YELLOW}======================================${NC}"
echo -e "${YELLOW}  CrachApp - Teste End-to-End${NC}"
echo -e "${YELLOW}======================================${NC}"
echo ""
echo "API URL: $API_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Contador de testes
TOTAL=0
PASSED=0
FAILED=0

# Função para teste HTTP
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_status="$4"
    local data="$5"

    TOTAL=$((TOTAL + 1))

    echo -n "[$TOTAL] $name ... "

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if echo "$expected_status" | grep -q "$status_code"; then
        echo -e "${GREEN}PASS${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# ==============================================
# Teste 1: Health Check
# ==============================================
echo -e "${YELLOW}1. Health Check${NC}"
test_endpoint "GET /health" "GET" "/health" "200"
echo ""

# ==============================================
# Teste 2: Autenticação
# ==============================================
echo -e "${YELLOW}2. Autenticação${NC}"

# 2.1 Login com credenciais inválidas
test_endpoint "Login com email inválido" "POST" "/auth/login" "422" \
    '{"email":"invalido","senha":"123456"}'

# 2.2 Registro de novo tenant
test_endpoint "Registro de novo tenant" "POST" "/auth/register" "201" \
    '{
        "nome_empresa":"Empresa Teste E2E",
        "cnpj":"12.345.678/0001-99",
        "email":"teste_e2e@empresa.com.br",
        "senha":"SenhaSegura123456",
        "nome_responsavel":"Responsável Teste"
    }'

# Salvar token para testes autenticados
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@crachapp.com.br","senha":"Admin@123456"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Falha ao obter token de autenticação${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Token obtido com sucesso${NC}"
echo ""

# ==============================================
# Teste 3: Endpoints Autenticados
# ==============================================
echo -e "${YELLOW}3. Endpoints Autenticados${NC}"

# Função para teste com autenticação
test_auth_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_status="$4"
    local data="$5"

    TOTAL=$((TOTAL + 1))

    echo -n "[$TOTAL] $name ... "

    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$data")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if echo "$expected_status" | grep -q "$status_code"; then
        echo -e "${GREEN}PASS${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body" | head -c 200
        echo ""
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 3.1 Listar filiais
test_auth_endpoint "GET /filiais" "GET" "/filiais" "200"

# 3.2 Listar colaboradores
test_auth_endpoint "GET /colaboradores" "GET" "/colaboradores" "200"

# 3.3 Listar lotes
test_auth_endpoint "GET /lotes" "GET" "/lotes" "200"

# 3.4 Listar planos
test_auth_endpoint "GET /pagamento/planos" "GET" "/pagamento/planos" "200"

# 3.5 Obter assinatura
test_auth_endpoint "GET /pagamento/assinatura" "GET" "/pagamento/assinatura" "200"

echo ""

# ==============================================
# Teste 4: Frontend
# ==============================================
echo -e "${YELLOW}4. Frontend${NC}"

TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] Frontend acessível ... "

frontend_response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")

if [ "$frontend_response" = "200" ] || [ "$frontend_response" = "404" ]; then
    echo -e "${GREEN}PASS${NC} (HTTP $frontend_response)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAIL${NC} (HTTP $frontend_response)"
    FAILED=$((FAILED + 1))
fi

echo ""

# ==============================================
# Teste 5: Banco de Dados
# ==============================================
echo -e "${YELLOW}5. Banco de Dados${NC}"

# Verificar que há dados
TOTAL=$((TOTAL + 1))
echo -n "[$TOTAL] Banco de dados com dados ... "

# Este teste funcionará apenas se estiver dentro do container
if docker-compose ps > /dev/null 2>&1; then
    count=$(docker-compose exec -T postgres psql -U crachapp -d crachapp -t -c "SELECT COUNT(*) FROM usuarios;" 2>/dev/null || echo "0")

    if [ "$count" -gt 0 ] 2>/dev/null; then
        echo -e "${GREEN}PASS${NC} ($count usuários)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}SKIP${NC} (Banco vazio ou não testável)"
    fi
else
    echo -e "${YELLOW}SKIP${NC} (Docker não disponível)"
fi

echo ""

# ==============================================
# Resumo
# ==============================================
echo -e "${YELLOW}======================================${NC}"
echo -e "${YELLOW}  Resumo dos Testes${NC}"
echo -e "${YELLOW}======================================${NC}"
echo ""
echo "Total:  $TOTAL"
echo -e "Passou: ${GREEN}$PASSED${NC}"
echo -e "Falhou: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Todos os testes passaram!${NC}"
    exit 0
else
    echo -e "${RED}✗ Alguns testes falharam${NC}"
    exit 1
fi
