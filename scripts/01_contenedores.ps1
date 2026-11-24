$Host.UI.RawUI.WindowTitle = 'RA4 01_contenedores'
Set-Location -LiteralPath 'C:\Users\uriel\Desktop\IDGS9-1\Desarrollo Web Integral\P3\Unidad 4 - Resultado de Aprendizaje Proyecto Orquestado con Docker'
function prompt { 'PS> ' }
Clear-Host
Write-Host 'PS> docker ps' -ForegroundColor Cyan
docker ps
if ($LASTEXITCODE -ne 0) { throw 'Fallo el comando' }
Set-Content -LiteralPath 'C:\Users\uriel\Desktop\IDGS9-1\Desarrollo Web Integral\P3\Unidad 4 - Resultado de Aprendizaje Proyecto Orquestado con Docker\tmp\01_contenedores.ok' -Value 'correcto'
