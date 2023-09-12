from django.core.paginator import Paginator


class PageUtil:

    @staticmethod
    def get_page(page_num, page_size, result):
        p = Paginator(result.values(), page_size)
        page_data = p.page(page_num)

        page_result = {
            'count': result.count(),
            'rows': list(page_data)
        }

        return page_result
