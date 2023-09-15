import requests


class Client:
    def __init__(self, baseUrl: str, username: str = '', password: str = '', apiToken: str = ''):
        """Provide either a username and password, or an API token to access the dcTrack database with Python."""
        self.__BASE_URL = baseUrl
        self.__USERNAME = username
        self.__PASSWORD = password
        self.__APITOKEN = apiToken

    def generateToken(self) -> str:
        """Generate and return an API token."""
        if self.__USERNAME and self.__PASSWORD and not self.__APITOKEN:
            return requests.request('POST', self.__BASE_URL + '/api/v2/authentication/login', auth=(self.__USERNAME, self.__PASSWORD)).headers['Authorization'].split()[1]
        else:
            raise Exception('Username/password undefined or token predefined.')

    def __request(self, method: str, endpoint: str, body: dict = None):
        if not self.__APITOKEN:
            self.__APITOKEN = self.generateToken()
        return requests.request(method, self.__BASE_URL + '/' + endpoint, json=body, headers={'Authorization': 'Bearer ' + self.__APITOKEN}).json()

    def getItem(self, id: int):
        """Get item details using the item ID."""
        return self.__request('GET', '/api/v2/dcimoperations/items/' + str(id) + '/?')

    def createItem(self, returnDetails: bool, payload: dict):
        """Create a new item. When returnDetails is set to true, the API call will return the full json payload. If set to false, the call returns only the "id" and "tiName"."""
        return self.__request('POST', '/api/v2/dcimoperations/items/?returnDetails=' + str(returnDetails) + '&', payload)

    def updateItem(self, id: int, returnDetails: bool, payload: dict):
        """Update an existing item. When returnDetails is set to true, the API call will return the full json payload. If set to false, the call returns only the "id" and "tiName"."""
        return self.__request('PUT', '/api/v2/dcimoperations/items/' + str(id) + '/?returnDetails=' + str(returnDetails) + '&', payload)

    def deleteItem(self, id: int):
        """Delete an item using the item ID."""
        return self.__request('DELETE', '/api/v2/dcimoperations/items/' + str(id) + '/?')

    def searchItems(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for items using criteria JSON object. Search criteria can be any of the fields applicable to items, including custom fields. Specify the fields to be included in the response. This API supports pagination. Returns a list of items with the specified information."""
        return self.__request('POST', '/api/v2/quicksearch/items/?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def getCabinetItems(self, CabinetId: int):
        """Returns a list of Items contained in a Cabinet using the ItemID of the Cabinet. The returned list includes all of the Cabinet's Items including Passive Items."""
        return self.__request('GET', '/api/v2/items/cabinetItems/' + str(CabinetId) + '/?')

    def createItemsBulk(self, payload: dict):
        """Add/Update/Delete Items."""
        return self.__request('POST', '/api/v2/dcimoperations/items/bulk/?', payload)

    def getMakes(self):
        """Returns a list of makes with basic information."""
        return self.__request('GET', '/api/v2/makes/?')

    def createMake(self, payload: dict):
        """Add a new Make. Returns JSON entity containing Make information that was passed in from the Request payload."""
        return self.__request('POST', '/api/v2/makes/?', payload)

    def updateMake(self, makeId: int, payload: dict):
        """Modify a Make. Returns JSON entity containing Make information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/makes/' + str(makeId) + '/?', payload)

    def deleteMake(self, makeId: int):
        """Delete a Make."""
        return self.__request('DELETE', '/api/v2/makes/' + str(makeId) + '/?')

    def searchMakes(self, makeName: str, payload: dict):
        """Search for a make using the make name. Returns a list of makes with basic information."""
        return self.__request('POST', '/api/v2/dcimoperations/search/makes/' + str(makeName) + '/?', payload)

    def getModel(self, modelId: int, usedCounts: int):
        """Get Model fields for the specified Model ID. usedCounts is an optional parameter that determines if the count of Items for the specified model is returned in the response. If set to "true" the counts will be included in the response, if omitted or set to "false" the item count will not be included in the response."""
        return self.__request('GET', '/api/v2/models/' + str(modelId) + '/?usedCounts=' + str(usedCounts) + '&')

    def createModel(self, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Add a new Model. Returns JSON entity containing Make information that was passed in from the Request payload. "proceedOnWarning" relates to the warning messages that are thrown in dcTrack when you try to delete custom fields that are in use. The "proceedOnWarning" value can equal either "true" or "false." If "proceedOnWarning" equals "true," business warnings will be ignored. If "proceedOnWarning" equals "false," business warnings will not be ignored. Fields that are not in the payload will remain unchanged."""
        return self.__request('POST', '/api/v2/models/?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def updateModel(self, id: int, returnDetails: bool, proceedOnWarning: bool, payload: dict):
        """Modify an existing Model. Fields that are not in the payload will remain unchanged. Returns a JSON entity containing Make information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/models/' + str(id) + '/?returnDetails=' + str(returnDetails) + '&proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def deleteModel(self, id: int):
        """Delete a Model using the Model ID."""
        return self.__request('DELETE', '/api/v2/models/' + str(id) + '/?')

    def searchModels(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for models by user supplied search criteria. Returns a list of models with the "selectedColumns" returned in the payload. Search by Alias is not supported."""
        return self.__request('POST', '/api/v2/quicksearch/models/?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def deleteModelImage(self, id: int, orientation: str):
        """Delete a Mode Image using the Model ID and the Image Orientation, where id is the Model Id and orientation is either front or back"""
        return self.__request('DELETE', '/api/v2/models/images/' + str(id) + '/' + str(orientation) + '/?')

    def getConnector(self, connectorId: int, usedCount: bool):
        """Get a Connector record by ID. Returns a Connector with all information including Compatible Connectors. The usedCount parameter is optional. If usedCount is true, the response will include the number of times the connector is in use by Models and Items. If false, no counts are returned. If omitted the default is false."""
        return self.__request('GET', '/api/v2/settings/connectors/' + str(connectorId) + '/?usedCount=' + str(usedCount) + '&')

    def createConnector(self, payload: dict):
        """Add a new Connector. Returns JSON entity containing Connector information that was passed in from the Request payload."""
        return self.__request('POST', '/api/v2/settings/connectors/?', payload)

    def updateConnector(self, connectorId: int, payload: dict):
        """Update an existing Connector. Returns JSON entity containing Connector information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v2/settings/connectors/' + str(connectorId) + '/?', payload)

    def removeConnector(self, payload: dict):
        """Delete one or more Connector records."""
        return self.__request('POST', '/api/v2/settings/connectors/delete/?', payload)

    def searchConnectors(self, pageNumber: int, pageSize: int, usedCount: bool, payload: dict):
        """Retrieve a List of Connectors. Returns JSON entity containing Connector information that was passed in from the Request payload. Please note, Compatible Connectors are not returned by this API, but can be returned when querying a single Connector using the /api/v2/settings/connectors/{connectorId} API."""
        return self.__request('POST', '/api/v2/settings/connectors/quicksearch/?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&usedCount=' + str(usedCount) + '&', payload)

    def deleteConnectorImage(self, connectorId: int):
        """Delete a Connector Image using the Connector ID."""
        return self.__request('DELETE', '/api/v2/settings/connectors/' + str(connectorId) + '/images/?')

    def getDataPorts(self, itemId: int):
        """Use the REST API to retrieve details from all data ports on an item. If the operation was successful, a status code 200 is displayed, and the body contains the item's data port details. If the operation failed, an error code is returned."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/dataports/?')

    def getDataPort(self, itemId: int, dataportId: int):
        """Use the REST API to read the details of an item's data port. To do this, specify the item and item data port ID. If the operation was successful, a status code 200 is displayed, and the body contains the item's data port details. If the operation failed, an error code is returned."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/dataports/' + str(dataportId) + '/?')

    def createDataPorts(self, itemId: int, payload: dict):
        """Use the REST API to create data ports for an existing item. If ports are already defined for the item because it is included in the Item Models Library, you can use the REST API to create additional ports for the item. Payload contains data port parameter details in json format. All required fields must be included."""
        return self.__request('POST', '/api/v1/items/' + str(itemId) + '/dataports/?', payload)

    def updateDataPort(self, itemId: int, dataportId: int, payload: dict):
        """Update an item's data port details using the REST API. To do this, specify the item and data port ID, and provide the updated parameter value(s). Payload contains data port parameter details in json format. All required fields must be included."""
        return self.__request('PUT', '/api/v1/items/' + str(itemId) + '/dataports/' + str(dataportId) + '/?', payload)

    def deleteDataPort(self, itemId: int, dataportId: int):
        """Delete an item's data port using the REST API by specifying the item ID and data port ID. If the operation is successful, a status code 200 is displayed. If the operation failed, an error code is returned."""
        return self.__request('DELETE', '/api/v1/items/' + str(itemId) + '/dataports/' + str(dataportId) + '/?')

    def getPowerPorts(self, itemId: int):
        """Use the REST API to retrieve details from all power ports on an item."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/powerports/?')

    def getPowerPort(self, itemId: int, portId: int):
        """Use the REST API to retrieve details from one power port on an item."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/powerports/' + str(portId) + '/?')

    def updatePowerPort(self, itemId: int, portId: int, proceedOnWarning: bool, payload: dict):
        """Use the REST API to create power ports for an existing item. If ports are already defined for the item because it is included in the Item Models Library, you can use the REST API to create additional ports for the item."""
        return self.__request('PUT', '/api/v1/items/' + str(itemId) + '/powerports/' + str(portId) + '/?proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def getCompatibleConnector(self, itemId: int, portId: int, connectorId: int):
        """Use the REST API to determine if a Connector is compatible with a specific Power Port."""
        return self.__request('GET', '/api/v1/items/' + str(itemId) + '/powerports/' + str(portId) + '/connectors/' + str(connectorId) + '/isCompatible/?')

    def getLocations(self):
        """Returns a list for all Locations."""
        return self.__request('GET', '/api/v1/locations/?')

    def getLocation(self, locationId: int):
        """Get a single Location. Returns json containing location data for the specified ID."""
        return self.__request('GET', '/api/v1/locations' + str(locationId) + '/?')

    def createLocation(self, proceedOnWarning: bool, payload: dict):
        """Add a Location. Returns the JSON entity containing location info that was passed in. Note: "proceedOnWarning" relates to the warning messages that are thrown in dcTrack when you try to delete custom fields that are in use. The "proceedOnWarning" value can equal either "true" or "false." If "proceedOnWarning" equals "true," business warnings will be ignored. If "proceedOnWarning" equals "false," business warnings will not be ignored."""
        return self.__request('POST', '/api/v1/locations/?proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def updateLocation(self, locationId: int, proceedOnWarning: bool, payload: dict):
        """Modify Location details for a single Location. Payload contains new location details. You do not have have to provide all details, but only those that you want to modify. Returns JSON entity containing Location information that was passed in from the Request payload."""
        return self.__request('PUT', '/api/v1/locations/' + str(locationId) + '/?proceedOnWarning=' + str(proceedOnWarning) + '&', payload)

    def deleteLocation(self, locationId: int):
        """Delete a Location."""
        return self.__request('DELETE', '/api/v1/locations/' + str(locationId) + '/?')

    def searchLocations(self, pageNumber: int, pageSize: int, payload: dict):
        """Search for Locations by user supplied search criteria. Returns a list of Locations with the "selectedColumns" returned in the payload."""
        return self.__request('POST', '/api/v2/quicksearch/locations/?pageNumber=' + str(pageNumber) + '&pageSize=' + str(pageSize) + '&', payload)

    def getLocationFieldList(self):
        """Returns a list of all Location fields."""
        return self.__request('GET', '/api/v2/quicksearch/locations/locationListFields/?')

    def getSublocationTree(self):
        """Get the sublocation tree."""
        return self.__request('GET', '/api/v2/subLocations/tree/?')

    def getSublocations(self, locationId: int):
        """Get all sub-locations for a given location in the hierarchy. The locationId is the ID of the location to get the sub-locations for."""
        return self.__request('GET', '/api/v2/subLocations/list/' + str(locationId) + '/?')

    def getSublocationsOfType(self, locationId: int, typeCode: str):
        """Get all sub-locations of given type for a given location in the hierarchy. The locationId is the id of the location you are querying the sub-location types for. The type is one of either 5016 and 5017 for rows and aisles respectively."""
        return self.__request('GET', '/api/v2/subLocations/' + str(locationId) + '/type/' + str(typeCode) + '/?')

    def getChildSublocations(self, subLocationId: int):
        """Get all child sub-locations for a given sub-location in the hierarchy. The locationId is the ID of the location to fetch the sub-locations for. The subLocationId is the ID of the parent sub-location that you are querying the children of."""
        return self.__request('GET', '/api/v2/subLocations/' + str(subLocationId) + '/children/?')

    def getSublocation(self, subLocationId: int):
        """Get details for a given sub-location. The subLocationId is the id of the sub-location you are querying for."""
        return self.__request('GET', '/api/v2/subLocations/' + str(subLocationId) + '/?')

    def createSublocation(self, payload: dict):
        """Add a new sub-location to the given location. Returns a list from the Sub-Location Hash."""
        return self.__request('POST', '/api/v2/subLocations/?', payload)

    def updateSublocation(self, subLocationId: int, payload: dict):
        """Update a sub-location. Returns a list from the Sub-Location Hash."""
        return self.__request('PUT', '/api/v2/subLocations/' + str(subLocationId) + '/?', payload)

    def deleteSublocation(self, subLocationId: int):
        """Deletes the given sub-location. The locationId is the ID of the location that the sub-location belongs to and the subLocationId is the ID of the location you are querying. Returns a success message upon success."""
        return self.__request('DELETE', '/api/v2/subLocations/' + str(subLocationId) + '/?')

    def getLocationFavorites(self, username: str):
        """Retrieve a List of Location Favorites for a specific User."""
        return self.__request('GET', '/api/v2/users/' + str(username) + '/favorites/LOCATION/?')

    def getLocationFavoritesAllUsers(self):
        """Retrieve a List of Location Favorites for all Users. Returns JSON entity containing Location Favorite information for all users."""
        return self.__request('GET', '/api/v2/users/favorites/LOCATION/?')

    def updateLocationFavorites(self, username: str, payload: dict):
        """Assign Location Favorites to a user where username is a valid dcTrack user and "favorite" is either true or false to indicate whether you are assigning or unassigning. JSON entity containing all Location Favorites for the specified user."""
        return self.__request('PUT', '/api/v2/users/' + str(username) + '/favorites/?', payload)

    def updateLocationFavoritesAllUsers(self, payload: dict):
        """Assign Location Favorites to a user. To Assign favorites the "favorite" column should be set to true. To Unassign favorites the "favorite" column should be set to false. Returns JSON entity containing all Location Favorites for the specified users."""
        return self.__request('PUT', '/api/v2/users/favorites/?', payload)

    def searchCabinetSpace(self, payload: dict):
        """Find Cabinets with available space based on RUs within the specified Locations."""
        return self.__request('POST', '/api/v2/capacity/cabinets/list/search/?', payload)

    def searchAvailableRUs(self, payload: dict):
        """Find the starting RUs within a Cabinet with the specified number of contiguous RUs."""
        return self.__request('POST', '/api/v2/items/uposition/available/?', payload)

    def getPermission(self, permissionId: int):
        """Get explicit permission by ID. Returns JSON entity containing Permission information for the specified Permission Id."""
        return self.__request('GET', '/api/v2/permissions/explicit/' + str(permissionId) + '/?')

    def createPermission(self, payload: dict):
        """Add explicit permission. Returns JSON entity containing Permission information for the added Permission."""
        return self.__request('POST', '/api/v2/permissions/explicit/?', payload)

    def updatePermission(self, permissionId: int, payload: dict):
        """Update explicit permission. Returns JSON entity containing Permission information for the updated Permission."""
        return self.__request('PUT', '/api/v2/permissions/explicit/' + str(permissionId) + '/?', payload)

    def deletePermission(self, permissionId: int):
        """Delete explicit permission."""
        return self.__request('DELETE', '/api/v2/permissions/explicit/' + str(permissionId) + '/?')

    def createPermissionsBulk(self, payload: dict):
        """Add/Update/Delete explicit permissions."""
        return self.__request('POST', '/api/v2/permissions/explicit/bulk/?', payload)

    def getPermissions(self):
        """Get all explicit permissions. Returns JSON entity containing Permission information."""
        return self.__request('GET', '/api/v2/permissions/explicit/?')

    def getPermissionsByEntityType(self, entityType: str):
        """Get explicit permissions by Entity Type. Returns JSON entity containing Permission information."""
        return self.__request('GET', '/api/v2/permissions/explicit/entityType/' + str(entityType) + '/?')

    def getPermissionsByEntityId(self, entityType: str, entityId: int):
        """Get explicit permissions by Entity Type and Entity ID. Returns JSON entity containing Permission information."""
        return self.__request('GET', '/api/v2/permissions/explicit/' + str(entityType) + '/' + str(entityId) + '/?')

    def getRecords(self, listType: str, id: int):
        """Get a list of records (options) for use in drop-down lists by indicating a list type and an ID. ID is optional for some list types. Returns a list of records for a given list type."""
        return self.__request('GET', '/api/v2/dcimoperations/lookups/' + str(listType) + '/' + str(id) + '/?')

    def getPicklistOptions(self, listType: str):
        """Get a list of records (options) for use in drop-down lists for dcTrack standard fields by list type. Returns a list of records for a given list type."""
        return self.__request('GET', '/api/v2/dcimoperations/picklists/' + str(listType) + '/?')

    def updatePicklistOptions(self, listType: str, payload: dict):
        """Update a list of records (options) for use in drop-down lists for dcTrack standard fields by list type. Returns a list of records for a given list type."""
        return self.__request('PUT', '/api/v2/dcimoperations/picklists/' + str(listType) + '/?', payload)

    def submitRequest(self, id: int, payload: dict):
        """Create a request."""
        return self.__request('PUT', '/api/v2/dcimoperations/items/' + str(id) + '/?', payload)

    def deleteRequest(self, requestId: int):
        """Cancel a request. Returns Returns request ID canceled."""
        return self.__request('DELETE', '/api/v2/dcimoperations/requests/' + str(requestId) + '/?')

    def completeRequest(self, requestId: int, payload: dict):
        """Change request status/stage to Complete using the request ID. Optionally, pass a request body with additional information. Returns request status information."""
        return self.__request('PUT', '/api/v2/dcimoperations/requests/complete/' + str(requestId) + '/?', payload)

    def completeWorkOrder(self, workOrderId: int, payload: dict):
        """Complete work order and change work order status/stage to Complete. Optionally, pass a request body with additional information. Returns work order status information."""
        return self.__request('PUT', '/api/v2/dcimoperations/workorders/complete/' + str(workOrderId) + '/?', payload)

    def getRequestStatusByItem(self, itemId: int):
        """Get a list of pending request status information for a given item ID. Returns list of request status."""
        return self.__request('GET', '/api/v2/dcimoperations/requests/pending/' + str(itemId) + '/?')

    def getRequest(self, requestId: int):
        """Get request status information for a given request ID. Returns full request status information."""
        return self.__request('GET', '/api/v2/dcimoperations/requests/status/' + str(requestId) + '/?')

    def searchRequests(self, payload: dict):
        """Get request status information for a given request ID. Returns full request status information."""
        return self.__request('POST', '/api/v2/dcimoperations/search/list/requests/?', payload)

    def createDataConnection(self, payload: dict):
        """Create a data connection. Returns the newly created data connection."""
        return self.__request('POST', '/api/v2/connections/dataconnections/?', payload)

    def updateDataConnection(self, connectionId: int, payload: dict):
        """Edit a data connection. Returns the newly edited data connection."""
        return self.__request('PUT', '/api/v2/connections/dataconnections/' + str(connectionId) + '/?', payload)

    def getDataConnection(self, connectionId: int):
        """Get a data connection and associated details. Requires the ID of the connection you want to retrieve. Returns the requested data connection and associated details."""
        return self.__request('GET', '/api/v2/connections/dataconnections/' + str(connectionId) + '/?')

    def getDataConnectionByNode(self, location: str, itemName: str, portName: str):
        """Get data connection details based on the specified location, item name, and port name. The itemName specified in the URL must be either the starting or ending Item in the connection. This API does not support Data Panel Ports. Returns the JSON payload with the requested data connection details."""
        return self.__request('GET', '/api/v2/connections/dataconnections/?location=' + str(location) + '&itemName=' + str(itemName) + '&portName=' + str(portName) + '&')

    def deleteDataConnection(self, connectionId: int):
        """Deletes the specified data connection."""
        return self.__request('DELETE', '/api/v2/connections/dataconnections/' + str(connectionId) + '/?')

    def createPowerConnection(self, payload: dict):
        """Create a power connection. Returns the newly created power connection."""
        return self.__request('POST', '/api/v2/connections/powerconnections/?', payload)

    def updatePowerConnection(self, connectionId: int, payload: dict):
        """Edit a power connection. Returns the newly edited power connection."""
        return self.__request('PUT', '/api/v2/connections/powerconnections/' + str(connectionId) + '/?', payload)

    def getPowerConnection(self, connectionId: int):
        """Get a power connection and associated details. Requires the ID of the connection you want to retrieve. Returns the requested power connection and associated details."""
        return self.__request('GET', '/api/v2/connections/powerconnections/' + str(connectionId) + '/?')

    def getPowerConnectionByNode(self, location: str, itemName: str, portName: str):
        """Get power connection details based on the specified location, item name, and port name. Returns the JSON payload with the requested power connection details."""
        return self.__request('GET', '/api/v2/connections/powerconnections/?location=' + str(location) + '&itemName=' + str(itemName) + '&portName=' + str(portName) + '&')

    def deletePowerConnection(self, connectionId: int):
        """Deletes the specified power connection. Deletes the power connection."""
        return self.__request('DELETE', '/api/v2/connections/powerconnections/' + str(connectionId) + '/?')

    def getCircuit(self, circuitType: str, location: str, itemName: str, portName: str):
        """Get power or data circuit details based on the specified circuit type location, item name, and port name. Returns the JSON payload with the requested power or data connection details."""
        return self.__request('GET', '/api/v2/dcimoperations/circuits/' + str(circuitType) + '/?location=' + str(location) + '&itemName=' + str(itemName) + '&portName=' + str(portName) + '&')
