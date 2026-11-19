FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/work
WORKDIR /work
COPY . .
RUN python -m pip install --no-cache-dir -r requirements.txt pip-audit PyYAML
RUN python -m pip check && python -m compileall -q app
RUN python -m pip_audit -r requirements.txt
RUN python -c "import yaml; yaml.safe_load(open('fintech-policy.yaml'))"
CMD ["true"]
