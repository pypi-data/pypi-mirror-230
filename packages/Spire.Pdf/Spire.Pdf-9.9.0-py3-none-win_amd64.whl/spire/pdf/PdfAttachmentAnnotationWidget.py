from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfAttachmentAnnotationWidget(PdfStyledAnnotationWidget):
    """
    Represents the attachment annotation from the loaded document.
    """

    @property
    def Icon(self) -> 'PdfAttachmentIcon':
        """
        Gets or sets the icon of the annotation.
        """
        GetDllLibPdf().PdfAttachmentAnnotationWidget_get_Icon.argtypes = [c_void_p]
        GetDllLibPdf().PdfAttachmentAnnotationWidget_get_Icon.restype = c_int
        ret = GetDllLibPdf().PdfAttachmentAnnotationWidget_get_Icon(self.Ptr)
        objwrapped = PdfAttachmentIcon(ret)
        return objwrapped

    @Icon.setter
    def Icon(self, value: 'PdfAttachmentIcon'):
        """
        Sets the icon of the annotation.
        """
        GetDllLibPdf().PdfAttachmentAnnotationWidget_set_Icon.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfAttachmentAnnotationWidget_set_Icon(self.Ptr, value.value)

    @property
    def FileName(self) -> str:
        """
        Gets the attachment file name of the annotation.
        """
        GetDllLibPdf().PdfAttachmentAnnotationWidget_get_FileName.argtypes = [c_void_p]
        GetDllLibPdf().PdfAttachmentAnnotationWidget_get_FileName.restype = c_void_p
        ret = PtrToStr(GetDllLibPdf().PdfAttachmentAnnotationWidget_get_FileName(self.Ptr))
        return ret

    def ObjectID(self) -> int:
        """
        Represents the Form field identifier.
        """
        GetDllLibPdf().PdfAttachmentAnnotationWidget_ObjectID.argtypes = [c_void_p]
        GetDllLibPdf().PdfAttachmentAnnotationWidget_ObjectID.restype = c_int
        ret = GetDllLibPdf().PdfAttachmentAnnotationWidget_ObjectID(self.Ptr)
        return ret