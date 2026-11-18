#!/usr/bin/env python3
"""B2 bounded qualification: synthetic aggregate fixtures and real offline audit.

python3 -B tools/research/ste_001/test_exp007_acceptance.py -v
All products stay in /tmp. No campaign entry point or campaign credit.
Synthetic full accounting exercises the actual evaluator, not a replacement;
its final reporting gate must remain blocked. It is not execution evidence.
"""
import copy
import io
import itertools
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp007_run as run

MODE = 'ACCEPTANCE_QUALIFICATION_ONLY'


class QualificationContract(run.Contract):
    """Bounded archive schedule only; frozen plan/count requirements unchanged."""
    def schedule(self, mode):
        if mode != MODE:
            raise AssertionError('qualification must never execute a campaign')
        yield from self.qualification_cases


def synthetic_completed(contract):
    """Explicit synthetic sufficient-statistic fixture, never a saved summary."""
    ledger = run.ledgers(contract, 'campaign')
    evidence = run.acceptance_evidence(contract)
    for key, row in ledger.items():
        n = row['required']
        for counters in (row, row['tested'], row['reference']):
            for field in ('generated', 'attempted', 'received', 'compared', 'passed'):
                counters[field] = n
            counters['missing'] = 0
        evidence[key].update(receipts=n, passed=n)
        if key.startswith('matrix_'):
            evidence[key]['matrix_predicates'] = dict(tested=6*n, reference=6*n)
    return dict(ledgers=ledger, acceptance_evidence=evidence, completed_receipts=552188,
                identities_verified=True, operational_incidents=0,
                unindexed_chunk_count=0, unfinished_attempt=None)


def remove_case(state, key):
    row = state['ledgers'][key]
    for counters in (row, row['tested'], row['reference']):
        for field in ('generated', 'attempted', 'received', 'compared', 'passed'):
            counters[field] -= 1
        counters['missing'] += 1
    state['acceptance_evidence'][key]['receipts'] -= 1
    state['acceptance_evidence'][key]['passed'] -= 1
    state['completed_receipts'] -= 1


class Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = QualificationContract()
        selections = [('named_candidates', 'F12', 0),
                      *[('named_candidates', 'F13-' + variant, 0) for variant in
                        ('duplicated_handle', 'foreign_handle', 'invalid_tree', 'invalid_root')],
                      ('auxiliary_m04_association', 'M04-association', 0),
                      *[('named_materials', name, 0) for name in
                        ('M01', 'M02', 'M03', 'M04', 'M05-P', 'M05-O', 'M05-I')],
                      ('matrix_star_s_free', 'star/S_free', 65),
                      ('matrix_f09_s_inc', 'F09-geometry/S_inc', 65),
                      ('material_outcome_orders', 'M04', 1),
                      *[('derived_observable_equivalence_laws', 'Q', r) for r in (0, 28, 812)]]
        cls.cases = [cls.contract.descriptor(next(s for s in cls.contract.suites if s['id'] == suite),
                     name, rank, i) for i, (suite, name, rank) in enumerate(selections)]
        cls.contract.qualification_cases = cls.cases
        cls.root = run.fresh(Path(tempfile.mkdtemp(prefix='exp007-b2-tests-')) / 'verified')
        cls.meta = run.prepare(cls.root, cls.contract, MODE, 60, 'cc')
        journal = run.Journal(cls.root)
        for _, group in itertools.groupby(cls.cases, key=lambda c: c['suite_id']):
            run.execute_batch(cls.root, cls.meta, cls.contract, journal, list(group), 60)
        cls.events = list(run.Journal(cls.root).records())
        cls.case_events = [e for e in cls.events if e['kind'] == 'case']
        cls.rows = {}
        for event in cls.case_events:
            cls.rows[(event['case']['suite_id'], event['case']['selector'])] = (
                event['case'], run.decode(journal.read(event['inputs'])),
                run.read_segment(cls.root, event['tested']['stdout']),
                run.read_segment(cls.root, event['reference']['stdout']))
        cls.original_files = {p: p.read_bytes() for p in cls.root.rglob('*') if p.is_file()}
        run.write_new(cls.root.parent / 'qualification.json', run.canonical(dict(
            mode=MODE, campaign_credit=0, CAMPAIGN_EXECUTED='NO', EXP007_STATUS='INCONCLUSIVE',
            bounded_receipts=len(cls.cases), test_source_sha256=run.file_hash(Path(__file__)))))

    def tearDown(self):
        # Mutations apply only to this synthetic external qualification archive.
        # Restore it for the next independent test; production never repairs it.
        for path, raw in self.original_files.items():
            if path.read_bytes() != raw:
                path.write_bytes(raw)

    def evaluate(self, state=None):
        return run.evaluate_acceptance(self.contract, 'campaign',
                                       synthetic_completed(self.contract) if state is None else state)

    def install_events(self, events):
        # Existing content-addressed chunk filenames can be reused by Journal;
        # only index.jsonl is replaced in this external corruption fixture.
        (self.root / 'index.jsonl').write_bytes(b'')
        journal = run.Journal(self.root)
        for event in events:
            journal.append(event)

    def test_completed_synthetic_evidence_enumerates_every_frozen_requirement(self):
        result = self.evaluate()
        self.assertEqual([r['requirement'] for r in result['requirements']],
                         self.contract.plan['full_acceptance']['required'])
        self.assertEqual([r['status'] for r in result['requirements']], ['PASS']*10 + ['UNVERIFIED'])
        self.assertEqual(result['scientific_acceptance'], 'BLOCKED')
        self.assertFalse(result['complete_scientific_acceptance'])
        self.assertEqual(result['unresolved_requirements'], ['FA11'])
        self.assertIn('EXP007_RESULTS.md', result['requirements'][10]['evidence'])

    def test_correct_three_category_accounting_and_determinism(self):
        a, b = self.evaluate(), self.evaluate()
        self.assertEqual(run.canonical(a), run.canonical(b))
        self.assertEqual(a['execution'], 'EXHAUSTIVE_EXECUTION')
        self.assertEqual({k: v['passed'] for k, v in a['counts'].items()},
                         dict(PRIMARY=529423, AUXILIARY=1, DERIVED=22764))
        self.assertEqual(a['matrix_candidate_obligations'], dict(tested=3145728, reference=3145728))

    def test_one_missing_primary(self):
        state = synthetic_completed(self.contract)
        remove_case(state, 'named_candidates')
        result = self.evaluate(state)
        self.assertEqual(result['primary_completion'], 'UNSATISFIED')
        self.assertEqual(result['counts']['PRIMARY']['missing'], 1)
        self.assertEqual(result['execution'], 'PARTIAL_EXECUTION')

    def test_missing_auxiliary(self):
        state = synthetic_completed(self.contract)
        remove_case(state, 'auxiliary_m04_association')
        result = self.evaluate(state)
        self.assertEqual(result['auxiliary_completion'], 'UNSATISFIED')
        self.assertEqual(result['primary_completion'], 'PASS')
        self.assertEqual(result['requirements'][1]['status'], 'UNSATISFIED')

    def test_one_missing_derived_law(self):
        state = synthetic_completed(self.contract)
        remove_case(state, 'derived_observable_equivalence_laws')
        result = self.evaluate(state)
        self.assertEqual(result['derived_laws'], 'UNSATISFIED')
        self.assertEqual(result['primary_completion'], 'PASS')
        self.assertEqual(result['counts']['DERIVED']['missing'], 1)

    def test_complete_execution_with_blocked_comparison_is_unverified(self):
        state = synthetic_completed(self.contract)
        key = 'material_outcome_orders'
        remove_case(state, key)
        evidence = state['acceptance_evidence'][key]
        evidence['receipts'] += 1
        evidence['blocked'] += 1
        row = state['ledgers'][key]
        for counters in (row, row['tested'], row['reference']):
            for field in ('generated', 'attempted', 'received'):
                counters[field] += 1
        row['blocked'] += 1
        state['completed_receipts'] += 1
        result = self.evaluate(state)
        self.assertEqual(result['execution'], 'EXHAUSTIVE_EXECUTION')
        self.assertEqual(result['requirements'][3]['status'], 'UNVERIFIED')
        self.assertFalse(result['complete_scientific_acceptance'])

    def test_incomplete_source_identity_evidence(self):
        meta = copy.deepcopy(self.meta)
        meta['source_hashes'].pop('exp007_c_adapter.c')
        with self.assertRaisesRegex(run.IntegrityError, 'incomplete source archive identities'):
            run.audit(self.root, meta, self.contract)

    def test_missing_matrix_predicate_evidence(self):
        state = synthetic_completed(self.contract)
        state['acceptance_evidence']['matrix_star_s_free']['matrix_predicates']['reference'] -= 1
        self.assertEqual(self.evaluate(state)['requirements'][2]['status'], 'UNVERIFIED')

    def test_ledger_disagreement_cannot_pass(self):
        state = synthetic_completed(self.contract)
        state['ledgers']['named_materials']['passed'] -= 1
        with self.assertRaisesRegex(run.IntegrityError, 'aggregate ledger disagreement'):
            self.evaluate(state)

    def test_verified_bounded_archive_and_expected_limitations(self):
        _, state = run.audit(self.root, self.meta, self.contract)
        result = state['acceptance']
        self.assertEqual(state['completed_receipts'], len(self.cases))
        self.assertEqual(result['integrity_audit'], 'PASS')
        self.assertEqual(result['execution'], 'NON_CAMPAIGN_EXECUTION')
        self.assertEqual(sum(r['passed'] for r in state['acceptance_evidence'].values()), len(self.cases))
        self.assertTrue(all(r['passed'] == 0 for r in result['counts'].values()))
        self.assertEqual(result['EXP004'], dict(historical_completeness='INCONCLUSIVE',
                                               material_equivalence='CALLER_ASSUMPTION'))
        f12 = self.rows[('named_candidates', 'F12')][2]['result']['candidate']
        self.assertIs(f12['conditional'], True)
        self.assertIn('ASSESSMENT_UNRESOLVED', f12['diagnostics'])
        for key, (_, _, tested, _) in self.rows.items():
            if key[1].startswith('F13-'):
                candidate = tested['result']['candidate']
                self.assertEqual(candidate['status'], 'UNSUPPORTED')
                self.assertIsNone(candidate['candidate_sets'])
                self.assertEqual(candidate['diagnostics'], ['INVALID_INPUT'])
        for name in ('M05-P', 'M05-O', 'M05-I'):
            row = self.rows[('named_materials', name)][2]['result']['material']
            self.assertEqual(row['scientific_claim'], 'INCONCLUSIVE')
        for event in self.case_events:
            self.assertEqual(run.decode(run.Journal(self.root).read(event['comparison']))['status'], 'PASS')

    def test_partial_archive_clean_integrity_has_no_acceptance(self):
        # Keep a complete first batch only, including its F12/F13 diagnostics.
        stop = next(i for i, e in enumerate(self.events) if e['kind'] == 'attempt' and e['start'] == 5)
        (self.root / 'index.jsonl').write_bytes(b''.join(
            self.original_files[self.root / 'index.jsonl'].splitlines(keepends=True)[:stop]))
        _, state = run.audit(self.root, self.meta, self.contract)
        self.assertEqual(state['completed_receipts'], 5)
        self.assertEqual(state['acceptance']['integrity_audit'], 'PASS')
        self.assertFalse(state['acceptance']['complete_scientific_acceptance'])
        self.assertEqual(state['acceptance']['primary_completion'], 'UNSATISFIED')

    def test_offline_audit_does_not_execute_adapters(self):
        with patch.object(run, 'run_process', side_effect=AssertionError('offline audit executed a process')):
            _, state = run.audit(self.root, self.meta, self.contract)
        self.assertEqual(state['acceptance']['integrity_audit'], 'PASS')

    def test_missing_internal_receipt(self):
        events = copy.deepcopy(self.events)
        position = next(i for i, e in enumerate(events) if e['kind'] == 'case')
        events.pop(position)
        self.install_events(events)
        with self.assertRaisesRegex(run.IntegrityError, 'duplicate/missing/out-of-order'):
            run.audit(self.root, self.meta, self.contract)

    def test_forged_untrusted_summary_file_is_ignored(self):
        _, before = run.audit(self.root, self.meta, self.contract)
        path = self.root / 'summary-forged.json'
        run.write_new(path, run.canonical(dict(complete_scientific_acceptance=True,
            scientific_acceptance='PASS', EXP007_STATUS='PASS', acceptance_evidence='invented')))
        _, after = run.audit(self.root, self.meta, self.contract)
        self.assertEqual(before['acceptance'], after['acceptance'])

    def test_contradictory_comparison_receipt(self):
        events = copy.deepcopy(self.events)
        event = next(e for e in events if e['kind'] == 'case')
        comparison = run.decode(run.Journal(self.root).read(event['comparison']))
        comparison['status'] = 'FAIL'
        event['comparison'] = run.Journal(self.root).object(comparison)
        self.install_events(events)
        with self.assertRaisesRegex(run.IntegrityError, 'stored comparison is not reproducible'):
            run.audit(self.root, self.meta, self.contract)

    def test_duplicate_and_out_of_order_receipts(self):
        for mutation in ('duplicate', 'out_of_order'):
            events = copy.deepcopy(self.events)
            positions = [i for i, e in enumerate(events) if e['kind'] == 'case']
            if mutation == 'duplicate':
                events.insert(positions[1], copy.deepcopy(events[positions[0]]))
            else:
                events[positions[0]], events[positions[1]] = events[positions[1]], events[positions[0]]
            self.install_events(events)
            with self.assertRaisesRegex(run.IntegrityError, 'duplicate/missing/out-of-order'):
                run.audit(self.root, self.meta, self.contract)

    def test_corrupt_raw_output(self):
        path = self.root / self.case_events[0]['tested']['stdout']['file']['path']
        raw = path.read_bytes()
        path.write_bytes(raw.replace(b'EVALUATED', b'EVALUATEX', 1))
        with self.assertRaisesRegex(run.IntegrityError, 'SHA256 mismatch'):
            run.audit(self.root, self.meta, self.contract)

    def test_mismatched_side_receipt(self):
        events = copy.deepcopy(self.events)
        next(e for e in events if e['kind'] == 'case')['tested']['case_id'] = 'wrong-case'
        self.install_events(events)
        with self.assertRaisesRegex(run.IntegrityError, 'side receipt identity drift'):
            run.audit(self.root, self.meta, self.contract)

    def test_forged_saved_summary(self):
        _, state = run.audit(self.root, self.meta, self.contract)
        event = run.event_base(self.root, self.meta, 'summary')
        event.update(completed_receipts=state['completed_receipts'], ledgers=state['ledgers'],
                     EXP007_STATUS='PASS', complete_scientific_acceptance=True)
        self.install_events([*self.events, event])
        with self.assertRaisesRegex(run.IntegrityError, 'unsupported scientific claim'):
            run.audit(self.root, self.meta, self.contract)

    def comparison_mutation(self, key, mutate):
        case, inputs, tested, reference = copy.deepcopy(self.rows[key])
        mutate(tested)
        comparison = run.compare_case(self.contract, case, inputs, tested, reference)
        self.assertNotEqual(comparison['status'], 'PASS')
        # Replace exactly one synthetic PASS by this real reconstructed verdict.
        state = synthetic_completed(self.contract)
        remove_case(state, case['suite_id'])
        for counters in (state['ledgers'][case['suite_id']],
                         state['ledgers'][case['suite_id']]['tested'],
                         state['ledgers'][case['suite_id']]['reference']):
            for field in ('generated', 'attempted', 'received'):
                counters[field] += 1
        run.observe_acceptance(state['acceptance_evidence'], case, comparison, tested, reference)
        run.credit(state['ledgers'][case['suite_id']], comparison['status'])
        state['completed_receipts'] += 1
        result = self.evaluate(state)
        self.assertFalse(result['complete_scientific_acceptance'])
        self.assertEqual(result['scientific_counterexamples_certified'], 0)
        return comparison, result

    def test_incomplete_material_evidence(self):
        def mutate(row):
            row['result']['material']['associations'].pop()
        _, result = self.comparison_mutation(('named_materials', 'M01'), mutate)
        self.assertEqual(result['requirements'][5]['status'], 'UNSATISFIED')
        self.assertEqual(result['requirements'][6]['status'], 'UNSATISFIED')

    def test_invalid_witness(self):
        def mutate(row):
            row['result']['material']['associations'][0]['decisions'][0]['witnesses'][0]['material']['l0'] = '0'
        comparison, _ = self.comparison_mutation(('named_materials', 'M01'), mutate)
        self.assertTrue(any(d.get('kind') == 'INVALID_WITNESS' for d in comparison['discrepancies']))

    def test_invalid_rejection_certificate(self):
        def mutate(row):
            row['result']['material']['associations'][0]['decisions'][0]['rejection_certificate'].pop()
        comparison, _ = self.comparison_mutation(('named_materials', 'M03'), mutate)
        self.assertTrue(any(d.get('kind') == 'INCOMPLETE_CERTIFICATE' for d in comparison['discrepancies']))

    def test_incorrect_consumption_trace(self):
        def mutate(row):
            row['consumption']['consumed_outcomes'].reverse()
        _, result = self.comparison_mutation(('material_outcome_orders', 'M04'), mutate)
        self.assertEqual(result['requirements'][3]['status'], 'UNSATISFIED')

    def test_reproducible_mismatch_remains_uncertified(self):
        def mutate(row):
            row['result']['candidate']['conditional'] = False
        a, result = self.comparison_mutation(('named_candidates', 'F12'), mutate)
        b, _ = self.comparison_mutation(('named_candidates', 'F12'), mutate)
        self.assertEqual(a, b)
        self.assertEqual(result['execution'], 'EXHAUSTIVE_EXECUTION')
        self.assertEqual(result['scientific_finding'], 'NEGATIVE_RESULT_PENDING_TRIAGE')
        self.assertEqual(result['pending_triage_cases'], 1)
        self.assertIn('B3:', result['requirements'][9]['dependency'])
        self.assertEqual(result['B3_STATUS'], 'IMPLEMENTED')

    def test_incorrect_frozen_negative_diagnostic(self):
        def mutate(row):
            row['result']['material']['scientific_claim'] = 'PASS'
        _, result = self.comparison_mutation(('named_materials', 'M05-I'), mutate)
        self.assertEqual(result['requirements'][8]['status'], 'UNSATISFIED')

    def test_incorrect_derived_law_verdict(self):
        def mutate(row):
            row['law']['law_holds'] = False
        _, result = self.comparison_mutation(('derived_observable_equivalence_laws', 'Q'), mutate)
        self.assertEqual(result['derived_laws'], 'UNSATISFIED')
        self.assertEqual(result['primary_completion'], 'PASS')

    def test_operational_incident_blocks_even_with_complete_counts(self):
        state = synthetic_completed(self.contract)
        state['operational_incidents'] = 1
        self.assertEqual(self.evaluate(state)['requirements'][9]['status'], 'UNSATISFIED')

    def test_public_validate_and_audit_exit_contract(self):
        output = subprocess.run([sys.executable, '-B', str(run.BASE / 'exp007_run.py'), 'validate'],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(run.decode(output.stdout)['CLI_GATE'], 'PASS_READ_ONLY')
        # Empty genuine archive is valid integrity with no campaign execution.
        empty = run.fresh(self.root.parent / 'empty')
        run.prepare(empty, self.contract, MODE, 60, 'cc')
        out = io.StringIO()
        with redirect_stdout(out):
            status = run.main(['audit', '--out', str(empty)])
        self.assertEqual(status, 0)
        report = run.decode(out.getvalue().encode())
        self.assertEqual(report['integrity_audit'], 'PASS')
        self.assertFalse(report['complete_scientific_acceptance'])


if __name__ == '__main__':
    unittest.main()
