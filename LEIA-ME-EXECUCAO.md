# Como executar o painel IBGE

1. Extraia a pasta `ibge-reconstruido` inteira para o computador. Não separe os CSVs da pasta.
2. Abra essa pasta no VS Code e abra um terminal nela (a pasta precisa conter `app_home.py` e `requirements.txt`).
3. Crie e ative o ambiente virtual no PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação, execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` nesse terminal e repita a ativação.

4. Inicie o Streamlit:

```powershell
python -m streamlit run app_home.py
```

5. Abra o endereço local que o terminal mostrar, normalmente `http://localhost:8501`.

Use o menu lateral do Streamlit para abrir os Projetos 1 a 5. Os arquivos que estavam vazios foram reconstruídos usando as bases CSV disponíveis. A página 3 original foi mantida e ajustada para localizar o CSV corretamente.

## Sobre os dados

As páginas leem os CSVs que acompanham o projeto. Os dados foram preservados como recebidos e a aplicação não consegue confirmar sua procedência. Antes de apresentar os resultados como números oficiais do IBGE, confira fonte, ano de referência e metodologia das bases, em especial `rendimento_responsaveis.csv` e as tabelas de exemplo.
