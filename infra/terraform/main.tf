# Infraestructura de demostración de NotaryVerify en Azure App Service:
# un plan Linux con dos Web Apps de contenedor (backend FastAPI y frontend
# estático). Solo identidades ficticias; sin servicios institucionales.

resource "random_string" "sufijo" {
  length  = 5
  upper   = false
  special = false
}

locals {
  nombre          = "${var.prefijo}-${random_string.sufijo.result}"
  nombre_backend  = "${local.nombre}-api"
  nombre_frontend = "${local.nombre}-web"
  url_backend     = "https://${local.nombre_backend}.azurewebsites.net"
  url_frontend    = "https://${local.nombre_frontend}.azurewebsites.net"
  siempre_activo  = var.sku_plan != "F1"

  # Solo se envían las variables de bootstrap con valor (el backend exige parejas completas).
  usuarios_demo = {
    for clave, valor in {
      NOTARYVERIFY_BOOTSTRAP_OPERATOR_EMAIL    = var.usuarios_demo.operador_correo
      NOTARYVERIFY_BOOTSTRAP_OPERATOR_PASSWORD = var.usuarios_demo.operador_password
      NOTARYVERIFY_BOOTSTRAP_ADMIN_EMAIL       = var.usuarios_demo.admin_correo
      NOTARYVERIFY_BOOTSTRAP_ADMIN_PASSWORD    = var.usuarios_demo.admin_password
    } : clave => valor if valor != ""
  }
}

resource "azurerm_resource_group" "principal" {
  name     = "rg-${local.nombre}"
  location = var.ubicacion
  tags     = var.etiquetas
}

resource "azurerm_service_plan" "principal" {
  name                = "asp-${local.nombre}"
  resource_group_name = azurerm_resource_group.principal.name
  location            = azurerm_resource_group.principal.location
  os_type             = "Linux"
  sku_name            = var.sku_plan
  tags                = var.etiquetas
}

resource "azurerm_linux_web_app" "backend" {
  name                = local.nombre_backend
  resource_group_name = azurerm_resource_group.principal.name
  location            = azurerm_resource_group.principal.location
  service_plan_id     = azurerm_service_plan.principal.id
  https_only          = true
  tags                = var.etiquetas

  site_config {
    always_on                         = local.siempre_activo
    ftps_state                        = "Disabled"
    minimum_tls_version               = "1.2"
    health_check_path                 = "/salud"
    health_check_eviction_time_in_min = 10

    application_stack {
      docker_image_name   = var.imagen_backend
      docker_registry_url = var.registro_url
    }
  }

  app_settings = merge({
    WEBSITES_PORT                       = "8000"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "true"
    NOTARYVERIFY_DATA_DIR               = "/home/data"
    NOTARYVERIFY_CORS_ORIGINS           = local.url_frontend
  }, local.usuarios_demo)
}

resource "azurerm_linux_web_app" "frontend" {
  name                = local.nombre_frontend
  resource_group_name = azurerm_resource_group.principal.name
  location            = azurerm_resource_group.principal.location
  service_plan_id     = azurerm_service_plan.principal.id
  https_only          = true
  tags                = var.etiquetas

  site_config {
    always_on           = local.siempre_activo
    ftps_state          = "Disabled"
    minimum_tls_version = "1.2"

    application_stack {
      docker_image_name   = var.imagen_frontend
      docker_registry_url = var.registro_url
    }
  }

  app_settings = {
    WEBSITES_PORT                       = "5500"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
  }
}
