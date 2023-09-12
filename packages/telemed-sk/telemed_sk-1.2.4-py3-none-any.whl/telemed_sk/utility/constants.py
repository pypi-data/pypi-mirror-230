from __future__ import annotations
from typing import Dict

code_to_region_name: Dict[int, str] = {
                 30: 'Lombardia',190: 'Sicilia',50: 'Veneto',80: 'Emilia-Romagna',120: 'Lazio',200: 'Sardegna',
                 150: 'Campania',10: 'Piemonte',42: 'Trento',70: 'Liguria',130: 'Abruzzo',100: 'Umbria',
                 180: 'Calabria',160: 'Puglia',110: 'Marche',90: 'Toscana',20: "Valle D Aosta",170: 'Basilicata',
                 60: 'Friuli-Venezia-Giulia',41: 'Bolzano',140: 'Molise'}


code_to_speciality: Dict[int, str] = {2: 'Cardiologia',
 3: 'Chirurgia Generale',
 13: 'Nefrologia',
 15: 'Neurologia',
 19: 'Ortopedia E Traumatologia',
 20: 'Ostetricia E Ginecologia',
 21: 'Otorinolaringoiatria',
 23: 'Psichiatria',
 12: 'Recupero E Riabilitazione',
 25: 'Urologia',
 18: 'Oncologia',
 16: 'Oculistica',
 5: 'Chirurgia Vascolare',
 27: 'Dermatologia',
 22: 'Pneumologia',
 10: 'Gastroenterologia',
 9: 'Endocrinologia'}


code_to_tipologia_medico: Dict[str, str] = {"F" : "MMG",
    "P" : "PLS",
    "H" : "Ospedaliero",
    "A" : "Specialista ambulatoriale (ex SUMAI)",
    "G" : "Guardia medica",
    "T" : "Guardia medica turistica",
    "C" : "Specialista di struttura privata accreditata",
    "U" : "Medico di azienda ospedaliero-universitaria",
    "D" : "Dipendente dei servizi territoriali ASL",
    "I" : "Medico INAIL",
    "Z" : "Specializzazione non compresa tra le precedenti",
    "X" : "Altro (tirocinanti, specializzandi, etc.)"}
