targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'

// Monitor application with Azure Monitor
module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    logAnalyticsName: '${prefix}-logworkspace'
    applicationInsightsName: '${prefix}-appinsights'
    applicationInsightsDashboardName: '${prefix}-dashboard'
  }
}

// Backing storage for Azure functions backend API
var validStoragePrefix = toLower(take(replace(prefix, '-', ''), 17))
module storageAccount 'core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: resourceGroup
  params: {
    name: '${validStoragePrefix}storage'
    location: location
    tags: tags
  }
}


// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan './core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: resourceGroup
  params: {
    name: '${prefix}-plan'
    location: location
    tags: tags
    sku: {
      name: 'Y1'
      tier: 'Dynamic'
    }
  }
}

module functionApp 'core/host/functions.bicep' = {
  name: 'function'
  scope: resourceGroup
  params: {
    name: '${prefix}-function-app'
    location: location
    tags: union(tags, { 'azd-service-name': 'api' })
    alwaysOn: false
    appSettings: {
      PYTHON_ISOLATE_WORKER_DEPENDENCIES: 1
    }
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.9'
    storageAccountName: storageAccount.outputs.name
  }
}

// CDN in front
module cdnProfile 'cdn-profile.bicep' = {
  name: 'cdn-profile'
  scope: resourceGroup
  params: {
    name: '${prefix}-cdn-profile'
    location: location
    tags: tags
  }
}

module cdnEndpoint 'cdn-endpoint.bicep' = {
  name: 'cdn-endpoint'
  scope: resourceGroup
  params: {
    name: '${prefix}-cdn-endpoint'
    location: location
    tags: tags
    cdnProfileName: '${prefix}-cdn-profile'
    functionAppName: functionApp.outputs.name
    originUrl: last(split(functionApp.outputs.uri, '//'))
  }
}

output SERVICE_API_ENDPOINTS array = [functionApp.outputs.uri, cdnEndpoint.outputs.uri]
