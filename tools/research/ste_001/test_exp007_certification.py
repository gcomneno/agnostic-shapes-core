#!/usr/bin/env python3
"""B3 bounded ARTIFICIAL qualification, never an official EXP-007 result.

python3 -B tools/research/ste_001/test_exp007_certification.py -v
All evidence is retained under /tmp. Mutations deliberately fabricate process
receipts in this qualification fixture only; no synthetic mismatch is claimed
as a real solver defect. No campaign, exhaustive matrix or sweep is executed.
"""
import copy
from contextlib import redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp007_run as run
import test_exp007_acceptance as b2

MODE = 'ARTIFICIAL_B3_QUALIFICATION_ONLY'


class ArtificialContract(run.Contract):
    def schedule(self, mode):
        if mode != MODE:
            raise AssertionError('B3 qualification cannot execute a campaign')
        yield from self.cases


def corrupt(row):
    """Deliberately artificial mutations, explicitly outside scientific evidence."""
    case_id = row['case_id']
    if '/F12/' in case_id:
        row['result']['candidate']['conditional'] = False
    elif '/F01/' in case_id:
        row['input']['assumes_unchanged_incidence'] = True
        # Supply an explicit transport discrepancy that the independent harness
        # check can attach to this artificial case's adjudication.
        row['transformation']['composed'] = True
    elif '/M01/' in case_id:
        row['result']['material']['associations'][0]['decisions'][0]['witnesses'][0]['material']['l1'] = 'rho'
    elif '/M03/' in case_id and '/named_materials/' in case_id:
        row['result']['material']['associations'][0]['decisions'][0]['rejection_certificate'][0]['violated'] = []
    elif '/M04/' in case_id and '/named_materials/' in case_id:
        row['result']['material']['observable_classes'][0]['members'][0]['decision'] = 'd_rho'
    elif '/F13-' in case_id:
        row['result']['candidate']['status'] = 'SUPPORTED'
    elif '/derived-observable-laws/' in case_id:
        row['law']['operation_results'][0] = not row['law']['operation_results'][0]


class ConcreteCertificationChecks(unittest.TestCase):
    """Focused in-memory regressions; no archives, processes or directories."""

    @classmethod
    def setUpClass(cls):
        cls.contract = run.Contract()
        suite = next(s for s in cls.contract.suites if s['id'] == 'named_materials')
        cls.case = cls.contract.descriptor(suite, 'M03', 0, 0)
        cls.inputs = cls.contract.materialize(cls.case)
        cls.good = run.reference_evaluate(cls.contract, cls.case, cls.inputs)

    def checked(self, row):
        ref = self.contract.ref
        with patch.object(ref, 'evaluate_candidate', side_effect=AssertionError('construction')), \
                patch.object(ref, 'evaluate_material', side_effect=AssertionError('construction')), \
                patch.object(ref, 'decision_obligations', side_effect=AssertionError('shared obligations')), \
                patch.object(run, 'run_process', side_effect=AssertionError('process execution')):
            return run.concrete_verification(self.case, self.inputs, row)

    @staticmethod
    def rejection(row):
        return next(d for a in row['result']['material']['associations'] for d in a['decisions']
                    if d['outcomes'] == [dict(tag='REJECT')])

    def test_violated_conjuncts_are_complete_unordered_collections(self):
        import itertools
        self.assertEqual(self.checked(self.good), dict(status='PASS', violations=[], blocked=[]))
        for order in itertools.permutations(['preserve:l2', 'update:left_lambda', 'update:right_rho']):
            row = copy.deepcopy(self.good)
            cert = next(r for r in self.rejection(row)['rejection_certificate']
                        if set(r['violated']) == set(order))
            cert['violated'] = list(order)
            before = copy.deepcopy(row)
            with self.subTest(order=order):
                self.assertEqual(self.checked(row), dict(status='PASS', violations=[], blocked=[]))
                self.assertEqual(row, before)

    def test_wrong_conjuncts_and_satisfaction_values_are_rejected(self):
        ids = ['preserve:l2', 'update:left_lambda', 'update:right_rho']
        for invalid in (ids[:-1], ids + ['extra'], ids + [ids[0]], ['wrong', *ids[1:]],
                        [], None, True, ids[0], {i: True for i in ids}, [False, *ids[1:]]):
            row = copy.deepcopy(self.good)
            cert = next(r for r in self.rejection(row)['rejection_certificate'] if len(r['violated']) == 3)
            cert['violated'] = invalid
            with self.subTest(violated=invalid):
                checked = self.checked(row)
                self.assertTrue(checked['violations'] or checked['blocked'])
        for invalid in (False, 1):
            row = copy.deepcopy(self.good)
            row['result']['candidate']['predicates'][0]['evidence_satisfied'] = invalid
            self.assertTrue(self.checked(row)['violations'])
        row = copy.deepcopy(self.good)
        witness = next(w for a in row['result']['material']['associations']
                       for d in a['decisions'] for w in d['witnesses'])
        witness['satisfied'] = [False]
        self.assertTrue(self.checked(row)['violations'])

    def test_incomplete_duplicate_and_malformed_certificates_are_rejected(self):
        mutations = [
            lambda d: d['rejection_certificate'].pop(),
            lambda d: d['rejection_certificate'].append(copy.deepcopy(d['rejection_certificate'][0])),
            lambda d: d['rejection_certificate'].__setitem__(1, copy.deepcopy(d['rejection_certificate'][0])),
            lambda d: d.__setitem__('rejection_certificate', None),
            lambda d: d.__setitem__('rejection_certificate', {}),
            lambda d: d['rejection_certificate'].__setitem__(0, None),
            lambda d: d['rejection_certificate'].__setitem__(0, []),
            lambda d: d['rejection_certificate'].__setitem__(0, {}),
            lambda d: d['rejection_certificate'][0].__setitem__('extra', True),
            lambda d: d['rejection_certificate'][0].__setitem__('material', []),
            lambda d: d['rejection_certificate'][0]['material'].__setitem__('foreign', '0'),
            lambda d: d['rejection_certificate'][0]['material'].__setitem__('l0', 'invalid'),
        ]
        for index, mutate in enumerate(mutations):
            row = copy.deepcopy(self.good)
            mutate(self.rejection(row))
            with self.subTest(mutation=index):
                checked = self.checked(row)
                self.assertTrue(checked['violations'] or checked['blocked'])

    def test_harness_fixture_has_an_independently_checked_transport_discrepancy(self):
        suite = next(s for s in self.contract.suites if s['id'] == 'named_candidates')
        case = self.contract.descriptor(suite, 'F01', 0, 0)
        inputs = self.contract.materialize(case)
        reference = run.reference_evaluate(self.contract, case, inputs)
        tested = copy.deepcopy(reference)
        tested.update(case_id=case['case_id'], input=copy.deepcopy(inputs['transformed']),
                      transformation=copy.deepcopy(inputs['transformation']),
                      consumption=dict(candidate_called=True, record_hook=True, received_records=[]))
        corrupt(tested)
        comparison = run.compare_case(self.contract, case, inputs, tested, reference)
        independent = run.independent_assessment(self.contract, dict(case_event=dict(case=case), inputs=inputs,
            rows=dict(tested=tested, reference=reference), comparison=comparison))
        self.assertEqual(independent['status'], 'VERIFIED')
        self.assertFalse(any(f['category'] == 'SCIENTIFIC' for f in independent['findings']))
        self.assertTrue(any(f['category'] == 'HARNESS' and f['obligation_id'] == 'FA04'
            and f['detail']['path'] == '$.transformation.composed'
            and any(run.discrepancy_covers(d, f['detail']) for d in comparison['discrepancies'])
            for f in independent['findings']))


class Certification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.area = Path(tempfile.mkdtemp(prefix='exp007-b3-artificial-'))
        cls.contract = ArtificialContract()
        selections = [('named_candidates', 'F01', 0), ('named_candidates', 'F12', 0),
                      *[('named_candidates', 'F13-' + v, 0) for v in
                        ('duplicated_handle', 'foreign_handle', 'invalid_tree', 'invalid_root')],
                      *[('named_materials', m, 0) for m in
                        ('M01', 'M02', 'M03', 'M04', 'M05-P', 'M05-O', 'M05-I')],
                      ('candidate_relabelings', 'F12', 19), ('material_relabelings', 'M02', 19),
                      ('vertex_layouts', 'F11', 575), ('association_orders', 'M03', 719),
                      ('material_outcome_orders', 'M04', 1),
                      # TRANSITIVITY/1/1/1: genuine ACCEPT materials for binding mutations.
                      ('derived_observable_equivalence_laws', 'Q', 1625)]
        cls.cases = [cls.contract.descriptor(next(s for s in cls.contract.suites if s['id'] == suite),
                     name, rank, i) for i, (suite, name, rank) in enumerate(selections)]
        cls.contract.cases = cls.cases
        cls.root = run.fresh(cls.area / 'original')
        cls.meta = run.prepare(cls.root, cls.contract, MODE, 60, 'cc')
        cls.good = {}
        real_process = run.run_process

        def artificial_process(root, argv, stdin_raw, timeout, label):
            p = real_process(root, argv, stdin_raw, timeout, label)
            if label in ('tested', 'replay-tested') and p['exit_status'] == 0:
                rows = [run.decode(raw) for raw, _ in run.output_lines(root, p['stdout'])]
                for row in rows:
                    cls.good.setdefault(row['case_id'], copy.deepcopy(row))
                    corrupt(row)
                path = root / p['stdout']['path']
                # Test-only fabrication of bounded external receipts. Production
                # never mutates a raw receipt or repairs an existing archive.
                path.write_bytes(b''.join(run.canonical(r) + b'\n' for r in rows))
                p['stdout'].update(bytes=path.stat().st_size, sha256=run.file_hash(path))
            return p
        cls.artificial_process = staticmethod(artificial_process)
        journal = run.Journal(cls.root)
        import itertools
        with patch.object(run, 'run_process', side_effect=artificial_process):
            for _, cases in itertools.groupby(cls.cases, key=lambda c: c['suite_id']):
                run.execute_batch(cls.root, cls.meta, cls.contract, journal, list(cases), 60)
        cls.events = [e for e in run.Journal(cls.root).records() if e['kind'] == 'case']
        cls.replays, cls.bindings = {}, {}
        for i, event in enumerate(cls.events):
            comparison = run.decode(journal.read(event['comparison']))
            if comparison['status'] != 'FAIL':
                continue
            case_id = event['case']['case_id']
            destination = cls.area / f'replay-{i}'
            with patch.object(run, 'run_process', side_effect=artificial_process), redirect_stdout(io.StringIO()):
                run.replay(cls.root, cls.meta, cls.contract, case_id, destination, 60)
            cls.replays[case_id] = destination
            cls.bindings[case_id] = run.adjudication_binding(cls.root, cls.meta, cls.contract, run,
                case_id, 'tested', destination)
        cls.snapshot = {p: p.read_bytes() for p in cls.area.rglob('*') if p.is_file()}
        run.write_new(cls.area / 'qualification.json', run.canonical(dict(
            qualification='ARTIFICIAL_MUTATIONS_ONLY_NOT_SCIENTIFIC_RESULTS', campaign_credit=0,
            CAMPAIGN_EXECUTED='NO', EXP007_STATUS='INCONCLUSIVE', cases=len(cls.cases),
            artificial_mismatches=len(cls.bindings), test_source_sha256=run.file_hash(Path(__file__)))))

    def setUp(self):
        self.store = self.area / ('store-' + self._testMethodName)

    def tearDown(self):
        for p, raw in self.snapshot.items():
            if p.read_bytes() != raw:
                p.write_bytes(raw)

    def binding(self, selector='F12', suite='named_candidates'):
        return copy.deepcopy(next(b for b in self.bindings.values()
                                  if b['case']['selector'] == selector and b['case']['suite_id'] == suite))

    def proposal(self, state='CERTIFIED_COUNTEREXAMPLE', selector='F12', suite='named_candidates'):
        binding = self.binding(selector, suite)
        category = 'HARNESS' if state == 'REJECTED_AS_HARNESS_ERROR' else 'SCIENTIFIC'
        findings = [f for f in binding['independent']['findings'] if f['category'] == category and
                    (category == 'HARNESS' or f['side'] == binding['side'])]
        finding = next((f for f in findings if any(run.discrepancy_covers(d['detail'], f['detail'])
                                                 for d in binding['discrepancies'])), None)
        if state == 'REJECTED_AS_HARNESS_ERROR':
            self.assertIsNotNone(finding, 'Harness adjudication fixture needs a checked, matching finding')
        obligation_id = finding['obligation_id'] if finding else 'FA05'
        conclusion = dict(CERTIFIED_COUNTEREXAMPLE='BOUNDED_NEGATIVE_RESULT',
                          REJECTED_AS_HARNESS_ERROR='HARNESS_ERROR', INCONCLUSIVE='INCONCLUSIVE',
                          PENDING_TRIAGE='PENDING_TRIAGE')[state]
        review = dict(reviewer=dict(identity='ARTIFICIAL reviewer for qualification only',
            role='independent scientific reviewer (synthetic declaration)',
            independence_statement='Synthetic declared review: no solver implementation contribution.',
            relationship_to_implementations=dict(tested='No declared contribution',
                reference='No declared contribution', driver='Qualification reviewer only')),
            frozen_obligation=dict(id=obligation_id,
                requirement=self.contract.plan['full_acceptance']['required'][int(obligation_id[2:])-1],
                protocol_sha256=self.contract.plan['protocol']['sha256']),
            discrepancy_ids=[d['id'] for d in binding['discrepancies']],
            finding_ids=[finding['id']] if finding else [],
            mathematical_derivation='Artificial F12 mutation: an unresolved record entails conditional enumeration; False violates that Boolean obligation.',
            oracle_validity_analysis='Concrete original and replay oracle checks are bound below; this is synthetic qualification.',
            harness_transport_exclusion_analysis='Concrete transport/input and source receipts checked; synthetic qualification only.',
            replay_evidence_references=binding['replay'],
            scoped_scientific_conclusion=dict(kind=conclusion, obligation_id=obligation_id, exhaustive_campaign_claim=False),
            rationale='Qualify the explicit decision mechanism, without asserting any real scientific finding.',
            timestamp='2026-11-17T12:00:00+00:00')
        return dict(schema=run.ADJUDICATION_SCHEMA, binding=binding, state=state, supersedes=None,
                    review=review if state != 'PENDING_TRIAGE' else None)

    def append(self, record):
        return run.append_adjudication(self.root, self.store, record, self.contract, self.meta, run)

    def audited(self):
        return run.audit_adjudications(self.root, self.store, self.contract, self.meta, run)

    def test_no_implicit_promotion_from_replay_certificate_file_or_flags(self):
        _, state = run.audit(self.root, self.meta, self.contract)
        before = state['acceptance']
        run.write_new(self.root / 'certificate.json', run.canonical(dict(certified=True, state='CERTIFIED_COUNTEREXAMPLE')))
        replay_root = self.replays[self.binding()['case']['case_id']]
        path = replay_root / 'replay.json'
        report = run.decode(path.read_bytes())
        report.update(discrepancy_reproduced=True, scientific_counterexample_certified=True, certified=True)
        path.write_bytes(run.canonical(report))
        _, after = run.audit(self.root, self.meta, self.contract)
        self.assertEqual(before, after['acceptance'])
        self.assertEqual(before['scientific_counterexamples_certified'], 0)
        self.assertEqual(before['pending_triage_cases'], len(self.bindings))

    def test_all_four_states_and_explicit_supersession(self):
        pending = self.proposal('PENDING_TRIAGE')
        first = self.append(pending)
        certified = self.proposal()
        with self.assertRaisesRegex(run.IntegrityError, 'supersession'):
            self.append(certified)
        certified['supersedes'] = first['record_sha256']
        second = self.append(certified)
        inconclusive = self.proposal('INCONCLUSIVE')
        inconclusive['supersedes'] = second['record_sha256']
        third = self.append(inconclusive)
        # A new binding to a different original case cannot supersede this case.
        harness = self.proposal('REJECTED_AS_HARNESS_ERROR', 'F01')
        harness['supersedes'] = third['record_sha256']
        with self.assertRaisesRegex(run.IntegrityError, 'supersession'):
            self.append(harness)
        harness['supersedes'] = None
        self.append(harness)
        report = self.audited()
        self.assertEqual(report['states']['INCONCLUSIVE'], 1)
        self.assertEqual(report['states']['REJECTED_AS_HARNESS_ERROR'], 1)
        self.assertEqual(report['records'], 4)
        self.assertEqual(report['campaign_credit'], 0)

    def test_all_states_can_be_superseded_but_history_is_never_overwritten(self):
        record = self.proposal('REJECTED_AS_HARNESS_ERROR', 'F01')
        first = self.append(record)
        files = {p: p.read_bytes() for p in (self.store / 'chunks').iterdir()}
        replacement = self.proposal('INCONCLUSIVE', 'F01')
        replacement['supersedes'] = first['record_sha256']
        self.append(replacement)
        for p, raw in files.items():
            self.assertEqual(p.read_bytes(), raw)
        self.assertEqual(self.audited()['records'], 2)

    def test_binding_mutations_are_rejected(self):
        record = self.proposal()
        mutations = [lambda b: b.__setitem__('run_id', 'different'),
            lambda b: b['case'].__setitem__('case_id', 'absent'),
            lambda b: b['case'].__setitem__('selector', 'F01'),
            lambda b: b['case'].__setitem__('variant_rank', 1),
            lambda b: b['case'].__setitem__('schedule_ordinal', 999),
            lambda b: b.__setitem__('attempt_id', 'wrong'),
            lambda b: b.__setitem__('side', 'reference'),
            lambda b: b['inputs']['original']['evidence'][0].__setitem__('assessment', 'ACCEPTED'),
            lambda b: b['inputs']['transformed']['evidence'][0].__setitem__('target', 'r1'),
            lambda b: b['identities']['binaries']['nonmatrix'].__setitem__('sha256', '0'*64),
            lambda b: b['original_receipt']['tested'].__setitem__('side', 'reference'),
            lambda b: b['original_processes']['processes']['tested']['stdout'].__setitem__('bytes', 0),
            lambda b: b['comparison'].__setitem__('status', 'PASS'),
            lambda b: b['replay']['comparison'].__setitem__('status', 'PASS'),
            lambda b: b['replay']['processes']['reference']['stdin'].__setitem__('sha256', '0'*64),
            lambda b: b['journal_prefix'].__setitem__('sha256', '0'*64),
            lambda b: b['journal_prefix'].__setitem__('bytes', b['journal_prefix']['bytes']-1)]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                bad = copy.deepcopy(record)
                mutate(bad['binding'])
                with self.assertRaises((run.IntegrityError, KeyError)):
                    self.append(bad)
        law = self.proposal(selector='Q', suite='derived_observable_equivalence_laws')
        operand = law['binding']['inputs']['law']['operands'][0]
        self.assertEqual(operand['tag'], 'ACCEPT')
        self.assertIn('material', operand)
        self.assertEqual(operand['material']['l0'], '0')
        operand['material']['l0'] = 'rho'
        with self.assertRaisesRegex(run.IntegrityError, 'binding drift'):
            self.append(law)

    def test_referenced_raw_content_length_hash_and_order_are_checked(self):
        binding = self.binding()
        receipts = [self.root / binding['original_receipt']['tested']['stdout']['file']['path'],
                    self.root / binding['original_receipt']['inputs']['path'],
                    self.root / 'sources/exp007_run.py', self.root / 'bin/nonmatrix',
                    Path(binding['replay']['root']) / binding['replay']['processes']['tested']['stdout']['path'],
                    Path(binding['replay']['root']) / binding['replay']['processes']['reference']['stdin']['path']]
        for path in receipts:
            for mutation in ('length', 'hash'):
                with self.subTest(path=str(path), mutation=mutation):
                    raw = path.read_bytes()
                    path.write_bytes(raw[:-1] if mutation == 'length' else bytes([raw[0] ^ 1]) + raw[1:])
                    with self.assertRaises((run.IntegrityError, ValueError)):
                        self.append(self.proposal())
                    path.write_bytes(raw)

    def test_duplicate_missing_conflicting_truncated_out_of_order_journal(self):
        path = self.root / 'index.jsonl'
        raw = path.read_bytes()
        lines = raw.splitlines(keepends=True)
        variants = [b''.join([lines[0], lines[0], *lines[1:]]), b''.join(lines[1:]),
                    b''.join([lines[1], lines[0], *lines[2:]]), raw[:-1]]
        for mutated in variants:
            path.write_bytes(mutated)
            with self.assertRaises(run.IntegrityError):
                self.append(self.proposal())
            path.write_bytes(raw)
        report = self.proposal()
        report['review']['discrepancy_ids'].append(report['review']['discrepancy_ids'][0])
        with self.assertRaisesRegex(run.IntegrityError, 'discrepancy'):
            self.append(report)

    def test_recorded_success_without_actual_reproduction_cannot_certify(self):
        binding = self.binding()
        replay_root = Path(binding['replay']['root'])
        path = replay_root / 'replay.json'
        report = run.decode(path.read_bytes())
        p = report['processes']['tested']
        raw_path = replay_root / p['stdout']['path']
        good = copy.deepcopy(self.good[binding['case']['case_id']])
        old = run.decode(raw_path.read_bytes())
        for k in ('request_id', 'request_index', 'response_id'):
            good[k] = old[k]
        raw_path.write_bytes(run.canonical(good) + b'\n')
        p['stdout'].update(bytes=raw_path.stat().st_size, sha256=run.file_hash(raw_path))
        inputs = binding['inputs']
        reference = run.decode((replay_root / report['processes']['reference']['stdout']['path']).read_bytes())
        report['comparison'] = run.compare_case(self.contract, binding['case'], inputs, good, reference)
        report['discrepancy_reproduced'] = True
        path.write_bytes(run.canonical(report))
        new_binding = run.adjudication_binding(self.root, self.meta, self.contract, run,
            binding['case']['case_id'], 'tested', replay_root)
        self.assertFalse(new_binding['replay']['reproduced'])
        record = self.proposal()
        record['binding'] = new_binding
        record['review']['replay_evidence_references'] = new_binding['replay']
        with self.assertRaisesRegex(run.IntegrityError, 'does not reproduce'):
            self.append(record)

    def test_review_is_complete_explicit_and_never_boolean_independence(self):
        record = self.proposal()
        for field in run.REVIEW_FIELDS:
            bad = copy.deepcopy(record)
            bad['review'].pop(field)
            with self.subTest(field=field), self.assertRaises(run.IntegrityError):
                self.append(bad)
        bad = copy.deepcopy(record)
        bad['review']['reviewer'] = dict(identity='someone', independent=True)
        with self.assertRaisesRegex(run.IntegrityError, 'boolean independence'):
            self.append(bad)
        for field in ('independence_statement', 'identity', 'relationship_to_implementations'):
            bad = copy.deepcopy(record)
            bad['review']['reviewer'][field] = True
            with self.assertRaises(run.IntegrityError):
                self.append(bad)

    def test_only_actual_original_discrepancies_and_consistent_obligations(self):
        for field, replacement in [('discrepancy_ids', ['0:' + '0'*64]), ('finding_ids', ['invented'])]:
            bad = self.proposal()
            bad['review'][field] = replacement
            with self.assertRaises(run.IntegrityError):
                self.append(bad)
        bad = self.proposal()
        bad['review']['frozen_obligation']['requirement'] = 'invented requirement'
        with self.assertRaisesRegex(run.IntegrityError, 'obligation drift'):
            self.append(bad)
        good_case = next(c for c in self.cases if c['selector'] == 'M02' and c['suite_id'] == 'named_materials')
        with self.assertRaisesRegex(run.IntegrityError, 'original mismatch'):
            run.verified_case(self.root, self.meta, self.contract, run, good_case['case_id'], run.index_prefix(self.root))

    def test_concrete_verifier_calls_no_solver_or_decision_obligations(self):
        ref = self.contract.ref
        with patch.object(ref, 'evaluate_candidate', side_effect=AssertionError('construction')), \
                patch.object(ref, 'evaluate_material', side_effect=AssertionError('construction')), \
                patch.object(ref, 'decision_obligations', side_effect=AssertionError('shared obligations')):
            for event in self.events:
                case = event['case']
                inputs = run.decode(run.Journal(self.root).read(event['inputs']))
                row = copy.deepcopy(self.good[case['case_id']])
                result = run.concrete_verification(case, inputs, row)
                with self.subTest(case=case['case_id']):
                    self.assertEqual(result, dict(status='PASS', violations=[], blocked=[]))

    def test_material_witness_preservation_rejection_and_membership_failures(self):
        for selector in ('M01', 'M03', 'M04'):
            record = self.proposal(selector=selector, suite='named_materials')
            with self.subTest(selector=selector):
                self.assertEqual(record['binding']['independent']['status'], 'VERIFIED')
                self.assertTrue(record['review']['finding_ids'])
                run.validate_adjudication(record, record['binding'], self.contract)
        record = self.proposal(selector='M03', suite='named_materials')
        check = record['binding']['independent']['checks']['tested']
        self.assertTrue(any('violated' in v['path'] for v in check['violations']))
        record = self.proposal(selector='M01', suite='named_materials')
        self.assertTrue(any('witnesses' in f['detail']['path'] for f in record['binding']['independent']['findings']))

    def test_missing_reject_certificate_and_duplicate_memberships_are_not_valid(self):
        for selector, mutate in (
            ('M03', lambda r: r['result']['material']['associations'][0]['decisions'][0].__setitem__('rejection_certificate', None)),
            ('M02', lambda r: r['result']['material']['observable_classes'][0]['members'].append(copy.deepcopy(r['result']['material']['observable_classes'][0]['members'][0])))):
            event = next(e for e in self.events if e['case']['selector'] == selector and e['case']['suite_id'] == 'named_materials')
            row = copy.deepcopy(self.good[event['case']['case_id']])
            mutate(row)
            result = run.concrete_verification(event['case'], run.decode(run.Journal(self.root).read(event['inputs'])), row)
            self.assertTrue(result['violations'])

    def test_input_and_transport_defects_prevent_scientific_certification(self):
        record = self.proposal(selector='F01')
        self.assertTrue(any(f['category'] == 'HARNESS' for f in record['binding']['independent']['findings']))
        with self.assertRaises(run.IntegrityError):
            self.append(record)
        self.append(self.proposal('REJECTED_AS_HARNESS_ERROR', 'F01'))
        inputs = self.binding('F12', 'candidate_relabelings')['inputs']
        case = self.binding('F12', 'candidate_relabelings')['case']
        inputs['transformation']['left_inverse']['l0'] = 'l0'
        self.assertTrue(run.concrete_transport_errors(self.contract, case, inputs))
        inputs['transformed']['evidence'][0]['provenance']['scope']['target'] = 'foreign'
        self.assertTrue(run.concrete_input_errors(inputs['transformed']))

    def test_f13_erroneous_acceptance_is_a_rejection_obligation_violation(self):
        for variant in ('duplicated_handle', 'foreign_handle', 'invalid_tree', 'invalid_root'):
            record = self.proposal(selector='F13-' + variant)
            with self.subTest(variant=variant):
                self.assertEqual(record['binding']['independent']['status'], 'VERIFIED')
                self.assertFalse(any(f['category'] == 'HARNESS' for f in record['binding']['independent']['findings']))
                run.validate_adjudication(record, record['binding'], self.contract)

    def test_special_negative_fixtures_do_not_become_false_counterexamples(self):
        for event in self.events:
            case = event['case']
            if case['selector'] in ('M03', 'M05-P', 'M05-O', 'M05-I', 'F12'):
                inputs = run.decode(run.Journal(self.root).read(event['inputs']))
                checked = run.concrete_verification(case, inputs, self.good[case['case_id']])
                self.assertEqual(checked['violations'], [])
                self.assertEqual(checked['blocked'], [])

    def test_append_only_deterministic_offline_audit_and_no_campaign_credit(self):
        self.append(self.proposal())
        with patch.object(run, 'run_process', side_effect=AssertionError('offline execution')):
            a, b = self.audited(), self.audited()
            _, state = run.audit(self.root, self.meta, self.contract, adjudications=self.store)
        self.assertEqual(run.canonical(a), run.canonical(b))
        self.assertEqual(a['states']['CERTIFIED_COUNTEREXAMPLE'], 1)
        self.assertEqual(state['acceptance']['scientific_counterexamples_certified'], 1)
        self.assertEqual(state['acceptance']['case_comparison'], 'UNSATISFIED')
        self.assertEqual(state['acceptance']['requirements'][10]['status'], 'UNVERIFIED')
        self.assertTrue(all(v['passed'] == 0 for v in state['acceptance']['counts'].values()))
        _, before = run.audit(self.root, self.meta, self.contract)
        for field in ('ledgers', 'measured_adapter_work', 'completed_receipts', 'process_invocations'):
            self.assertEqual(before[field], state[field])
        self.assertEqual(a['campaign_credit'], 0)

    def test_prefix_survives_later_journal_appends(self):
        self.append(self.proposal())
        before = self.audited()
        journal = run.Journal(self.root)
        list(journal.records())
        event = run.event_base(self.root, self.meta, 'incident')
        event['reason'] = 'ARTIFICIAL later incident, no earlier receipt changes'
        journal.append(event)
        self.assertEqual(before, self.audited())

    def test_conflicting_duplicate_or_torn_adjudications_are_rejected(self):
        record = self.proposal()
        self.append(record)
        with self.assertRaisesRegex(run.IntegrityError, 'supersession'):
            self.append(record)
        journal = run.Journal(self.store)
        events = list(journal.records())
        journal.append(events[0])
        with self.assertRaisesRegex(run.IntegrityError, 'duplicate'):
            self.audited()

    def test_external_storage_and_no_overwrite(self):
        with self.assertRaisesRegex(run.IntegrityError, 'outside the repository'):
            run.append_adjudication(self.root, run.ROOT / 'b3-forbidden', self.proposal(), self.contract, self.meta, run)
        with self.assertRaisesRegex(run.IntegrityError, 'separate'):
            run.append_adjudication(self.root, self.root / 'adjudications', self.proposal(), self.contract, self.meta, run)
        self.append(self.proposal())
        for path, raw in self.snapshot.items():
            self.assertEqual(path.read_bytes(), raw)

    def test_unsupported_checks_are_blocked_and_cannot_be_certified(self):
        record = self.proposal(selector='M01', suite='named_materials')
        record['binding']['independent']['status'] = 'BLOCKED'
        record['binding']['independent']['blocked'] = ['unsupported qualification input']
        # validate_adjudication checks this gate even with a self-consistent
        # binding supplied by a trusted caller; append always recomputes it.
        with self.assertRaisesRegex(run.IntegrityError, 'BLOCKED'):
            run.validate_adjudication(record, record['binding'], self.contract)

    def test_archived_replay_driver_remains_independent_of_current_runner(self):
        root = run.fresh(self.area / 'historical-driver')
        contract = run.Contract()
        meta = run.prepare(root, contract, MODE, 60, 'cc')
        original_driver = run.git('show', 'c66f40b023721fa0601f7b926d8cc27019ac833f:' + run.REL + 'exp007_run.py')
        (root / 'sources/exp007_run.py').write_bytes(original_driver)
        sha = run.digest(original_driver)
        meta['driver_sha256'] = sha
        meta['source_hashes']['exp007_run.py'].update(sha256=sha, bytes=len(original_driver))
        (root / 'metadata.json').write_bytes(run.canonical(meta))
        first = next(contract.schedule('campaign'))  # declaration only, no campaign execution
        run.execute_batch(root, meta, contract, run.Journal(root), [first], 60)
        archived_meta, archived_contract, driver = run.archive_context(root)
        self.assertNotEqual(driver.file_hash(driver.BASE / 'exp007_run.py'), run.file_hash(run.BASE / 'exp007_run.py'))
        with patch.object(run, 'compare_case', side_effect=AssertionError('current comparison substituted')):
            _, state = run.audit(root, archived_meta, archived_contract, original_driver=driver)
        self.assertEqual(state['completed_receipts'], 1)
        self.assertEqual(state['acceptance']['scientific_counterexamples_certified'], 0)
        output = subprocess.run([sys.executable, '-B', str(run.BASE / 'exp007_run.py'), 'audit', '--out', str(root)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(output.returncode, 0, output.stderr.decode())
        self.assertEqual(run.decode(output.stdout)['CAMPAIGN_EXECUTED'], 'NO')


if __name__ == '__main__':
    unittest.main()
