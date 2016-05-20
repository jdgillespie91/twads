from collections import deque


class Adapter(object):
    """ An adapter to the Twitter Ads API.

    The adapter is responsible for two things; pagination and retrying. In
    particular, there is some care taken to ensure that we don't bail out of
    the request too early.

    """

    def __init__(self):
        self.queue = deque()

    def enqueue(self, request):
        self.queue.append(request)

    def dequeue(self):
        return self.queue.popleft()

    def process_queue(self):
        while self.queue:
            request = self.dequeue()
            self._send(request)

    def _send(self, request):
        data = []
        errors = []

        response = self._retry(request)

        if response.status_code != 200:
            errors.extend(response.json())
        else:
            data.extend(response.json()['data'])

            try:
                request.next_cursor = response.json()['next_cursor']
            except KeyError:
                pass
            else:
                self.enqueue(request)

        return data, errors

    def _retry(self, request):
        retry_codes = [429]
        max_tries = 3
        tries = 0
        resp = None

        while True:
            resp = requests.get(url=self.endpoint, params=self.params, auth=self.auth)
            if resp.status_code in retry_codes and tries < max_tries:
                # 429 is RATE_LIMIT_EXCEEDED. In the response header, Twitter provides the
                # time at which our rate limit will reset (at most, 15 minutes). We sleep
                # until then.
                if resp.status_code == 429:
                    sleep_for = max(
                        0, int(resp.headers['x-cost-rate-limit-reset']) - int(time.time())
                    )
                    time.sleep(sleep_for)

                tries += 1
                continue
            break
        return resp
