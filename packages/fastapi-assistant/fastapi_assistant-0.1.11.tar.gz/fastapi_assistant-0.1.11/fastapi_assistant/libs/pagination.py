from fastapi import Query


class Pagination:
    def __init__(self, page: int = Query(1, ge=1, description="页数"),
                 size: int = Query(10, gt=0, description="每页个数")):
        self.page = page
        self.size = size
