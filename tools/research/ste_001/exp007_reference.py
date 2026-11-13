#!/usr/bin/env python3
"""EXP-007 phase A: bounded, independent research oracle (standard library only).

Usage (redirect output outside the repository if an artifact is needed):
  PYTHONDONTWRITEBYTECODE=1 python3 exp007_reference.py --self-test
  python3 -B exp007_reference.py --fixture F10 F11 M03 M04
  python3 -B exp007_reference.py --fixture M03 --compare /tmp/c11.json

The comparison input uses the same ste-exp007-reference-v1 envelope and result
fields emitted by --fixture. Metadata and work counters are implementation-owned
and excluded from comparison (C11 must not claim 512 relation classifications).
All candidate relations are concrete [source, target] pairs. Collections are
compared extensionally, with duplicate candidates/outcomes reported as failures;
pair orientation is significant. Decisions, obligations, accepting witnesses,
full rejection certificates, and observable partitions are part of comparison.
This contract does not prescribe the C11 generator, filters, or material solver.

No C11 code, STE classification, TPI engine, full polarity campaign, or full
transformation campaign is implemented here. --self-test runs only named cases,
31 frozen record presentations and a few explicitly counted boundary probes.
Expected encodings/tuples are decoded only by test functions, never by the oracle.
Every supported decision checks all 27 maps, including when an early witness
exists. A missing policy is not an empty witness set. No file is written.
"""

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PROTOCOL_SHA256 = '61a586c706cf5e3cfb78ffbfd835dcbdc060c4c46f6cc427fbf2379a095664f1'
FREEZE_COMMIT = '101eb2c5df29c1e65d8ccea2b9ea8be510c32315'
BASE = Path(__file__).resolve().parent
VALUES = ('0', 'lambda', 'rho')
SET_NAMES = ('U_H', 'C_E', 'A_E')
MAX_JSON_BYTES = 2_000_000
MAX_CASES = 64


class InvalidInput(ValueError):
    """Outside the frozen, well-formed finite input domain."""


def require(condition, reason):
    if not condition:
        raise InvalidInput(reason)


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def ordered(values):
    return sorted(values, key=stable)


def unique(values):
    """Extensional union, used only where the mathematical model calls for it."""
    return [json.loads(s) for s in sorted({stable(v) for v in values})]


def nonempty_string(value):
    return isinstance(value, str) and bool(value)


def string_list(value, size=None):
    return (isinstance(value, list) and all(nonempty_string(x) for x in value)
            and (size is None or len(value) == size))


def no_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidInput('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    require(len(raw) <= MAX_JSON_BYTES, 'JSON exceeds bounded input size')
    return json.loads(raw, object_pairs_hook=no_duplicate_json_keys)


def expand(groups):
    return [case for group in groups for case in group.get('variants', [group])]


def load_manifest(path):
    manifest = read_json(path)
    require(manifest['schema'] == 'ste-exp007-fixtures-v1', 'unknown fixture schema')
    identity = manifest['protocol']
    require(identity['sha256'] == PROTOCOL_SHA256, 'manifest protocol hash changed')
    require(identity['freeze_commit'] == FREEZE_COMMIT, 'manifest freeze commit changed')
    actual = hashlib.sha256((BASE / 'EXP007_PROTOCOL.md').read_bytes()).hexdigest()
    require(actual == PROTOCOL_SHA256, 'local frozen protocol hash mismatch')
    require([f['id'] for f in manifest['candidate_fixtures']] ==
            [f'F{i:02}' for i in range(1, 15)], 'missing/reordered named candidate fixtures')
    require([m['id'] for m in manifest['material_fixtures']] ==
            [f'M{i:02}' for i in range(1, 6)], 'missing/reordered material scenarios')
    cases = (expand(manifest['candidate_fixtures']) + manifest['sensitivity_cases']
             + manifest['material_association_fixtures'] + expand(manifest['material_fixtures']))
    require(len(cases) <= MAX_CASES, 'too many declared cases')
    require(len({c['id'] for c in cases}) == len(cases), 'duplicate fixture ID')
    return manifest


def validate_snapshot(snapshot):
    require(isinstance(snapshot, dict), 'snapshot must be an object')
    require(nonempty_string(snapshot['id']), 'snapshot identity required')
    vertices, occurrences, root = (snapshot[k] for k in ('vertices', 'occurrences', 'root'))
    require(string_list(vertices, 4), 'exactly four vertex handles required')
    require(len(set(vertices)) == 4, 'duplicated vertex handle')
    require(nonempty_string(root) and root in vertices, 'invalid designated root')
    require(string_list(occurrences, 3) and len(set(occurrences)) == 3,
            'exactly three distinct non-root occurrences required')
    require(set(occurrences) == set(vertices) - {root}, 'invalid non-root occurrence domain')
    edges = snapshot['incidence']
    require(isinstance(edges, list) and len(edges) == 3, 'tree needs exactly three incidences')
    require(all(string_list(e, 2) for e in edges), 'incidences must be directed handle pairs')
    require(len({tuple(e) for e in edges}) == 3, 'duplicate incidence')
    require(all(a in vertices and b in vertices and a != b for a, b in edges),
            'foreign vertex or self incidence')
    require(all(sum(b == v for _, b in edges) == (0 if v == root else 1)
                for v in vertices), 'invalid tree parent occupancy')
    # A disconnected cycle can pass the parent counts; root reachability is required.
    reached = {root}
    for _ in range(4):
        reached |= {b for a, b in edges if a in reached}
    require(reached == set(vertices), 'snapshot is not a rooted tree: unreachable/cyclic vertices')


def validate_candidate(fixture):
    left, right = (fixture['snapshots'][k] for k in ('left', 'right'))
    validate_snapshot(left)
    validate_snapshot(right)
    require(left['id'] != right['id'], 'snapshots require separate identities')
    require(set(left['vertices']).isdisjoint(right['vertices']), 'cross-snapshot duplicate handle')
    require(fixture['profile'] in ('S_free', 'S_inc'), 'unsupported structural profile')
    require(type(fixture['assumes_unchanged_incidence']) is bool,
            'unchanged-incidence assumption must be explicit Boolean')
    if fixture['profile'] == 'S_inc':
        require(fixture['assumes_unchanged_incidence'], 'S_inc requires explicit authorization')
    records = fixture['evidence']
    require(isinstance(records, list) and len(records) <= 64, 'evidence outside bounded record domain')
    by_id = {}
    for record in records:
        require(nonempty_string(record['id']), 'evidence record identity required')
        require(record['source'] in left['occurrences'] and record['target'] in right['occurrences'],
                'foreign evidence handle')
        require(record['polarity'] in ('REQUIRE', 'EXCLUDE'), 'unsupported evidence polarity')
        require(record['assessment'] in ('ACCEPTED', 'REJECTED', 'UNRESOLVED'),
                'unsupported assessment status')
        provenance = record['provenance']
        require(all(nonempty_string(provenance[k]) for k in
                    ('origin', 'source', 'assessment_rule', 'assumed_trust')),
                'synthetic provenance and trust assumptions required')
        scope = provenance['scope']
        require(scope['snapshots'] == [left['id'], right['id']] and
                scope['source'] == record['source'] and scope['target'] == record['target'],
                'provenance scope must follow concrete selectors')
        require(record['id'] not in by_id or by_id[record['id']] == record,
                'same evidence ID has contradictory presentations')
        by_id[record['id']] = record


def recognize_bijections(left, right):
    """Visit every binary relation; no permutation generator or pruning."""
    pairs = [(source, target) for source in left for target in right]
    recognized = []
    for mask in range(1 << len(pairs)):
        relation = frozenset(pair for bit, pair in enumerate(pairs) if mask & (1 << bit))
        row_occupancy = [sum(s == source for s, _ in relation) for source in left]
        column_occupancy = [sum(t == target for _, t in relation) for target in right]
        if all(n == 1 for n in row_occupancy) and all(n == 1 for n in column_occupancy):
            recognized.append(relation)
    return recognized


def evidence_satisfied(relation, records):
    for record in records:
        if record['assessment'] != 'ACCEPTED':
            continue
        present = (record['source'], record['target']) in relation
        if record['polarity'] == 'REQUIRE' and not present:
            return False
        if record['polarity'] == 'EXCLUDE' and present:
            return False
    return True


def structure_satisfied(relation, fixture):
    if fixture['profile'] == 'S_free':
        return True
    left, right = (fixture['snapshots'][k] for k in ('left', 'right'))
    transport = dict(relation)
    transport[left['root']] = right['root']
    return ({(transport[a], transport[b]) for a, b in left['incidence']} ==
            {tuple(e) for e in right['incidence']})


def relation_json(relation):
    return [list(pair) for pair in sorted(relation)]


def evaluate_candidate(fixture):
    """No access to fixture expectations; invalid input has no candidate sets."""
    try:
        validate_candidate(fixture)
    except (InvalidInput, KeyError, TypeError, ValueError) as error:
        return dict(status='UNSUPPORTED', diagnostics=['INVALID_INPUT'], reason=str(error),
                    conditional=None, candidate_sets=None, counts=None,
                    relations_examined=0, predicates=None, evidence_records=None,
                    assessment_counts=None)
    left, right = (fixture['snapshots'][k] for k in ('left', 'right'))
    universe = recognize_bijections(left['occurrences'], right['occurrences'])
    evidence = [phi for phi in universe if evidence_satisfied(phi, fixture['evidence'])]
    structural = {phi for phi in universe if structure_satisfied(phi, fixture)}
    admissible = [phi for phi in evidence if phi in structural]
    counts = {status: sum(e['assessment'] == status for e in fixture['evidence'])
              for status in ('ACCEPTED', 'REJECTED', 'UNRESOLVED')}
    diagnostics = []
    if not fixture['evidence']:
        diagnostics.append('MISSING_EVIDENCE')
    if counts['UNRESOLVED']:
        diagnostics.append('ASSESSMENT_UNRESOLVED')
    if not evidence:
        diagnostics.append('EVIDENCE_INCONSISTENT')
    elif not admissible:
        diagnostics.append('STRUCTURALLY_UNSATISFIABLE')
    sets = {key: ordered(relation_json(phi) for phi in phis)
            for key, phis in zip(SET_NAMES, (universe, evidence, admissible))}
    predicates = ordered(dict(association=relation_json(phi),
                              evidence_satisfied=evidence_satisfied(phi, fixture['evidence']),
                              structure_satisfied=phi in structural) for phi in universe)
    return dict(status='SUPPORTED', diagnostics=sorted(diagnostics), conditional=bool(counts['UNRESOLVED']),
                candidate_sets=sets, counts={k: len(v) for k, v in sets.items()},
                relations_examined=512, predicates=predicates,
                assessment_counts=counts, evidence_records=copy.deepcopy(fixture['evidence']))


def validate_material(material, fixture):
    require(material['values'] == list(VALUES), 'unsupported material value domain')
    for side in ('left', 'right'):
        require(material['initial'][side] ==
                {v: '0' for v in fixture['snapshots'][side]['occurrences']},
                'initial material must be 0 on non-root occurrences only')
    updates = material['updates']
    require(isinstance(updates, list) and 1 <= len(updates) <= 2, 'unsupported update domain')
    require(all(nonempty_string(u['id']) for u in updates), 'intention IDs required')
    ids = {u['id'] for u in updates}
    require(len(ids) == len(updates), 'duplicated intention ID')
    for update in updates:
        require(update['side'] in ('left', 'right'), 'invalid update side')
        require(update['target'] in fixture['snapshots'][update['side']]['occurrences'],
                'foreign material selector')
        require(update['value'] in VALUES and update['mandatory'] is True,
                'only mandatory single-valued equality updates are supported')
    policy = material['policy']
    require(isinstance(policy, dict) and policy['complete'] is True,
            'required complete retention/loss policy is absent')
    decisions = policy['decisions']
    require(isinstance(decisions, list) and 1 <= len(decisions) <= 2,
            'complete finite decision set required (one or two decisions)')
    require(all(nonempty_string(d['id']) for d in decisions), 'decision IDs required')
    require(len({d['id'] for d in decisions}) == len(decisions), 'duplicate policy decision')
    for decision in decisions:
        retained, waived = decision['retained'], decision['waived']
        require(string_list(retained) and string_list(waived), 'explicit retention/loss lists required')
        require(len(set(retained)) == len(retained) and len(set(waived)) == len(waived),
                'duplicate intention in policy decision')
        require(set(retained).isdisjoint(waived) and set(retained) | set(waived) == ids,
                'each intention must be retained or explicitly waived, exactly once')
        require(nonempty_string(decision['authorization']), 'policy authorization required')
    require(material['independent_comparison'] in ('PENDING', 'INCOMPLETE'),
            'phase A cannot assert independent C11 comparison completion')


def decision_obligations(material, fixture, relation, decision):
    """Build conjunct descriptions, not a result assignment or outcome."""
    inverse = {target: source for source, target in relation}
    obligations = []
    for update in material['updates']:
        if update['id'] not in decision['retained']:
            continue
        target = (update['target'] if update['side'] == 'left' else inverse[update['target']])
        obligations.append(dict(id='update:' + update['id'], kind='UPDATE',
                                intention=update['id'], side=update['side'], selector=update['target'],
                                target=target, value=update['value']))
    targeted = {o['target'] for o in obligations}
    obligations.extend(dict(id='preserve:' + source, kind='PRESERVE', target=source, value='0')
                       for source in fixture['snapshots']['left']['occurrences'] if source not in targeted)
    return ordered(obligations)


def observable(outcome, query):
    """Undefined observations have no equivalence class."""
    if query != 'Q':
        return None
    return copy.deepcopy(outcome)


def equivalent(first, second, query='Q'):
    a, b = observable(first, query), observable(second, query)
    return None if a is None or b is None else a == b


def evaluate_material(material, fixture, candidate):
    base = dict(scientific_claim='INCONCLUSIVE', independent_comparison=material.get('independent_comparison'),
                associations=None, observable_classes=None, assignments_examined=0)
    if candidate['status'] != 'SUPPORTED':
        return dict(base, policy_status='UNSUPPORTED', observable_status='NOT_EVALUATED',
                    diagnostics=['INVALID_INPUT'], reason='invalid candidate model')
    try:
        validate_material(material, fixture)
    except (InvalidInput, KeyError, TypeError, ValueError) as error:
        return dict(base, policy_status='UNSUPPORTED', observable_status='NOT_EVALUATED',
                    diagnostics=['POLICY_UNSUPPORTED'], reason=str(error))
    sources = fixture['snapshots']['left']['occurrences']
    associations, class_members, examined = [], {}, 0
    for relation in candidate['candidate_sets']['A_E']:
        decisions, witness_union, decision_outcomes = [], [], []
        for decision in material['policy']['decisions']:
            conjuncts = decision_obligations(material, fixture, relation, decision)
            witnesses, failures = [], []
            # Enumerate the full carrier. No direct material outcome constructor.
            for values in itertools.product(VALUES, repeat=3):
                assignment = dict(zip(sources, values))
                violated = [o['id'] for o in conjuncts if assignment[o['target']] != o['value']]
                examined += 1
                if violated:
                    failures.append(dict(material=assignment, violated=sorted(violated)))
                else:
                    witnesses.append(dict(material=assignment, satisfied=sorted(o['id'] for o in conjuncts)))
            witness_union.extend(w['material'] for w in witnesses)
            outcomes = ([dict(tag='ACCEPT', material=w['material']) for w in witnesses]
                        if witnesses else [dict(tag='REJECT')])
            decisions.append(dict(id=decision['id'], authorization=decision['authorization'],
                                  retained_intentions=ordered(u for u in material['updates']
                                                             if u['id'] in decision['retained']),
                                  waived_intentions=ordered(u for u in material['updates']
                                                           if u['id'] in decision['waived']),
                                  obligations=conjuncts, assignments_examined=27,
                                  W_phi_d=ordered(w['material'] for w in witnesses),
                                  witnesses=ordered(witnesses),
                                  rejection_certificate=ordered(failures) if not witnesses else None,
                                  outcomes=ordered(outcomes)))
            for outcome in outcomes:
                decision_outcomes.append(dict(decision=decision['id'], outcome=outcome))
                observation = observable(outcome, material['query'])
                if observation is not None:
                    key = stable(observation)
                    class_members.setdefault(key, []).append(dict(association=relation, decision=decision['id']))
        # Independently evaluate P_phi = OR_d P_phi,d for every assignment, not
        # just the union of an outcome constructor's selected materials.
        union_by_predicate = []
        for values in itertools.product(VALUES, repeat=3):
            assignment = dict(zip(sources, values))
            if any(all(assignment[o['target']] == o['value'] for o in decision['obligations'])
                   for decision in decisions):
                union_by_predicate.append(assignment)
        require(unique(witness_union) == ordered(union_by_predicate), 'W_phi union/predicate disagreement')
        associations.append(dict(association=relation, decisions=ordered(decisions),
                                 W_phi=ordered(union_by_predicate), union_assignments_examined=27,
                                 rejected_under_all_decisions=not bool(union_by_predicate),
                                 outcomes=ordered(decision_outcomes)))
    defined = material['query'] == 'Q'
    classes = [dict(observable=json.loads(k), members=ordered(v)) for k, v in sorted(class_members.items())]
    diagnostics = ([] if defined else ['OBSERVABLE_UNDEFINED'])
    if material['independent_comparison'] == 'INCOMPLETE':
        diagnostics.append('INDEPENDENT_COMPARISON_INCOMPLETE')
    if candidate['conditional']:
        diagnostics.append('ASSESSMENT_UNRESOLVED')
    if not candidate['candidate_sets']['A_E']:
        diagnostics.append('NO_ADMISSIBLE_ASSOCIATIONS')
    return dict(base, policy_status='SUPPORTED', observable_status='DEFINED' if defined else 'OBSERVABLE_UNDEFINED',
                diagnostics=sorted(diagnostics), associations=ordered(associations),
                observable_classes=classes if defined else None, assignments_examined=examined,
                union_assignments_examined=27 * len(associations))


def catalog(manifest):
    candidates = {f['id']: f for f in (expand(manifest['candidate_fixtures']) +
                                     manifest['sensitivity_cases'] + manifest['material_association_fixtures'])}
    materials = {m['id']: m for m in expand(manifest['material_fixtures'])}
    groups = {g['id']: [v['id'] for v in g['variants']] for g in
              manifest['candidate_fixtures'] + manifest['material_fixtures'] if 'variants' in g}
    return candidates, materials, groups


def evaluate_named(identifier, candidates, materials):
    if identifier in candidates:
        return dict(id=identifier, candidate=evaluate_candidate(candidates[identifier]))
    material = materials[identifier]
    fixture = candidates[material['candidate_fixture']]
    candidate = evaluate_candidate(fixture)
    return dict(id=identifier, candidate=candidate,
                material=evaluate_material(material, fixture, candidate))


def expected_relation(code, fixture):
    """Test-side decoding of the frozen table only; never used in enumeration."""
    left, right = (fixture['snapshots'][s]['occurrences'] for s in ('left', 'right'))
    return relation_json(zip(left, (right[int(index)] for index in code)))


def check_candidate_expectation(fixture, actual):
    expected = fixture['expected']
    require(actual['status'] == expected['status'], 'candidate status mismatch')
    require(actual['diagnostics'] == expected['diagnostics'], 'candidate diagnostics mismatch')
    require(actual['conditional'] == expected['conditional'], 'assessment conditionality mismatch')
    if expected['status'] == 'UNSUPPORTED':
        require(actual['candidate_sets'] is None and actual['counts'] is None and
                actual['relations_examined'] == 0, 'invalid input was enumerated')
        return
    require(actual['relations_examined'] == 512, 'not all binary relations visited')
    for key in SET_NAMES:
        wanted = ordered(expected_relation(code, fixture) for code in expected[key])
        got = actual['candidate_sets'][key]
        require(got == wanted, key + ' exact set mismatch: ' + stable(dict(expected=wanted, actual=got)))
        require(len({stable(phi) for phi in got}) == len(got), 'duplicate emitted candidate')
        require(actual['counts'][key] == len(wanted), 'candidate count mismatch')


def check_material_expectation(material, fixture, actual):
    expected = material['expected']
    for key in ('policy_status', 'observable_status', 'scientific_claim'):
        require(actual[key] == expected[key], key + ' mismatch')
    if expected['outcomes'] is None:
        require(actual['associations'] is None and actual['assignments_examined'] == 0,
                'unsupported policy supplied material outcomes')
        return
    wanted = {}
    for code, decisions in expected['outcomes'].items():
        association = stable(expected_relation(code, fixture))
        wanted[association] = {}
        for decision, outcomes in decisions.items():
            wanted[association][decision] = ordered(
                dict(tag='REJECT') if o['tag'] == 'REJECT' else
                dict(tag='ACCEPT', material=dict(zip(fixture['snapshots']['left']['occurrences'], o['values'])))
                for o in outcomes)
    got = {stable(a['association']): {d['id']: d['outcomes'] for d in a['decisions']}
           for a in actual['associations']}
    require(got == wanted, 'exact per-association/per-decision material outcome mismatch')
    for association in actual['associations']:
        for decision in association['decisions']:
            require(decision['assignments_examined'] == 27, 'incomplete material assignment scan')
            conjuncts = decision['obligations']
            for witness in decision['witnesses']:
                require(all(witness['material'][o['target']] == o['value'] for o in conjuncts),
                        'invalid acceptance witness')
                require(witness['satisfied'] == sorted(o['id'] for o in conjuncts), 'missing satisfied obligations')
            certificate = decision['rejection_certificate']
            if decision['outcomes'] == [dict(tag='REJECT')]:
                require(certificate is not None and len(certificate) == 27, 'incomplete rejection certificate')
                require(len({stable(row['material']) for row in certificate}) == 27,
                        'repeated assignments in rejection certificate')
                for row in certificate:
                    violated = sorted(o['id'] for o in conjuncts if row['material'][o['target']] != o['value'])
                    require(bool(violated) and violated == row['violated'], 'invalid rejection conjuncts')
            else:
                require(certificate is None, 'accepting decision carries rejection certificate')
    classes = actual['observable_classes']
    require((None if classes is None else len(classes)) == expected['observable_class_count'],
            'observable class mismatch')
    if classes is not None:
        observations = [c['observable'] for c in classes]
        for a in observations:
            require(equivalent(a, a), 'observable reflexivity failure')
            for b in observations:
                require(equivalent(a, b) == equivalent(b, a), 'observable symmetry failure')
                for c in observations:
                    require(not (equivalent(a, b) and equivalent(b, c)) or equivalent(a, c),
                            'observable transitivity failure')


def normalize_comparison(value, field='', failures=None, path='$'):
    """Collection order is irrelevant; source/target pair orientation is retained."""
    if failures is None:
        failures = []
    if field == 'association':
        require(isinstance(value, list) and all(string_list(p, 2) for p in value),
                'malformed relation at ' + path)
        require(len(value) == 3 and len({tuple(p) for p in value}) == 3, 'invalid relation at ' + path)
        return sorted(value)
    if field in SET_NAMES and not path.endswith('.counts.' + field):
        require(isinstance(value, list), 'candidate set must be a list at ' + path)
        rows = [normalize_comparison(v, 'association', failures, path) for v in value]
        duplicates = len(rows) - len({stable(r) for r in rows})
        if duplicates:
            failures.append(dict(path=path, kind='DUPLICATES', count=duplicates))
        return ordered(rows)
    if field == 'snapshots' and string_list(value):
        # The provenance scope lists source snapshot first, target snapshot second.
        return value
    if isinstance(value, dict):
        return {k: normalize_comparison(v, k, failures, path + '.' + k) for k, v in value.items()
                if k not in ('relations_examined', 'assignments_examined', 'union_assignments_examined')}
    if isinstance(value, list):
        rows = [normalize_comparison(v, '', failures, path + '[]') for v in value]
        if field in ('outcomes', 'W_phi', 'W_phi_d', 'witnesses', 'rejection_certificate',
                     'decisions', 'associations', 'observable_classes', 'members', 'results', 'predicates'):
            duplicates = len(rows) - len({stable(r) for r in rows})
            if duplicates:
                failures.append(dict(path=path, kind='DUPLICATES', count=duplicates))
        return ordered(rows)
    return value


def compare_results(reference, submitted):
    failures = []
    require(isinstance(submitted, dict), 'comparison must be an object')
    require(submitted['schema'] == reference['schema'], 'comparison schema mismatch')
    require(submitted['protocol_sha256'] == PROTOCOL_SHA256, 'comparison protocol mismatch')
    require(isinstance(submitted['results'], list) and len(submitted['results']) <= MAX_CASES,
            'comparison result count outside bound')
    for result in submitted['results']:
        require(isinstance(result, dict), 'comparison result must be an object')
        for field in ('candidate', 'material'):
            if field in result:
                require(isinstance(result[field], dict),
                        'comparison ' + field + ' must be an object')
    normalized = normalize_comparison(submitted['results'], 'results', failures)
    expected = normalize_comparison(reference['results'], 'results')
    ids = [r['id'] for r in submitted['results']]
    if len(ids) != len(set(ids)):
        failures.append(dict(kind='DUPLICATE_FIXTURE_ID'))
    # Report extensional candidate false positives and negatives, not just counts.
    actual_by_id = {r['id']: r for r in normalized}
    for result in expected:
        identifier = result['id']
        if identifier not in actual_by_id:
            failures.append(dict(id=identifier, kind='MISSING_FIXTURE'))
            continue
        other = actual_by_id[identifier]
        a_sets = other.get('candidate', {}).get('candidate_sets')
        e_sets = result['candidate']['candidate_sets']
        if isinstance(a_sets, dict) and e_sets is not None:
            for key in SET_NAMES:
                a = {stable(phi) for phi in a_sets.get(key, [])}
                e = {stable(phi) for phi in e_sets[key]}
                if a != e:
                    failures.append(dict(id=identifier, field=key,
                                         false_positives=[json.loads(s) for s in sorted(a-e)],
                                         false_negatives=[json.loads(s) for s in sorted(e-a)]))
        e_material = result.get('material', {}).get('associations')
        a_material = other.get('material', {}).get('associations')
        if isinstance(e_material, list) and isinstance(a_material, list):
            a_decisions = {(stable(a['association']), d['id']): d
                           for a in a_material for d in a['decisions']}
            e_decisions = {(stable(a['association']), d['id']): d
                           for a in e_material for d in a['decisions']}
            for key in sorted(set(a_decisions) | set(e_decisions)):
                a_decision, e_decision = a_decisions.get(key), e_decisions.get(key)
                if a_decision != e_decision:
                    a_out = {stable(o) for o in a_decision['outcomes']} if a_decision else set()
                    e_out = {stable(o) for o in e_decision['outcomes']} if e_decision else set()
                    failures.append(dict(id=identifier, kind='MATERIAL_DECISION_MISMATCH',
                                         association=json.loads(key[0]), decision=key[1],
                                         false_positives=[json.loads(s) for s in sorted(a_out-e_out)],
                                         false_negatives=[json.loads(s) for s in sorted(e_out-a_out)],
                                         expected=e_decision, actual=a_decision))
        if other != result:
            failures.append(dict(id=identifier, kind='EXACT_RESULT_MISMATCH',
                                 fields=sorted(k for k in set(other) | set(result) if other.get(k) != result.get(k))))
    for identifier in sorted(set(actual_by_id) - {r['id'] for r in expected}):
        failures.append(dict(id=identifier, kind='UNEXPECTED_FIXTURE'))
    return dict(status='FAIL' if failures else 'PASS', compared_fixtures=len(expected),
                failures=failures, qualification='PHASE_A_COMPARISON_ONLY')


def rename_fixture(fixture, renaming):
    transformed = copy.deepcopy(fixture)
    for side in ('left', 'right'):
        snapshot = transformed['snapshots'][side]
        mapping = renaming[side]
        snapshot['vertices'] = [mapping.get(v, v) for v in snapshot['vertices']]
        snapshot['occurrences'] = [mapping[v] for v in snapshot['occurrences']]
        snapshot['incidence'] = [[mapping.get(a, a), mapping.get(b, b)] for a, b in snapshot['incidence']]
    for record in transformed['evidence']:
        record['source'] = renaming['left'][record['source']]
        record['target'] = renaming['right'][record['target']]
        record['provenance']['scope']['source'] = record['source']
        record['provenance']['scope']['target'] = record['target']
    return transformed


def transport_json(value, mapping):
    """Test transport over concrete handles, including preservation conjunct IDs."""
    if isinstance(value, str):
        if value.startswith('preserve:'):
            return 'preserve:' + mapping.get(value[9:], value[9:])
        return mapping.get(value, value)
    if isinstance(value, list):
        return [transport_json(v, mapping) for v in value]
    if isinstance(value, dict):
        return {mapping.get(k, k): transport_json(v, mapping) for k, v in value.items()}
    return value


def self_test(manifest):
    """Small bounded validation; failures accumulate and cause exit status 1."""
    candidates, materials, _ = catalog(manifest)
    failures, checks = [], []
    coverage = dict(named_candidate_variants=dict(completed=0, required=17),
                    assessment_sensitivity=dict(completed=0, required=2),
                    material_association_inputs=dict(completed=0, required=1),
                    named_material_variants=dict(completed=0, required=7),
                    record_orders=dict(completed=0, required=23),
                    record_duplications=dict(completed=0, required=8),
                    accepted_polarity_instance_configurations=dict(completed=0, required=524288),
                    candidate_label_renamings=dict(completed=0, required=468),
                    material_label_renamings=dict(completed=0, required=144),
                    vertex_layouts=dict(completed=0, required=2304),
                    association_presentation_orders=dict(completed=0, required=2160),
                    outcome_presentation_orders=dict(completed=0, required=2))
    work = dict(relation_classifications=0, material_assignment_checks=0,
                material_union_assignment_checks=0)
    cached_candidates, cached_materials = {}, {}

    def candidate(fixture):
        result = evaluate_candidate(fixture)
        work['relation_classifications'] += result['relations_examined']
        return result

    def material(case, fixture, result):
        output = evaluate_material(case, fixture, result)
        work['material_assignment_checks'] += output['assignments_examined']
        work['material_union_assignment_checks'] += output.get('union_assignments_examined', 0)
        return output

    def run(name, operation, suite=None):
        if suite:
            coverage[suite]['completed'] += 1
        try:
            operation()
        except Exception as error:  # Each check must remain visible, including unexpected failures.
            failures.append(dict(check=name, error=type(error).__name__, detail=str(error)))
        else:
            checks.append(name)

    def named_candidate(fixture):
        result = candidate(fixture)
        cached_candidates[fixture['id']] = result
        check_candidate_expectation(fixture, result)

    for fixture in expand(manifest['candidate_fixtures']):
        run(fixture['id'], lambda f=fixture: named_candidate(f), 'named_candidate_variants')
    for fixture in manifest['sensitivity_cases']:
        run(fixture['id'], lambda f=fixture: named_candidate(f), 'assessment_sensitivity')
    for fixture in manifest['material_association_fixtures']:
        run(fixture['id'], lambda f=fixture: named_candidate(f), 'material_association_inputs')

    def named_material(case):
        fixture = candidates[case['candidate_fixture']]
        result = material(case, fixture, cached_candidates[fixture['id']])
        cached_materials[case['id']] = result
        check_material_expectation(case, fixture, result)

    for case in materials.values():
        run(case['id'], lambda m=case: named_material(m), 'named_material_variants')

    def record_variant(identifier, records):
        fixture = copy.deepcopy(candidates[identifier])
        fixture['evidence'] = list(records)
        check_candidate_expectation(fixture, candidate(fixture))

    for identifier in ('F02', 'F03', 'F06', 'F07', 'F08', 'F10', 'F11', 'F14'):
        records = candidates[identifier]['evidence']
        # Permutations here reorder evidence presentations only, never candidates.
        for index, order in enumerate(itertools.permutations(records)):
            run(f'{identifier}/record-order-{index}',
                lambda i=identifier, r=order: record_variant(i, r), 'record_orders')
        repeated = [e for record in records for e in (record, copy.deepcopy(record))]
        run(identifier + '/repeated-records',
            lambda i=identifier, r=repeated: record_variant(i, r), 'record_duplications')

    def layout(identifier):
        fixture = copy.deepcopy(candidates[identifier])
        for snapshot in fixture['snapshots'].values():
            snapshot['vertices'].reverse()  # Both designated roots now stored last.
        require(candidate(fixture) == cached_candidates[identifier], 'root/layout-dependent result')

    for identifier in ('F01', 'F09', 'F10', 'F11'):
        run(identifier + '/roots-stored-last', lambda i=identifier: layout(i), 'vertex_layouts')

    def move_boundary():
        fixture = copy.deepcopy(candidates['F11'])
        fixture['profile'] = 'S_inc'
        fixture['assumes_unchanged_incidence'] = True
        result = candidate(fixture)
        require(result['counts'] == dict(U_H=6, C_E=1, A_E=0), 'MOVE did not violate incidence preservation')
        require(result['diagnostics'] == ['STRUCTURALLY_UNSATISFIABLE'], 'MOVE evidence misdiagnosed')
        witnesses = [p['association'] for p in result['predicates'] if p['structure_satisfied']]
        require(witnesses == [expected_relation('210', fixture)], 'MOVE endpoint isomorphism mismatch')

    run('F11/separate-incidence-countercheck', move_boundary)

    def renamings(fixture):
        left, right = (fixture['snapshots'][s]['occurrences'] for s in ('left', 'right'))
        return dict(left=dict(zip(left, left[1:] + left[:1])),
                    right=dict(zip(right, list(reversed(right)))))

    def candidate_renaming():
        fixture = candidates['F11']
        mapping = renamings(fixture)
        result = candidate(rename_fixture(fixture, mapping))
        wanted = transport_json(cached_candidates['F11'], {**mapping['left'], **mapping['right']})
        require(normalize_comparison(result) == normalize_comparison(wanted), 'candidate equivariance failure')

    run('F11/independent-label-renaming', candidate_renaming, 'candidate_label_renamings')

    def material_renaming():
        case = copy.deepcopy(materials['M03'])
        fixture = candidates[case['candidate_fixture']]
        mapping = renamings(fixture)
        renamed = rename_fixture(fixture, mapping)
        for side in ('left', 'right'):
            case['initial'][side] = {mapping[side][k]: v for k, v in case['initial'][side].items()}
        for update in case['updates']:
            update['target'] = mapping[update['side']][update['target']]
        result = material(case, renamed, candidate(renamed))
        wanted = transport_json(cached_materials['M03'], {**mapping['left'], **mapping['right']})
        require(normalize_comparison(result) == normalize_comparison(wanted), 'material equivariance failure')

    run('M03/independent-label-renaming', material_renaming, 'material_label_renamings')

    def association_order():
        case = materials['M02']
        fixture = candidates[case['candidate_fixture']]
        result = copy.deepcopy(cached_candidates[fixture['id']])
        result['candidate_sets']['A_E'].reverse()
        require(material(case, fixture, result) == cached_materials['M02'], 'association order dependence')

    run('M02/reversed-six-association-order', association_order, 'association_presentation_orders')

    def decision_order():
        case = copy.deepcopy(materials['M04'])
        case['policy']['decisions'].reverse()
        fixture = candidates[case['candidate_fixture']]
        require(material(case, fixture, cached_candidates[fixture['id']]) == cached_materials['M04'],
                'decision order selected/lost an authorized outcome')

    run('M04/reversed-policy-decision-order-smoke', decision_order)

    def distinct_repeated_attestations():
        fixture = copy.deepcopy(candidates['F02'])
        record = copy.deepcopy(fixture['evidence'][0])
        record['id'] += '/independent-attestation'
        fixture['evidence'].append(record)
        check_candidate_expectation(fixture, candidate(fixture))

    run('F02/distinct-ID-same-polarity-attestation', distinct_repeated_attestations)

    def missing_not_rejected():
        require(cached_candidates['F01']['counts'] == cached_candidates['F05']['counts'],
                'REJECTED evidence became a negation')
        require('MISSING_EVIDENCE' not in cached_candidates['F05']['diagnostics'],
                'present rejected evidence was called missing')
        require(cached_candidates['F12']['conditional'], 'unresolved evidence hidden')
        require(equivalent(dict(tag='REJECT'), dict(tag='REJECT'), 'undeclared') is None,
                'undefined observable equated to a defined observation')
        require(cached_materials['M05-O']['associations'] == cached_materials['M01']['associations'],
                'undefined query discarded valid material witnesses')
        require(cached_materials['M05-I']['policy_status'] == 'SUPPORTED' and
                cached_materials['M05-I']['observable_status'] == 'DEFINED' and
                cached_materials['M05-I']['scientific_claim'] == 'INCONCLUSIVE',
                'incomplete comparison confused with unsupported policy/rejection')

    run('diagnostic-boundaries', missing_not_rejected)

    def malformed_boundary():
        fixture = copy.deepcopy(candidates['F09'])
        fixture['assumes_unchanged_incidence'] = False
        result = candidate(fixture)
        require(result['candidate_sets'] is None and result['relations_examined'] == 0,
                'undeclared incidence restriction silently used')
        case = copy.deepcopy(materials['M04'])
        case['policy']['decisions'][0]['waived'] = []
        source = candidates[case['candidate_fixture']]
        result = material(case, source, cached_candidates[source['id']])
        require(result['policy_status'] == 'UNSUPPORTED' and result['associations'] is None,
                'incomplete retention policy certified an outcome')

    run('malformed-policy-and-profile-boundaries', malformed_boundary)

    def comparison_boundaries():
        reference = dict(schema='ste-exp007-reference-v1', protocol_sha256=PROTOCOL_SHA256,
                         results=[dict(id='F02', candidate=cached_candidates['F02']),
                                  dict(id='M04', candidate=cached_candidates['M04-association'],
                                       material=cached_materials['M04'])])
        submitted = copy.deepcopy(reference)
        submitted['results'].reverse()
        for row in submitted['results']:
            for phis in row['candidate']['candidate_sets'].values():
                phis.reverse()
                for phi in phis:
                    phi.reverse()
        # Tested-side generation and material construction have different work.
        submitted['results'][0]['candidate']['relations_examined'] = 6
        submitted['results'][0]['material'].pop('assignments_examined')
        for association in submitted['results'][0]['material']['associations']:
            for decision in association['decisions']:
                decision.pop('assignments_examined')
        require(compare_results(reference, submitted)['status'] == 'PASS', 'comparison depends on order')
        bad = copy.deepcopy(submitted)
        bad['results'][0]['material']['associations'][0]['decisions'].pop()
        require(compare_results(reference, bad)['status'] == 'FAIL', 'omitted material alternative undetected')
        bad = copy.deepcopy(submitted)
        rows = bad['results'][1]['candidate']['candidate_sets']['A_E']
        rows.append(copy.deepcopy(rows[0]))
        require(any(f.get('kind') == 'DUPLICATES' for f in compare_results(reference, bad)['failures']),
                'duplicate candidate not reported')
        bad = copy.deepcopy(submitted)
        bad['results'][1]['candidate']['candidate_sets']['C_E'].pop()
        require(any(f.get('false_negatives') for f in compare_results(reference, bad)['failures']),
                'candidate false negative not reported')
        bad = copy.deepcopy(submitted)
        bad['results'][1]['candidate']['candidate_sets']['A_E'][0][0].reverse()
        require(compare_results(reference, bad)['status'] == 'FAIL', 'pair orientation ignored')
        outcomes = copy.deepcopy(reference['results'][1]['material']['associations'][0]['outcomes'])
        require(outcomes[0]['outcome'] != outcomes[1]['outcome'], 'M04 lost an observable alternative')
        # The second outcome order of the named M04 presentation suite.
        bad = copy.deepcopy(reference)
        bad['results'][1]['material']['associations'][0]['outcomes'].reverse()
        require(compare_results(reference, bad)['status'] == 'PASS', 'outcome order affected comparison')

    run('comparison-contract-and-M04-reversed-outcome-order', comparison_boundaries, 'outcome_presentation_orders')

    def malformed_comparison(field, value):
        submitted = dict(schema='ste-exp007-reference-v1', protocol_sha256=PROTOCOL_SHA256,
                         results=[dict(id='M04', candidate=cached_candidates['M04-association'],
                                       material=cached_materials['M04'])])
        submitted['results'][0][field] = value
        # Exercise the real CLI and JSON reader; keep all temporary input outside the repository.
        with tempfile.TemporaryDirectory(prefix='exp007-malformed-', dir='/tmp') as directory:
            path = Path(directory) / 'comparison.json'
            path.write_text(stable(submitted), encoding='utf-8')
            process = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                                      '--fixture', 'M04', '--compare', str(path)],
                                     text=True, capture_output=True, check=False)
        require(process.returncode == 2, 'malformed comparison must exit 2')
        require(process.stdout == '', 'malformed comparison emitted a result envelope')
        require(json.loads(process.stderr) ==
                dict(status='UNSUPPORTED', diagnostics=['INVALID_INPUT'],
                     reason='comparison ' + field + ' must be an object',
                     qualification='NOT_QUALIFIED_PHASE_A'),
                'malformed comparison diagnostic JSON mismatch')

    for field in ('candidate', 'material'):
        for label, value in (('null', None), ('array', [])):
            run('CLI/' + field + '-' + label,
                lambda f=field, v=value: malformed_comparison(f, v))
    return dict(status='FAIL' if failures else 'PASS', scope='PHASE_A_BOUNDED_SELF_CHECKS_ONLY',
                completed_checks=len(checks) + len(failures), passed_checks=len(checks),
                failed_checks=len(failures), failures=failures, checks_passed=checks,
                coverage=coverage, measured_work=work,
                skipped_suites=['Complete accepted-polarity matrix', 'Remaining frozen transformation cases',
                                'Independent C11 comparison', 'Full EXP-007 qualification'],
                scientific_claim='INCONCLUSIVE', EXP004_historical_completeness='INCONCLUSIVE',
                EXP004_material_equivalence='CALLER_ASSUMPTION')


def metadata(manifest_path):
    try:
        revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=BASE,
                                  text=True, capture_output=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        revision = 'UNAVAILABLE'
    return dict(freeze_commit=FREEZE_COMMIT, code_revision=revision,
                oracle_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                manifest_sha256=hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest(),
                python=sys.version.split()[0], compiler='NOT_APPLICABLE_PHASE_A',
                c11_flags='NOT_RUN', command=[sys.executable, '-B', *sys.argv])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--manifest', type=Path, default=BASE / 'EXP007_FIXTURES.json')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--list', action='store_true', help='list bounded fixture IDs without enumeration')
    action.add_argument('--self-test', action='store_true', help='bounded phase A checks; no full campaign')
    action.add_argument('--fixture', nargs='+', metavar='ID', help='emit selected exact sets and certificates')
    parser.add_argument('--compare', type=Path, help='compare a future C11 result JSON for the selected IDs')
    args = parser.parse_args(argv)
    if args.compare and not args.fixture:
        parser.error('--compare requires --fixture')
    try:
        manifest = load_manifest(args.manifest)
        candidates, materials, groups = catalog(manifest)
        envelope = dict(schema='ste-exp007-reference-v1', protocol_sha256=PROTOCOL_SHA256,
                        metadata=metadata(args.manifest), qualification='NOT_QUALIFIED_PHASE_A')
        if args.list:
            envelope['fixtures'] = sorted(set(candidates) | set(materials) | set(groups))
        elif args.self_test:
            envelope['self_test'] = self_test(manifest)
        else:
            identifiers = [case for name in args.fixture for case in groups.get(name, [name])]
            require(len(identifiers) <= MAX_CASES and len(set(identifiers)) == len(identifiers),
                    'fixture selections must be distinct and bounded')
            require(all(i in candidates or i in materials for i in identifiers), 'unknown fixture selection')
            envelope['results'] = [evaluate_named(i, candidates, materials) for i in identifiers]
            if args.compare:
                envelope['comparison'] = compare_results(envelope, read_json(args.compare))
        print(json.dumps(envelope, indent=2, sort_keys=True))
        if args.self_test:
            return int(envelope['self_test']['status'] != 'PASS')
        if args.compare:
            return int(envelope['comparison']['status'] != 'PASS')
        return 0
    except (InvalidInput, KeyError, TypeError, ValueError, OSError) as error:
        print(json.dumps(dict(status='UNSUPPORTED', diagnostics=['INVALID_INPUT'], reason=str(error),
                              qualification='NOT_QUALIFIED_PHASE_A')), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
