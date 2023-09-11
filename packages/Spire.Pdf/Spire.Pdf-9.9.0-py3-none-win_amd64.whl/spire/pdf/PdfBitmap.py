from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfBitmap(PdfImage):
    """
    Represents the bitmap images.
    """

    @property
    def ActiveFrame(self) -> int:
        """
        Gets or sets the active frame of the bitmap.
        :return: The active frame index.
        """
        GetDllLibPdf().PdfBitmap_get_ActiveFrame.argtypes = [c_void_p]
        GetDllLibPdf().PdfBitmap_get_ActiveFrame.restype = c_int
        ret = GetDllLibPdf().PdfBitmap_get_ActiveFrame(self.Ptr)
        return ret

    @ActiveFrame.setter
    def ActiveFrame(self, value: int):
        """
        Sets the active frame of the bitmap.
        :param value: The active frame index.
        """
        GetDllLibPdf().PdfBitmap_set_ActiveFrame.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfBitmap_set_ActiveFrame(self.Ptr, value)

    @property
    def FrameCount(self) -> int:
        """
        Gets the number of frames in the bitmap.
        :return: The frame count.
        """
        GetDllLibPdf().PdfBitmap_get_FrameCount.argtypes = [c_void_p]
        GetDllLibPdf().PdfBitmap_get_FrameCount.restype = c_int
        ret = GetDllLibPdf().PdfBitmap_get_FrameCount(self.Ptr)
        return ret

    @property
    def Mask(self) -> 'PdfMask':
        """
        Gets or sets the mask of bitmap.
        :return: New PdfMask.
        """
        GetDllLibPdf().PdfBitmap_get_Mask.argtypes = [c_void_p]
        GetDllLibPdf().PdfBitmap_get_Mask.restype = c_void_p
        intPtr = GetDllLibPdf().PdfBitmap_get_Mask(self.Ptr)
        ret = None if intPtr == None else PdfMask(intPtr)
        return ret

    @Mask.setter
    def Mask(self, value: 'PdfMask'):
        """
        Sets the mask of bitmap.
        :param value: New PdfMask.
        """
        GetDllLibPdf().PdfBitmap_set_Mask.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfBitmap_set_Mask(self.Ptr, value.Ptr)

    @property
    def Quality(self) -> int:
        """
        Gets or sets the quality.
        The range is from 0 to 100, 100 is the best quality.
        :return: The quality.
        """
        GetDllLibPdf().PdfBitmap_get_Quality.argtypes = [c_void_p]
        GetDllLibPdf().PdfBitmap_get_Quality.restype = c_long
        ret = GetDllLibPdf().PdfBitmap_get_Quality(self.Ptr)
        return ret

    @Quality.setter
    def Quality(self, value: int):
        """
        Sets the quality.
        The range is from 0 to 100, 100 is the best quality.
        :param value: The quality.
        """
        GetDllLibPdf().PdfBitmap_set_Quality.argtypes = [c_void_p, c_long]
        GetDllLibPdf().PdfBitmap_set_Quality(self.Ptr, value)

    def Dispose(self):
        """
        Performs application-defined tasks associated with freeing,
        releasing, or resetting unmanaged resources.
        """
        GetDllLibPdf().PdfBitmap_Dispose.argtypes = [c_void_p]
        GetDllLibPdf().PdfBitmap_Dispose(self.Ptr)