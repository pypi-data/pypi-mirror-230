from grpc_requests import Client

company_pages_grpc_endpoint = "company-pages.grpc.delphai.com:80"


class ScrapedCompanyPage:
    def __init__(self):
        client = Client(company_pages_grpc_endpoint)

        health = client.service("grpc.health.v1.Health")
        assert health.method_names == ("Check", "Watch")

        result = health.Check()
        assert result == {"status": "SERVING"}

        self.CompanyPages = client.service("delphai.CompanyPages")

    def list_domains(self, prefix: str, limit: int = 20):
        stream = self.CompanyPages.list_domains({"prefix": prefix, "limit": limit})
        return stream

    def list_pages(self, domain: str):
        stream = self.CompanyPages.list_urls({"domain": domain})
        return stream

    def get_content_for_class(
        self,
        content_type: str,
        domain: str = None,
        company_id: str = None,
        page_classes: list = None,
        classifier: str = None,
        language: str = None,
    ):
        request = {}
        request["type"] = content_type

        if domain or company_id:
            if domain:
                request["domain"] = domain
            if company_id:
                request["company_id"] = company_id
        else:
            raise ValueError("Should provide a domain or a company_id.")

        if page_classes:
            request["page_classes"] = page_classes
        if classifier:
            request["classifier"] = classifier
        if language:
            request["language"] = language

        stream = self.CompanyPages.pages(request)
        page_list = list(stream)
        return page_list, len(page_list)

    def get_page_metadata(self, url: str):
        stream = self.CompanyPages.get_page_metadata({"url": url})
        return stream

    def get_page_content(self, url: str, content_type: str, language: str = None):
        request = {}
        request["url"] = url
        request["type"] = content_type
        if language:
            request["language"] = language

        stream = self.CompanyPages.page(request)
        return stream
