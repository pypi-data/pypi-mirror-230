from inspqcommun.fa.validateurs.validateur_usager import ValidateurUsager
from inspqcommun.fa.validateurs.validateur_acte_vaccinal import ValidateurActeVaccinal
from inspqcommun.fa.convertisseurs.convertisseur_usager import ConvertisseurUsager
from inspqcommun.fa.convertisseurs.convertisseur_acte_vaccinal import ConvertisseurActeVaccinal
from inspqcommun.fa.ressources.usager import Usager
from inspqcommun.fa.ressources.acte_vaccinal import ActeVaccinal
from inspqcommun.fa.chargeur_fichiers import ChargeurFichiers
from inspqcommun.fhir.clients.patient_client import PatientClient
from inspqcommun.fhir.clients.immunization_client import ImmunizationClient
from fhirclient.models.operationoutcome import OperationOutcome
from typing import List
import logging, json

log = logging.getLogger(__name__)

class ChargementService:

    def __init__(self, chargeur_fichiers : ChargeurFichiers, validateur_usager: ValidateurUsager, validateur_acte_vaccinal: ValidateurActeVaccinal,
                 convertisseur_usager : ConvertisseurUsager, convertisseur_acte_vaccinal : ConvertisseurActeVaccinal, patient_client: PatientClient,
                 immunization_client: ImmunizationClient):
        self.__chargeur_fichiers : ChargeurFichiers = chargeur_fichiers
        self.__validateur_usager : ValidateurUsager = validateur_usager
        self.__validateur_acte_vaccinal : ValidateurActeVaccinal = validateur_acte_vaccinal
        self.__convertisseur_usager : ConvertisseurUsager = convertisseur_usager
        self.__convertisseur_acte_vaccinal : ConvertisseurActeVaccinal = convertisseur_acte_vaccinal
        self.__patient_client : PatientClient = patient_client
        self.__immunization_client : ImmunizationClient = immunization_client
        self.nb_ressources_fichier = 0
        self.nb_ressources_converties = 0

    def charger_donnees_par_fonctions_allegees(self):
        for ressources_a_charger in self.__valider_et_obtenir_ressources_dans_les_fichiers():
            for ressource in ressources_a_charger:
                if isinstance(ressource, Usager):
                    self.__charger_usager(usager=ressource)
                elif isinstance(ressource, ActeVaccinal):
                    self.__charger_actes_vaccinaux(acte_vaccinal=ressource)

    def valider_fichier_donnees(self) -> bool:
        self.__valider_et_obtenir_ressources_dans_les_fichiers()
        return self.nb_ressources_converties == self.nb_ressources_fichier

    def __valider_et_obtenir_ressources_dans_les_fichiers(self):
        fichier_en_erreur: bool = False
        listes_ressources_a_charger = []

        for nom_fichier in self.__chargeur_fichiers.obtenir_noms_fichiers():
            ressources_a_charger = []
            validations_echouees: bool = False

            contenu_fichier = self.__chargeur_fichiers.obtenir_contenu_fichier_par_nom(nom_fichier)
            if contenu_fichier is not None:
                for ressource in contenu_fichier:
                    if "ressource" in ressource:
                        self.nb_ressources_fichier += 1
                        ressource_convertie = None
                        if ressource["ressource"] == "Usager":
                            ressource_convertie = self.__obtenir_ressource_convertie_si_valide(ressource, self.__convertisseur_usager, self.__validateur_usager)
                        if ressource["ressource"] ==  "ActeVaccinal":
                            ressource_convertie = self.__obtenir_ressource_convertie_si_valide(ressource, self.__convertisseur_acte_vaccinal, self.__validateur_acte_vaccinal)
                            
                        if ressource_convertie:
                            self.nb_ressources_converties += 1
                            ressources_a_charger.append(ressource_convertie)
                        else:
                            validations_echouees = True

                if not validations_echouees:
                    listes_ressources_a_charger.append(ressources_a_charger)
                else:
                    fichier_en_erreur = True
            else:
                fichier_en_erreur = True

        return listes_ressources_a_charger if not fichier_en_erreur else []

    def __obtenir_ressource_convertie_si_valide(self, ressource: str, convertisseur, validateur) -> any:
        ressource_convertie = convertisseur.fromJson(**ressource)
        erreurs = validateur.valider(ressource_convertie)
        if not erreurs:
            return ressource_convertie
        else:
            log.error("La ressource de type {} n'est pas valide: {}".format(type(ressource_convertie), [";".join(erreur) for erreur in erreurs]))
            return None
    
    def __charger_usager(self, usager: Usager):
        patient = self.__convertisseur_usager.toFhir(usager)
        match_response = self.__patient_client.match(patient)
        if match_response.status_code == 204:
            create_response = self.__patient_client.create(patient)
            if create_response.status_code == 200:
                log.info("L'usager a été créé avec succès")
            else:
                outcome = OperationOutcome(json.loads(create_response.content))
                log.error("La création de l'usager a eu des problèmes: {}".format(json.dumps(outcome.as_json())))
        elif match_response.status_code == 200:
            # TODO supporter la modification de l'usager
            log.warn("L'usager n'a pas pu être créé car il existe déjà")
        else:
            outcome = OperationOutcome(json.loads(match_response.content))
            log.error("L'appariement de l'usager a eu des problèmes: {}".format(json.dumps(outcome.as_json())))
    
    # TODO supporter la modification de l'acte vaccinal s'il existe (faire un appariement)
    def __charger_actes_vaccinaux(self, acte_vaccinal: ActeVaccinal):
        immunization = self.__convertisseur_acte_vaccinal.toFhir(acte_vaccinal)
        response = self.__immunization_client.create(immunization)
        if response.status_code == 201:
            log.info("L'acte vaccinal a été créé avec succès")
        else:
            outcome = OperationOutcome(json.loads(response.content))
            log.error("La création de l'acte vaccinal n'a pas fonctionné: {}".format(json.dumps(outcome.as_json())))
        
