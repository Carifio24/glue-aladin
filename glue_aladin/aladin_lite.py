from qtpy import QtWebEngineWidgets  # noqa: F401
from qtpy.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from qtpy.QtWidgets import QWidget, QVBoxLayout

from glue_qt.utils import Worker, get_qapp

ALADIN_LITE_HTML = """
<html>
<head>
    <!-- Mandatory when setting up Aladin Lite v3 for a smartphones/tablet usage -->
    <!--
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, user-scalable=no">
    -->
</head>
<body style="margin: 0;">

<div id="aladin-lite-div" style="width: 100%; height: 100%;"></div>
<script
    type="text/javascript"
    src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js"
    charset="utf-8"
></script>

<script type="text/javascript">
    var aladin;
    var aladinPromise = A.init;
    aladinPromise.then(() => {
        aladin = A.aladin('#aladin-lite-div', {
            fov: 360,
            cooFrame: 'ICRS',
            projection: 'TAN',
            showCooGridControl: false,
            showSimbadPointerControl: false,
            showCooGrid: false,
            showReticle: false,
            showProjectionControl: false,
            showFullscreenControl: false,
            showShareControl: false,
            showFrame: false,
        });
    });
</script>

</body>
</html>
"""


class AladinWebEnginePage(QWebEnginePage):

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        print(f"JavaScript console message: {message} (level: {level}, line: {line_number}, source: {source_id})")

    def _process_js_response(self, result):
        self._js_response_received = True
        self._js_response = result

    def runJavaScript(self, code):
        app = get_qapp()
        self._js_response_received = False
        self._js_response = None
        super(AladinWebEnginePage, self).runJavaScript(code, self._process_js_response)

        while not self._js_response_received:
            app.processEvents()

        return self._js_response


class AladinLiteQtWidget(QWidget):
    
    _ready = False
    _queued_js = []
    _ready_worker = None

    def __init__(self, block_until_ready=False, *args, **kwargs):
        super(AladinLiteQtWidget, self).__init__(*args, **kwargs)
        web = QWebEngineView()
        layout = QVBoxLayout()
        self.setLayout(layout)
        page = AladinWebEnginePage()
        web.setPage(page)
        web.setHtml(ALADIN_LITE_HTML)
        layout.addWidget(web)
        self.web = web
        self.page = web.page()

        if block_until_ready:
            self._check_for_ready()
        else:
            self._ready_worker = Worker(self._check_for_ready)
            self._ready_worker.start()

    def __del__(self):
        if self._ready_worker is not None and self._ready_worker.isRunning():
            self._ready_worker.quit()

    def _check_for_ready(self):
        app = get_qapp()
        aladin = None
        while aladin is None:
            self.run_js("aladin", force_run=True)
            app.processEvents()
            aladin = self.page._js_response

        self._ready = True
        print("Running Queued JS")
        for js in self._queued_js:
            self.run_js(js)
        self._queued_js.clear()

    def run_js(self, js, force_run=False):
        if not (force_run or self._ready):
            self._queued_js.append(js)
            print("Queueing javascript: " + js)
        else:
            print("Running javascript: " + js)
            return self.page.runJavaScript(js)
