from .models import Adapter, Request, Response, PreparedRequest


class Client:
    def __init__(self):
        self._adapter = Adapter(auth)

    def get_accounts(self):
        request = Request(resource='accounts', with_deleted=False)
        return self.send(request)

    def get_campaigns(self):
        request = Request(resource='campaigns', with_deleted=False)
        return self.send(request)
    
    def send(self, request):
        if isinstance(request, Request):
            prepared_requests = request.prepare()

        if isinstance(request, PreparedRequest):
            prepared_requests = [request]

        for request in prepared_requests:
            self.adapter.enqueue(request)

        self.adapter.process_queue()
