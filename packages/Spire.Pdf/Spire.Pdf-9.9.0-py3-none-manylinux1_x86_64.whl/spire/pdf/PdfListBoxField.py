from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfListBoxField(PdfListField):
    """
    Represents list box field of the PDF form.
    """

    @property
    def MultiSelect(self) -> bool:
        """
        Gets or sets a value indicating whether the field is multiselectable.

        Returns:
            bool: True if multiselectable; otherwise, False.
        """
        GetDllLibPdf().PdfListBoxField_get_MultiSelect.argtypes = [c_void_p]
        GetDllLibPdf().PdfListBoxField_get_MultiSelect.restype = c_bool
        ret = GetDllLibPdf().PdfListBoxField_get_MultiSelect(self.Ptr)
        return ret

    @MultiSelect.setter
    def MultiSelect(self, value: bool):
        """
        Sets a value indicating whether the field is multiselectable.

        Args:
            value (bool): True if multiselectable; otherwise, False.
        """
        GetDllLibPdf().PdfListBoxField_set_MultiSelect.argtypes = [c_void_p, c_bool]
        GetDllLibPdf().PdfListBoxField_set_MultiSelect(self.Ptr, value)