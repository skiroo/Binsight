def calculer_criticite(etat, pluie_mm):
    """
    Criticité sur 4 niveaux :
    0 : normale
    1 : pluie faible OU poubelle pleine
    2 : poubelle pleine + pluie
    3 : pluie forte + poubelle pleine
    """
    if not etat:
        return 0
    if etat == 'clean':
        return 1 if pluie_mm and pluie_mm > 5 else 0
    if etat == 'dirty':
        if pluie_mm and pluie_mm > 10:
            return 3
        elif pluie_mm and pluie_mm > 0:
            return 2
        else:
            return 1
    return 0