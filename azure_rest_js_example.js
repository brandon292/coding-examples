updateCustomInfo : function (customInfo, azProperties) {
    var NAME = MOOBOT_NAME + "updateCustomInfo -- ";
    aeLogger.debug/*TODO trace? */(NAME + "Updating alert custom info using " + JSON.stringify(azProperties));
    if(botModules.botUtil.isObjectDefined(customInfo, 'eventDetails.data.alertContext.properties.aa-component-id')) { // component ID is at the alert group level
        // if we don't have componentId setup, initialize with an empty array
        if(!Array.isArray(customInfo.eventDetails.componentId)) {
            if (customInfo.eventDetails.componentId && customInfo.eventDetails.componentId != "") {
                customInfo.eventDetails.componentId = [customInfo.eventDetails.componentId]; // place a single value into an array
            } else {
                customInfo.eventDetails.componentId = []; // otherwise initialize with a new array
            }
        }
        
        aeLogger.debug/*TODO trace*/(NAME + " Adding Component ID from Azure tag at alert group level " + customInfo.eventDetails.data.alertContext.properties['aa-component-id']);
        customInfo.eventDetails.componentId.push(customInfo.eventDetails.data.alertContext.properties['aa-component-id']);
        }
    else if(botModules.botUtil.isObjectDefined(azProperties, 'tags.aa-component-id')) { // we have a Component ID at resource level
        // if we don't have componentId setup, initialize with an empty array
        if(!Array.isArray(customInfo.eventDetails.componentId)) {
            if (customInfo.eventDetails.componentId && customInfo.eventDetails.componentId != "") {
                customInfo.eventDetails.componentId = [customInfo.eventDetails.componentId]; // place a single value into an array
            } else {
                customInfo.eventDetails.componentId = []; // otherwise initialize with a new array
            }
        }
        
        aeLogger.debug/*TODO trace*/(NAME + " Adding Component ID from Azure tag at resource level " + azProperties.tags['aa-component-id']);
        customInfo.eventDetails.componentId.push(azProperties.tags['aa-component-id']);
        }
    //    aeLogger.debug/*TODO trace*/(NAME + "Made it past component ID");
    else if(botModules.botUtil.isObjectDefined(customInfo, 'eventDetails.data.alertContext.properties.aa-app-shortname')) { // we have an shortname at action group level
        aaEnrichArcher.setShortname(customInfo.eventDetails.data.alertContext.properties['aa-app-shortname'], customInfo);
        aeLogger.debug/*TODO trace*/(NAME + " Adding shortname from Azure tag at action group level " + customInfo.eventDetails.data.alertContext.properties['aa-app-shortname']);
        }
    else if(botModules.botUtil.isObjectDefined(azProperties, 'tags.aa-app-shortname')) { // we have an shortname at resource level
        aeLogger.debug/*TODO trace*/(NAME + " Adding shortname from Azure tag at resource level " + azProperties.tags['aa-app-shortname']);
        aaEnrichArcher.setShortname(azProperties.tags['aa-app-shortname'], customInfo);
        }
    else if(botModules.botUtil.isObjectDefined(customInfo, 'eventDetails.data.alertContext.properties.aa-app-id')) { // we have an Archer ID at the action group level
        aeLogger.debug/*TODO trace*/(NAME + " Adding Archer ID from Azure tag at action group level " + customInfo.eventDetails.data.alertContext.properties['aa-app-id']);
        aaEnrichArcher.setArcherId(customInfo.eventDetails.data.alertContext.properties['aa-app-id'], customInfo);
        }
    else if(botModules.botUtil.isObjectDefined(azProperties, 'tags.aa-app-id')) { // we have an Archer ID at the resource level
        aeLogger.debug/*TODO trace*/(NAME + " Adding Archer ID from Azure tag at resource level " + azProperties.tags['aa-app-id']);
        aaEnrichArcher.setArcherId(azProperties.tags['aa-app-id'], customInfo);
        }
    //    aeLogger.debug/*TODO trace*/(NAME + "Made it past archer ID/shortname");
    customInfo = aaUtils.populateCustomInfo(null, customInfo); // refresh dependant properties, if we set/changed anything
    // TODO: Do we want to enrich with more than tags (eg location)?
    if (!customInfo.enrichment) {
        customInfo.enrichment = {}
    }
    azPropertiesString = JSON.stringify(azProperties);
    if (azPropertiesString.length > 16347) {
        aeLogger.debug/*TODO trace*/(NAME + "Dropping excessivly long details from Azure event.");
        customInfo.enrichment.azure = "Azure properties is TLDR. Archer ID extracted.";
    } else {
        customInfo.enrichment.azure = azProperties; // this is safe, since until now azureEnrichment shouldn't have been set
    }
    // Lastly, leave evidence that we touched each alert
    customInfo.moogHandling.enrichedByAzure = true; // we have successfully enriched this alert ;)
    customInfo.moogHandling.azureEnrichment.evidence = "Enriched by the Azure Enricher module v1.3"; // TODO: Link this to GHE SHA?
    // not used: return true;
},

/**
 * Login to Azure and store the token (with expiry) into shared constants
 */
azureLogin: function () {
    var NAME = MOOBOT_NAME + "azureLogin -- ";
    var threshold = new Date().getTime() - 15;
    if (!constants.contains("azure_login_expires") || constants.get("azure_login_expires") < threshold) {
        // we either haven't logged in yet, or the token has expired - either way, time to login again.
        aeLogger.debug(NAME + "going to get a new token from Azure. The token we had expired (" + constants.get("azure_login_expires") + " vs. " + threshold + ").");
        var result = rest.sendPost({
            url: 'xxxxxxxxxxxxxxxx',
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: 'grant_type=client_credentials&client_id=' + azureClientId + '&client_secret=' + azureClientSecret + '&resource=https://management.azure.com/'
        });
        aeLogger.trace(NAME + "Response from Azure login attempt:" + JSON.stringify(result));
        if (result.status_code != 200) {
            var warning = NAME + "Unexpected response from login attempt: " + result.status_code + "\n" + JSON.stringify(result);
            aeLogger.warning(warning);
            throw warning; // nothing else we can do.
        }
        var response = JSON.parse(result.response);
        if (response.error) {
            var warning = NAME + "Error response from login attempt: " + response.error + "\n" + JSON.stringify(result);
            aeLogger.warning(warning);
            throw warning; // nothing else we can do.
        }
        constants.put("azure_login_expires", response.expires_on);
        aeLogger.debug/*TODO trace*/(NAME + "New access token expires " + response.expires_on);
        aeLogger.debug/*TODO trace or remove*/(NAME + "Constants azure_login_expires:" + constants.get("azure_login_expires"));
        constants.put("azure_login_token", response.access_token);
        aeLogger.debug/*TODO trace*/(NAME + "New access token " + response.access_token);
    }
},