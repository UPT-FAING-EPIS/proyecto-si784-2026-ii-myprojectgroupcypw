# Pruebas de la infraestructura con proveedores simulados: no requieren
# credenciales de Azure ni crean recursos. Ejecutar: terraform test

mock_provider "azurerm" {
  # El proveedor valida el formato de los ID de Azure incluso con mocks.
  mock_resource "azurerm_service_plan" {
    defaults = {
      id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-prueba/providers/Microsoft.Web/serverFarms/asp-prueba"
    }
  }
}
mock_provider "random" {}

run "configuracion_por_defecto" {
  command = apply

  assert {
    condition     = azurerm_service_plan.principal.os_type == "Linux" && azurerm_service_plan.principal.sku_name == "B1"
    error_message = "El plan debe ser Linux B1 por defecto."
  }

  assert {
    condition     = azurerm_linux_web_app.backend.https_only && azurerm_linux_web_app.frontend.https_only
    error_message = "Ambas Web Apps deben exigir HTTPS."
  }

  assert {
    condition     = azurerm_linux_web_app.backend.site_config[0].ftps_state == "Disabled" && azurerm_linux_web_app.frontend.site_config[0].ftps_state == "Disabled"
    error_message = "FTP debe estar deshabilitado."
  }

  assert {
    condition     = azurerm_linux_web_app.backend.site_config[0].health_check_path == "/salud"
    error_message = "El backend debe usar el healthcheck /salud."
  }

  assert {
    condition     = azurerm_linux_web_app.backend.app_settings["WEBSITES_PORT"] == "8000" && azurerm_linux_web_app.frontend.app_settings["WEBSITES_PORT"] == "5500"
    error_message = "Los puertos deben coincidir con los Dockerfile (8000 y 5500)."
  }

  assert {
    condition     = azurerm_linux_web_app.backend.app_settings["NOTARYVERIFY_DATA_DIR"] == "/home/data"
    error_message = "Los datos runtime deben ir al almacenamiento persistente /home."
  }

  assert {
    condition     = !strcontains(azurerm_linux_web_app.backend.app_settings["NOTARYVERIFY_CORS_ORIGINS"], "*")
    error_message = "CORS no debe usar comodines."
  }

  assert {
    condition     = azurerm_linux_web_app.backend.app_settings["NOTARYVERIFY_CORS_ORIGINS"] == output.url_frontend
    error_message = "CORS del backend debe permitir exactamente la URL del frontend."
  }

  assert {
    condition     = !contains(keys(azurerm_linux_web_app.backend.app_settings), "NOTARYVERIFY_BOOTSTRAP_ADMIN_EMAIL")
    error_message = "Sin usuarios_demo no se crean usuarios en el backend."
  }

  assert {
    condition     = azurerm_resource_group.principal.tags["proyecto"] == "NotaryVerify"
    error_message = "Los recursos deben llevar las etiquetas del proyecto."
  }
}

run "plan_gratuito_sin_always_on" {
  command = apply

  variables {
    sku_plan = "F1"
  }

  assert {
    condition     = azurerm_linux_web_app.backend.site_config[0].always_on == false
    error_message = "El plan F1 no admite always_on."
  }
}

run "usuarios_demo_opcionales" {
  command = apply

  variables {
    usuarios_demo = {
      admin_correo   = "admin@example.test"
      admin_password = "clave-de-prueba"
    }
  }

  assert {
    condition     = nonsensitive(azurerm_linux_web_app.backend.app_settings["NOTARYVERIFY_BOOTSTRAP_ADMIN_EMAIL"]) == "admin@example.test"
    error_message = "Los usuarios ficticios configurados deben llegar al backend."
  }

  assert {
    condition     = !contains(keys(azurerm_linux_web_app.backend.app_settings), "NOTARYVERIFY_BOOTSTRAP_OPERATOR_EMAIL")
    error_message = "No deben enviarse variables de bootstrap vacías."
  }
}

run "rechaza_sku_no_permitido" {
  command = plan

  variables {
    sku_plan = "P3v3"
  }

  expect_failures = [var.sku_plan]
}

run "rechaza_prefijo_invalido" {
  command = plan

  variables {
    prefijo = "Notary_Verify"
  }

  expect_failures = [var.prefijo]
}
