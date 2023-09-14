from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from foledol.django.tools.table import TableColumn, TableView

from ..models import Grid


class GridTables(TableView):
    def __init__(self):
        super().__init__(Grid, [
            TableColumn('name', "Nom", sortable=True),
            TableColumn('table', "Table", method="table_as_str")
        ], path='django/grids', search=True, sort='name_asc')
        self.update = 'django:grid_update'
        self.create = 'django:grid_create'

    def select(self, grids, search, order_by):
        if len(search) > 0:
            grids = Grid.objects.filter(name__contains=search)
        if order_by == 'name_asc':
            return grids.order_by('name')
        elif order_by == 'name_desc':
            return grids.order_by('-name')
        return grids


@login_required
@staff_member_required
def grid_list(request):
    return GridTables().render(request)


def grid_renumber(grid):
    order = 10
    for column in grid.column_set.all().order_by('order'):
        if column.order != order:
            column.order = order
            column.save()
        order += 10






