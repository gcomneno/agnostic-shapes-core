#!/usr/bin/env python3
"""Reproducible, nonnormative STE EXP-007 orchestrator (standard library only).

No action is the default. Examples (all output directories must be external):
  python3 -B tools/research/ste_001/exp007_run.py validate
  python3 -B tools/research/ste_001/exp007_run.py dry-run --out /tmp/exp007-dry
  python3 -B tools/research/ste_001/exp007_run.py campaign --execute --out /tmp/exp007-run
  python3 -B tools/research/ste_001/exp007_run.py resume --execute --out /tmp/exp007-run
  python3 -B tools/research/ste_001/exp007_run.py audit --out /tmp/exp007-run
  python3 -B tools/research/ste_001/exp007_run.py replay --execute --run /tmp/exp007-run \
      --case-id EXP007/C/V1/named_materials/M03/000000 --out /tmp/exp007-replay

campaign/resume --max-cases N deliberately stop after at most N NEW receipts,
without changing the frozen schedule. dry-run runs exactly the plan's twenty
matrix probes, in a separate namespace with ZERO campaign credit. A successful
command/process is not scientific acceptance. Exit 0: bounded command completed;
1: discrepancy/operational failure; 2: CLI/identity/integrity failure; 3: blocked
obligation or partial campaign. A complete scientific verdict requires replay
confirmation of discrepancies and every frozen/derived gate, not process success.

The two M04 outcome-order cases use an independent Python ordered consumer
before observation/partitioning; both sides' complete actual receipts are
checked separately from extensional results. Aggregate acceptance enumerates
every frozen requirement from audited evidence. Final reporting qualification
and automatic scientific counterexample certification remain unavailable.
Replay retains exact deltas for human triage. Audit exit codes retain their
integrity/comparison meaning; inspect acceptance separately from exit status.

Storage: exclusively created immutable blobs/chunks; append-only hash-chained
index.jsonl; fsync files and parent directories before checkpoint credit.
Sequential schedule-prefix credit permits constant-memory uniqueness checks.
A torn index/chunk, missing ordinal, identity drift or changed receipt fails
closed; no truncation, deletion, repair or automatic cleanup. Unindexed crash
artifacts are retained and never credited. An exclusive flock on metadata.json
serializes writers/readers. This is local POSIX crash safety, not adversarial
tamper-proof storage or a claim about an unsynchronized remote filesystem.

The archived sources/exp007_run.py can audit/resume/replay its own evidence
even after the working driver's revision changes; it verifies the saved
artifacts and executable identities without regenerating different inputs.

Each process receives at most 16 cases; every JSON envelope <=2,000,000 bytes.
Raw files are bounded per process, never by a campaign-wide evidence quota.
Inputs, traces and comparisons are read one case at a time. Retries, replay,
dry-run, baseline recomputation, actual work and logical coverage are separate.
No network, repository products, production APIs, SHAPES/PETRA/TPI changes,
historical-data rewriting, or promotion of research semantics.
EXP-004 remains INCONCLUSIVE / CALLER_ASSUMPTION.
"""

import argparse
import copy
import datetime
import fcntl
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
REL = 'tools/research/ste_001/'
# Published source provenance, not the revision of this driver or a future fix.
BASELINE = 'e33db15d8f95499337409151d6063127734e079e'
PLAN_HASH = 'f817bb6267f8eee2ddcc3bc24de498e00d19a412599d3df3ff31ce79f2e592bf'
LIMIT = 2_000_000
BATCH = 16
FLAGS = ['-std=c11', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-O2']
CURRENT_PINS = {
    'exp007_campaign.c': '4e78410f97e10c977d62b5f5b56449097e18100eb886e3262c454b119636eb06',
    'exp007_c_adapter.c': '041b0b8959fea236c67048bfb86cf41a17010c176b0d1b72e94c9d047897e8ec',
    'exp007_reference_adapter.py': '09d94b196c577d52907d6487e863bfdc5b2e826c1bb3f02d82c515a732940b7f',
    'test_exp007.c': '753ce10bb5e8c90c5af2e9abbdeb2f84c089c47fb1211d16b2dadcf3cdb7fed2',
}
ORDER_SUITES = {'record_orders', 'record_duplications', 'association_orders',
                'material_outcome_orders'}
# Immutable published content pins remain separate from Git commit identity.
BASELINE_PINS = {
    'exp007_reference_adapter.py': '09d94b196c577d52907d6487e863bfdc5b2e826c1bb3f02d82c515a732940b7f',
}
BLOCKED = [{
    'obligation': 'complete_scientific_acceptance',
    'missing_contract': 'Verified final EXP007_RESULTS.md / exp007_evidence.json reporting of bounded model-relative scope and all frozen limitations',
    'effect': 'Frozen full_acceptance.required[10] remains UNVERIFIED; aggregate acceptance is BLOCKED',
}, {
    'obligation': 'automatic_scientific_counterexample_certification',
    'missing_contract': 'Independent review of input/oracle/transport/replay validity and semantic versus harness triage',
    'effect': 'A reproducible discrepancy is NEGATIVE_RESULT_PENDING_TRIAGE, not a certified scientific counterexample',
}]


class IntegrityError(ValueError):
    """Evidence cannot be credited; preserve it unchanged."""


def require(condition, message):
    if not condition:
        raise IntegrityError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def keys_unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key: ' + key)
        value[key] = item
    return value


def decode(raw):
    require(len(raw) <= LIMIT, 'envelope exceeds 2000000 bytes')
    return json.loads(raw, object_pairs_hook=keys_unique,
                      parse_constant=lambda v: (_ for _ in ()).throw(IntegrityError('nonfinite JSON: ' + v)))


def read_small(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, 'oversized artifact: ' + str(path))
    return raw


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            value.update(block)
    return value.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def git(*argv):
    return subprocess.run(['git', *argv], cwd=ROOT, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def load_module(name, path):
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name, path))
    exec(compile(read_small(path), str(path), 'exec'), module.__dict__)
    return module


class Contract:
    def __init__(self, base=BASE):
        self.base = Path(base)
        plan_raw = read_small(self.base / 'EXP007_CAMPAIGN_PLAN.json')
        require(digest(plan_raw) == PLAN_HASH, 'frozen plan drift')
        self.plan = decode(plan_raw)
        self.hashes = {'EXP007_CAMPAIGN_PLAN.json': PLAN_HASH, **CURRENT_PINS}
        for artifact in self.plan['implementation_identity']['read_only_artifacts']:
            name = Path(artifact['path']).name
            if name != 'test_exp007.c':
                self.hashes[name] = artifact['sha256']
        for name, sha in self.hashes.items():
            require(file_hash(self.base / name) == sha, 'source identity drift: ' + name)
        self.ref = load_module('_exp007_independent_reference', self.base / 'exp007_reference.py')
        self.outcome_adapter = load_module('_exp007_ordered_reference', self.base / 'exp007_reference_adapter.py')
        self.manifest = self.ref.load_manifest(self.base / 'EXP007_FIXTURES.json')
        self.candidates, self.materials, _ = self.ref.catalog(self.manifest)
        self.suites = self.plan['suites']
        require([s['id'] for s in self.suites] == self.plan['execution']['suite_order'],
                'suite order drift')
        require(sum(s['required_cases'] or 0 for s in self.suites
                    if s['in_frozen_suite_total']) == 529423, 'primary count drift')
        require(sum(s['required_cases'] or 0 for s in self.suites) == 529424,
                'auxiliary count drift')

    def count(self, suite, identifier):
        if suite['id'].startswith('matrix_'):
            return 262144
        if suite['id'] == 'derived_observable_equivalence_laws':
            return 22764
        if suite['id'] == 'record_orders':
            return math.factorial(len(self.candidates[identifier]['evidence']))
        count = suite.get('cases_per_fixture', 1)
        return count if isinstance(count, int) else count[suite['fixture_ids'].index(identifier)]

    def schedule(self, mode):
        ordinal = 0
        if mode == 'dry-run':
            for instance in self.plan['dry_run']['instance_order']:
                suite = next(s for s in self.suites if s.get('instance_id') == instance)
                token = self.plan['input_encoding']['record_emission']['instance_tokens'][instance]
                for rank in self.plan['dry_run']['config_ids']:
                    row = self.descriptor(suite, instance, rank, ordinal)
                    row.update(case_id=f'EXP007/C/V1/DRY-RUN/{token}/{rank:06d}',
                               count_class='DRY_RUN')
                    yield row
                    ordinal += 1
            return
        for suite in self.suites:
            ids = suite.get('fixture_ids', [suite.get('instance_id', 'Q')])
            for identifier in ids:
                for rank in range(self.count(suite, identifier)):
                    yield self.descriptor(suite, identifier, rank, ordinal)
                    ordinal += 1

    def descriptor(self, suite, identifier, rank, ordinal):
        law = suite['id'] == 'derived_observable_equivalence_laws'
        case_id = f"EXP007/C/V1/{suite['id']}/{identifier}/{rank:06d}"
        if law:
            kind, ranks = law_ranks(rank)
            case_id = ('EXP007/C/V1/derived-observable-laws/' + kind + '/' +
                       '/'.join(str(v) if v is not None else 'na' for v in ranks))
        return dict(case_id=case_id, global_ordinal=ordinal if not law else None,
                    schedule_ordinal=ordinal, suite_id=suite['id'], selector=identifier,
                    variant_rank=rank, count_class='DERIVED' if law else
                    'PRIMARY' if suite['in_frozen_suite_total'] else 'AUXILIARY')

    def materialize(self, case):
        suite, identifier, rank = case['suite_id'], case['selector'], case['variant_rank']
        if suite == 'derived_observable_equivalence_laws':
            kind, ranks = law_ranks(rank)
            return dict(original=None, transformed=None, transformation=None,
                        law=dict(law=kind, ranks=ranks,
                                 operands=[law_operand(r) for r in ranks if r is not None]))
        is_matrix = suite.startswith('matrix_')
        if is_matrix:
            declared = next(s for s in self.suites if s['id'] == suite)
            fixture = self.candidates[declared['original_candidate_fixture']]
            material = None
        else:
            material = self.materials.get(identifier)
            fixture = self.candidates[material['candidate_fixture'] if material else identifier]
        original = {k: copy.deepcopy(fixture[k]) for k in
                    ('snapshots', 'profile', 'assumes_unchanged_incidence', 'evidence')}
        original['material'] = None if material is None else {
            k: copy.deepcopy(v) for k, v in material.items() if k != 'expected'}
        transformed = copy.deepcopy(original)
        maps = {s: {h: h for h in [fixture['snapshots'][s]['root'],
                                   *fixture['snapshots'][s]['occurrences']]} for s in ('left', 'right')}
        record_order, association_order, outcome_order = None, None, None
        if is_matrix:
            transformed['evidence'] = self.matrix_records(identifier, rank)
        elif suite == 'record_orders':
            record_order = permutation(len(original['evidence']), rank)
            transformed['evidence'] = [copy.deepcopy(original['evidence'][i]) for i in record_order]
        elif suite == 'record_duplications':
            record_order = [i for i in range(len(original['evidence'])) for _ in range(2)]
            transformed['evidence'] = [copy.deepcopy(original['evidence'][i]) for i in record_order]
        elif suite in ('candidate_relabelings', 'material_relabelings'):
            for side, subrank in zip(('left', 'right'), (rank // 6, rank % 6)):
                occurrences = fixture['snapshots'][side]['occurrences']
                maps[side].update(zip(occurrences, [occurrences[i] for i in permutation(3, subrank)]))
            # Transport only typed handle references; never arbitrary text.
            renamed = self.ref.rename_fixture(dict(id=fixture['id'], **{
                k: original[k] for k in ('snapshots', 'profile', 'assumes_unchanged_incidence', 'evidence')}), maps)
            transformed.update({k: renamed[k] for k in
                                ('snapshots', 'profile', 'assumes_unchanged_incidence', 'evidence')})
            if material:
                for side in ('left', 'right'):
                    transformed['material']['initial'][side] = {
                        maps[side][h]: v for h, v in original['material']['initial'][side].items()}
                for update in transformed['material']['updates']:
                    update['target'] = maps[update['side']][update['target']]
        elif suite == 'vertex_layouts':
            for side, subrank in zip(('left', 'right'), (rank // 24, rank % 24)):
                vertices = original['snapshots'][side]['vertices']
                transformed['snapshots'][side]['vertices'] = [vertices[i] for i in permutation(4, subrank)]
        elif suite == 'association_orders':
            association_order = permutation(6, rank)
        elif suite == 'material_outcome_orders':
            outcome_order = permutation(2, rank)
        transform = dict(suite=suite, left_transport=maps['left'], right_transport=maps['right'],
                         left_inverse={v: k for k, v in maps['left'].items()},
                         right_inverse={v: k for k, v in maps['right'].items()},
                         left_vertex_layout=transformed['snapshots']['left']['vertices'],
                         right_vertex_layout=transformed['snapshots']['right']['vertices'], composed=False)
        return dict(original=original, transformed=transformed, transformation=transform,
                    record_order=record_order, association_order=association_order,
                    outcome_order=outcome_order)

    def matrix_records(self, instance, config):
        encoding = self.plan['input_encoding']
        emission = encoding['record_emission']
        token = emission['instance_tokens'][instance]
        records, states = [], [(config // 4**i) % 4 for i in range(9)]
        require(sum(state * 4**i for i, state in enumerate(states)) == config, 'base4 round trip')
        for i, state in enumerate(states):
            source, target = encoding['pair_order'][i]
            for polarity in encoding['states'][state]['emitted_polarities']:
                fields = dict(instance_token=token, config_id=config, i=i, polarity=polarity)
                provenance = emission['provenance']
                records.append(dict(id=emission['id_format'].format(**fields), source=source,
                                    target=target, polarity=polarity, assessment='ACCEPTED',
                                    provenance=dict(origin=provenance['origin'],
                                        source=provenance['source_format'].format(**fields),
                                        assessment_rule=provenance['assessment_rule'],
                                        assumed_trust=provenance['assumed_trust'],
                                        scope=dict(snapshots=['snapshot_L', 'snapshot_R'],
                                                   source=source, target=target))))
        return records


def permutation(n, rank):
    require(0 <= rank < math.factorial(n), 'permutation rank out of bounds')
    return list(next(itertools.islice(itertools.permutations(range(n)), rank, None)))


def law_ranks(rank):
    require(0 <= rank < 22764, 'law rank out of bounds')
    if rank < 28:
        return 'REFLEXIVITY', [rank, None, None]
    if rank < 812:
        return 'SYMMETRY', [(rank - 28) // 28, (rank - 28) % 28, None]
    rank -= 812
    return 'TRANSITIVITY', [rank // 784, rank // 28 % 28, rank % 28]


def law_operand(rank):
    if rank == 0:
        return dict(tag='REJECT')
    values = list(itertools.product(('0', 'lambda', 'rho'), repeat=3))[rank - 1]
    return dict(tag='ACCEPT', material=dict(zip(('l0', 'l1', 'l2'), values)))


class ObservedList(list):
    """Record actual yield order at the independent Python function boundary.

    Multiple validation/filter/assessment traversals stay separate, including
    short-circuit prefixes. No requested order is substituted for observed work.
    """
    def __init__(self, values, log):
        super().__init__(values)
        self.log = log

    def __iter__(self):
        visit = []
        self.log.append(visit)
        for position in range(len(self)):
            value = self[position]
            visit.append(dict(position=position, value=copy.deepcopy(value)))
            yield value

    def __deepcopy__(self, memo):
        return [copy.deepcopy(self[i], memo) for i in range(len(self))]


def reference_evaluate(contract, case, inputs):
    """Adapt existing independent oracle; do not implement a second solver."""
    ref = contract.ref
    if case['count_class'] == 'DERIVED':
        operands = inputs['law']['operands']
        pairs = [(0, 0)] if len(operands) == 1 else [(0, 1), (1, 0)] if len(operands) == 2 else [(0, 1), (1, 2), (0, 2)]
        verdicts = [ref.equivalent(operands[a], operands[b]) for a, b in pairs]
        exact = [operands[a] == operands[b] for a, b in pairs]
        return dict(law=dict(law=inputs['law']['law'], operands=[dict(rank=r, observable=o)
                    for r, o in zip([r for r in inputs['law']['ranks'] if r is not None], operands)],
                    operation_results=verdicts, expected_results=exact,
                    law_holds=verdicts[0] if len(verdicts) == 1 else
                        verdicts[0] == verdicts[1] if len(verdicts) == 2 else
                        not (verdicts[0] and verdicts[1]) or verdicts[2],
                    operation_matches_extensional_equality=verdicts == exact),
                    work=dict(law_checks=1, law_equivalence_calls=len(pairs)))
    value = copy.deepcopy(inputs['transformed'])
    material = value.pop('material')
    records, associations = [], []
    consumption = dict(record_hook='ObservedList/actual-yield-to-reference',
                       association_hook='ObservedList/actual-yield-to-evaluate_material',
                       record_iterations=records, association_iterations=associations,
                       outcome_hook=None, partition_called=False, outcome_complete=False,
                       consumed_outcomes=[])
    outcome_work = {}
    value['evidence'] = ObservedList(value['evidence'], records)
    candidate = ref.evaluate_candidate(value)
    result = dict(id=case['selector'], candidate=candidate)
    if material is not None:
        material_candidate = copy.deepcopy(candidate)
        ordered_relations = material_candidate['candidate_sets']['A_E']
        if inputs['association_order'] is not None:
            # Only the frozen presentation basis; not a generator/filter oracle.
            basis = next(s for s in contract.suites if s['id'] == 'association_orders')['association_order_basis']
            fixture = inputs['original']
            declared = [ref.expected_relation(code, fixture) for code in basis]
            require(ref.ordered(ordered_relations) == ref.ordered(declared), 'association order domain differs')
            # Reorder independently recognized relations themselves. The frozen
            # basis selects presentation positions, never supplies solver rows.
            by_relation = {canonical(sorted(relation)): relation for relation in ordered_relations}
            ordered_relations = [by_relation[canonical(sorted(declared[i]))] for i in inputs['association_order']]
        material_candidate['candidate_sets']['A_E'] = ObservedList(ordered_relations, associations)
        if case['suite_id'] == 'material_outcome_orders':
            require(case['selector'] == 'M04' and case['variant_rank'] in (0, 1)
                    and inputs['outcome_order'] == permutation(2, case['variant_rank']),
                    'unsupported M04 outcome-order obligation')
            result['material'] = contract.outcome_adapter.evaluate_m04_outcome_order(
                ref, material, value, material_candidate, inputs['outcome_order'],
                consumption=consumption, work=outcome_work)
        else:
            result['material'] = ref.evaluate_material(material, value, material_candidate)
    work = dict(reference_relation_classifications=candidate['relations_examined'],
                candidates_generated=0 if candidate['counts'] is None else candidate['counts']['U_H'],
                candidate_evaluations=0 if candidate['counts'] is None else candidate['counts']['U_H'],
                decision_assignment_checks=result.get('material', {}).get('assignments_examined', 0),
                union_assignment_checks=result.get('material', {}).get('union_assignments_examined', 0),
                **outcome_work)
    baseline = None
    if case['suite_id'] in ('record_orders', 'record_duplications', 'candidate_relabelings',
                            'material_relabelings', 'vertex_layouts', 'association_orders', 'material_outcome_orders'):
        original = copy.deepcopy(inputs['original'])
        original_material = original.pop('material')
        base_candidate = ref.evaluate_candidate(original)
        baseline = dict(id=case['selector'], candidate=base_candidate)
        work['baseline_relation_classifications'] = base_candidate['relations_examined']
        work['baseline_candidate_evaluations'] = base_candidate['counts']['U_H']
        work['baseline_candidates_generated'] = base_candidate['counts']['U_H']
        work['baseline_recomputations'] = 1
        if original_material:
            baseline['material'] = ref.evaluate_material(original_material, original, base_candidate)
            work['baseline_decision_assignment_checks'] = baseline['material']['assignments_examined']
            work['baseline_union_assignment_checks'] = baseline['material'].get('union_assignments_examined', 0)
    return dict(result=result, baseline=baseline, consumption=consumption, work=work)


def internal_reference():
    contract = Contract()
    ordinal = 0
    while True:
        line = sys.stdin.buffer.readline(LIMIT + 1)
        if not line:
            break
        require(line.endswith(b'\n') and len(line) <= LIMIT, 'truncated/oversized independent reference input')
        ordinal += 1
        request = decode(line)
        output = reference_evaluate(contract, request['case'], request['inputs'])
        output.update(schema='ste-exp007-run-reference-v1', request_id=request['request_id'],
                      request_index=ordinal, response_id=ordinal, status='EVALUATED',
                      case_id=request['case']['case_id'], protocol_sha256=contract.plan['protocol']['sha256'],
                      plan_sha256=PLAN_HASH, work_complete=True)
        raw = canonical(output) + b'\n'
        require(len(raw) <= LIMIT, 'reference envelope overflow')
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
    return 0


def diff(expected, actual, path='$'):
    """Deterministic first concrete delta; raw outputs preserve every later one."""
    if type(expected) is not type(actual):
        return dict(path=path, kind='TYPE', expected=expected, actual=actual)
    if isinstance(expected, dict):
        for key in sorted(set(expected) | set(actual)):
            if key not in expected or key not in actual:
                return dict(path=path + '.' + key, kind='MISSING_OR_EXTRA_FIELD',
                            expected=expected.get(key), actual=actual.get(key))
            found = diff(expected[key], actual[key], path + '.' + key)
            if found:
                return found
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            return dict(path=path, kind='LENGTH', expected=expected, actual=actual)
        for i, (left, right) in enumerate(zip(expected, actual)):
            found = diff(left, right, f'{path}[{i}]')
            if found:
                return found
    elif expected != actual:
        return dict(path=path, kind='VALUE', expected=expected, actual=actual)
    return None


def identity_duplicates(value, path='$'):
    problems = []
    if isinstance(value, dict):
        for key, rows in value.items():
            identity = {'decisions': 'id', 'associations': 'association', 'predicates': 'association',
                        'witnesses': 'material', 'rejection_certificate': 'material',
                        'observable_classes': 'observable'}.get(key)
            if identity and isinstance(rows, list):
                seen = {}
                for position, row in enumerate(rows):
                    marker = canonical(row[identity])
                    if marker in seen:
                        problems.append(dict(path=path + '.' + key, kind='DUPLICATE_IDENTITY',
                                             positions=[seen[marker], position], value=row))
                    seen[marker] = position
            problems.extend(identity_duplicates(rows, path + '.' + key))
    elif isinstance(value, list):
        for i, row in enumerate(value):
            problems.extend(identity_duplicates(row, f'{path}[{i}]'))
    return problems


def presentation_equal(expected, actual, path):
    # Lists deliberately retain order here. This is independent of extensional
    # scientific normalization and catches receipt/input-consumption defects.
    found = diff(expected, actual, path)
    return [] if found is None else [found]


def input_equal(expected, actual, path):
    # Incidence is a directed SET. F11's C declaration uses a different edge
    # presentation than JSON. Vertex/occurrence/evidence orders remain exact.
    expected, actual = copy.deepcopy(expected), copy.deepcopy(actual)
    for value in (expected, actual):
        for snapshot in value['snapshots'].values():
            snapshot['incidence'] = sorted(snapshot['incidence'])
    return presentation_equal(expected, actual, path)


def verify_material_evidence(ref, inputs, row):
    """Check received C witnesses/certificates using independent declared predicates.

    This verifier calls the existing Python obligation interpretation. It never
    constructs C outcomes, changes expected sets, or feeds oracle values to C.
    Counters increment at the actual supplied witness/certificate row checks.
    """
    failures = []
    work = dict(witnesses_checked=0, certificate_rows_checked=0)
    material = inputs['transformed']['material']
    if material is None or material['policy'] is None:
        return failures, work
    sources = inputs['transformed']['snapshots']['left']['occurrences']
    domain = {canonical(dict(zip(sources, values)))
              for values in itertools.product(('0', 'lambda', 'rho'), repeat=3)}
    for ai, association in enumerate(row['material']['associations'] or []):
        for di, decision in enumerate(association['decisions']):
            path = f'$.material.associations[{ai}].decisions[{di}]'
            declared = next((d for d in material['policy']['decisions'] if d['id'] == decision['id']), None)
            if declared is None:
                failures.append(dict(path=path + '.id', kind='UNDECLARED_DECISION', actual=decision['id']))
                continue
            obligations = ref.decision_obligations(material, inputs['transformed'], association['association'], declared)
            for wi, witness in enumerate(decision['witnesses']):
                work['witnesses_checked'] += 1
                valid = canonical(witness['material']) in domain
                satisfied = sorted(o['id'] for o in obligations)
                valid = valid and all(witness['material'].get(o['target']) == o['value'] for o in obligations)
                if not valid or sorted(witness['satisfied']) != satisfied:
                    failures.append(dict(path=f'{path}.witnesses[{wi}]', kind='INVALID_WITNESS',
                                         expected=dict(satisfied=satisfied, obligations=obligations), actual=witness))
            certificate = decision['rejection_certificate']
            rejected = any(o['tag'] == 'REJECT' for o in decision['outcomes'])
            if rejected:
                if certificate is None:
                    failures.append(dict(path=path, kind='UNVERIFIED_REJECTION', expected='27-map certificate', actual=None))
                    continue
                maps = [canonical(r['material']) for r in certificate]
                if len(maps) != 27 or set(maps) != domain:
                    failures.append(dict(path=path + '.rejection_certificate', kind='INCOMPLETE_CERTIFICATE',
                                         expected='27 distinct full concrete maps', actual=certificate))
                for ri, supplied in enumerate(certificate):
                    work['certificate_rows_checked'] += 1
                    violated = sorted(o['id'] for o in obligations
                                      if supplied['material'].get(o['target']) != o['value'])
                    if not violated or sorted(supplied['violated']) != violated:
                        failures.append(dict(path=f'{path}.rejection_certificate[{ri}]', kind='INVALID_CERTIFICATE_ROW',
                                             expected=violated, actual=supplied))
            elif certificate is not None:
                failures.append(dict(path=path + '.rejection_certificate', kind='CERTIFICATE_ON_ACCEPT',
                                     expected=None, actual=certificate))
            for oi, outcome in enumerate(decision['outcomes']):
                if outcome['tag'] == 'ACCEPT' and not any(w['material'] == outcome['material'] for w in decision['witnesses']):
                    failures.append(dict(path=f'{path}.outcomes[{oi}]', kind='MISSING_WITNESS', actual=outcome))
    return failures, work


def compare_m04_consumption(contract, inputs, tested, reference):
    """Compare actual streams without sorting/deduplicating their positions.

    The separate original Python computation anchors each full item. Only sets
    *inside* an item are extensional; assignment scan counts are Python-only
    measured data. Hook identities and invocation/exhaustion are mandatory.
    """
    ref = contract.ref
    failures, blocked = [], []
    association = reference['baseline']['material']['associations'][0]
    by_id = {d['id']: d for d in association['decisions']}
    basis = ('d_lambda', 'd_rho')
    expected = [dict(position=position, association=association['association'],
                     decision=by_id[basis[index]])
                for position, index in enumerate(inputs['outcome_order'])]
    expected = [ref.normalize_comparison(item) for item in expected]
    streams = {}
    for side, response, hook in (
            ('tested', tested, 'ca_partition/received-item-before-equivalence'),
            ('reference', reference, contract.outcome_adapter.OUTCOME_HOOK)):
        trace = response.get('consumption') or {}
        path = '$.' + side + '.consumption'
        if trace.get('outcome_hook') != hook or trace.get('partition_called') is not True:
            blocked.append(side + ': actual ordered partition invocation unverified; expected ' + hook)
        if side == 'reference' and trace.get('outcome_complete') is not True:
            blocked.append('reference: ordered outcome consumer did not exhaust its input')
        received = trace.get('consumed_outcomes')
        if not isinstance(received, list):
            blocked.append(side + ': complete actual consumed-outcome receipt unavailable')
            continue
        # Normalize each full item independently, never the received stream.
        normalized = []
        for position, item in enumerate(received):
            try:
                normalized.append(ref.normalize_comparison(item))
            except (ValueError, KeyError, TypeError) as error:
                failures.append(dict(path=f'{path}.consumed_outcomes[{position}]',
                                     kind='INVALID_CONSUMED_ITEM', actual=str(error)))
        streams[side] = normalized
        failures += presentation_equal(expected, normalized, path + '.consumed_outcomes')
        if side == 'reference':
            # Preserve and verify the Python-only complete decision work field.
            counts = [item.get('decision', {}).get('assignments_examined')
                      if isinstance(item, dict) else None for item in received]
            failures += presentation_equal([27, 27], counts, path + '.decision_assignment_counts')
    if len(streams) == 2:
        failures += presentation_equal(streams['reference'], streams['tested'], '$.paired_consumed_outcomes')
    return failures, blocked


def compare_case(contract, case, inputs, tested, reference):
    ref = contract.ref
    failures, blocked = [], []
    verifier_work = dict(witnesses_checked=0, certificate_rows_checked=0)
    if case['count_class'] == 'DERIVED':
        expected = reference['law']
        actual = {k: tested['law'][k] for k in expected}
        failures += presentation_equal(expected, actual, '$.law')
        if not expected['law_holds'] or not expected['operation_matches_extensional_equality']:
            failures.append(dict(path='$.reference.law', kind='REFERENCE_LAW_FAILURE',
                                 expected=True, actual=expected))
        report = dict(status='FAIL' if failures else 'PASS', failures=failures)
    else:
        matrix = case['suite_id'].startswith('matrix_')
        if matrix:
            expected_input = {k: inputs['transformed'][k] for k in
                              ('snapshots', 'profile', 'assumes_unchanged_incidence')}
            expected_input['pair_states'] = [(case['variant_rank'] // 4**i) % 4 for i in range(9)]
            for side, response in (('tested', tested), ('reference', reference)):
                failures += input_equal(expected_input, response['input'], '$.' + side + '.input')
                failures += presentation_equal(inputs['transformed']['evidence'],
                    response['candidate']['evidence_records'], '$.' + side + '.evidence_records')
            expected_row = dict(id=case['selector'], candidate=reference['candidate'])
            actual_row = dict(id=case['selector'], candidate=tested['candidate'])
        else:
            expected_row, actual_row = reference['result'], tested['result']
            failures += input_equal(inputs['transformed'], tested['input'], '$.tested.input')
            # Transformation layout uses declared vertex presentation; match it
            # exactly even when incidence presentation is extensionally compared.
            failures += presentation_equal(inputs['transformation'], tested['transformation'], '$.transformation')
            trace = tested['consumption']
            records = inputs['transformed']['evidence']
            failures += presentation_equal([dict(position=i, record=e) for i, e in enumerate(records)],
                                           trace['received_records'], '$.consumed_records')
            if not trace['candidate_called'] or not trace['record_hook']:
                blocked.append('C candidate input-consumption hook missing')
            if case['suite_id'] in ('record_orders', 'record_duplications'):
                visits = reference['consumption']['record_iterations']
                wanted = [dict(position=i, value=e) for i, e in enumerate(records)]
                if (not visits or wanted not in visits or
                        not reference['consumption'].get('record_hook')):
                    blocked.append('No complete actual Python record-consumption traversal')
                if trace['records_assessed'] != len(records):
                    failures.append(dict(path='$.consumption.records_assessed', kind='COUNT',
                                         expected=len(records), actual=trace['records_assessed']))
            if case['suite_id'] == 'association_orders':
                basis = next(s for s in contract.suites if s['id'] == 'association_orders')['association_order_basis']
                relations = [ref.expected_relation(code, inputs['original']) for code in basis]
                offered = [relations[i] for i in inputs['association_order']]
                actual = trace['consumed_associations']
                wanted = [dict(position=i, association=sorted(r)) for i, r in enumerate(offered)]
                normalized_trace = [dict(position=r['position'], association=sorted(r['association'])) for r in actual]
                failures += presentation_equal(wanted, normalized_trace, '$.consumed_associations')
                visits = reference['consumption']['association_iterations']
                want_visit = [dict(position=i, value=sorted(r)) for i, r in enumerate(offered)]
                visits = [[dict(position=r['position'], value=sorted(r['value'])) for r in v] for v in visits]
                if (visits != [want_visit] or not trace['material_called'] or not trace['association_hook']
                        or not reference['consumption'].get('association_hook')):
                    blocked.append('Incomplete actual independent association-consumption receipt')
            if case['suite_id'] == 'material_outcome_orders':
                trace_failures, trace_blocked = compare_m04_consumption(contract, inputs, tested, reference)
                failures += trace_failures
                blocked += trace_blocked
            baseline = reference.get('baseline')
            if baseline is not None:
                mapping = {**inputs['transformation']['left_transport'], **inputs['transformation']['right_transport']}
                transported = ref.transport_json(baseline, mapping)
                # Record presentation/counts are independently compared on the
                # transformed input, not claimed invariant under duplication.
                transported = copy.deepcopy(transported)
                transformed_semantics = copy.deepcopy(expected_row)
                for row in (transported, transformed_semantics):
                    row['candidate'].pop('evidence_records', None)
                    row['candidate'].pop('assessment_counts', None)
                failures += presentation_equal(ref.normalize_comparison(transported),
                    ref.normalize_comparison(transformed_semantics), '$.transported_baseline')
        envelope = dict(schema='ste-exp007-reference-v1', protocol_sha256=contract.plan['protocol']['sha256'])
        report = ref.compare_results(dict(envelope, results=[expected_row]), dict(envelope, results=[actual_row]))
        failures += report['failures']
        failures += identity_duplicates(actual_row)
        if not matrix and 'material' in actual_row:
            evidence_failures, verifier_work = verify_material_evidence(ref, inputs, actual_row)
            failures += evidence_failures
        expected_normal = ref.normalize_comparison(expected_row)
        actual_normal = ref.normalize_comparison(actual_row)
        exact = diff(expected_normal, actual_normal)
        if exact:
            failures.append(exact)
        # Validate frozen expectations on independent ORIGINAL computations only;
        # transformed outputs have a separate exact equivariance comparison.
        if not matrix:
            baseline = reference.get('baseline') or reference['result']
            material = contract.materials.get(case['selector'])
            fixture = contract.candidates[material['candidate_fixture'] if material else case['selector']]
            try:
                ref.check_candidate_expectation(fixture, baseline['candidate'])
                if material:
                    ref.check_material_expectation(material, fixture, baseline['material'])
            except (ValueError, KeyError, TypeError) as error:
                failures.append(dict(path='$.frozen_expectation', kind='EXPECTATION',
                                     expected='frozen expectation', actual=str(error)))
    # Expected unsupported fixtures can pass their diagnostic test, while a
    # missing *operation* or independent obligation never becomes PASS.
    status = 'FAIL' if failures else 'BLOCKED' if blocked else 'PASS'
    return dict(status=status, exact_comparison=report, discrepancies=failures,
                blocked=blocked, scientific_claim='INCONCLUSIVE',
                driver_verifier_work=verifier_work,
                normalization='Existing extensional reference contract; ordered input and consumption compared separately',
                triage='NEGATIVE_RESULT_PENDING_TRIAGE' if failures else 'INCONCLUSIVE' if blocked else 'BOUNDED_OBLIGATION_ONLY')


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_new(path, raw):
    path = Path(path)
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    fsync_directory(path.parent)


def publish_new(path, raw):
    """Publish an immutable completed report atomically, without replacement.

    The synchronized staging name is deliberately retained: no cleanup or
    rename-overwrite of historical data. Readers never see a partial final
    report. The journal's fsynced chain remains the authoritative checkpoint.
    """
    path = Path(path)
    staging = path.with_name(path.name + '.pending-' + uuid.uuid4().hex)
    write_new(staging, raw)
    os.link(staging, path)
    fsync_directory(path.parent)


def external(path):
    path = Path(path).expanduser().resolve()
    require(not path.is_relative_to(ROOT.resolve()), 'output must be outside the repository')
    return path


def fresh(path):
    path = external(path)
    path.mkdir(parents=True, exist_ok=False)
    fsync_directory(path.parent)
    for name in ('blobs', 'chunks', 'attempts', 'sources', 'bin'):
        (path / name).mkdir()
    fsync_directory(path)
    return path


def safe_child(root, relative):
    child = (root / relative).resolve()
    require(child.is_relative_to(root.resolve()) and child != root, 'evidence path escapes run directory')
    require(not (root / relative).is_symlink(), 'evidence symlink forbidden')
    return child


class Journal:
    def __init__(self, root):
        self.root = root
        self.sequence, self.previous = 0, None

    def blob(self, raw):
        require(len(raw) <= LIMIT, 'blob envelope overflow')
        sha = digest(raw)
        relative = 'blobs/' + sha
        path = self.root / relative
        if path.exists():
            require(read_small(path) == raw, 'content-address collision')
        else:
            write_new(path, raw)
        return dict(path=relative, bytes=len(raw), sha256=sha)

    def object(self, value):
        return self.blob(canonical(value))

    def read(self, receipt):
        path = safe_child(self.root, receipt['path'])
        require(path.stat().st_size == receipt['bytes'], 'blob length mismatch: ' + str(path))
        require(file_hash(path) == receipt['sha256'], 'blob SHA256 mismatch: ' + str(path))
        return read_small(path)

    def append(self, value):
        raw = canonical(value) + b'\n'
        require(len(raw) <= LIMIT, 'journal chunk too large')
        relative = f'chunks/{self.sequence:09d}-{uuid.uuid4().hex}.jsonl'
        write_new(self.root / relative, raw)
        index = dict(sequence=self.sequence, path=relative, bytes=len(raw), sha256=digest(raw),
                     previous_sha256=self.previous, ordinal_range=value.get('ordinal_range'),
                     plan_sha256=PLAN_HASH)
        with (self.root / 'index.jsonl').open('ab') as stream:
            stream.write(canonical(index) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        fsync_directory(self.root)
        self.sequence += 1
        self.previous = index['sha256']

    def records(self):
        index_path = self.root / 'index.jsonl'
        if not index_path.exists():
            return
        with index_path.open('rb') as stream:
            while True:
                raw = stream.readline(LIMIT + 1)
                if not raw:
                    break
                require(raw.endswith(b'\n'), 'torn index: explicit recovery review required; no repair')
                index = decode(raw)
                require(index['sequence'] == self.sequence and index['previous_sha256'] == self.previous
                        and index['plan_sha256'] == PLAN_HASH, 'broken journal sequence/hash chain')
                chunk = self.read(index)
                require(chunk.endswith(b'\n') and chunk.count(b'\n') == 1, 'truncated/multiple chunk records')
                event = decode(chunk)
                require(event.get('ordinal_range') == index['ordinal_range'], 'ordinal range binding failure')
                self.sequence += 1
                self.previous = index['sha256']
                yield event


def environment():
    # Deliberately explicit, minimal environment: no credentials or arbitrary
    # inherited Python paths/preloads copied into evidence or child execution.
    return dict(PATH=os.defpath, LC_ALL='C', LANG='C', TZ='UTC', PYTHONDONTWRITEBYTECODE='1')


def process_limit():
    resource.setrlimit(resource.RLIMIT_FSIZE, (LIMIT * BATCH, LIMIT * BATCH))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run_process(root, argv, stdin_raw, timeout, label):
    attempt = 'attempts/' + uuid.uuid4().hex + '-' + label
    stdin_path = root / (attempt + '.stdin')
    write_new(stdin_path, stdin_raw)
    started = now()
    with stdin_path.open('rb') as inp, (root / (attempt + '.stdout')).open('xb') as out, \
            (root / (attempt + '.stderr')).open('xb') as err:
        process = subprocess.Popen(argv, stdin=inp, stdout=out, stderr=err, cwd=root,
                                   env=environment(), preexec_fn=process_limit)
        timed_out = False
        try:
            status = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            status = process.wait()
        except BaseException:
            process.kill()
            process.wait()
            out.flush(); err.flush()
            os.fsync(out.fileno()); os.fsync(err.fileno())
            fsync_directory(root / 'attempts')
            raise
        out.flush(); err.flush()
        os.fsync(out.fileno()); os.fsync(err.fileno())
    fsync_directory(root / 'attempts')
    def receipt(suffix):
        path = root / (attempt + '.' + suffix)
        return dict(path=str(path.relative_to(root)), bytes=path.stat().st_size, sha256=file_hash(path))
    return dict(argv=argv, cwd=str(root), environment_overrides=environment(),
                started_at_utc=started, finished_at_utc=now(), exit_status=status,
                signal=-status if status < 0 else None, timeout=timed_out,
                stdin=receipt('stdin'), stdout=receipt('stdout'), stderr=receipt('stderr'))


def verify_file(root, receipt, maximum=LIMIT * BATCH):
    path = safe_child(root, receipt['path'])
    require(0 <= receipt['bytes'] <= maximum and path.stat().st_size == receipt['bytes'],
            'raw process file length mismatch')
    require(file_hash(path) == receipt['sha256'], 'raw process file SHA256 mismatch')


def output_lines(root, receipt):
    with safe_child(root, receipt['path']).open('rb') as stream:
        while True:
            offset = stream.tell()
            raw = stream.readline(LIMIT + 1)
            if not raw:
                return
            require(raw.endswith(b'\n') and len(raw) <= LIMIT, 'truncated/oversized process envelope')
            yield raw, dict(file=receipt, offset=offset, bytes=len(raw), sha256=digest(raw))


def read_segment(root, segment):
    path = safe_child(root, segment['file']['path'])
    require(0 <= segment['offset'] and 0 < segment['bytes'] <= LIMIT
            and segment['offset'] + segment['bytes'] <= segment['file']['bytes'], 'invalid raw segment')
    with path.open('rb') as stream:
        stream.seek(segment['offset'])
        raw = stream.read(segment['bytes'])
    require(digest(raw) == segment['sha256'] and raw.endswith(b'\n'), 'raw segment integrity failure')
    return decode(raw)


def validate_sources(contract):
    historical = next(a for a in contract.plan['implementation_identity']['read_only_artifacts']
                      if a['path'].endswith('/test_exp007.c'))
    if BASE.name == 'sources' and (BASE.parent / 'metadata.json').is_file():
        # Original qualification checked Git objects. Replay uses the pinned
        # archives, without substituting a later working tree or Git revision.
        require(file_hash(BASE / 'test_exp007.historical.c') == historical['sha256'],
                'archived historical test source identity mismatch')
    else:
        # A later publication may contain this fix. Require published ancestry
        # and exact pinned source bytes, not a self-referential driver commit.
        git('merge-base', '--is-ancestor', BASELINE, 'HEAD')
        for name, sha in contract.hashes.items():
            require(digest(git('show', BASELINE + ':' + REL + name)) == BASELINE_PINS.get(name, sha),
                    'baseline artifact identity mismatch: ' + name)
        require(digest(git('show', historical['last_change_commit'] + ':' + historical['path']))
                == historical['sha256'], 'historical test source identity mismatch')
        require(digest(git('show', contract.plan['protocol']['freeze_commit'] + ':' +
                           contract.plan['protocol']['path'])) == contract.plan['protocol']['sha256'],
                'protocol freeze commit identity mismatch')
    return dict(historical_frozen_test=historical,
                current_baseline_test=dict(revision=BASELINE, sha256=CURRENT_PINS['test_exp007.c'],
                                           path=REL + 'test_exp007.c'),
                historical_and_current_are_distinct=True)


def prepare(root, contract, mode, timeout, cc):
    require(BASE.name != 'sources', 'new runs require the authorized repository; archive supports audit/resume/replay only')
    identities = validate_sources(contract)
    compiler = Path(shutil.which(cc) or cc).resolve()
    require(compiler.is_file(), 'compiler unavailable')
    source_receipts = {}
    for name in [*contract.hashes, 'exp007_run.py']:
        raw = read_small(BASE / name)
        write_new(root / 'sources' / name, raw)
        source_receipts[name] = dict(sha256=digest(raw), bytes=len(raw), path='sources/' + name)
    historical = identities['historical_frozen_test']
    historical_raw = git('show', historical['last_change_commit'] + ':' + historical['path'])
    historical_path = 'sources/test_exp007.historical.c'
    write_new(root / historical_path, historical_raw)
    # Keep bootstrap/build process outputs even when compilation fails. There is
    # no cleanup. Metadata is committed only after all binaries are bound.
    version = run_process(root, [str(compiler), '--version'], b'', timeout, 'compiler-version')
    require(version['exit_status'] == 0, 'compiler identity invocation failed')
    builds, binaries = {}, {}
    for name, source in (('matrix', 'exp007_campaign.c'), ('nonmatrix', 'exp007_c_adapter.c')):
        binary = root / 'bin' / name
        argv = [str(compiler), *FLAGS, str(root / 'sources' / source), '-o', str(binary)]
        build = run_process(root, argv, b'', timeout, 'build-' + name)
        builds[name] = build
        require(build['exit_status'] == 0 and binary.is_file(), 'C11 build failed; outputs retained in ' + str(root))
        with binary.open('rb') as stream:
            os.fsync(stream.fileno())
        binaries[name] = dict(path='bin/' + name, sha256=file_hash(binary), bytes=binary.stat().st_size)
    fsync_directory(root / 'bin')
    meta = dict(schema='ste-exp007-run-v1', run_id=uuid.uuid4().hex, mode=mode,
                started_at_utc=now(), baseline=BASELINE, protocol=contract.plan['protocol'],
                plan_id=contract.plan['artifact']['id'], plan_sha256=PLAN_HASH,
                source_hashes=source_receipts, test_identities=identities,
                historical_test_source=dict(path=historical_path, bytes=len(historical_raw), sha256=digest(historical_raw)),
                driver_sha256=file_hash(BASE / 'exp007_run.py'),
                repository_head=git('rev-parse', 'HEAD').decode().strip(),
                repository_root=str(ROOT),
                dirty_tracked_diff_sha256=digest(git('diff', 'HEAD', '--binary')),
                repository_state=git('status', '--short', '--branch').decode(),
                compiler=dict(path=str(compiler), sha256=file_hash(compiler), version=version),
                c11_flags=FLAGS, builds=builds, binaries=binaries,
                interpreter=dict(path=str(Path(sys.executable).resolve()), sha256=file_hash(sys.executable),
                                 version=sys.version), platform=platform.platform(),
                executed_argv=[sys.executable, '-B', *sys.argv], working_directory=str(Path.cwd()),
                environment_overrides=environment(), frozen_primary_required=529423,
                auxiliary_required=1, derived_required=22764, blocked_obligations=BLOCKED,
                scientific_claim='INCONCLUSIVE', automatic_cleanup=False)
    write_new(root / 'metadata.json', canonical(meta))
    return meta


def verify_meta(root, meta, contract):
    require(meta['schema'] == 'ste-exp007-run-v1' and meta['baseline'] == BASELINE
            and meta['plan_sha256'] == PLAN_HASH and meta['protocol'] == contract.plan['protocol'],
            'metadata contract drift')
    require(set(meta['source_hashes']) == set(contract.hashes) | {'exp007_run.py'},
            'incomplete source archive identities')
    for name, receipt in meta['source_hashes'].items():
        verify_file(root, receipt, LIMIT)
        require(receipt['sha256'] == contract.hashes.get(name, meta['driver_sha256']), 'pinned source archive drift: ' + name)
        require(receipt['sha256'] == file_hash(BASE / name), 'current source/driver differs: ' + name)
    require(meta['driver_sha256'] == file_hash(BASE / 'exp007_run.py'), 'driver drift')
    require(meta['test_identities'] == validate_sources(contract), 'test identity binding changed')
    verify_file(root, meta['historical_test_source'], LIMIT)
    require(meta['historical_test_source']['sha256'] ==
            meta['test_identities']['historical_frozen_test']['sha256'], 'historical source archive drift')
    require(meta['interpreter']['sha256'] == file_hash(meta['interpreter']['path']), 'interpreter drift')
    require(meta['compiler']['sha256'] == file_hash(meta['compiler']['path']), 'compiler drift')
    require(meta['c11_flags'] == FLAGS, 'strict C11 flags drift')
    for receipt in meta['binaries'].values():
        verify_file(root, receipt, LIMIT * BATCH)
    for process in [meta['compiler']['version'], *meta['builds'].values()]:
        for key in ('stdin', 'stdout', 'stderr'):
            verify_file(root, process[key])
        require(process['exit_status'] == 0, 'unqualified build process')
    require(meta['compiler']['version']['argv'] == [meta['compiler']['path'], '--version'],
            'compiler version command drift')
    require(set(meta['builds']) == set(meta['binaries']) == {'matrix', 'nonmatrix'},
            'incomplete build identities')
    for name, source in (('matrix', 'exp007_campaign.c'), ('nonmatrix', 'exp007_c_adapter.c')):
        process = meta['builds'][name]
        require(process['argv'] == [meta['compiler']['path'], *FLAGS,
                    str(root / 'sources' / source), '-o', str(root / meta['binaries'][name]['path'])]
                and process['cwd'] == str(root) and process['environment_overrides'] == environment()
                and not process['timeout'] and process['signal'] is None,
                'strict reproducible C11 build metadata drift')


def verify_execution_identities(root, meta):
    for receipt in meta['binaries'].values():
        verify_file(root, receipt)
    for receipt in meta['source_hashes'].values():
        verify_file(root, receipt, LIMIT)
    require(file_hash(meta['interpreter']['path']) == meta['interpreter']['sha256'], 'execution interpreter drift')


def response_identity(contract, case, response, side, ordinal, request_id):
    require(response['status'] == 'EVALUATED' and response.get('error_code') is None,
            side + ': unsupported/error operation cannot be PASS')
    require(response.get('work_complete', True) is True, side + ': incomplete work receipt')
    require(response['protocol_sha256'] == contract.plan['protocol']['sha256'] and
            response['plan_sha256'] == PLAN_HASH, side + ': protocol/plan identity mismatch')
    require(response['request_id'] == request_id and response['request_index'] == ordinal
            and response['response_id'] == ordinal, side + ': response framing identity mismatch')
    matrix = case['suite_id'].startswith('matrix_')
    expected_schema = ('ste-exp007-worker-v1' if side == 'tested' else
                       'ste-exp007-reference-adapter-v1') if matrix else (
                       'ste-exp007-c-adapter-v1' if side == 'tested' else 'ste-exp007-run-reference-v1')
    require(response['schema'] == expected_schema, side + ': adapter schema mismatch')
    if not matrix and side == 'tested':
        require(response['solver_sha256'] == contract.hashes['historical_associations.c']
                and response['fixture_sha256'] == contract.hashes['EXP007_FIXTURES.json'],
                'C declared source/fixture identity mismatch')
    if matrix and side == 'reference':
        require(response['reference_sha256'] == contract.hashes['exp007_reference.py']
                and response['fixture_sha256'] == contract.hashes['EXP007_FIXTURES.json'],
                'Python declared source/fixture identity mismatch')
    expected_case = case['case_id']
    if case['count_class'] == 'DRY_RUN':
        expected_case = f"EXP007/C/V1/{case['suite_id']}/{case['selector']}/{case['variant_rank']:06d}"
    require(response['case_id'] == expected_case, side + ': wrong logical case identity')
    if matrix:
        require(response['instance_id'] == case['selector'] and response['config_id'] == case['variant_rank'],
                side + ': wrong matrix selectors')
    for key, count in response['work'].items():
        require(count is None or type(count) is int and count >= 0, side + ': invalid measured work: ' + key)


def ledgers(contract, mode):
    result = {}
    for suite in contract.suites:
        required = 20 if mode == 'dry-run' and suite['id'].startswith('matrix_') else suite['required_cases']
        if mode == 'dry-run':
            required = 10 if suite['id'].startswith('matrix_') else 0
        elif required is None:
            required = 22764
        result[suite['id']] = dict(required=required, generated=0, attempted=0, received=0,
                                  compared=0, passed=0, failed=0, blocked=0, skipped=0,
                                  missing=required, duplicate=0,
                                  tested=dict(required=required, generated=0, attempted=0, received=0,
                                              compared=0, passed=0, failed=0, skipped=0, missing=required, duplicate=0),
                                  reference=dict(required=required, generated=0, attempted=0, received=0,
                                                 compared=0, passed=0, failed=0, skipped=0, missing=required, duplicate=0))
    return result


def credit(ledger, status):
    if status == 'BLOCKED':
        ledger['blocked'] += 1
    else:
        ledger['compared'] += 1
        ledger['passed' if status == 'PASS' else 'failed'] += 1
    ledger['missing'] = ledger['required'] - ledger['compared']
    for side in ('tested', 'reference'):
        for key in ('compared', 'passed', 'failed', 'missing'):
            ledger[side][key] = ledger[key]


def validate_process_batch(root, contract, cases, inputs, ids, side, process):
    expected_stdin = b''.join(make_frames(c, v, r)[0 if side == 'tested' else 1]
                              for c, v, r in zip(cases, inputs, ids))
    require(process['stdin']['bytes'] == len(expected_stdin)
            and process['stdin']['sha256'] == digest(expected_stdin), side + ': submitted input drift')
    stream = iter(output_lines(root, process['stdout']))
    for i, (case, request_id) in enumerate(zip(cases, ids), 1):
        raw, _ = next(stream, (None, None))
        require(raw is not None, side + ': missing response')
        response_identity(contract, case, decode(raw), side, i, request_id)
    require(next(stream, None) is None, side + ': excess/duplicate response')


def acceptance_evidence(contract):
    """Bounded accumulator, populated only after audit reconstructs a case.

    This is independent of credit()/saved ledgers and contains no saved summary
    claims. Counts describe checked obligations, never estimated process work.
    """
    return {s['id']: dict(receipts=0, passed=0, failed=0, blocked=0,
                          matrix_predicates=dict(tested=0, reference=0))
            for s in contract.suites}


def observe_acceptance(evidence, case, comparison, tested, reference):
    row = evidence[case['suite_id']]
    row['receipts'] += 1
    require(comparison['status'] in ('PASS', 'FAIL', 'BLOCKED'), 'unknown case verdict')
    row[{'PASS': 'passed', 'FAIL': 'failed', 'BLOCKED': 'blocked'}[comparison['status']]] += 1
    if comparison['status'] == 'PASS' and case['suite_id'].startswith('matrix_'):
        for side, response in (('tested', tested), ('reference', reference)):
            candidate = response['candidate']
            # Do not turn reported work totals into discharged obligations.
            predicates = candidate['predicates']
            require(len(predicates) == 6 and candidate['counts']['U_H'] == 6
                    and len({canonical(p['association']) for p in predicates}) == 6,
                    'matrix six-candidate obligation receipt incomplete')
            row['matrix_predicates'][side] += len(predicates)


def evaluate_acceptance(contract, mode, state):
    """Pure deterministic B2 evaluator of independently audited evidence.

    Callers must use audit(), never deserialize a summary into this function.
    All eleven conditions retain the frozen text and position. A completed
    execution, expected negative fixture, mismatch and certified scientific
    finding are distinct. B3 has no certification input here: replay alone
    cannot authorize a scientific FAIL. Final reporting has no trustworthy
    evidence assessment contract yet and therefore cannot PASS, even with complete counts.
    """
    requirements = contract.plan['full_acceptance']['required']
    require(len(requirements) == 11, 'unmapped frozen acceptance requirement')
    evidence = state['acceptance_evidence']
    ledger = state['ledgers']
    require(set(evidence) == set(ledger) == {s['id'] for s in contract.suites},
            'aggregate suite accounting mismatch')
    for key, row in evidence.items():
        saved = ledger[key]
        require(all(type(row[f]) is int and row[f] >= 0
                    for f in ('receipts', 'passed', 'failed', 'blocked'))
                and row['receipts'] <= saved['required']
                and row['receipts'] == row['passed'] + row['failed'] + row['blocked']
                and row['passed'] == saved['passed'] and row['failed'] == saved['failed']
                and row['blocked'] == saved['blocked']
                and row['passed'] + row['failed'] == saved['compared'],
                'case comparison / aggregate ledger disagreement: ' + key)
    require(sum(r['receipts'] for r in evidence.values()) == state['completed_receipts'],
            'aggregate receipt accounting mismatch')
    campaign = mode == 'campaign'
    groups = {'PRIMARY': [], 'AUXILIARY': [], 'DERIVED': []}
    required_by_suite = {}
    for suite in contract.suites:
        key = suite['id']
        category = ('DERIVED' if key == 'derived_observable_equivalence_laws' else
                    'PRIMARY' if suite['in_frozen_suite_total'] else 'AUXILIARY')
        groups[category].append(key)
        required_by_suite[key] = (suite['required_cases'] if suite['required_cases'] is not None
                                  else contract.plan['derived_gates']['observable_equivalence']['required_law_checks'])
    counts = {}
    for category, keys in groups.items():
        required = sum(required_by_suite[k] for k in keys)
        counts[category] = dict(required=required, **{
            field: sum(evidence[k][field] for k in keys) if campaign else 0
            for field in ('receipts', 'passed', 'failed', 'blocked')})
        counts[category]['missing'] = required - counts[category]['passed'] - counts[category]['failed']
    require({k: v['required'] for k, v in counts.items()} ==
            dict(PRIMARY=529423, AUXILIARY=1, DERIVED=22764), 'frozen aggregate count drift')

    def gate(keys):
        if not campaign:
            return 'UNSATISFIED'
        if any(evidence[k]['failed'] for k in keys):
            return 'UNSATISFIED'
        if any(evidence[k]['blocked'] for k in keys):
            return 'UNVERIFIED'
        return ('PASS' if all(evidence[k]['passed'] == required_by_suite[k] for k in keys)
                else 'UNSATISFIED')

    primary = groups['PRIMARY'] + groups['AUXILIARY']
    matrix = [k for k in primary if k.startswith('matrix_')]
    named_transforms = [k for k in primary if k not in matrix]
    material = ['named_materials', 'material_relabelings', 'association_orders', 'material_outcome_orders']
    matrix_obligations = {side: sum(evidence[k]['matrix_predicates'][side] for k in matrix)
                          if campaign else 0 for side in ('tested', 'reference')}
    matrix_status = gate(matrix)
    if matrix_status == 'PASS' and any(v != 3145728 for v in matrix_obligations.values()):
        matrix_status = 'UNVERIFIED'
    all_execution = campaign and all(v['receipts'] == v['required'] for v in counts.values())
    all_passed = all(gate(keys) == 'PASS' for keys in groups.values())
    clean = (state['operational_incidents'] == 0 and state['unindexed_chunk_count'] == 0
             and state['unfinished_attempt'] is None)
    pending = sum(v['failed'] for v in counts.values())
    statuses = [
        'PASS' if state['identities_verified'] else 'UNVERIFIED',
        gate(primary), matrix_status, gate(named_transforms), gate(primary),
        gate(material), gate(material), gate(groups['DERIVED']),
        gate(['named_candidates', 'named_materials']),
        'PASS' if all_passed and clean else 'UNSATISFIED',
        'UNVERIFIED',
    ]
    sources = [
        'verify_meta: frozen/current/historical sources, compiler/interpreter/binaries, strict flags and build commands; audit: raw execution argv/input/output bindings',
        'audit schedule-prefix receipts; independently recounted case comparisons and paired/side ledgers',
        'both matrix suite receipts and six distinct compared predicates per side per configuration',
        'exact frozen named expectations and isolated transport/actual consumption comparisons',
        'compare_case: exact sets, predicates, diagnostics, assessments and duplicate checks',
        'compare_case / verify_material_evidence: complete independent outcomes, authorizations, witnesses and 27-map certificates',
        'compare_case: exact normalized concrete observable maps and association/decision membership after material comparison',
        'separate derived suite receipts and exact independent law verdicts',
        'frozen original F13/F12/M05 expectations; EXP004 limitations explicitly retained in this report',
        'hash-verified journals/raw receipts/replay records, operational incidents and exact coverage gaps',
        'BLOCKED: no verified final EXP007_RESULTS.md / exp007_evidence.json reporting with explicit bounded model-relative qualification and frozen limitations; final reporting assessment is not implemented',
    ]
    rows = [dict(id=f'FA{i + 1:02d}', frozen_index=i, requirement=text,
                 status=statuses[i], evidence=sources[i],
                 dependency=('B3: semantic versus harness triage and independent certification of every mismatch'
                             if i == 9 and pending else None))
            for i, text in enumerate(requirements)]
    accepted = all(r['status'] == 'PASS' for r in rows)
    return dict(requirements=rows, counts=counts,
                integrity_audit='PASS', execution='EXHAUSTIVE_EXECUTION' if all_execution else
                    'PARTIAL_EXECUTION' if campaign else 'NON_CAMPAIGN_EXECUTION',
                primary_completion=gate(groups['PRIMARY']), auxiliary_completion=gate(groups['AUXILIARY']),
                derived_laws=gate(groups['DERIVED']), matrix_candidate_obligations=matrix_obligations,
                case_comparison='UNSATISFIED' if pending else 'PASS' if all_passed else 'INCONCLUSIVE',
                scientific_acceptance='PASS' if accepted else 'BLOCKED' if all_passed and clean else 'INCONCLUSIVE',
                complete_scientific_acceptance=accepted,
                scientific_finding='NEGATIVE_RESULT_PENDING_TRIAGE' if pending else 'INCONCLUSIVE',
                pending_triage_cases=pending, scientific_counterexamples_certified=0,
                B3_STATUS='OPEN',
                scientific_claim_scope=contract.plan['full_acceptance']['scientific_claim_scope'],
                EXP004=contract.plan['negative_and_inconclusive']['EXP004'],
                reporting_gate='BLOCKED', unresolved_requirements=[r['id'] for r in rows if r['status'] != 'PASS'])


def audit(root, meta, contract):
    """Reconstruct only a verified sequential prefix; no ID set proportional to campaign size."""
    verify_meta(root, meta, contract)
    acceptance = acceptance_evidence(contract)
    journal = Journal(root)
    ledger = ledgers(contract, meta['mode'])
    scheduler = iter(contract.schedule(meta['mode']))
    completed, first_failure, first_incident = 0, None, None
    work = dict(tested={}, reference={})
    attempts, process_invocations = 0, dict(tested=0, reference=0)
    retry_invocations = dict(tested=0, reference=0)
    process_bytes = dict(tested=0, reference=0)
    verifier_work = dict(witnesses_checked=0, certificate_rows_checked=0)
    active = None
    # At most BATCH uncredited descriptors, even across partial retry batches.
    lookahead = []
    blocked_cases = []
    incident_count = 0
    for event in journal.records():
        require(event['run_id'] == meta['run_id'] and event['metadata_sha256'] == file_hash(root / 'metadata.json'),
                'journal run binding mismatch')
        if event['kind'] == 'attempt':
            require(event['start'] == completed, 'attempt is not at uncredited schedule prefix')
            require(0 < len(event['inputs']) <= BATCH and len(event['request_ids']) == len(event['inputs'])
                    and len(set(event['request_ids'])) == len(event['request_ids']), 'attempt size/IDs invalid')
            while len(lookahead) < len(event['inputs']):
                planned = next(scheduler, None)
                require(planned is not None, 'attempt exceeds frozen schedule')
                lookahead.append(dict(case=planned, generated=False,
                                      tested_attempted=False, reference_attempted=False,
                                      tested_received=False, reference_received=False))
            require(event['ordinal_range'] == [completed, completed + len(event['inputs']) - 1],
                    'attempt ordinal range mismatch')
            for observed, receipt in zip(lookahead, event['inputs']):
                value = decode(journal.read(receipt))
                require(value == contract.materialize(observed['case']), 'prepared input is not frozen schedule input')
                if not observed['generated']:
                    row = ledger[observed['case']['suite_id']]
                    row['generated'] += 1
                    row['tested']['generated'] += 1
                    row['reference']['generated'] += 1
                    observed['generated'] = True
            active = event
            attempts += 1
        elif event['kind'] == 'processes':
            require(active is not None and event['attempt_id'] == active['attempt_id']
                    and 'processes' not in active, 'unbound/duplicate process attempt')
            require(set(event['processes']) == {'tested', 'reference'}, 'missing side process')
            active = dict(active, processes=event['processes'], process_sequence=journal.sequence - 1)
            for side, process in event['processes'].items():
                process_invocations[side] += 1
                for key in ('stdin', 'stdout', 'stderr'):
                    verify_file(root, process[key])
                    process_bytes[side] += process[key]['bytes']
                count = len(active['inputs'])
                candidates = [o['case'] for o in lookahead[:count]]
                if any(o[side + '_attempted'] for o in lookahead[:count]):
                    retry_invocations[side] += 1
                values = [decode(journal.read(r)) for r in active['inputs']]
                expected_argv = commands_for(root, meta, candidates[0])[0 if side == 'tested' else 1]
                require(process['argv'] == expected_argv and process['cwd'] == str(root)
                        and process['environment_overrides'] == environment(), 'execution command binding drift')
                received = process['exit_status'] == 0 and not process['timeout']
                if received:
                    try:
                        validate_process_batch(root, contract, candidates, values, active['request_ids'], side, process)
                    except (IntegrityError, ValueError, KeyError, TypeError):
                        require(event.get('incident') is not None, 'malformed output without retained operational incident')
                        received = False
                for observed in lookahead[:count]:
                    row = ledger[observed['case']['suite_id']]
                    before_attempted = observed['tested_attempted'] or observed['reference_attempted']
                    before_received = observed['tested_received'] and observed['reference_received']
                    if not observed[side + '_attempted']:
                        row[side]['attempted'] += 1
                        observed[side + '_attempted'] = True
                    if received and not observed[side + '_received']:
                        row[side]['received'] += 1
                        observed[side + '_received'] = True
                    if not before_attempted:
                        row['attempted'] += 1
                    if not before_received and observed['tested_received'] and observed['reference_received']:
                        row['received'] += 1
            if event.get('incident') and first_incident is None:
                first_incident = dict(sequence=journal.sequence - 1, incident=event['incident'])
            if event.get('incident'):
                incident_count += 1
        elif event['kind'] == 'case':
            require(active is not None and active.get('processes') is not None
                    and event['attempt_id'] == active['attempt_id'], 'case has no completed side processes')
            planned = lookahead[0]['case'] if lookahead else None
            require(planned is not None and event['case'] == planned, 'duplicate/missing/out-of-order case receipt')
            require(event['ordinal_range'] == [completed, completed], 'case checkpoint ordinal mismatch')
            inputs = decode(journal.read(event['inputs']))
            require(inputs == contract.materialize(planned), 'saved input differs from deterministic frozen input')
            require(event['input_sha256'] == digest(canonical(inputs['transformed'])), 'canonical input hash mismatch')
            tested, reference = (read_segment(root, event[s]['stdout']) for s in ('tested', 'reference'))
            position = completed - active['start']
            require(0 <= position < len(active['inputs']) and event['inputs'] == active['inputs'][position],
                    'case input not bound to attempt')
            for side, response in (('tested', tested), ('reference', reference)):
                receipt = event[side]
                process = active['processes'][side]
                require(receipt['stdout']['file'] == process['stdout'] and receipt['stderr'] == process['stderr']
                        and process['exit_status'] == 0 and not process['timeout'], 'invalid process receipt')
                require(receipt['executable_sha256'] == execution_hash(meta, planned, side), 'executable binding mismatch')
                response_identity(contract, planned, response, side, position + 1,
                                  active['request_ids'][position])
                require(receipt['case_id'] == planned['case_id'] and receipt['side'] == side
                        and receipt['ordinal'] == planned['global_ordinal']
                        and receipt['attempt_id'] == active['attempt_id']
                        and receipt['input_sha256'] == event['input_sha256']
                        and receipt['stdout_sha256'] == receipt['stdout']['sha256']
                        and receipt['stderr_sha256'] == process['stderr']['sha256']
                        and receipt['exit_status'] == process['exit_status'], 'side receipt identity drift')
            comparison = compare_case(contract, planned, inputs, tested, reference)
            require(comparison == decode(journal.read(event['comparison'])), 'stored comparison is not reproducible')
            for key, count in comparison['driver_verifier_work'].items():
                verifier_work[key] += count
            for side in ('tested', 'reference'):
                require(event[side]['comparison_status'] == comparison['status']
                        and event[side]['failure_class'] == (None if comparison['status'] == 'PASS'
                                                            else comparison['triage']), 'side verdict drift')
            observe_acceptance(acceptance, planned, comparison, tested, reference)
            credit(ledger[planned['suite_id']], comparison['status'])
            completed += 1
            lookahead.pop(0)
            if comparison['status'] == 'BLOCKED':
                require(len(blocked_cases) < 2, 'unexpected additional unverified consumption obligation')
                blocked_cases.append(dict(case=planned, reason=comparison['blocked'], side='paired'))
            if comparison['status'] == 'FAIL' and first_failure is None:
                first_failure = dict(case_id=planned['case_id'], schedule_ordinal=planned['schedule_ordinal'])
            if event.get('replay'):
                replay = decode(journal.read(event['replay']))
                require(replay['case_id'] == planned['case_id'] and replay['transformed_input_sha256'] == event['input_sha256'],
                        'counterexample replay binding mismatch')
            else:
                require(comparison['status'] == 'PASS', 'missing negative/inconclusive replay evidence')
        elif event['kind'] == 'summary':
            require(event['completed_receipts'] == completed and event['ledgers'] == ledger, 'summary ledger mismatch')
            require(event['EXP007_STATUS'] == 'INCONCLUSIVE' and event['complete_scientific_acceptance'] is False,
                    'summary makes unsupported scientific claim')
        elif event['kind'] == 'incident':
            incident_count += 1
            if first_incident is None:
                first_incident = dict(sequence=journal.sequence - 1, incident=event['reason'])
        else:
            raise IntegrityError('unknown journal event: ' + str(event.get('kind')))
    # Actual process work includes retries/baseline/cache work even when no
    # case checkpoint was committed. Scan raw completed process outputs rather
    # than summing case receipts (which would double-count or lose crash work).
    second = Journal(root)
    for event in second.records():
        if event['kind'] == 'processes':
            for side, process in event['processes'].items():
                if process['exit_status'] != 0 or process['timeout']:
                    work[side]['incomplete_process_work_unavailable'] = True
                    continue
                for raw, _ in output_lines(root, process['stdout']):
                    row = decode(raw)
                    for key, count in row.get('work', {}).items():
                        if count is None:
                            work[side][key] = None
                        elif work[side].get(key, 0) is not None:
                            work[side][key] = work[side].get(key, 0) + count
    for row in ledger.values():
        for counters in (row, row['tested'], row['reference']):
            require(counters['compared'] == counters['passed'] + counters['failed']
                    and 0 <= counters['compared'] <= counters['received'] <= counters['attempted']
                    <= counters['generated'] <= counters['required']
                    and counters['missing'] == counters['required'] - counters['compared'],
                    'coverage ledger invariant failure')
    state = dict(completed_receipts=completed, ledgers=ledger, measured_adapter_work=work,
                         acceptance_evidence=acceptance, identities_verified=True,
                         process_invocations=process_invocations, attempts=attempts,
                         retry_invocations=retry_invocations, raw_process_bytes_written=process_bytes,
                         committed_driver_verifier_work=verifier_work,
                         current_audit_verifier_work=verifier_work.copy(),
                         current_audit_case_comparisons=completed,
                         unindexed_chunk_count=sum(1 for _ in os.scandir(root / 'chunks')) - journal.sequence,
                         operational_incidents=incident_count, blocked_cases=blocked_cases,
                         first_mismatch=first_failure, first_operational_incident=first_incident,
                         missing_tail=dict(first_schedule_ordinal=completed,
                             last_schedule_ordinal=(19 if meta['mode'] == 'dry-run' else 552187),
                             sides=['tested', 'reference', 'paired'],
                             reason='Uncommitted suffix: use frozen schedule to expand exact per-ID gaps'),
                         unfinished_attempt=None if active is None or completed == active['start'] + len(active['inputs'])
                             else active['attempt_id'])
    state['acceptance'] = evaluate_acceptance(contract, meta['mode'], state)
    return journal, state


def execution_hash(meta, case, side):
    if side == 'reference':
        return meta['interpreter']['sha256']
    return meta['binaries']['matrix' if case['suite_id'].startswith('matrix_') else 'nonmatrix']['sha256']


def commands_for(root, meta, case):
    matrix = case['suite_id'].startswith('matrix_')
    tested = [str(root / meta['binaries']['matrix' if matrix else 'nonmatrix']['path'])]
    reference = [meta['interpreter']['path'], '-B', str(root / 'sources' /
                 ('exp007_reference_adapter.py' if matrix else 'exp007_run.py'))]
    if not matrix:
        reference += ['--_reference']
    return tested, reference


def make_frames(case, inputs, request_id):
    if case['suite_id'].startswith('matrix_'):
        frame = f"EXP007/1 {request_id} EVAL {case['selector']} {case['variant_rank']}\n".encode('ascii')
        return frame, frame
    tested = f"EXP007/1 {request_id} EVAL {case['suite_id']} {case['selector']} {case['variant_rank']}\n".encode('ascii')
    reference = canonical(dict(case=case, inputs=inputs, request_id=request_id)) + b'\n'
    return tested, reference


def event_base(root, meta, kind):
    return dict(kind=kind, run_id=meta['run_id'], metadata_sha256=file_hash(root / 'metadata.json'),
                recorded_at_utc=now())


def replay_record(root, meta, contract, case, inputs, comparison, tested, reference, attempt_id):
    fields = contract.plan['first_mismatch_replay']['required_fields']
    value = dict.fromkeys(fields)
    value.update(run_id=meta['run_id'], case_id=case['case_id'], global_ordinal=case['global_ordinal'],
                 suite_id=case['suite_id'], fixture_id=case['selector'], variant_rank=case['variant_rank'],
                 protocol_version='V1', protocol_freeze_commit=contract.plan['protocol']['freeze_commit'],
                 protocol_sha256=contract.plan['protocol']['sha256'], plan_sha256=PLAN_HASH,
                 fixture_manifest_sha256=contract.hashes['EXP007_FIXTURES.json'],
                 original_untransformed_fixture_input=inputs['original'],
                 original_input_sha256=digest(canonical(inputs['original'])),
                 fully_materialized_transformed_input=inputs['transformed'],
                 transformed_input_sha256=digest(canonical(inputs['transformed'])),
                 implementation_revision=BASELINE, driver_revision=meta['driver_sha256'],
                 source_hashes=meta['source_hashes'], attempt_ids=[attempt_id],
                 compiler_identity=meta['compiler'], compiler_flags=FLAGS, build_argv=meta['builds'],
                 cwd=str(root), environment_overrides=environment(), triage_status=comparison['triage'],
                 normalization_and_transport_steps=dict(normalization=comparison['normalization'],
                                                        transformation=inputs.get('transformation')),
                 evidence_offsets_and_hashes=dict(tested=tested, reference=reference),
                 standalone_replay_argv=[meta['interpreter']['path'], '-B', str(root / 'sources' / 'exp007_run.py'),
                    'replay', '--execute', '--run', str(root), '--case-id', case['case_id'],
                    '--out', '/tmp/exp007-replay-CHOOSE-FRESH-DIRECTORY'])
    matrix = case['suite_id'].startswith('matrix_')
    commands = commands_for(root, meta, case)
    value.update(instance_id=case['selector'] if matrix else None,
                 config_id=case['variant_rank'] if matrix else None,
                 tested_executable_path=commands[0][0], tested_executable_sha256=tested['executable_sha256'],
                 reference_executable_path=commands[1][0], reference_executable_sha256=reference['executable_sha256'],
                 reference_script_sha256=meta['source_hashes']['exp007_reference_adapter.py' if matrix else 'exp007_run.py']['sha256'],
                 execution_argv=dict(tested=commands[0], reference=commands[1]),
                 exit_statuses=dict(tested=tested['exit_status'], reference=reference['exit_status']),
                 signals={s: -r['exit_status'] if r['exit_status'] < 0 else None
                          for s, r in (('tested', tested), ('reference', reference))},
                 ledger_snapshot=dict(committed_prefix_schedule_cases=case['schedule_ordinal'],
                     index_bytes=(root / 'index.jsonl').stat().st_size,
                     index_prefix_sha256=file_hash(root / 'index.jsonl'),
                     reconstruction='Audit this immutable index prefix against frozen schedule; no inferred passes.'),
                 association_presentation_order=inputs.get('association_order'),
                 material_outcome_presentation_order=inputs.get('outcome_order'))
    tested_output = read_segment(root, tested['stdout'])
    reference_output = read_segment(root, reference['stdout'])
    trace = tested_output.get('consumption') or {}
    value.update(consumed_record_order=dict(tested=trace.get('received_records'),
                     reference=reference_output.get('consumption', {}).get('record_iterations')),
                 consumed_association_order=dict(tested=trace.get('consumed_associations'),
                     reference=reference_output.get('consumption', {}).get('association_iterations')),
                 consumed_outcome_order=dict(tested=trace.get('consumed_outcomes'),
                     reference=reference_output.get('consumption', {}).get('consumed_outcomes')),
                 consumption_details=dict(tested=trace, reference=reference_output.get('consumption', {})),
                 consumption_hook_identity=dict(tested={k: v for k, v in trace.items() if k.endswith('_hook')},
                     reference={k: v for k, v in reference_output.get('consumption', {}).items() if k.endswith('_hook')}))
    value['false_positive_concrete_relations'] = [f for f in comparison['discrepancies'] if f.get('false_positives')]
    value['false_negative_concrete_relations'] = [f for f in comparison['discrepancies'] if f.get('false_negatives')]
    value['duplicate_positions_and_values'] = [f for f in comparison['discrepancies'] if 'DUPLICATE' in f.get('kind', '')]
    value['witness_or_certificate_discrepancy'] = [f for f in comparison['discrepancies']
                                                 if 'witness' in str(f).lower() or 'certificate' in str(f).lower()]
    value['observable_class_map_and_membership_discrepancy'] = [f for f in comparison['discrepancies']
                                                              if 'observable' in str(f).lower()]
    material_row = (tested_output.get('result') or {}).get('material') or {}
    if material_row.get('associations') is not None:
        value['association_pairs'] = [a['association'] for a in material_row['associations']]
        value['policy_decision_id'] = [d['id'] for a in material_row['associations'] for d in a['decisions']]
        value['retained_and_waived_intentions'] = [dict(association=a['association'], decision=d['id'],
            retained=d['retained_intentions'], waived=d['waived_intentions'], authorization=d['authorization'])
            for a in material_row['associations'] for d in a['decisions']]
    if comparison['discrepancies']:
        first = next((f for f in comparison['discrepancies'] if f.get('path')), comparison['discrepancies'][0])
        value.update(exact_discrepancy_json_path=first.get('path', first.get('field')),
                     exact_discrepancy_kind=first.get('kind'), expected_field_value=first.get('expected'),
                     actual_field_value=first.get('actual'))
    for side, receipt in (('tested', tested), ('reference', reference)):
        value['raw_' + side + '_stdout_bytes'] = dict(storage='lossless indexed raw bytes', **receipt['stdout'])
        value['raw_' + side + '_stderr_bytes'] = dict(storage='lossless indexed raw bytes', **receipt['stderr'])
        value['unnormalized_' + side + '_output'] = dict(storage='decode referenced raw stdout without normalization')
    transform = inputs.get('transformation') or {}
    for target, source in (('left_transport_map', 'left_transport'), ('right_transport_map', 'right_transport'),
                           ('left_vertex_layout', 'left_vertex_layout'), ('right_vertex_layout', 'right_vertex_layout')):
        value[target] = transform.get(source)
    value['inverse_transport_maps'] = {k: transform.get(k) for k in ('left_inverse', 'right_inverse')}
    if inputs['transformed']:
        value['designated_root_handles'] = {s: inputs['transformed']['snapshots'][s]['root'] for s in ('left', 'right')}
        value['record_presentation_order_with_positions_and_ids'] = [dict(position=i, id=r['id'], record=r)
            for i, r in enumerate(inputs['transformed']['evidence'])]
    value['null_reasons'] = {k: 'Not applicable, or unavailable; see exact comparison/raw receipts and BLOCKED obligations. No value inferred.'
                             for k, v in value.items() if v is None}
    return value


def execute_batch(root, meta, contract, journal, cases, timeout):
    verify_execution_identities(root, meta)
    attempt_id = uuid.uuid4().hex
    values = [contract.materialize(case) for case in cases]
    input_receipts = [journal.object(v) for v in values]
    ids = [f'a{attempt_id[:20]}-{i}' for i in range(len(cases))]
    frames = [make_frames(c, v, r) for c, v, r in zip(cases, values, ids)]
    event = event_base(root, meta, 'attempt')
    event.update(attempt_id=attempt_id, start=cases[0]['schedule_ordinal'],
                 inputs=input_receipts, request_ids=ids,
                 ordinal_range=[cases[0]['schedule_ordinal'], cases[-1]['schedule_ordinal']])
    journal.append(event)
    commands = commands_for(root, meta, cases[0])
    processes = {}
    for i, side in enumerate(('tested', 'reference')):
        processes[side] = run_process(root, commands[i], b''.join(f[i] for f in frames), timeout, side)
    incident = None
    if any(p['exit_status'] != 0 or p['timeout'] for p in processes.values()):
        incident = 'OPERATIONAL_FAILURE: process exit/timeout; no batch coverage credited'
    if incident is None:
        try:
            for side, process in processes.items():
                validate_process_batch(root, contract, cases, values, ids, side, process)
        except (IntegrityError, ValueError, KeyError, TypeError) as error:
            incident = 'OPERATIONAL_FAILURE: ' + str(error)
    event = event_base(root, meta, 'processes')
    event.update(attempt_id=attempt_id, processes=processes, incident=incident)
    journal.append(event)
    require(incident is None, incident or '')
    streams = {side: iter(output_lines(root, p['stdout'])) for side, p in processes.items()}
    for position, (case, inputs, input_receipt) in enumerate(zip(cases, values, input_receipts)):
        rows, receipts = {}, {}
        for side in ('tested', 'reference'):
            raw, segment = next(streams[side], (None, None))
            require(raw is not None, side + ': missing response')
            row = decode(raw)
            response_identity(contract, case, row, side, position + 1, ids[position])
            rows[side] = row
            receipts[side] = dict(case_id=case['case_id'], ordinal=case['global_ordinal'],
                input_sha256=digest(canonical(inputs['transformed'])), attempt_id=attempt_id, side=side,
                executable_sha256=execution_hash(meta, case, side), stdout=segment,
                stdout_sha256=segment['sha256'], stderr=processes[side]['stderr'],
                stderr_sha256=processes[side]['stderr']['sha256'], exit_status=processes[side]['exit_status'])
        comparison = compare_case(contract, case, inputs, rows['tested'], rows['reference'])
        comparison_receipt = journal.object(comparison)
        replay = None
        if comparison['status'] != 'PASS':
            replay = journal.object(replay_record(root, meta, contract, case, inputs, comparison,
                                                  receipts['tested'], receipts['reference'], attempt_id))
        event = event_base(root, meta, 'case')
        for receipt in receipts.values():
            receipt.update(comparison_status=comparison['status'],
                           failure_class=None if comparison['status'] == 'PASS' else comparison['triage'],
                           evidence_offsets=receipt['stdout'])
        event.update(case=case, inputs=input_receipt, input_sha256=digest(canonical(inputs['transformed'])),
                     attempt_id=attempt_id, comparison=comparison_receipt, replay=replay,
                     ordinal_range=[case['schedule_ordinal'], case['schedule_ordinal']], **receipts)
        journal.append(event)
    for side, stream in streams.items():
        require(next(stream, None) is None, side + ': excess/duplicate response')


def summary(meta, state):
    completed = state['completed_receipts']
    frozen = sum(s['compared'] for key, s in state['ledgers'].items()
                 if key not in ('auxiliary_m04_association', 'derived_observable_equivalence_laws'))
    if meta['mode'] != 'campaign':
        frozen = 0
        execution = ('DRY_RUN_QUALIFICATION' if completed == 20 else 'PARTIAL_DRY_RUN')
        if meta['mode'] != 'dry-run':
            execution = 'NON_CAMPAIGN_EXECUTION'
    else:
        execution = 'EXHAUSTIVE_EXECUTION' if completed == 529424 + 22764 else 'PARTIAL_EXECUTION'
    negative = any(s['failed'] for s in state['ledgers'].values())
    measured = {}
    for side, raw in state['measured_adapter_work'].items():
        def total(*fields):
            values = [raw.get(f, 0) for f in fields]
            return None if any(v is None for v in values) else sum(values)
        measured[side] = dict(side=side, process_invocations=state['process_invocations'][side],
            input_conversions=None,
            actual_candidate_generations=total('candidates_generated', 'baseline_candidates_generated'),
            actual_candidate_evaluations=total('candidate_evaluations', 'cache_candidate_evaluations', 'baseline_candidate_evaluations'),
            actual_binary_relation_classifications=total('reference_relation_classifications', 'baseline_relation_classifications'),
            actual_decision_assignment_checks=total('decision_assignment_checks', 'baseline_decision_assignment_checks'),
            actual_union_assignment_checks=total('union_assignment_checks', 'baseline_union_assignment_checks'),
            actual_rejection_certificate_rows_generated=total('rejection_rows_generated') if side == 'tested' else None,
            actual_certificate_rows_verified=total('certificate_rows_verified') if side == 'tested' else None,
            baseline_reuses=total('cache_hits'), baseline_recomputations=total('baseline_recomputations', 'cache_builds'),
            retry_invocations=state['retry_invocations'][side], bytes_written=state['raw_process_bytes_written'][side],
            unavailable_reason='No input conversion hook; reference certificate generation/verification not separately instrumented. '
                               'Unreceipted interrupted process work is unavailable; counters cover durable completed process receipts only.')
    logical_matrix = {side: 6 * sum(row['compared'] for key, row in state['ledgers'].items()
                                   if key.startswith('matrix_')) for side in ('tested', 'reference')}
    if meta['mode'] != 'campaign':
        logical_matrix = dict(tested=0, reference=0)
    return dict(execution=execution, result='NEGATIVE_RESULT_PENDING_TRIAGE' if negative else 'INCONCLUSIVE_RESULT',
                qualification=('PASS_BOUNDED_DRY_RUN_ONLY' if meta['mode'] == 'dry-run' and completed == 20
                               and not negative and not state['operational_incidents'] else 'INCONCLUSIVE'),
                integrity_audit='PASS',
                scientific_acceptance=state['acceptance']['scientific_acceptance'],
                complete_scientific_acceptance=state['acceptance']['complete_scientific_acceptance'],
                EXP007_STATUS='INCONCLUSIVE',
                CAMPAIGN_EXECUTED='YES' if meta['mode'] == 'campaign' else 'NO',
                campaign_primary_compared=frozen,
                campaign_auxiliary_compared=state['ledgers']['auxiliary_m04_association']['compared'] if meta['mode'] == 'campaign' else 0,
                dry_run_receipts=completed if meta['mode'] == 'dry-run' else 0,
                measured_work=measured, logical_matrix_candidate_obligations_discharged=logical_matrix,
                dry_run_candidate_obligations_per_side=completed * 6 if meta['mode'] == 'dry-run' else 0,
                frozen_totals=dict(primary=529423, auxiliary=1, derived=22764),
                blocked_obligations=BLOCKED, **state)


def run_campaign(root, meta, contract, max_cases, timeout):
    journal, state = audit(root, meta, contract)
    start = state['completed_receipts']
    scheduler = itertools.islice(contract.schedule(meta['mode']), start, None)
    remaining = max_cases
    pending = next(scheduler, None)
    last_update = 0
    while pending is not None and (remaining is None or remaining > 0):
        batch = [pending]
        size = min(BATCH, remaining) if remaining is not None else BATCH
        pending = None
        while len(batch) < size:
            candidate = next(scheduler, None)
            if candidate is None:
                break
            if candidate['suite_id'] != batch[0]['suite_id']:
                pending = candidate
                break
            batch.append(candidate)
        try:
            execute_batch(root, meta, contract, journal, batch, timeout)
        except (Exception, KeyboardInterrupt) as error:
            event = event_base(root, meta, 'incident')
            event.update(reason=type(error).__name__ + ': ' + str(error),
                         interrupted_batch_start=batch[0]['schedule_ordinal'],
                         scientific_claim='INCONCLUSIVE')
            journal.append(event)
            raise
        if remaining is not None:
            remaining -= len(batch)
        if batch[-1]['schedule_ordinal'] - last_update >= 1024:
            print(canonical(dict(progress_schedule_ordinal=batch[-1]['schedule_ordinal'],
                                 scientific_claim='INCONCLUSIVE')).decode(), file=sys.stderr, flush=True)
            last_update = batch[-1]['schedule_ordinal']
        if pending is None:
            pending = next(scheduler, None)
    # Independent reconstruction, including raw process and comparison checks,
    # is required before publishing any durable completion/ledger summary.
    journal, state = audit(root, meta, contract)
    report = summary(meta, state)
    event = event_base(root, meta, 'summary')
    event.update(report)
    journal.append(event)
    report['journal_head_sha256'] = journal.previous
    report['index_sha256'] = file_hash(root / 'index.jsonl')
    report['index_bytes'] = (root / 'index.jsonl').stat().st_size
    report['metadata_sha256'] = file_hash(root / 'metadata.json')
    publish_new(root / ('summary-' + uuid.uuid4().hex + '.json'), canonical(report))
    print(canonical(report).decode())
    if report['first_mismatch']:
        return 1
    return 0 if report['qualification'] == 'PASS_BOUNDED_DRY_RUN_ONLY' else 3


def replay(root, meta, contract, case_id, destination, timeout):
    _, state = audit(root, meta, contract)
    saved = None
    journal = Journal(root)
    for event in journal.records():
        if event['kind'] == 'case' and event['case']['case_id'] == case_id:
            require(saved is None, 'duplicate replay case identity')
            saved = event
    require(saved is not None, 'case has no validated durable receipt')
    inputs = decode(journal.read(saved['inputs']))
    case = saved['case']
    require(inputs == contract.materialize(case), 'saved exact replay input drift')
    target = fresh(destination)
    replay_journal = Journal(target)
    request_id = 'replay-' + uuid.uuid4().hex[:20]
    frames = make_frames(case, inputs, request_id)
    commands = commands_for(root, meta, case)
    processes = {}
    rows = {}
    for i, side in enumerate(('tested', 'reference')):
        processes[side] = run_process(target, commands[i], frames[i], timeout, 'replay-' + side)
        require(processes[side]['exit_status'] == 0 and not processes[side]['timeout'], 'replay process failure; raw retained')
        stream = iter(output_lines(target, processes[side]['stdout']))
        raw, _ = next(stream, (None, None))
        require(raw is not None and next(stream, None) is None, 'replay response count failure')
        rows[side] = decode(raw)
        response_identity(contract, case, rows[side], side, 1, request_id)
    result = compare_case(contract, case, inputs, rows['tested'], rows['reference'])
    previous = decode(journal.read(saved['comparison']))
    report = dict(mode='REPLAY_ONLY', campaign_credit=0, case_id=case_id,
                  saved_run_id=meta['run_id'], original_inputs=replay_journal.object(inputs),
                  original_receipt=saved, metadata_sha256=file_hash(root / 'metadata.json'),
                  processes=processes, comparison=result, previous_comparison=previous,
                  discrepancy_reproduced=(result == previous),
                  EXP007_STATUS='INCONCLUSIVE', scientific_counterexample_certified=False,
                  original_verified_coverage=state['completed_receipts'])
    publish_new(target / 'replay.json', canonical(report))
    print(canonical(report).decode())
    return 1 if result['status'] == 'FAIL' or result != previous else 3 if result['status'] == 'BLOCKED' else 0


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('must be positive')
    return number


def main(argv=None):
    global ROOT
    argv = sys.argv[1:] if argv is None else argv
    if argv == ['--_reference']:
        return internal_reference()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate', help='read-only frozen identities, lazy schedule counts and blocked contracts')
    for command in ('dry-run', 'campaign', 'resume', 'audit', 'replay'):
        child = sub.add_parser(command)
        child.add_argument('--out', required=True, type=Path, help='external directory; fresh except resume/audit')
        if command != 'audit':
            child.add_argument('--timeout', type=positive, default=60, help='per-process seconds')
        if command in ('campaign', 'resume', 'replay'):
            child.add_argument('--execute', action='store_true', required=True, help='explicit execution opt-in')
        if command in ('campaign', 'resume'):
            child.add_argument('--max-cases', type=positive, help='maximum NEW receipts; partial stays INCONCLUSIVE')
        if command in ('dry-run', 'campaign'):
            child.add_argument('--cc', default='cc', help='local C compiler, no shell')
        if command == 'replay':
            child.add_argument('--run', required=True, type=Path)
            child.add_argument('--case-id', required=True)
    args = parser.parse_args(argv)
    if BASE.name == 'sources' and (BASE.parent / 'metadata.json').is_file():
        archive = decode(read_small(BASE.parent / 'metadata.json'))
        ROOT = Path(archive['repository_root']).resolve()
    contract = Contract()
    if args.command == 'validate':
        identities = validate_sources(contract)
        # Count without enumerating 529424 inputs or running any solver.
        calculated = {s['id']: sum(contract.count(s, identifier) for identifier in
                      s.get('fixture_ids', [s.get('instance_id', 'Q')])) for s in contract.suites}
        require(all(calculated[s['id']] == (s['required_cases'] if s['required_cases'] is not None else 22764)
                    for s in contract.suites), 'schedule cardinality mismatch')
        print(canonical(dict(CLI_GATE='PASS_READ_ONLY', SCHEDULING_GATE='PASS_DECLARATIONS',
            suite_counts=calculated, primary_required=529423, auxiliary_required=1,
            derived_required=22764, test_identities=identities, source_hashes=contract.hashes,
            blocked_obligations=BLOCKED, CAMPAIGN_EXECUTED='NO', EXP007_STATUS='INCONCLUSIVE')).decode())
        return 0
    if args.command in ('dry-run', 'campaign'):
        root = fresh(args.out)
        meta = prepare(root, contract, args.command, args.timeout, args.cc)
    else:
        root = external(args.run if args.command == 'replay' else args.out)
        meta = decode(read_small(root / 'metadata.json'))
    # Readers also lock exclusively so audit cannot inspect a partially appended
    # writer record. No separate mutable lock/index database is created.
    with (root / 'metadata.json').open('rb') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        verify_meta(root, meta, contract)
        if args.command == 'replay':
            return replay(root, meta, contract, args.case_id, args.out, args.timeout)
        if args.command == 'audit':
            journal, state = audit(root, meta, contract)
            report = summary(meta, state)
            report.update(journal_head_sha256=journal.previous,
                          index_sha256=file_hash(root / 'index.jsonl') if (root / 'index.jsonl').exists() else None)
            print(canonical(report).decode())
            return 1 if state['first_mismatch'] else 0
        return run_campaign(root, meta, contract, getattr(args, 'max_cases', None), args.timeout)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('INTERRUPTED: evidence retained; run audit before resume; EXP007_STATUS=INCONCLUSIVE', file=sys.stderr)
        sys.exit(130)
    except (IntegrityError, ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        print(canonical(dict(status='BLOCKED', failure_class='OPERATIONAL_FAILURE',
                             missing_contract_or_error=str(error), EXP007_STATUS='INCONCLUSIVE',
                             evidence='Retained without repair/deletion; no credit for incomplete receipts')).decode(), file=sys.stderr)
        sys.exit(2)
