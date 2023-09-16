import psutil

class DjangoMon:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Measure CPU and RAM usage before the request
        before_cpu_percent = psutil.cpu_percent()
        before_memory = psutil.virtual_memory().used

        response = self.get_response(request)

        # Measure CPU and RAM usage after the request
        after_cpu_percent = psutil.cpu_percent()
        after_memory = psutil.virtual_memory().used

        # Log or store the resource usage data
        print(f'Request: {request.path}')
        print(f'CPU Usage: {after_cpu_percent - before_cpu_percent}%')
        print(f'Memory Usage: {after_memory - before_memory} bytes')

        return response