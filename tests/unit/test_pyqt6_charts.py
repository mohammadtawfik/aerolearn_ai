def test_pyqt6_charts_import():
    try:
        from PyQt6.QtCharts import QChart
    except ImportError:
        assert False, "PyQt6-Charts is not installed or importable"