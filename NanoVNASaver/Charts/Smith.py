#  NanoVNASaver
#
#  A python program to view and export Touchstone data from a NanoVNA
#  Copyright (C) 2019, 2020  Rune B. Broberg
#  Copyright (C) 2020,2021 NanoVNA-Saver Authors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import math
import logging

from PyQt5 import QtGui, QtCore

from NanoVNASaver.RFTools import Datapoint
from NanoVNASaver.Charts.Chart import Chart
from NanoVNASaver.Charts.Square import SquareChart

logger = logging.getLogger(__name__)


class SmithChart(SquareChart):
    def __init__(self, name=""):
        super().__init__(name)
        self.dim.width = 250
        self.dim.height = 250

        self.setMinimumSize(self.dim.width + 40, self.dim.height + 40)
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, Chart.color.background)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

    def paintEvent(self, _: QtGui.QPaintEvent) -> None:
        qp = QtGui.QPainter(self)
        # qp.begin(self)  # Apparently not needed?
        self.drawSmithChart(qp)
        self.drawValues(qp)
        qp.end()

    def drawSmithChart(self, qp: QtGui.QPainter):
        centerX = int(self.width()/2)
        centerY = int(self.height()/2)
        qp.setPen(QtGui.QPen(Chart.color.text))
        qp.drawText(3, 15, self.name)
        qp.setPen(QtGui.QPen(Chart.color.foreground))
        qp.drawEllipse(QtCore.QPoint(centerX, centerY),
                       int(self.dim.width / 2),
                       int(self.dim.height / 2))
        qp.drawLine(
            centerX - int(self.dim.width / 2),
            centerY,
            centerX + int(self.dim.width / 2),
            centerY)

        qp.drawEllipse(QtCore.QPoint(centerX + int(self.dim.width/4), centerY),
                       int(self.dim.width/4), int(self.dim.height/4))  # Re(Z) = 1
        qp.drawEllipse(QtCore.QPoint(centerX + int(2/3*self.dim.width/2), centerY),
                       int(self.dim.width/6), int(self.dim.height/6))  # Re(Z) = 2
        qp.drawEllipse(QtCore.QPoint(centerX + int(3 / 4 * self.dim.width / 2), centerY),
                       int(self.dim.width / 8), int(self.dim.height / 8))  # Re(Z) = 3
        qp.drawEllipse(QtCore.QPoint(centerX + int(5 / 6 * self.dim.width / 2), centerY),
                       int(self.dim.width / 12), int(self.dim.height / 12))  # Re(Z) = 5

        qp.drawEllipse(QtCore.QPoint(centerX + int(1 / 3 * self.dim.width / 2), centerY),
                       int(self.dim.width / 3), int(self.dim.height / 3))  # Re(Z) = 0.5
        qp.drawEllipse(QtCore.QPoint(centerX + int(1 / 6 * self.dim.width / 2), centerY),
                       int(self.dim.width / 2.4), int(self.dim.height / 2.4))  # Re(Z) = 0.2

        qp.drawArc(centerX + int(3/8*self.dim.width), centerY, int(self.dim.width/4),
                   int(self.dim.width/4), 90*16, 152*16)  # Im(Z) = -5
        qp.drawArc(centerX + int(3/8*self.dim.width), centerY, int(self.dim.width/4),
                   -int(self.dim.width/4), -90 * 16, -152 * 16)  # Im(Z) = 5
        qp.drawArc(centerX + int(self.dim.width/4), centerY, int(self.dim.width/2),
                   int(self.dim.height/2), 90*16, 127*16)  # Im(Z) = -2
        qp.drawArc(centerX + int(self.dim.width/4), centerY, int(self.dim.width/2),
                   -int(self.dim.height/2), -90*16, -127*16)  # Im(Z) = 2
        qp.drawArc(centerX, centerY,
                   self.dim.width, self.dim.height,
                   90*16, 90*16)  # Im(Z) = -1
        qp.drawArc(centerX, centerY,
                   self.dim.width, -self.dim.height,
                   -90 * 16, -90 * 16)  # Im(Z) = 1
        qp.drawArc(centerX - int(self.dim.width / 2), centerY,
                   self.dim.width * 2, self.dim.height * 2,
                   int(99.5*16), int(43.5*16))  # Im(Z) = -0.5
        qp.drawArc(centerX - int(self.dim.width / 2), centerY,
                   self.dim.width * 2, -self.dim.height * 2,
                   int(-99.5 * 16), int(-43.5 * 16))  # Im(Z) = 0.5
        qp.drawArc(centerX - self.dim.width * 2, centerY,
                   self.dim.width * 5, self.dim.height * 5,
                   int(93.85 * 16), int(18.85 * 16))  # Im(Z) = -0.2
        qp.drawArc(centerX - self.dim.width*2, centerY,
                   self.dim.width*5, -self.dim.height*5,
                   int(-93.85 * 16), int(-18.85 * 16))  # Im(Z) = 0.2

        self.drawTitle(qp)

        qp.setPen(Chart.color.swr)
        for swr in self.swrMarkers:
            if swr <= 1:
                continue
            gamma = (swr - 1)/(swr + 1)
            r = round(gamma * self.dim.width/2)
            qp.drawEllipse(QtCore.QPoint(centerX, centerY), r, r)
            qp.drawText(
                QtCore.QRect(centerX - 50, centerY - 4 + r, 100, 20),
                QtCore.Qt.AlignCenter, str(swr))

    def drawValues(self, qp: QtGui.QPainter):
        if len(self.data) == 0 and len(self.reference) == 0:
            return
        pen = QtGui.QPen(Chart.color.sweep)
        pen.setWidth(self.dim.point)
        line_pen = QtGui.QPen(Chart.color.sweep)
        line_pen.setWidth(self.dim.line)
        highlighter = QtGui.QPen(QtGui.QColor(20, 0, 255))
        highlighter.setWidth(1)
        qp.setPen(pen)
        for i in range(len(self.data)):
            x = self.getXPosition(self.data[i])
            y = int(self.height()/2 + self.data[i].im * -1 * self.dim.height/2)
            qp.drawPoint(x, y)
            if self.flag.draw_lines and i > 0:
                prevx = self.getXPosition(self.data[i-1])
                prevy = int(self.height() / 2 + self.data[i-1].im * -1 * self.dim.height / 2)
                qp.setPen(line_pen)
                qp.drawLine(x, y, prevx, prevy)
                qp.setPen(pen)
        pen.setColor(Chart.color.reference)
        line_pen.setColor(Chart.color.reference)
        qp.setPen(pen)
        if len(self.data) > 0:
            fstart = self.data[0].freq
            fstop = self.data[len(self.data)-1].freq
        else:
            fstart = self.reference[0].freq
            fstop = self.reference[len(self.reference)-1].freq
        for i in range(len(self.reference)):
            data = self.reference[i]
            if data.freq < fstart or data.freq > fstop:
                continue
            x = self.getXPosition(data)
            y = int(self.height()/2 + data.im * -1 * self.dim.height/2)
            qp.drawPoint(x, y)
            if self.flag.draw_lines and i > 0:
                prevx = self.getXPosition(self.reference[i-1])
                prevy = int(self.height() / 2 + self.reference[i-1].im * -1 * self.dim.height / 2)
                qp.setPen(line_pen)
                qp.drawLine(x, y, prevx, prevy)
                qp.setPen(pen)
        # Now draw the markers
        for m in self.markers:
            if m.location != -1:
                x = self.getXPosition(self.data[m.location])
                y = self.height() / 2 + self.data[m.location].im * -1 * self.dim.height / 2
                self.drawMarker(x, y, qp, m.color, self.markers.index(m)+1)

    def getXPosition(self, d: Datapoint) -> int:
        return int(self.width()/2 + d.re * self.dim.width/2)

    def getYPosition(self, d: Datapoint) -> int:
        return int(self.height()/2 + d.im * -1 * self.dim.height/2)

    def heightForWidth(self, a0: int) -> int:
        return a0

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.buttons() == QtCore.Qt.RightButton:
            a0.ignore()
            return
        x = a0.x()
        y = a0.y()
        absx = x - (self.width() - self.dim.width) / 2
        absy = y - (self.height() - self.dim.height) / 2
        if absx < 0 or absx > self.dim.width or absy < 0 or absy > self.dim.height \
                or len(self.data) == len(self.reference) == 0:
            a0.ignore()
            return
        a0.accept()

        if len(self.data) > 0:
            target = self.data
        else:
            target = self.reference
        positions = []
        for d in target:
            thisx = self.width() / 2 + d.re * self.dim.width / 2
            thisy = self.height() / 2 + d.im * -1 * self.dim.height / 2
            positions.append(math.sqrt((x - thisx)**2 + (y - thisy)**2))

        minimum_position = positions.index(min(positions))
        m = self.getActiveMarker()
        if m is not None:
            m.setFrequency(str(round(target[minimum_position].freq)))
            m.frequencyInput.setText(str(round(target[minimum_position].freq)))
        return
