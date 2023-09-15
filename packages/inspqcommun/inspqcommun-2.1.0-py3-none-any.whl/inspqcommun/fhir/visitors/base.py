from fhirclient.models.extension import Extension
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from datetime import datetime

class BaseVisitor():
    DEFAULT_CODING_SYSTEM = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    DEFAULT_CODING_VERSION = "1.0.0"

    __fhir_resource = None

    def getFhirResource(self):
        return self.__fhir_resource
    
    def setFhirResource(self, fhir_resource):
        self.__fhir_resource = fhir_resource

    def str_date_to_fhir_date(self, str_date):
        fhir_date  = FHIRDate()
        fhir_date.date = datetime.strptime(str_date, '%Y-%m-%d').date()
        return fhir_date

    def fhir_date_to_str_date(self, fhir_date):
        str_date = None
        if fhir_date is not None and fhir_date.date is not None:
            str_date = fhir_date.isostring
        return str_date

    def add_or_update_extension_to_extensions(self, extension, extensions):
        if extensions is None:
            extensions = [extension]
        else:
            ext_found = False
            for ext in extensions:
                if type(ext) is Extension:
                    if ext.url == extension.url:
                        extensions.remove(ext)
                        extensions.append(extension)
                        ext_found = True
                        break
                elif type(ext) is list:
                    for sub_ext in ext:
                        ext = self.add_or_update_extension_to_extensions(extension=sub_ext, extensions=ext)
            if not ext_found:
                extensions.append(extension)
        return extensions
    
    def _to_codeable_concept(self, code: str, display:str=None, coding_system: str=DEFAULT_CODING_SYSTEM, coding_version: str=DEFAULT_CODING_VERSION) -> CodeableConcept:
        codeableConcept = CodeableConcept()
        coding = Coding()
        coding.code = code
        if display:
            coding.display = display
        coding.system = coding_system
        coding.version = coding_version
        codeableConcept.coding = [coding]
        return codeableConcept
    
    def _get_coding_par_system(self, codeableConcept: CodeableConcept, coding_system:str=DEFAULT_CODING_SYSTEM, coding_version:str=DEFAULT_CODING_VERSION) -> Coding:
        coding: Coding
        for coding in codeableConcept.coding:
            if coding.system == coding_system and coding.version == coding_version:
                return coding
        return None
    
    def _creer_extension(self, url: str, **kwargs) -> Extension:
        extension = Extension()
        extension.url = url
        if "valueString" in kwargs:
            extension.valueString = kwargs["valueString"]
        elif "valueDate" in kwargs:
            extension.valueDate = kwargs["valueDate"]
        elif "valueCodeableConcept" in kwargs:
            extension.valueCodeableConcept = kwargs["valueCodeableConcept"]
        elif "valueInteger" in kwargs:
            extension.valueInteger = kwargs["valueInteger"]
        return extension