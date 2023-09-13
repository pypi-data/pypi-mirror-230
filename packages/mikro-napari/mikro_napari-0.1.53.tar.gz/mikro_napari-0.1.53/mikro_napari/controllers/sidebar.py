from mikro_napari.controllers.base import BaseMikroNapariController
from mikro_napari.widgets.sidebar.sidebar import SidebarWidget
from rekuest.qt.builders import qtinloopactifier
from mikro.api.schema import TableFragment


class SidebarController(BaseMikroNapariController):
    def __init__(self, sidebar: SidebarWidget, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.sidebar = sidebar

        self.app.rekuest.register(
            self.open_table,
            actifier=qtinloopactifier,
            parent=self,
            collections=["display", "interactive"],
        )

    def open_table(self, table: TableFragment):
        """Open Table in Sidebar

        Opens the table in an accessible sidebar widget.

        Args:
            table (TableFragment): Table to open


        """
        self.sidebar.show_table_widget(table)
