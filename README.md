# Maze Madness

Funkciou aplikácie je hra hľadania cesty bludiskom proti ostatným hráčom v lokálnej sieti s
možnosťou chatovania.

## Dependencies

- `pygame`
- `requests`
- `pytest`
- `pylint`
- ```bash
  pip install pygame requests pytest pylint

## Spustenie aplikácie

1. **Spustenie servera**
2. **Spustenie klienta**
    - Server musí bežať v rovnakej lokálnej sieti ako klienti.

## Použitie

Po objavení grafického okna s názvom *Maze Madness* môžete zadať vaše meno. **Meno musí byť:**

- Unikátne
- Kratšie ako 9 písmen

Ak meno nesplní tieto podmienky, budete o tom informovaný. **Nie je potrebné klikať do políčka na
písanie; môžete začať rovno písať.**  
Po stlačení **ENTER** alebo kliknutí na tlačidlo **Connect** sa odošle požiadavok na server a
dostanete sa do **Menu**.

### Funkcie v Menu

- Vaše meno bude zvýraznené zelenou farbou pre jednoduchšiu identifikáciu.
- Číslo pred menom predstavuje skóre (počet vyhratých hier).
- Ihneď po vstupe do **Menu** môžete začať písať a posielať správy ostatným hráčom stlačením 
**ENTER** (tu nie je tlačidlo na odoslanie).

#### Výzva na hru

- Hráča môžete vyzvať na partiu kliknutím na jeho meno v stĺpci **Online Players**.
- Vaša výzva sa mu zobrazí v strednom stĺpci **Challenges**.
- Ak si výzvu rozmyslíte, môžete ju stiahnuť opätovným kliknutím na meno hráča.
- Výzva sa prijme kliknutím na meno vyzývateľa v strednom stĺpci.

### Po prijatí výzvy

- Server vygeneruje bludisko a z **Menu** sa presuniete do hry.
- Vaše odoslané výzvy sa stanú neplatnými a zmiznú z ponuky.

### Herné pokyny

- Po presune do hry sa môžete okamžite hýbať klávesami **A**, **W**, **S**, **D**.
- **Cieľ hry:** Dostať sa do cieľa.
    - Vy ste **zelený**.
    - Protihráč je **červený**.
    - Cieľ je **zlatý**.
- Môžete písať súperovi kliknutím do políčka na písanie naľavo.

**Poznámka:** Ak hru opustíte bez dohratia, hra sa zruší a nikto nevyhrá.

---

## Testovanie

Na spustenie testov v príkazovom riadku použite:

```bash
pytest
```

V priečinku **helpers** sa nachádzajú aj skripty `test.sh` a `killRunners.sh`, ktoré uľahčujú
testovanie.  
Avšak, pri ich použití je väčšia šanca, že sa niečo pokazí. Napriek mojej veľkej snahe sa občas stáva, že
sa spojenie medzi serverom a klientom preruší.  
Pri manuálnom spustení sa tento problém nevyskytuje tak často.

## Dodatky

Neskoro som si všimol, že je vytvorená vetva na semestrálku v našich repozitároch, ja som ju celý
čas vyvíjal vo vlastne vytvorenom repozitáry. Poslal som vám pozvanie doňho, túto verziu nájdete
v priečinku **pygame-try** vo vetvi **without-spectator**


