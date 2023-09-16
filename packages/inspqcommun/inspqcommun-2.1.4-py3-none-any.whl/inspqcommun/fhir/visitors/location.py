from fhirclient.models.location import Location
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.period import Period
from fhirclient.models.extension import Extension

from inspqcommun.fhir.visitors.base import BaseVisitor

class LocationVisitor(BaseVisitor):
    
    RRSS_SYSTEM = 'https://pro.consultation.rrss.rtss.qc.ca'
    RRSS_MOT_CLE_EXTENSION_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/rrss/1.0.0/extensions/#motscles'
    PERIOD_URL = "http://www.santepublique.rtss.qc.ca/sipmi/rrss/1.0.0/extensions/period"

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource=fhir_resource if fhir_resource else Location())

    def getFhirResource(self) -> Location:
        return super().getFhirResource()        

    def have_mot_cle(self, mot_cle=None):
        if mot_cle is not None and self.getFhirResource().extension is not None:
            for extension in self.getFhirResource().extension:
                if extension.url == self.RRSS_MOT_CLE_EXTENSION_URL and extension.valueString == mot_cle:
                    return True
        return False

    def set_name(self, name=None):
        self.getFhirResource().name = name

    def get_name(self):
        return self.getFhirResource().name

    def get_id(self):
        return self.getFhirResource().id

    def get_id_rrss(self):
        if self.getFhirResource().identifier is not None:
            for identifier in self.getFhirResource().identifier:
                if identifier.system == self.RRSS_SYSTEM:
                    return identifier.value
        return None

    def get_address_city(self):
        if self.getFhirResource().address:
            return self.getFhirResource().address.city
        return None

    def get_phones(self):
        phones = []
        if self.getFhirResource().telecom is None:
            return phones
        for telecom in self.getFhirResource().telecom:
            if telecom.system == "phone":
                phone = {}
                phone["value"] = telecom.value
                phone["use"] = telecom.use
                phones.append(phone)
        return phones

    def get_effective_from(self):
        period_ext = self.__get_period_ext()
        if period_ext is not None and period_ext.valuePeriod is not None:
                return period_ext.valuePeriod.start
        return None

    def get_effective_to(self):
        period_ext = self.__get_period_ext()
        if period_ext is not None and period_ext.valuePeriod is not None:
                return period_ext.valuePeriod.end
        return None

    def set_effective_from(self, effective_from=None):
        fhir_effective_from = None
        if type(effective_from) is str:
            fhir_effective_from = FHIRDate(jsonval=effective_from)
        elif type(effective_from) is FHIRDate:
            fhir_effective_from = effective_from
        period_ext = self.__get_period_ext()
        if period_ext is None or period_ext.valuePeriod is None:
            period = Period()
        else:
            period = period_ext.valuePeriod
        period.start = fhir_effective_from
        self.__set_period_ext(period=period)

    def set_effective_to(self, effective_to=None):
        fhir_effective_to = None
        if type(effective_to) is str:
            fhir_effective_to = FHIRDate(jsonval=effective_to)
        elif type(effective_to) is FHIRDate:
            fhir_effective_to = effective_to
        period_ext = self.__get_period_ext()
        if period_ext is None or period_ext.valuePeriod is None:
            period = Period()
        else:
            period = period_ext.valuePeriod
        period.end = fhir_effective_to
        self.__set_period_ext(period=period)

    def is_active(self):
        return self.getFhirResource().status == "active"
    
    def __get_period_ext(self):
        if self.getFhirResource().extension is not None:
            for ext in self.getFhirResource().extension:
                if ext.url == self.PERIOD_URL:
                    return ext
        return None

    def __set_period_ext(self, period=None):
        if self.getFhirResource().extension is None:
            self.getFhirResource().extension = []
        period_ext = self.__get_period_ext()
        if period_ext is None:
            period_ext = Extension()
            period_ext.url = self.PERIOD_URL
            self.getFhirResource().extension.append(period_ext)
        period_ext.valuePeriod = period
        
    