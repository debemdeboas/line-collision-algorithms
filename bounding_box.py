from OpenGL.GL.exceptional import glBegin, glVertex, glEnd
from OpenGL.raw.GL.VERSION.GL_1_0 import GL_POLYGON

from Linha import Linha


class BoundingBox:
    """
    Bounding box class
    """

    def __init__(self, line: Linha) -> None:
        """
        Creates a bounding box for the given line

        Args:
            line (Linha): The line whose bounding box will be created
        """

        self._line = line
        self.center = ((line.x1 + line.x2) / 2, (line.y1 + line.y2) / 2)
        self.half_length = (abs(line.x1 - line.x2) / 2, abs(line.y1 - line.y2) / 2)

    def draw(self):
        """
        Draws this bounding box on the screen
        """

        glBegin(GL_POLYGON)
        glVertex(self._line.x1, self._line.y1)
        glVertex(self._line.x2, self._line.y1)
        glVertex(self._line.x2, self._line.y2)
        glVertex(self._line.x1, self._line.y2)
        glEnd()
