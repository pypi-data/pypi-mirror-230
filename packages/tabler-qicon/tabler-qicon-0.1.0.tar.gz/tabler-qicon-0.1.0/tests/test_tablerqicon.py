# Standard Library Imports
# ------------------------
import os
from pathlib import Path

# Related Third Party Imports
# ---------------------------
import pytest
from PyQt5 import QtGui, QtWidgets

# Local Imports
# -------------
os.environ['QT_API'] = 'PyQt5'
from tablerqicon import TablerQIcon


# Fixture Definition
# ------------------
@pytest.fixture(scope="class")
def qt_application():
    app = QtWidgets.QApplication([])
    yield app
    app.quit()


@pytest.fixture
def tabler_qicon_instance():
    return TablerQIcon()


# Test Cases
# ----------
class TestTablerQIcon(object):
    """Test case for the TablerQIcon class.
    """

    def test_icon_names(self, tabler_qicon_instance):
        """Test the get_icon_names method.
        """
        icon_names = tabler_qicon_instance.get_icon_names()
        assert isinstance(icon_names, list)
        assert len(icon_names) > 0

    def test_icon_path(self, tabler_qicon_instance):
        """Test the get_icon_path method.
        """
        # Put the name of one icon from your directory here.
        icon_path = tabler_qicon_instance.get_icon_path('users')
        assert isinstance(icon_path, Path)
        assert os.path.exists(icon_path)

    def test_icon_retrieval_instance(self, qt_application, tabler_qicon_instance):
        """Test the icon retrieval from an instance of TablerQIcon.
        """
        # Use the name of an icon from your directory here.
        icon = tabler_qicon_instance.users
        assert isinstance(icon, QtGui.QIcon)

    def test_icon_retrieval_class(self, qt_application):
        """Test the icon retrieval from the TablerQIcon class itself.
        """
        # Use the name of an icon from your directory here.
        icon = TablerQIcon.users
        assert isinstance(icon, QtGui.QIcon)

    def test_icon_name_read_only_instance(self, tabler_qicon_instance):
        """Test if icon names are read-only on an instance of TablerQIcon.
        """
        with pytest.raises(AttributeError):
            tabler_qicon_instance.users = QtGui.QIcon()

    def test_icon_name_read_only_class(self):
        """Test if icon names are read-only on the TablerQIcon class itself.
        """
        with pytest.raises(AttributeError):
            TablerQIcon.users = QtGui.QIcon()
