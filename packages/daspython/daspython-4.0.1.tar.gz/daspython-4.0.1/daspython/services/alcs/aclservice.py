from daspython.common.api import ApiMethods, Token

class ChangeOwnershipRequest():
    attributeId: int
    entryId: str
    newOwnerId: int    

class ChangeOwnershipRequestV2():
    code: str
    email: str    

class AclService(ApiMethods):

    def __init__(self, auth: Token):
        super().__init__(auth)

    def change_owner(self, request: ChangeOwnershipRequest) -> bool:
        api_url = '/api/services/app/Entry/UpdateEntryOwnership'       
        response = self.put_data(url=api_url, body=request)
        return response.get('success')
    
    def change_owner_v2(self, code: str, new_owner_email: str) -> bool:
        api_url = '/api/services/app/Entry/UpdateEntryOwnershipV2'  
        request = ChangeOwnershipRequestV2()
        request.code = code
        request.email = new_owner_email     
        response = self.put_data(url=api_url, body=request)
        return response.get('success')