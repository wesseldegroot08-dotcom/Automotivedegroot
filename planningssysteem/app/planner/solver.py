"""De solver: OR-Tools CP-SAT. Kiest per rit een eenheid (trekker + chassis), een chauffeur en een begintijd.

Model in het kort:
- Elke rit gaat naar hoogstens één eenheid. Niet plannen kan, maar kost veel ('ongepland'-straf).
- Alleen toegestane combinaties (uit de voorfilter met de harde regels).
- Elke eenheid krijgt voor de hele dag één chauffeur. Een chauffeur zit op hoogstens één eenheid.
  (Vereenvoudiging: wisselen van trekker tijdens de dag komt later.)
- Per eenheid een volgorde van ritten (circuit). Tussen twee ritten zit het lege rijden van de
  afleverplek naar de volgende ophaalplek. De dag begint en eindigt op de standplaats.
- Benadering rij- en rusttijd: maximaal 9 uur rijden (minder als de week bijna vol is),
  na 4,5 uur rijden 45 minuten pauze in de dienst, dienst maximaal 13 uur.
- Doel: zo min mogelijk ongepland, dan zo weinig mogelijk leeg rijden en overwerk,
  en liefst de vaste chauffeur op zijn eigen trekker.
Daarna toetst de exacte controle (rules/) het resultaat. Zie planner/voorstel.py.
"""

import time as _time

from ortools.sat.python import cp_model

from app.planner.probleem import Oplossing, Probleem, Toewijzing

STRAF_ONGEPLAND = 10_000
BONUS_VASTE_TREKKER = 30
KOSTEN_EENHEID = 20
DAG_MIN = 24 * 60
VROEGER_MAX = 120
STAP = 5
LAAT = DAG_MIN + 12 * 60


class CpSatSolver:
    """Implementatie van de Solver-interface met OR-Tools CP-SAT."""

    def los_op(self, p: Probleem, tijdlimiet_sec: float) -> Oplossing:
        begin = _time.monotonic()
        try:
            uit = self._los_op(p, tijdlimiet_sec)
        except Exception as e:  # de solver mag nooit crashen: alles wordt ongepland met reden
            uit = Oplossing("FOUT", {}, {t.rit_id: f"Solver-fout: {e}" for t in p.taken if not t.vast})
        uit.rekentijd_ms = int((_time.monotonic() - begin) * 1000)
        for t in p.taken:  # niets mag stilletjes verdwijnen
            if t.rit_id not in uit.toewijzingen and t.rit_id not in uit.ongepland:
                uit.ongepland[t.rit_id] = p.niet_te_plannen.get(t.rit_id, "Geen plek gevonden.")
        return uit

    def _los_op(self, p: Probleem, tijdlimiet_sec: float) -> Oplossing:
        model = cp_model.CpModel()
        uit = Oplossing("GEEN")
        taken = {t.rit_id: t for t in p.taken}
        for rid, reden in p.niet_te_plannen.items():
            uit.ongepland[rid] = reden
        planbaar = [t for t in p.taken if t.rit_id not in p.niet_te_plannen and p.toegestaan.get(t.rit_id)]
        chauffeurs = {c.id: c for c in p.chauffeurs}
        eenheden = {e.sleutel: e for e in p.eenheden}

        start = {}
        for t in planbaar:
            start[t.rit_id] = model.NewIntVar(t.start_min, t.start_max, f"start_{t.rit_id}")
            if not t.vast and -(-t.start_min // STAP) <= t.start_max // STAP:  # begintijden op hele 5 minuten
                stap = model.NewIntVar(-(-t.start_min // STAP), t.start_max // STAP, f"stap_{t.rit_id}")
                model.Add(start[t.rit_id] == STAP * stap)
        x: dict[tuple[int, str], cp_model.IntVar] = {}
        z: dict[tuple[int, str, int], cp_model.IntVar] = {}
        y: dict[tuple[str, int], cp_model.IntVar] = {}
        for t in planbaar:
            for e, c in p.toegestaan[t.rit_id]:
                if (t.rit_id, e) in p.verboden and not t.vast:
                    continue
                if e not in eenheden or c not in chauffeurs:
                    continue
                if (t.rit_id, e) not in x:
                    x[(t.rit_id, e)] = model.NewBoolVar(f"x_{t.rit_id}_{e}")
                if (e, c) not in y:
                    y[(e, c)] = model.NewBoolVar(f"y_{e}_{c}")
                z[(t.rit_id, e, c)] = model.NewBoolVar(f"z_{t.rit_id}_{e}_{c}")
                model.AddImplication(z[(t.rit_id, e, c)], y[(e, c)])

        gepland = {}
        for t in planbaar:
            xs = [v for (r, _e), v in x.items() if r == t.rit_id]
            gepland[t.rit_id] = model.NewBoolVar(f"gepland_{t.rit_id}")
            model.Add(sum(xs) == gepland[t.rit_id])
            for (r, e), v in x.items():
                if r == t.rit_id:
                    model.Add(sum(zv for (rr, ee, _c), zv in z.items() if rr == r and ee == e) == v)
            if t.vast:
                model.Add(gepland[t.rit_id] == 1)
                model.Add(start[t.rit_id] == t.vast_start)
            if t.hint_eenheid and (t.rit_id, t.hint_eenheid) in x:
                model.AddHint(x[(t.rit_id, t.hint_eenheid)], 1)
                model.AddHint(start[t.rit_id], max(t.start_min, min(t.start_max, t.hint_start)))

        for e in eenheden:
            model.Add(sum(v for (ee, _c), v in y.items() if ee == e) <= 1)
        for c in chauffeurs:
            model.Add(sum(v for (_e, cc), v in y.items() if cc == c) <= 1)

        doel = []
        stand = p.standplaats_id
        for e in eenheden:
            kand = [t for t in planbaar if (t.rit_id, e) in x]
            if not kand:
                continue
            gebruikt = model.NewBoolVar(f"gebruikt_{e}")
            model.AddMaxEquality(gebruikt, [x[(t.rit_id, e)] for t in kand])
            dienst_begin = model.NewIntVar(0, LAAT, f"db_{e}")
            dienst_eind = model.NewIntVar(0, LAAT, f"de_{e}")
            arcs = [(0, 0, gebruikt.Not())]
            rij_termen, bezig_termen = [], []
            for i, t in enumerate(kand, start=1):
                xi = x[(t.rit_id, e)]
                arcs.append((i, i, xi.Not()))
                rij_termen.append(t.reis_min * xi)
                bezig_termen.append(t.duur * xi)
                aan_min, aan_km = p.reistijd(stand, t.van_id)
                terug_min, terug_km = p.reistijd(t.naar_id, stand)
                a0 = model.NewBoolVar(f"a0_{e}_{t.rit_id}")
                a1 = model.NewBoolVar(f"a1_{e}_{t.rit_id}")
                arcs += [(0, i, a0), (i, 0, a1)]
                model.Add(dienst_begin == start[t.rit_id] - aan_min).OnlyEnforceIf(a0)
                model.Add(dienst_eind == start[t.rit_id] + t.duur + terug_min).OnlyEnforceIf(a1)
                rij_termen += [aan_min * a0, terug_min * a1]
                bezig_termen += [aan_min * a0, terug_min * a1]
                doel += [aan_min * a0, terug_min * a1]
                for j, t2 in enumerate(kand, start=1):
                    if i == j:
                        continue
                    leeg_min, _km = p.reistijd(t.naar_id, t2.van_id)
                    if t.start_min + t.duur + leeg_min > t2.start_max:
                        continue  # kan nooit in deze volgorde
                    a = model.NewBoolVar(f"a_{e}_{t.rit_id}_{t2.rit_id}")
                    arcs.append((i, j, a))
                    model.Add(start[t2.rit_id] >= start[t.rit_id] + t.duur + leeg_min).OnlyEnforceIf(a)
                    rij_termen.append(leeg_min * a)
                    bezig_termen.append(leeg_min * a)
                    doel.append(leeg_min * a)
            model.AddCircuit(arcs)
            rijden = model.NewIntVar(0, LAAT, f"rijden_{e}")
            model.Add(rijden == sum(rij_termen))
            bezig = model.NewIntVar(0, 3 * LAAT, f"bezig_{e}")
            model.Add(bezig == sum(bezig_termen))
            model.Add(dienst_eind - dienst_begin <= p.max_dienst).OnlyEnforceIf(gebruikt)
            pauze = model.NewBoolVar(f"pauze_{e}")
            model.Add(rijden <= p.pauze_na).OnlyEnforceIf(pauze.Not())
            model.Add(dienst_eind - dienst_begin >= bezig + p.pauze_duur).OnlyEnforceIf(pauze)
            overwerk = model.NewIntVar(0, LAAT, f"over_{e}")
            for (ee, c), yv in y.items():
                if ee != e:
                    continue
                ch = chauffeurs[c]
                # Eerder beginnen dan de standaardtijd mag tot 2 uur, maar kost net als overwerk
                model.Add(dienst_begin >= ch.begin_min - VROEGER_MAX).OnlyEnforceIf(yv)
                model.Add(overwerk >= ch.begin_min - dienst_begin).OnlyEnforceIf(yv)
                model.Add(rijden <= ch.rest_rij_min).OnlyEnforceIf(yv)
                model.Add(overwerk >= dienst_eind - ch.eind_min).OnlyEnforceIf(yv)
                if ch.voorkeur_trekker_id == eenheden[e].trekker_id:
                    doel.append(-BONUS_VASTE_TREKKER * yv)
            doel += [overwerk, KOSTEN_EENHEID * gebruikt]

        for t in planbaar:
            doel.append(STRAF_ONGEPLAND * t.prioriteit * (1 - gepland[t.rit_id]))
        model.Minimize(sum(doel))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max(1.0, float(tijdlimiet_sec))
        solver.parameters.num_workers = 4
        solver.parameters.random_seed = 1  # zelfde invoer, zelfde voorstel
        status = solver.Solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            reden = ("De vaste (toegezegde of gestarte) ritten passen niet samen. Controleer ze op het planbord."
                     if status == cp_model.INFEASIBLE else "Binnen de rekentijd geen oplossing gevonden.")
            for t in planbaar:
                if not t.vast:
                    uit.ongepland[t.rit_id] = reden
            uit.status = "GEEN"
            return uit
        uit.status = "OPTIMAAL" if status == cp_model.OPTIMAL else "GOED"
        for t in planbaar:
            if not solver.Value(gepland[t.rit_id]):
                uit.ongepland[t.rit_id] = _reden_ongepland(p, t, taken)
                continue
            for (r, e, c), zv in z.items():
                if r == t.rit_id and solver.Value(zv):
                    uit.toewijzingen[t.rit_id] = Toewijzing(e, c, solver.Value(start[t.rit_id]))
        return uit


def _hhmm(minuten: int) -> str:
    minuten = max(0, minuten)
    return f"{minuten // 60:02d}:{minuten % 60:02d}"


def _reden_ongepland(p: Probleem, t, taken) -> str:
    n = len(p.toegestaan.get(t.rit_id, []))
    return (f"Geen ruimte: de {n} geschikte combinatie(s) zijn al bezet tussen {_hhmm(t.start_min)} en "
            f"{_hhmm(t.start_max)} (begintijd), of de rijtijd van de chauffeurs is op.")
