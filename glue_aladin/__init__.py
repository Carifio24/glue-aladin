def setup():
    from qtpy import QtWebEngineWidgets  # noqa: F401
    from .data_viewer import AladinLiteViewer
    from glue.config import qt_client
    qt_client.add(AladinLiteViewer)
