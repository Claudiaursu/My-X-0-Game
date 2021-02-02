import time
import copy
import numpy as np
import pygame
import sys
import statistics

DIM_CELULA = 100
ADANCIME_MAX = 6
TIMPI_CALCULATOR = []  # lista cu toti timpii de gandire al calculatorului
NR_NODURI = []  # lista cu nr de noduri generate pentru fiecare mutare

#functie care returneaza toate diagonalele cu lungime >= 4
def diagonale(matr):
    matrice = np.array(matr)
    diags = [matrice[::-1, :].diagonal(i) for i in range(-matrice.shape[0] + 1, matrice.shape[1])]
    diags.extend(matrice.diagonal(i) for i in range(matrice.shape[1] - 1, -matrice.shape[0], -1))
    for diag in diags:
        diag = diag.tolist()
    return diags

def elem_identice(lista):
    if (len(set(lista)) == 1):
        castigator = lista[0]
        if castigator != Joc.GOL:
            return castigator
    return False

def grupari_linie_punctaj(lista, jucator):
    nrGrupari = 0
    i = 0
    adversar = '0' if jucator == 'x' else 'x'
    lista = lista.tolist()
    while i < len(lista) - 2:
        if lista[i] == jucator:
            comp = lista[i]
            if lista[i+1] == comp and lista[i+2] == comp:
                nrGrupari += 10
            if lista[i+1] == comp and lista[i+2] != comp:
                nrGrupari += 3
            i = i + 3
        else:
            i += 1
    return nrGrupari

# returneaza daca in lista primita e o grupare succesiva de 2 sau de 3 (returneaza cate grupari sunt)
def cate_grupari_linie(lista, jucator):
    nrGrupari = 0
    i = 0
    adversar = '0' if jucator == 'x' else 'x'
    lista = lista.tolist()
    while i < len(lista) - 2:
        if lista[i] == jucator:
            comp = lista[i]
            if lista[i + 1] == comp and lista[i + 2] == comp:
                nrGrupari += 1
            if lista[i + 1] == comp and lista[i + 2] != comp:
                nrGrupari += 1
            i = i + 3
        else:
            i += 1
    return nrGrupari

def cate_grupari_linie_optimizat(lista, jucator):
    nrGrupari = 0
    are_spatii = []  # pt fiecare grupare de 2 sau 3 simboluri retinem 0 daca e blocata sau 1 daca are spatii
                     #  0xx0 -> aici xx e blocat de 0-uri
                     #  0xx  -> aici nu e blocat, mai poate continua in dreapta

    i = 0
    adversar = '0' if jucator == 'x' else 'x'
    lista = lista.tolist()
    while i < len(lista) - 2:
        if lista[i] == jucator:
            comp = lista[i]
            if lista[i + 1] == comp and lista[i + 2] == comp:
                nrGrupari += 1
                are_spatii.append(are_spatiu(i, i+2, lista))
            if lista[i + 1] == comp and lista[i + 2] != comp:
                nrGrupari += 1
                are_spatii.append(are_spatiu(i, i+1, lista))
            i = i + 3
        else:
            i += 1
    return nrGrupari, are_spatii

# se returneaza 1 daca sunt destule spatii in stg/dreapta pentru a se forma combinatie de 4
def are_spatiu(start, end, lista):
    if start - 1 > 0 and lista[start - 1] != Joc.GOL and end + 1 < len(lista) and lista[end + 1] != Joc.GOL:
        return 0
    if start == 0 and end + 1 < len(lista) and lista[end + 1] != Joc.GOL:
        return 0
    if end == len(lista) - 1 and start - 1 > 0 and lista[start - 1] != Joc.GOL:
        return 0
    else:
        mai_trebuie = 4 - (abs(end - start) + 1)
        if mai_trebuie == 2:
            # 2 spatii goale in stanga indicilor
            if start - 1 > 0 and lista[start - 1] == '#' and start - 2 > 0 and lista[start - 2] == '#':
                return 1
            # 2 spatii goale in dreapta indicilor
            if end + 1 < len(lista) and lista[end + 1] == '#' and end + 2 < len(lista) and lista[end + 2] == '#':
                return 1
            # 1 spatiu in stanga si unul in dreapta
            if start - 1 > 0 and lista[start - 1] == '#' and end + 1 < len(lista) and lista[end + 1] == '#':
                return 1
            else:
                return 0
        else:
            # 1 spatiu in stanga indicilor
            if start - 1 > 0 and lista[start - 1] == '#':
                return 1
            # 1 spatiu in dreapta indicilor
            if end + 1 < len(lista) and lista[end + 1] == '#':
                return 1
            else:
                return 0


def are_rezultat(lista):
    for i in range(len(lista) - 3):
        if lista[i] != Joc.GOL:
            are = True
            comp = lista[i]
            for j in range(i, i + 4):
                if lista[j] != comp:
                    are = False
                    break
                if j == i + 3 and are is True:
                    return lista[j]
    return False


def deseneaza_grid(display, tabla, marcaj=()):  # tabla de exemplu este ["#","x","#","0",......]
    w_gr = h_gr = 100  # width-ul si height-ul unei celule din grid

    x_img = pygame.image.load('ics.png')
    x_img = pygame.transform.scale(x_img, (w_gr, h_gr))
    zero_img = pygame.image.load('zero.png')
    zero_img = pygame.transform.scale(zero_img, (w_gr, h_gr))
    drt = []  # este lista de liste cu patratelele din grid
    for i in range(Joc.NR_LINII):
        linie_patratele = []
        for j in range(Joc.NR_COLOANE):
            patrat = pygame.Rect(j*(w_gr + 1), i*(h_gr + 1), w_gr, h_gr)
            # print(str(coloana*(w_gr+1)), str(linie*(h_gr+1)))
            linie_patratele.append(patrat)
            if len(marcaj) != 0 and marcaj[0] == i and marcaj[1] == j:
                # daca am o patratica selectata, o desenez cu rosu
                culoare = (255, 0, 0)
            else:
                # altfel o desenez cu alb
                culoare = (255, 255, 255)
            pygame.draw.rect(display, culoare, patrat)  # alb = (255,255,255)
            if tabla[i][j] == 'x':
                display.blit(x_img, (j * (w_gr + 1), i * (h_gr + 1)))
            elif tabla[i][j] == '0':
                display.blit(zero_img, (j * (w_gr + 1), i * (h_gr + 1)))
        drt.append(linie_patratele)
    pygame.display.flip()
    return drt


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """
    NR_COLOANE = 10
    NR_LINII = 10
    JMIN = None
    JMAX = None
    GOL = '#'

    def __init__(self, tabla=None):  # Joc()
        if tabla is not None:
            self.matr = tabla
        else:
            self.matr = []
            for i in range(self.NR_LINII):
                self.matr.append([Joc.GOL] * Joc.NR_COLOANE)

    @classmethod
    def jucator_opus(cls, jucator):
        if jucator == cls.JMIN:
            return cls.JMAX
        else:
            return cls.JMIN

    # TO DO 5
    def final(self):
        matrice = np.array(self.matr)
        diags = diagonale(self.matr)
        for diag in diags:
            if len(diag) < 4:
                continue
            rez = are_rezultat(diag)
            if rez:
                return rez
            else:
                continue

        for i in range(self.NR_LINII):
            rez = are_rezultat(self.matr[i])
            if rez:
                return rez

        for j in range(self.NR_COLOANE):
            rez = are_rezultat(matrice[:, j])
            if rez:
                return rez

        remiza = True
        for i in range(self.NR_LINII):
            for j in range(self.NR_COLOANE):
                if self.matr[i][j] == Joc.GOL:
                    remiza = False
        if remiza:
            return 'remiza'
        else:
            return False

    #verifica daca pe tabla de joc se poate pozitiona un pion al juc_curent la linia/col specificata
    def verificaPozitieJ(self, linie, col, juc_curent):
        veciniAdversar = 0
        veciniJucCurent = 0
        if juc_curent == 'x':
            adversar = '0'
        else:
            adversar = 'x'
        # verificare veicn de jos
        if linie + 1 < self.NR_LINII and self.matr[linie + 1][col] != Joc.GOL:
            if self.matr[linie + 1][col] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1
        # verificare vecin de sus
        if linie - 1 >= 0 and self.matr[linie - 1][col] != Joc.GOL:
            if self.matr[linie - 1][col] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1
        # verificare vecin de la dreapta
        if col + 1 < self.NR_COLOANE and self.matr[linie][col + 1] != Joc.GOL:
            if self.matr[linie][col + 1] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1
        # verificare vecin de la stanga
        if col - 1 >= 0 and self.matr[linie][col - 1] != Joc.GOL:
            if self.matr[linie][col - 1] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1

        if veciniAdversar > veciniJucCurent:
            return False
        if veciniJucCurent == 0 and veciniAdversar == 0:
            return True
        else:
            return True

    # se genereaza m=toate mutarile posibile pe tabla de joc cand muta jucatorul dat ca parametru
    def mutari(self, jucator):  # jucator = simbolul jucatorului care muta
        l_mutari = []
        for i in range(self.NR_LINII):
            for j in range(self.NR_COLOANE):
                # generare mutari pion nou:
                if self.matr[i][j] == Joc.GOL and self.verificaPozitieJ(i, j, jucator):
                    copie_matr = copy.deepcopy(self.matr)
                    copie_matr[i][j] = jucator
                    l_mutari.append(Joc(copie_matr))
                #generare mutari din mutarea unui pion existent
                if self.matr[i][j] == jucator:
                    if i + 1 < self.NR_LINII and self.matr[i + 1][j] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i+1][j] = jucator
                        l_mutari.append(Joc(copie_matr))
                    if i - 1 >= 0 and self.matr[i - 1][j] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i - 1][j] = jucator
                        l_mutari.append(Joc(copie_matr))
                    if j + 1 < self.NR_COLOANE and self.matr[i][j + 1] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i][j + 1] = jucator
                        l_mutari.append(Joc(copie_matr))
                    if j - 1 >= 0 and self.matr[i][j - 1] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i][j - 1] = jucator
                        l_mutari.append(Joc(copie_matr))
                    if i - 1 >= 0 and j - 1 >= 0 and self.matr[i - 1][j - 1] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i - 1][j - 1] = jucator
                        l_mutari.append(Joc(copie_matr))
                    if i - 1 >= 0 and j + 1 < self.NR_COLOANE and self.matr[i - 1][j + 1] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i - 1][j + 1] = jucator
                        l_mutari.append(Joc(copie_matr))
                    if i + 1 < self.NR_LINII and j + 1 < self.NR_COLOANE and self.matr[i + 1][j + 1] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i + 1][j + 1] = jucator
                        l_mutari.append(Joc(copie_matr))
                    if i + 1 < self.NR_LINII and j - 1 >= 0 and self.matr[i + 1][j - 1] == Joc.GOL:
                        copie_matr = copy.deepcopy(self.matr)
                        copie_matr[i + 1][j - 1] = jucator
                        l_mutari.append(Joc(copie_matr))

        return l_mutari

    # verifica daca acest punct este izolat, nu are absolut niciun vecin(indiferent de tip)
    def izolat(self, linie, col):
        if linie - 1 >= 0 and self.matr[linie - 1][col] != Joc.GOL:
            return False
        if linie + 1 < self.NR_LINII and self.matr[linie + 1][col] != Joc.GOL:
            return False
        if col + 1 < self.NR_COLOANE and self.matr[linie][col + 1] != Joc.GOL:
            return False
        if col - 1 >= 0 and self.matr[linie][col - 1] != Joc.GOL:
            return False
        if col - 1 >= 0 and linie + 1 < self.NR_LINII and self.matr[linie + 1][col - 1] != Joc.GOL:
            return False
        if col + 1 < self.NR_COLOANE and linie - 1 >= 0 and self.matr[linie - 1][col + 1] != Joc.GOL:
            return False
        if col + 1 < self.NR_COLOANE and linie + 1 < self.NR_LINII and self.matr[linie + 1][col + 1] != Joc.GOL:
            return False
        if col - 1 >= 0 and linie - 1 >= 0 and self.matr[linie - 1][col - 1] != Joc.GOL:
            return False
        return True

    # aceasta functie verifica daca un simbol nu mai are alti vecini de acelasi tip (deci este singur)
    # obs: el poate avea vecini adversari
    def simbol_izolat(self, linie, col, jucator):
        if linie - 1 >= 0 and self.matr[linie - 1][col] == jucator:
            return False
        if linie + 1 < self.NR_LINII and self.matr[linie + 1][col] == jucator:
            return False
        if col + 1 < self.NR_COLOANE and self.matr[linie][col + 1] == jucator:
            return False
        if col - 1 >= 0 and self.matr[linie][col - 1] == jucator:
            return False
        if col - 1 >= 0 and linie + 1 < self.NR_LINII and self.matr[linie + 1][col - 1] == jucator:
            return False
        if col + 1 < self.NR_COLOANE and linie - 1 >= 0 and self.matr[linie - 1][col + 1] == jucator:
            return False
        if col + 1 < self.NR_COLOANE and linie + 1 < self.NR_LINII and self.matr[linie + 1][col + 1] == jucator:
            return False
        if col - 1 >= 0 and linie - 1 >= 0 and self.matr[linie - 1][col - 1] == jucator:
            return False
        return True

    # functie care returneaza true daca pionul de la pozitia indicata are toti vecinii ocupati
    def totiVeciniiOcupati(self, linie, coloana):
        if linie - 1 >= 0 and self.matr[linie - 1][coloana] == Joc.GOL:
            return False
        if linie + 1 < self.NR_LINII and self.matr[linie + 1][coloana] == Joc.GOL:
            return False
        if coloana + 1 < self.NR_COLOANE and self.matr[linie][coloana + 1] == Joc.GOL:
            return False
        if coloana - 1 >= 0 and self.matr[linie][coloana - 1] == Joc.GOL:
            return False
        if coloana - 1 >= 0 and linie + 1 < self.NR_LINII and self.matr[linie + 1][coloana - 1] == Joc.GOL:
            return False
        if coloana + 1 < self.NR_COLOANE and linie - 1 >= 0 and self.matr[linie - 1][coloana + 1] == Joc.GOL:
            return False
        if coloana + 1 < self.NR_COLOANE and linie + 1 < self.NR_LINII and self.matr[linie + 1][coloana + 1] == Joc.GOL:
            return False
        if coloana - 1 >= 0 and linie - 1 >= 0 and self.matr[linie - 1][coloana - 1] == Joc.GOL:
            return False
        return True

    def nr_grupari(self, jucator):
        estimare = 0
        #copie = copy.deepcopy(self.matr)
        array_copie = np.array(self.matr)  #pentru a putea folosi [:,]
        #adversar = '0' if jucator == 'x' else 'x'
        if jucator == 'x':
            adversar = '0'
        else:
            adversar = 'x'

        # pentru gruparile de 2 si 3 din coloane
        for j in range(self.NR_COLOANE):
            estimare += grupari_linie_punctaj(array_copie[:, j], jucator)

        # pentru gruparile de 2 si 3 din linii
        for i in range(self.NR_LINII):
            estimare += grupari_linie_punctaj(array_copie[i], jucator)
        #acordam prioritate pionilor care nu se afla pe liniile/col marginale si care blocheaza adversarul
        for i in range(1, self.NR_LINII - 1):
            for j in range(1, self.NR_COLOANE - 1):
                if array_copie[i][j] == adversar:
                    if self.izolat(i, j):
                        #print("AICI e ", adversar, "izolat, la ", i, j)
                        if i + 2 < self.NR_LINII and i + 2 != self.NR_LINII - 1 and array_copie[i + 2][j] == jucator:
                            estimare += 2
                            array_copie[i + 2][j] = 'f'
                        if i - 2 > 0 and array_copie[i - 2][j] == jucator:
                            estimare += 2
                            array_copie[i - 2][j] = 'f'
                        if j + 2 < self.NR_COLOANE and j + 2 != self.NR_COLOANE - 1 and array_copie[i][j + 2] == jucator:
                            estimare += 2
                            array_copie[i][j + 2] = 'f'
                        if j - 2 > 0 and array_copie[i][j - 2] == jucator:
                            estimare += 2
                            array_copie[i][j - 2] = 'f'
                if array_copie[i][j] == jucator:
                    estimare += 1

        # pentru gruparile de 2 si 3 din diagonale
        diags = diagonale(self.matr)
        for diag in diags:
            if len(diag) < 4:
                continue
            estimare += grupari_linie_punctaj(diag, jucator)

        return estimare


    def estimeaza_scor(self, adancime):
        t_final = self.final()
        if t_final == self.__class__.JMAX:  # self.__class__ referinta catre clasa instantei
            return (100000 + adancime)
        elif t_final == self.__class__.JMIN:
            return (-100000 - adancime)
        elif t_final == 'remiza':
            return 0
        else:
            return (self.nr_grupari(self.__class__.JMAX) - self.nr_grupari(self.__class__.JMIN))  # aici facem diferenta intre punctajele fiecarui jucator

    def estimeaza_scor2(self, adancime):
        t_final = self.final()
        if t_final == self.__class__.JMAX:  # self.__class__ referinta catre clasa instantei
            return (100000 + adancime)
        elif t_final == self.__class__.JMIN:
            return (-100000 - adancime)
        elif t_final == 'remiza':
            return 0
        else:
            return (self.nr_grupari_relativ(self.__class__.JMAX) - self.nr_grupari_relativ(self.__class__.JMIN))

    # numarul de grupari in raport cu numarul de pioni de acelasi tipul 'jucator' de pe tabla
    # unde o grupare poate fi o reprezentata de 1, 2 sau 3 simboluri alaturate pe linie/col/diag
    def nr_grupari_relativ(self, jucator):
        array_copie = np.array(self.matr)  # pentru a putea folosi [:,]
        total_pioni_jucator = 0
        au_spatii = []  # pentru fiecare grupare avem 0 daca e blocata si 1 daca are spatii
        nr_grupari = 0
        if jucator == 'x':
            adversar = '0'
        else:
            adversar = 'x'

        for i in range(self.NR_LINII):
            for j in range(self.NR_COLOANE):
                if self.matr[i][j] == jucator:
                    total_pioni_jucator += 1

        # pentru gruparile de 2 si 3 din coloane
        for j in range(self.NR_COLOANE):
            nrGrup, spatii = cate_grupari_linie_optimizat(array_copie[:, j], jucator)
            nr_grupari += nrGrup
            au_spatii.extend(spatii)

        # pentru gruparile de 2 si 3 din linii
        for i in range(self.NR_LINII):
            nrGrup, spatii = cate_grupari_linie_optimizat(array_copie[i], jucator)
            nr_grupari += nrGrup
            au_spatii.extend(spatii)

        # pentru gruparile de 2 si 3 din diagonale
        diags = diagonale(self.matr)
        for diag in diags:
            if len(diag) < 2:
                continue
            nrGrup, spatii = cate_grupari_linie_optimizat(diag, jucator)
            nr_grupari += nrGrup
            au_spatii.extend(spatii)

        # cautam gruparile 'izolate' (de cate un simbol)
        for i in range(self.NR_LINII):
            for j in range(self.NR_COLOANE):
                if self.matr[i][j] == jucator and self.simbol_izolat(i, j, jucator):
                    #print("E izolat punctul ", jucator, " la ", i,j)
                    nr_grupari += 1

        if nr_grupari != 0 and total_pioni_jucator != 0:
            sumaa = sum(au_spatii)
            estim = (total_pioni_jucator / nr_grupari) + sumaa
            return estim
        else:
            estimare = 0
            # acordam prioritate pionilor care nu se afla pe liniile/col marginale si care blocheaza adversarul
            for i in range(1, self.NR_LINII - 1):
                for j in range(1, self.NR_COLOANE - 1):
                    if array_copie[i][j] == adversar:
                        if self.izolat(i, j):
                            # print("AICI e ", adversar, "izolat, la ", i, j)
                            if i + 2 < self.NR_LINII and i + 2 != self.NR_LINII - 1 and array_copie[i + 2][j] == jucator:
                                estimare += 2
                                array_copie[i + 2][j] = 'f'
                            if i - 2 > 0 and array_copie[i - 2][j] == jucator:
                                estimare += 2
                                array_copie[i - 2][j] = 'f'
                            if j + 2 < self.NR_COLOANE and j + 2 != self.NR_COLOANE - 1 and array_copie[i][j + 2] == jucator:
                                estimare += 2
                                array_copie[i][j + 2] = 'f'
                            if j - 2 > 0 and array_copie[i][j - 2] == jucator:
                                estimare += 2
                                array_copie[i][j - 2] = 'f'
                    if array_copie[i][j] == jucator:
                        estimare += 1

            return estimare

    def __str__(self):
        sir = "  |"
        for i in range(self.NR_COLOANE):
            sir += str(i) + " "
        sir += "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        for i in range(self.NR_LINII):  # itereaza prin linii
            sir += str(i) + " |" + " ".join(str(x) for x in self.matr[i]) + "\n"
        # [0,1,2,3,4,5,6,7,8]
        return sir


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    O instanta din clasa stare este un nod din arborele minimax
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    # TO DO 2
    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, estimare=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # estimarea favorabilitatii starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.estimare = estimare

        # lista de mutari posibile (tot de tip Stare) din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        # e de tip Stare (cel mai bun succesor)
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)  # lista de informatii din nodurile succesoare
        juc_opus = Joc.jucator_opus(self.j_curent)

        # mai jos calculam lista de noduri-fii (succesori)
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

    #versiunea mai buna de verificaPozitie care apeleaza verificaPozitieJ din clasa Joc
    def verificaPozitie_J(self, linie, col):
        return self.tabla_joc.verificaPozitieJ(linie, col, self.j_curent)

    def verificaPozitie(self, linie, col):
        veciniAdversar = 0
        veciniJucCurent = 0
        if self.j_curent == 'x':
            adversar = '0'
        else:
            adversar = 'x'
        # verificare vecin de jos
        if linie + 1 < self.tabla_joc.NR_LINII and self.tabla_joc.matr[linie + 1][col] != Joc.GOL:
            if self.tabla_joc.matr[linie + 1][col] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1
        # verificare vecin de sus
        if linie - 1 >= 0 and self.tabla_joc.matr[linie - 1][col] != Joc.GOL:
            if self.tabla_joc.matr[linie - 1][col] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1
        # verificare vecin de la dreapta
        if col + 1 < self.tabla_joc.NR_COLOANE and self.tabla_joc.matr[linie][col + 1] != Joc.GOL:
            if self.tabla_joc.matr[linie][col + 1] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1
        # verificare vecin de la stanga
        if col - 1 >= 0 and self.tabla_joc.matr[linie][col - 1] != Joc.GOL:
            if self.tabla_joc.matr[linie][col - 1] == adversar:
                veciniAdversar += 1
            else:
                veciniJucCurent += 1

        if veciniAdversar > veciniJucCurent:
            return False
        if veciniJucCurent == 0 and veciniAdversar == 0:
            return True
        else:
            return True


    def verificaPozitieMutare(self, linieNoua, coloanaNoua, linieVeche, coloanaVeche):
        #verificare daca e o pozitie vecina pe linie/coloana/diagonala
        # scadere = (linieVeche + coloanaVeche) - (linieNoua + coloanaNoua)
        # if abs(scadere) in [0, 1, 2] and self.tabla_joc.matr[linieNoua][coloanaNoua] == Joc.GOL:
        #     return True
        # else:
        #     return False

        if self.tabla_joc.matr[linieNoua][coloanaNoua] == Joc.GOL and abs(linieNoua - linieVeche) == 1 and coloanaNoua == coloanaVeche:
            return True
        elif self.tabla_joc.matr[linieNoua][coloanaNoua] == Joc.GOL and abs(coloanaNoua - coloanaVeche) == 1 and linieVeche == linieNoua:
            return True
        elif self.tabla_joc.matr[linieNoua][coloanaNoua] == Joc.GOL and abs(coloanaNoua - coloanaVeche) == 1 and abs(linieNoua - linieVeche) == 1:
            return True
        else:
            return False


    # verifica daca piesa de la pozitia specificata se poate muta de acolo (nu e inconjurata))
    def ePosibilaMutarea(self, linieVeche, coloanaVeche):
        nrVeciniOcupati = 0
        nrVeciniValizi = 0
        if linieVeche + 1 < self.tabla_joc.NR_LINII:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche + 1][coloanaVeche] != Joc.GOL:
                nrVeciniOcupati += 1
        if linieVeche - 1 >= 0:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche - 1][coloanaVeche] != Joc.GOL:
                nrVeciniOcupati += 1
        if coloanaVeche + 1 < self.tabla_joc.NR_COLOANE:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche][coloanaVeche + 1] != Joc.GOL:
                nrVeciniOcupati += 1
        if coloanaVeche - 1 >= 0:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche][coloanaVeche - 1] != Joc.GOL:
                nrVeciniOcupati += 1
        if linieVeche - 1 >= 0 and coloanaVeche - 1 >= 0:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche - 1][coloanaVeche - 1] != Joc.GOL:
                nrVeciniOcupati += 1
        if linieVeche - 1 >= 0 and coloanaVeche + 1 < self.tabla_joc.NR_COLOANE:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche - 1][coloanaVeche + 1] != Joc.GOL:
                nrVeciniOcupati += 1
        if linieVeche + 1 < self.tabla_joc.NR_LINII  and coloanaVeche + 1 < self.tabla_joc.NR_COLOANE:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche + 1][coloanaVeche + 1] != Joc.GOL:
                nrVeciniOcupati += 1
        if linieVeche + 1 < self.tabla_joc.NR_LINII and coloanaVeche - 1 >= 0:
            nrVeciniValizi += 1
            if self.tabla_joc.matr[linieVeche + 1][coloanaVeche - 1] != Joc.GOL:
                nrVeciniOcupati += 1
        if nrVeciniValizi == nrVeciniOcupati:
            return False
        else:
            return True

    def jucator_opus(self):
        if self.j_curent == Joc.JMIN:
            return Joc.JMAX
        else:
            return Joc.JMIN

    def __str__(self):
        sir = str(self.tabla_joc) + "(Joc curent:" + self.j_curent + ")\n"
        return sir


""" Algoritmul MinMax """


def min_max(stare, nrTotalNoduri):
    # daca sunt la o frunza in arborele minimax sau la o stare finala
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        NR_NODURI.append(nrTotalNoduri)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()
    nrTotalNoduri += len(stare.mutari_posibile)

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutariCuEstimare = [min_max(x, nrTotalNoduri) for x in stare.mutari_posibile]  # expandez(constr subarb) fiecare nod x din mutari posibile

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu estimarea maxima
        stare.stare_aleasa = max(mutariCuEstimare, key=lambda x: x.estimare)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu estimarea minima
        stare.stare_aleasa = min(mutariCuEstimare, key=lambda x: x.estimare)

    stare.estimare = stare.stare_aleasa.estimare
    return stare


def alpha_beta(alpha, beta, stare, nrTotalNoduri):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor2(stare.adancime)
        NR_NODURI.append(nrTotalNoduri)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()
    nrTotalNoduri += len(stare.mutari_posibile)

    print("Nr de noduri generate pentru alegerea acestei mutari: ", len(stare.mutari_posibile))

    if stare.j_curent == Joc.JMAX:
        estimare_curenta = float('-inf')

        for mutare in stare.mutari_posibile:
            # calculeaza estimarea pentru starea noua, realizand subarborele
            stare_noua = alpha_beta(alpha, beta, mutare, nrTotalNoduri)  # aici construim subarborele pentru stare_noua

            if (estimare_curenta < stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if (alpha < stare_noua.estimare):
                alpha = stare_noua.estimare
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        estimare_curenta = float('inf')
        # completati cu rationament similar pe cazul stare.j_curent==Joc.JMAX
        for mutare in stare.mutari_posibile:
            # calculeaza estimarea
            stare_noua = alpha_beta(alpha, beta, mutare, nrTotalNoduri)  # aici construim subarborele pentru stare_noua

            if (estimare_curenta > stare_noua.estimare):
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if (beta > stare_noua.estimare):
                beta = stare_noua.estimare
                if alpha >= beta:
                    break

    stare.estimare = stare.stare_aleasa.estimare

    return stare


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()  # metoda final() returneaza "remiza" sau castigatorul ("x" sau "0") sau False daca nu e stare finala
    if final:
        if final == "remiza":
            print("Remiza!")
        else:
            print("A castigat " + final)

        print("Timpul minim de gandire al calculatorului: ", min(TIMPI_CALCULATOR))
        print("Timpul maxim de gandire al calculatorului: ", max(TIMPI_CALCULATOR))
        print("Media timpilor calculatorului: ", sum(TIMPI_CALCULATOR) / len(TIMPI_CALCULATOR))
        print("Mediana timpilor calculatorului: ", statistics.median(TIMPI_CALCULATOR))

        print("Nr minim de noduri generate pt o mutare (din totalul situatiilor): ", min(NR_NODURI))
        print("Nr maxim de noduri generate pt o mutare (din totalul situatiilor): ", max(NR_NODURI))
        print("Media nr de noduri generate (din totalul situatiilor): ", sum(NR_NODURI) / len(NR_NODURI))
        print("Mediana nr de noduri generate (din totalul situatiilor): ", statistics.median(NR_NODURI))
        return True

    return False


def main():
    # initializare algoritm
    raspuns_valid = False
    MUTARI_CALC = 0  # nr de mutari calc
    MUTARI_JUC = 0  # nr de mutari juc

    while not raspuns_valid:
        try:
            tip_algoritm = int(input("Algoritmul folosit? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-beta\n "))
            if tip_algoritm in [1, 2]:
                raspuns_valid = True
            else:
                print("Nu ati ales o varianta corecta.")
        except ValueError:
            print("Nr introdus trebuie sa fie numar intreg")

    raspuns_valid = False
    while not raspuns_valid:
        try:
            nrLinii = int(input("Cate linii sa aiba tabla de joc?"))
            nrColoane = int(input("Cate coloane sa aiba tabla de joc?"))
            if nrLinii <= 10 and nrLinii >= 5 and nrColoane <= 10 and nrColoane >= 5:
                raspuns_valid = True
                Joc.NR_LINII = nrLinii
                Joc.NR_COLOANE = nrColoane
            else:
                print("Nu ati ales o varianta corecta. Numerele trebuie sa fie in intervalul [5,10]")
        except ValueError:
            print("Trebuie sa introduceti numere intregi!")

    raspuns_valid = False
    while not raspuns_valid:
        try:
            nivel = int(input("Alegeti nivelul de dificultate:\n1= incepator\n2= mediu\n3= avansat\n"))
            if nivel in [1, 2, 3]:
                raspuns_valid = True
                ADANCIME_MAX = nivel
            else:
                print("Nu ati ales o varianta corecta. Numerele trebuie sa fie in intervalul [5,10]")
        except ValueError:
            print("Trebuie sa introduceti numere intregi!")

    # initializare jucatori
    raspuns_valid = False
    while not raspuns_valid:
        Joc.JMIN = input("Doriti sa jucati cu x sau cu 0? ").lower()
        if (Joc.JMIN in ['x', '0']):
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie x sau 0.")
    Joc.JMAX = '0' if Joc.JMIN == 'x' else 'x'
    # expresie= val_true if conditie else val_false  (conditie? val_true: val_false)

    # initializare tabla
    tabla_curenta = Joc();  # apelam constructorul
    print("Tabla initiala")
    print(str(tabla_curenta))

    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, 'x', ADANCIME_MAX)

    # setari interf grafica
    pygame.init()
    pygame.display.set_caption('x si 0 personalizat')
    # dimensiunea ferestrei in pixeli
    ecran = pygame.display.set_mode(size=(Joc.NR_COLOANE*DIM_CELULA + Joc.NR_COLOANE - 1, Joc.NR_LINII*DIM_CELULA + Joc.NR_LINII - 1))
    # pentru ecran: N *100+ N-1

    de_mutat = False
    patratele = deseneaza_grid(ecran, tabla_curenta.matr)
    start_joc = int(round(time.time() * 1000))

    while True:
        if (stare_curenta.j_curent == Joc.JMIN):
            # muta jucatorul

            print("Acum muta utilizatorul cu simbolul", stare_curenta.j_curent)
            raspuns_valid = False
            '''
            tip mutare poate fi 0 sau 1
                       1 -> adaugare pion nou
                       2 -> mutare pion existent
            '''
            mai_exita_mutari = False
            for i in range(Joc.NR_LINII):
                for j in range(Joc.NR_COLOANE):
                    # verificam daca s-ar putea pozitiona un pion aici, in acest loc gol
                    if stare_curenta.tabla_joc.matr[i][j] == Joc.GOL and stare_curenta.verificaPozitie(i, j):
                        mai_exita_mutari = True
                        break
                    # daca gasim un pion de al utilizatorului care nu are toti vecinii ocupati
                    elif stare_curenta.tabla_joc.matr[i][j] == Joc.JMIN and not stare_curenta.tabla_joc.totiVeciniiOcupati(i, j):
                        mai_exita_mutari = True
                        break

            if mai_exita_mutari:

                t_inainte = int(round(time.time() * 1000))
                while not raspuns_valid:
                    for event in pygame.event.get(): # luam cate un eveniment nou din coada de evenim
                        if event.type == pygame.QUIT:
                            pygame.quit() #inchidere fereastra
                            sys.exit() #inchidere program
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()  # coordonatele clickului

                            for i in range(Joc.NR_LINII):
                                for j in range(Joc.NR_COLOANE):
                                    if patratele[i][j].collidepoint(pos):
                                        #daca se vrea o mutare a unui pion
                                        if stare_curenta.tabla_joc.matr[i][j] == Joc.JMIN:
                                            if (de_mutat and i == de_mutat[0] and j == de_mutat[1]):
                                                # daca am facut click chiar pe patratica selectata, o deselectez
                                                de_mutat = False
                                                deseneaza_grid(ecran, stare_curenta.tabla_joc.matr)
                                            else:
                                                if stare_curenta.ePosibilaMutarea(i, j):
                                                    de_mutat = (i, j)
                                                    # desenez gridul cu patratelul marcat
                                                    deseneaza_grid(ecran, stare_curenta.tabla_joc.matr, de_mutat)
                                                else:
                                                    print("Nu se poate muta aceasta piesa!")

                                        # daca se vrea punerea unui pion intr-o caseta goala
                                        if stare_curenta.tabla_joc.matr[i][j] == Joc.GOL:
                                            if de_mutat:  # daca tocmai urmeaza sa se aseze un pion mutat
                                                #test legat de mutarea simbolului
                                                if stare_curenta.verificaPozitieMutare(i, j, de_mutat[0], de_mutat[1]):
                                                    stare_curenta.tabla_joc.matr[de_mutat[0]][de_mutat[1]] = Joc.GOL
                                                    de_mutat = False
                                                    print("Mutare corecta")
                                                    stare_curenta.tabla_joc.matr[i][j] = Joc.JMIN
                                                    raspuns_valid = True
                                                else:
                                                    print("Nu se poate muta aici!")

                                            # dupa iesirea din while sigur am valide atat linia cat si coloana
                                            # deci pot plasa simbolul pe "tabla de joc"
                                            else:
                                                if stare_curenta.verificaPozitie(i, j):
                                                    stare_curenta.tabla_joc.matr[i][j] = Joc.JMIN
                                                    raspuns_valid = True
                                                else:
                                                    print("Nu se poate pozitiona aici un pion!")

                                            # afisarea starii jocului in urma mutarii utilizatorului
                                            print("Tabla dupa mutarea jucatorului")
                                            print("Jucatorul a facut o mutare cu estimarea: ", stare_curenta.tabla_joc.nr_grupari(Joc.JMIN))
                                            print(str(stare_curenta))

                                            if raspuns_valid:
                                                patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr)
                                                t_dupa = int(round(time.time() * 1000))
                                                print("Jucatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")

                                                # S-a realizat o mutare. Schimb jucatorul cu cel opus si incrementam nr mutari
                                                #stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
                                                stare_curenta.j_curent = stare_curenta.jucator_opus()
                                                MUTARI_JUC += 1
                # testez daca jocul a ajuns intr-o stare finala
                # si afisez un mesaj corespunzator in caz ca da
                if (afis_daca_final(stare_curenta)):
                    final_joc = int(round(time.time() * 1000))
                    print("Durata totala a jocului: ", final_joc - start_joc, "milisecunde")
                    print("Numarul de mutari ale calculatorului: ", MUTARI_CALC)
                    print("NUmarul de mutari ale jucatorului: ", MUTARI_JUC)
                    break
            else:
                # nu exista nicio mutare ramasa posibila pt jucator, asa ca schimbam randul
                stare_curenta.j_curent = stare_curenta.jucator_opus()

        # -------------------------------------------------------
        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator

            print("Acum muta calculatorul cu simbolul", stare_curenta.j_curent)
            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.time() * 1000))

            # stare actualizata e starea mea curenta in care am setat stare_aleasa (mutarea urmatoare)
            if tip_algoritm == 1:
                nrNoduri = 0
                stare_actualizata = min_max(stare_curenta, nrNoduri)
                print("Calculatorul a facut o mutare cu estimarea: ", stare_actualizata.estimare)
                print("Nr de noduri generate pentru alegerea acestei mutari: ", NR_NODURI[MUTARI_CALC])

            else:  # tip_algoritm==2
                nrNoduri = 0
                stare_actualizata = alpha_beta(-1000, 1000, stare_curenta, nrNoduri)
                print("Calculatorul a facut o mutare cu estimarea: ", stare_actualizata.estimare)

            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc  # aici se face de fapt mutarea !!!
            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta))

            patratele = deseneaza_grid(ecran, stare_curenta.tabla_joc.matr)
            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            TIMPI_CALCULATOR.append(t_dupa - t_inainte)
            print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.\n")
            MUTARI_CALC += 1
            if (afis_daca_final(stare_curenta)):
                final_joc = int(round(time.time() * 1000))
                print("Durata totala a jocului: ", final_joc - start_joc, "milisecunde")
                print("Numarul de mutari ale calculatorului: ", MUTARI_CALC)
                print("NUmarul de mutari ale jucatorului: ", MUTARI_JUC)
                break

            # S-a realizat o mutare.  jucatorul cu cel opus
            #stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
            stare_curenta.j_curent = stare_curenta.jucator_opus()


if __name__ == "__main__":
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

