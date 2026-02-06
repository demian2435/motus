FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install --no-root
CMD ["poetry", "run", "python", "-m", "motus"]
