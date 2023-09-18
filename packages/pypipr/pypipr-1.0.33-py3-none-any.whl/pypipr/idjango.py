from django.http.response import HttpResponse


class APIMixinView:
    """
    APIView adalah class view untuk membuat Website API
    Cara kerjanya adalah dengan menggunakan variabel GET untuk menerima data.
    ```py
    class ExampleAPIView(APIMixinView, View):
        pass
    ```
    """

    APIDict = {}

    def get(self, *args, **kwargs):
        self.get_data(*args, **kwargs)
        if self.process_data(*args, **kwargs):
            return self.success(*args, **kwargs)
        return self.failure(*args, **kwargs)

    def get_data(self, *args, **kwargs):
        if self.APIDict:
            for k, v in self.APIDict:
                self.APIDict[k] = self.request.GET.get(k, v)
        else:
            self.APIDict = self.request.GET

    def process_data(self, *args, **kwargs):
        return True

    def success(self, *args, **kwargs):
        return HttpResponse(status=200)

    def failure(self, *args, **kwargs):
        return HttpResponse(status=500)
