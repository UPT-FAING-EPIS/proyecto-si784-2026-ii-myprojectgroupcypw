terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

# La suscripción y las credenciales se leen del entorno (ARM_SUBSCRIPTION_ID,
# ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_TENANT_ID); nunca se versionan.
provider "azurerm" {
  features {}
}
