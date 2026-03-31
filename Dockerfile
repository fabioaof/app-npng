# Base Ubuntu
FROM ubuntu:22.04

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Instalar Quasar CLI (v2)
RUN npm install -g @quasar/cli

# Criar diretório da app
WORKDIR /app

# Expor porta do dev server
EXPOSE 8090

# Comando padrão
CMD ["bash"]

