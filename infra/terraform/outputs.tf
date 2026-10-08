output "grupo_recursos" {
  description = "Nombre del Resource Group."
  value       = azurerm_resource_group.principal.name
}

output "webapp_backend" {
  description = "Nombre de la Web App del backend."
  value       = azurerm_linux_web_app.backend.name
}

output "webapp_frontend" {
  description = "Nombre de la Web App del frontend."
  value       = azurerm_linux_web_app.frontend.name
}

output "url_backend" {
  description = "URL pública de la API."
  value       = local.url_backend
}

output "url_frontend" {
  description = "URL pública de la estación de verificación."
  value       = local.url_frontend
}
