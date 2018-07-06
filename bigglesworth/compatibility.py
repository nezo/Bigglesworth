import sys
from Qt import QtCore, QtGui, QtWidgets

#workarounds for menu separators with labels on Windows and Mac
class MenuSeparator(QtWidgets.QWidgetAction):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidgetAction.__init__(self, *args, **kwargs)
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum))
        self.label.setMaximumHeight(self.label.frameWidth())
        self.setDefaultWidget(self.label)
        if sys.platform == 'win32':
            self.label.setFrameStyle(QtWidgets.QFrame.StyledPanel|QtWidgets.QFrame.Sunken)
        else:
            self.label.setStyleSheet('''
                QLabel {
                    border: 1px solid lightgray;
                    margin: 2px;
                    padding-left: {l}px;
                    padding-right: {r}px;
                }
            ''')
            if self.parent():
                self.parent().aboutToShow.connect(self.setMenuFont)

    def setMenuFont(self):
        #menu item font sizes has to be forced to float (at least for osx 10.5)
        menu = self.parent()
        menu.aboutToShow.disconnect(self.setMenuFont)
        for action in menu.actions():
            if not isinstance(action, QtWidgets.QWidgetAction):
                option = QtWidgets.QStyleOptionMenuItem()
                menu.initStyleOption(option, action)
                labelFont = self.label.font()
                labelFont.setPointSizeF(option.font.pointSizeF())
                self.label.setFont(labelFont)
                break

    def setText(self, text):
        self.label.setText(text)
        if text:
            self.label.setMaximumHeight(16777215)
        else:
            self.label.setMaximumHeight(self.label.frameWidth())


class MacSeparatorLabel(QtWidgets.QLabel):
    done = False
    def __init__(self, parentMenu, text=''):
        QtWidgets.QLabel.__init__(self, text)
        self.parentMenu = parentMenu
        self.setAlignment(QtCore.Qt.AlignCenter)

    def setText(self, text):
        QtWidgets.QLabel.setText(self, text)
        if self.done:
            self.compute()

    def showEvent(self, event):
        if not self.done:
            self.done = True
            parent = self.parent()
            layout = QtWidgets.QHBoxLayout()
            parent.setLayout(layout)
            layout.addWidget(self)
            left, top, right, bottom = layout.getContentsMargins()
            self.margins = left + right
            layout.setContentsMargins(0, 0, 0, 0)
            parent.setContentsMargins(0, 0, 0, 0)
#            self.setContentsMargins(left, 0, right, 0)
            self.setContentsMargins(0, 0, 0, 0)
            parent.installEventFilter(self)
            parent.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
            self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
            parent.setStyleSheet('''
            MacSeparatorLabel {{
                border: 1px solid lightgray;
                margin: 2px;
                padding-left: {l}px;
                padding-right: {r}px;
            }}
            '''.format(l=left - 1, r=right - 1))

    def compute(self):
        option = QtWidgets.QStyleOptionMenuItem()
        maxWidth = 0
        minHeight = 0
        baseSize = QtCore.QSize(0, 0)
        for action in self.parentMenu.actions():
            if isinstance(action, QtWidgets.QWidgetAction):
                widget = action.defaultWidget()
                if widget != self and isinstance(widget, MacSeparatorLabel):
                    maxWidth = max(maxWidth, widget.fontMetrics().width(widget.text()))
                continue
            self.parentMenu.initStyleOption(option, action)
            #font has to be "reset" using pointsize, for unknown reasons
            option.font.setPointSizeF(option.font.pointSizeF())
            contents = self.parentMenu.style().sizeFromContents(QtWidgets.QStyle.CT_MenuItem, option, baseSize)
            maxWidth = max(maxWidth, contents.width(), QtGui.QFontMetrics(option.font).width(option.text) + self.margins)
            minHeight = min(minHeight, contents.height())

        self.setFont(option.font)
        fontMetrics = self.fontMetrics()
        minWidth = max((maxWidth + self.margins), fontMetrics.width(self.text()) + self.margins)
        self.setMinimumWidth(minWidth)
        self.parent().setMinimumWidth(minWidth)
        l, t, r, b = self.getContentsMargins()
        
        self.setContentsMargins(l, fontMetrics.descent(), r, fontMetrics.descent())
        self.parent().setMinimumHeight(minHeight)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Paint:
            self.parentPaintEvent(event)
            return True
        return QtWidgets.QLabel.eventFilter(self, source, event)

    def parentPaintEvent(self, event):
        self.compute()
        qp = QtGui.QPainter(self.parent())
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtGui.QColor(255, 255, 255, 245))
        qp.drawRect(self.parent().rect())


class MacMenuBarSeparator(QtWidgets.QWidgetAction):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidgetAction.__init__(self, *args, **kwargs)
        self.setSeparator(True)
        self.label = MacSeparatorLabel(self.parent())
        self.setDefaultWidget(self.label)

    def setText(self, text):
        self.setSeparator(False if text else True)
        self.label.setText(text)


if sys.platform == 'win32':

    def addSeparator(self):
        action = MenuSeparator(self)
        QtWidgets.QMenu.addAction(self, action)
        return action

    def insertSeparator(self, before):
        action = MenuSeparator(self)
        QtWidgets.QMenu.insertAction(self, before, action)
        return action

else:

    #QWidgetAction in a QMenuBar don't draw the backgrounds, this hack
    #ensures that the QMacNativeWidget (which is created as a parent of the 
    #defaultWidget) is correctly layed out and stylized.
    def addSeparator(self):
        parent = self.parent()
        while isinstance(parent, QtWidgets.QMenu):
            parent = parent.parent()
        if isinstance(parent, QtWidgets.QMenuBar):
            action = MacMenuBarSeparator(self)
        else:
            action = MenuSeparator(self)
        self.addAction(action)
        return action

    def insertSeparator(self, before):
        parent = self.parent()
        while isinstance(parent, QtWidgets.QMenu):
            parent = parent.parent()
        if isinstance(parent, QtWidgets.QMenuBar):
            action = MacMenuBarSeparator(self)
        else:
            action = MenuSeparator(self)
        self.insertAction(before, action)
        return action
    
QtWidgets.QMenu.insertSeparator = insertSeparator
QtWidgets.QMenu.addSeparator = addSeparator


if sys.platform == 'darwin':
    #workaround for QIcon.fromTheme not properly working on OSX with cx_freeze
    QtGui.QIcon._fromTheme = QtGui.QIcon.fromTheme
    sizes = (64, 32, 24, 22, 16, 8)
    iconCache = {}
    iconDir = QtCore.QDir(':/icons/{}/'.format(QtGui.QIcon.themeName()))

    @staticmethod
    def fromTheme(name, fallback=None):
        if fallback:
            icon = QtGui.QIcon._fromTheme(name, fallback)
            if not icon.isNull():
                return icon
        icon = iconCache.get(name)
        if icon:
            return icon
        icon = QtGui.QIcon._fromTheme('')
#            if icon.isNull():
        for size in sizes:
            path = '{s}x{s}/{n}.svg'.format(s=size, n=name)
            if iconDir.exists(path):
                icon.addFile(iconDir.filePath(path), QtCore.QSize(size, size))
        iconCache[name] = icon
        return icon

    QtGui.QIcon.fromTheme = fromTheme