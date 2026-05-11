# -Smart-Life-Coach-backend
Backend for the repository Smart-Life-Coach

## Intrucciones para obtener las variables de .env
Entrar en el repositorio Smart-Life-Coach-DB  y con el comando:
```bash
npx supabase status
```
Obtener la SUPABASE_JWT_SECRET y ponerla en el .env

## Correr en entorno virtual con uv y uvicorn
```bash
uv venv .venv --python 3.13.5
```

```bash
source .venv/bin/activate
```

```bash
uv pip install -r requirements.txt
```

```bash
uvicorn main:app --port 8000 --reload
```

##  Docker
Para montar la imagen de Docker estando en la carpeta frontend vamos a ejecutar estos dos comandos (obviamente debes tener Docker instalado y corriendo):

```Bash 
docker docker build -t fast-backend .
```

```Bash 
docker run -p 8000:8000\
  --name mi-server-fastapi \
  --add-host host.docker.internal:host-gateway \
  -e SUPABASE_URL=http://host.docker.internal:54321\
  fast-backend
```
Abrir http://localhost:8000/docs en tu navegador para ver el status de tu api
