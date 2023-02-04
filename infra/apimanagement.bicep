param location string
param tags object
param prefix string
param functionAppName string
param functionAppUrl string
param functionAppId string
@secure()
param functionAppKey string
param appInsightsName string
param appInsightsId string
param appInsightsKey string
param publisherEmail string
param publisherName string
param allowedOrigin string

resource apimService 'Microsoft.ApiManagement/service@2021-12-01-preview' = {
  name: '${prefix}-function-app-apim'
  location: location
  tags: tags
  sku: {
    name: 'Consumption'
    capacity: 0
  }
  properties: {
    publisherEmail: publisherEmail
    publisherName: publisherName
  }
}


resource apimNamedValuesKey 'Microsoft.ApiManagement/service/namedValues@2021-12-01-preview' = {
  parent: apimService
  name: 'function-app-key'
  properties: {
    displayName: 'function-app-key'
    value: functionAppKey
    tags: [
      'key'
      'function'
      'auto'
    ]
    secret: true
  }
}

resource apimBackend 'Microsoft.ApiManagement/service/backends@2021-12-01-preview' = {
  parent: apimService
  name: functionAppName
  properties: {
    description: functionAppName
    url: 'https://${functionAppUrl}/api'
    protocol: 'http'
    resourceId: '${environment().resourceManager}${functionAppId}'
    credentials: {
      header: {
        'x-functions-key': [
          '{{function-app-key}}'
        ]
      }
    }
  }
  dependsOn: [
    apimNamedValuesKey
  ]
}


resource apimAPI 'Microsoft.ApiManagement/service/apis@2021-12-01-preview' = {
  parent: apimService
  name: 'icon-writer-function'
  properties: {
    displayName: 'icon-writer-function'
    apiRevision: '1'
    subscriptionRequired: true
    protocols: [
      'https'
    ]
    path: 'icon-writer-function'
  }
}

resource apimAPIGet 'Microsoft.ApiManagement/service/apis/operations@2021-12-01-preview' = {
  parent: apimAPI
  name: 'icon-writer-api-get'
  properties: {
    displayName: 'IconWriter'
    method: 'GET'
    urlTemplate: '/IconWriter'
    request: {
      queryParameters: [
        {
          name: 'text'
          description: 'Text to display on icon.'
          type: 'string'
          required: true
        }
        {
          name: 'size'
          description: 'Size of icon (in pixels). Icons are always square.'
          type: 'integer'
          required: false
        }
        {
          name: 'bgcolor'
          description: 'Background color of icon, specified in hexadecimal notation.'
          type: 'string'
          required: false
        }
        {
          name: 'fontcolor'
          description: 'Color of text in icon, specified in hexadecimal notation.'
          type: 'string'
          required: false
        }
      ]
    }
  }
}


resource apimAPIGetPolicy 'Microsoft.ApiManagement/service/apis/operations/policies@2021-12-01-preview' = {
  parent: apimAPIGet
  name: 'policy'
  properties: {
    format: 'xml'
    value: '<policies>\r\n<inbound>\r\n<base />\r\n<set-backend-service id="apim-generated-policy" backend-id="${functionAppName}" />\r\n<cors allow-credentials="false">\r\n<allowed-origins>\r\n<origin>${allowedOrigin}</origin>\r\n</allowed-origins>\r\n<allowed-methods>\r\n<method>GET</method>\r\n</allowed-methods>\r\n</cors>\r\n<validate-parameters specified-parameter-action="prevent" unspecified-parameter-action="ignore" errors-variable-name="validationErrors" />\r\n</inbound>\r\n<backend>\r\n<base />\r\n</backend>\r\n<outbound>\r\n<base />\r\n</outbound>\r\n<on-error>\r\n<base />\r\n</on-error>\r\n</policies>'
  }
  dependsOn: [
    apimBackend
  ]
}


/* Logging*/

resource namedValueAppInsightsKey 'Microsoft.ApiManagement/service/namedValues@2021-01-01-preview' = {
  parent: apimService
  name: 'logger-credentials'
  properties: {
    displayName: 'logger-credentials'
    value: appInsightsKey
    secret: true
  }
}

resource apimLogger 'Microsoft.ApiManagement/service/loggers@2021-12-01-preview' = {
  parent: apimService
  name: appInsightsName
  properties: {
    loggerType: 'applicationInsights'
    credentials: {
      instrumentationKey: '{{logger-credentials}}'
    }
    isBuffered: true
    resourceId: appInsightsId
  }
  dependsOn: [
    namedValueAppInsightsKey
  ]
}

resource apimAPIDiagnostics 'Microsoft.ApiManagement/service/apis/diagnostics@2021-12-01-preview' = {
  parent: apimAPI
  name: 'applicationinsights'
  properties: {
    alwaysLog: 'allErrors'
    loggerId: apimLogger.id
  }
}

output apimServiceID string = apimService.id
