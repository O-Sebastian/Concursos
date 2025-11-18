@echo off
setlocal enabledelayedexpansion

:: Definir o caminho para o arquivo de configuração
set CONFIG_FILE=config.txt

:: Verificar se o arquivo de configuração existe
if not exist %CONFIG_FILE% (
    echo Erro: Arquivo de configuração não encontrado!
    exit /b 1
)

:: Ler o arquivo de configuração e atribuir as variáveis
for /f "tokens=1,2 delims==" %%a in (%CONFIG_FILE%) do (
    if "%%a"=="SEBASTIAN-NOTE" set CAMINHO_CASA=%%b
    if "%%a"=="OBRAS-SEBASTIAN" set CAMINHO_SERVICO=%%b
)

:: Detectar o drive e configurar o caminho adequado
echo Detectando o drive do HD externo...

:: Aqui, você pode verificar o nome do computador ou o drive específico
:: Uma forma simples de verificar seria pelo nome do computador (exemplo)
set COMPUTER_NAME=%COMPUTERNAME%

if "%COMPUTER_NAME%"=="SEBASTIAN-NOTE" (
    echo Usando caminho de casa: %CAMINHO_CASA%
    set REPOSITORIO_PATH=%CAMINHO_CASA%
) else (
    echo Usando caminho do serviço: %CAMINHO_SERVICO%
    set REPOSITORIO_PATH=%CAMINHO_SERVICO%
)

:: Fazer algo com o repositório, por exemplo, executar um comando Git:
:: git config --global safe.directory F:/Desenvolvimento/wwwroot/Convenios
cd %REPOSITORIO_PATH%
git config --global safe.directory %REPOSITORIO_PATH%
git config user.name "O-Sebastian"
git config user.email "senhasdoze@hotmail.com"
git config remote.origin.url https://github.com/O-Sebastian/Concursos.git
git switch dev

:: Exibir o caminho final
echo O caminho do repositório é: %REPOSITORIO_PATH%
echo O nome de usuário configurado:
git config user.name
echo O e-mail configurado:
git config user.email
echo O link do GitHub:
git config remote.origin.url
echo E o branch ativo:
git branch
echo Status atual:
:: git push -u origin dev
git status
pause