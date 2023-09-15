import hcl2
import lark.exceptions
from lark import UnexpectedCharacters


class LinesMetric:
    """ This is an abstract class the concrete classes measuring lines of code will extend.
    """

    def __init__(self, script: str):
        """The class constructor.

        Parameters
        ----------
        script : str
            A plain Terraform file

        """

        if script is None:
            raise TypeError("Parameter 'script' meant to be a string, not None.")
        try :
            # Check if is a valid hcl file
            self.__hcl = hcl2.loads(script, with_meta=True)
            if self.__hcl is None:
                raise TypeError("Expected a not empty Terraform script")

            self.__hcl = script

        except UnexpectedCharacters as e:
            raise TypeError("Expected a valid Terraform script")
        except lark.exceptions.VisitError:
            self.__hcl = script

    @property
    def hcl(self):
        """Il file Terraform in formato HCL."""
        return self.__hcl

    def count(self):
        """Metodo per eseguire la metrica."""
        pass