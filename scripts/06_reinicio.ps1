$Host.UI.RawUI.WindowTitle = 'RA4 06_reinicio'
Set-Location -LiteralPath 'C:\Users\uriel\Desktop\IDGS9-1\Desarrollo Web Integral\P3\Unidad 4 - Resultado de Aprendizaje Proyecto Orquestado con Docker'
function prompt { 'PS> ' }
Clear-Host
Write-Host 'PS> docker compose down' -ForegroundColor Cyan
docker compose down
if ($LASTEXITCODE -ne 0) { throw 'Fallo el comando' }
Write-Host 'PS> docker compose up -d --wait' -ForegroundColor Cyan
docker compose up -d --wait
if ($LASTEXITCODE -ne 0) { throw 'Fallo el comando' }
Set-Content -LiteralPath 'C:\Users\uriel\Desktop\IDGS9-1\Desarrollo Web Integral\P3\Unidad 4 - Resultado de Aprendizaje Proyecto Orquestado con Docker\tmp\06_reinicio.ok' -Value 'correcto'
