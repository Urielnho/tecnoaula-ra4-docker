$Host.UI.RawUI.WindowTitle = 'RA4 08_usuario_despues'
Set-Location -LiteralPath 'C:\Users\uriel\Desktop\IDGS9-1\Desarrollo Web Integral\P3\Unidad 4 - Resultado de Aprendizaje Proyecto Orquestado con Docker'
function prompt { 'PS> ' }
Clear-Host
Write-Host 'PS> docker compose exec -T backend python verificar_persistencia.py persistencia.ra4@tecnoaula.local' -ForegroundColor Cyan
docker compose exec -T backend python verificar_persistencia.py persistencia.ra4@tecnoaula.local
if ($LASTEXITCODE -ne 0) { throw 'Fallo el comando' }
Write-Host 'PS> docker ps' -ForegroundColor Cyan
docker ps
if ($LASTEXITCODE -ne 0) { throw 'Fallo el comando' }
Set-Content -LiteralPath 'C:\Users\uriel\Desktop\IDGS9-1\Desarrollo Web Integral\P3\Unidad 4 - Resultado de Aprendizaje Proyecto Orquestado con Docker\tmp\08_usuario_despues.ok' -Value 'correcto'
