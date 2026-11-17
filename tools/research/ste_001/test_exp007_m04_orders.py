#!/usr/bin/env python3
"""Bounded M04 qualification; external products, zero campaign credit.

Run: python3 -B tools/research/ste_001/test_exp007_m04_orders.py -v
Set EXP007_M04_TEST_OUT to a fresh external directory to retain all evidence.
No campaign entry point is called. Frozen case IDs remain unchanged.
"""

import copy
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp007_run as run
import exp007_reference_adapter as adapter


IDENTITY = [['l0', 'r0'], ['l1', 'r1'], ['l2', 'r2']]


def expected_decision(value):
    """Literal contract, independent of both solver outputs."""
    other = 'rho' if value == 'lambda' else 'lambda'
    update = dict(id='left_lambda' if value == 'lambda' else 'right_rho',
                  side='left' if value == 'lambda' else 'right',
                  target='l0' if value == 'lambda' else 'r0', value=value, mandatory=True)
    waived = dict(id='right_rho' if value == 'lambda' else 'left_lambda',
                  side='right' if value == 'lambda' else 'left',
                  target='r0' if value == 'lambda' else 'l0', value=other, mandatory=True)
    material = dict(l0=value, l1='0', l2='0')
    obligations = [dict(id='preserve:' + h, kind='PRESERVE', target=h, value='0')
                   for h in ('l1', 'l2')]
    obligations.append(dict(id='update:' + update['id'], kind='UPDATE',
                            intention=update['id'], side=update['side'], selector=update['target'],
                            target='l0', value=value))
    return dict(id='d_' + value,
                authorization=f'M04 explicitly authorizes waiving {other} while retaining {value}.',
                retained_intentions=[update], waived_intentions=[waived], obligations=obligations,
                assignments_examined=27, W_phi_d=[material],
                witnesses=[dict(material=material, satisfied=sorted(o['id'] for o in obligations))],
                rejection_certificate=None, outcomes=[dict(tag='ACCEPT', material=material)])


class M04Orders(unittest.TestCase):
    negative_checks = 0

    @classmethod
    def setUpClass(cls):
        cls.contract = run.Contract()
        destination = os.environ.get('EXP007_M04_TEST_OUT')
        cls.area = Path(destination) if destination else Path(tempfile.mkdtemp(prefix='exp007-m04-tests-')) / 'run'
        cls.area = run.fresh(cls.area)
        cls.meta = run.prepare(cls.area, cls.contract, 'M04_QUALIFICATION_ONLY', 60, 'cc')
        suite = next(s for s in cls.contract.suites if s['id'] == 'material_outcome_orders')
        ordinal = sum(s['required_cases'] for s in cls.contract.suites[:cls.contract.suites.index(suite)])
        cls.cases = [cls.contract.descriptor(suite, 'M04', rank, ordinal + rank) for rank in (0, 1)]
        cls.inputs = [cls.contract.materialize(c) for c in cls.cases]
        # Persistent C and Python streams exercise rank 0, rank 1, rank 0.
        sequence = [0, 1, 0]
        cls.frames = [run.make_frames(cls.cases[r], cls.inputs[r], f'm04-{i}')
                      for i, r in enumerate(sequence)]
        commands = run.commands_for(cls.area, cls.meta, cls.cases[0])
        cls.processes, cls.rows, cls.receipts = {}, {}, {}
        for side_index, side in enumerate(('tested', 'reference')):
            process = run.run_process(cls.area, commands[side_index],
                                      b''.join(f[side_index] for f in cls.frames), 60, side)
            if process['exit_status'] != 0 or process['timeout']:
                raise AssertionError(f'{side} process failed; evidence: {cls.area}')
            output = list(run.output_lines(cls.area, process['stdout']))
            if len(output) != 3:
                raise AssertionError(f'{side}: expected three complete responses')
            cls.processes[side] = process
            cls.rows[side], cls.receipts[side] = [], []
            for i, (raw, segment) in enumerate(output):
                row = run.decode(raw)
                run.response_identity(cls.contract, cls.cases[sequence[i]], row, side, i + 1, f'm04-{i}')
                cls.rows[side].append(row)
                cls.receipts[side].append(dict(stdout=segment, stderr=process['stderr'],
                    executable_sha256=run.execution_hash(cls.meta, cls.cases[sequence[i]], side),
                    exit_status=0))
        cls.comparisons = [run.compare_case(cls.contract, cls.cases[r], cls.inputs[r],
                                           cls.rows['tested'][i], cls.rows['reference'][i])
                           for i, r in enumerate(sequence)]
        cls.replays = []
        # Exercise the real bounded batch pipeline, preserving frozen IDs and
        # ordinals. This isolated journal is never audited/credited as a campaign
        # prefix; its metadata and qualification receipt expressly grant zero credit.
        journal = run.Journal(cls.area)
        run.execute_batch(cls.area, cls.meta, cls.contract, journal, cls.cases, 60)
        cls.integrated_cases = [e for e in run.Journal(cls.area).records() if e['kind'] == 'case']
        run.write_new(cls.area / 'qualification.json', run.canonical(dict(
            mode='M04_QUALIFICATION_ONLY', campaign_credit=0, CAMPAIGN_EXECUTED='NO',
            EXP007_STATUS='INCONCLUSIVE', cases=cls.cases, sequence=sequence,
            processes=cls.processes, comparisons=cls.comparisons,
            integrated_cases=cls.integrated_cases,
            test_source_sha256=run.file_hash(Path(__file__)))))
        run.write_new(cls.area / 'test_exp007_m04_orders.py', Path(__file__).read_bytes())
        for rank in (0, 1):
            replay = run.replay_record(cls.area, cls.meta, cls.contract, cls.cases[rank],
                cls.inputs[rank], cls.comparisons[rank], cls.receipts['tested'][rank],
                cls.receipts['reference'][rank], 'qualification-only')
            cls.replays.append(replay)
            run.write_new(cls.area / f'rank-{rank}-replay.json', run.canonical(replay))

    def compare(self, side, mutate, rank=0):
        rows = {s: copy.deepcopy(self.rows[s][rank]) for s in ('tested', 'reference')}
        mutate(rows[side])
        comparison = run.compare_case(self.contract, self.cases[rank], self.inputs[rank],
                                       rows['tested'], rows['reference'])
        self.record_negative(dict(side=side, case=self.cases[rank],
                                  mutated_outputs=rows, comparison=comparison))
        return comparison

    def record_negative(self, evidence):
        type(self).negative_checks += 1
        run.write_new(self.area / f'negative-{self.negative_checks:03d}.json', run.canonical(dict(
            test=self.id(), campaign_credit=0, classification='REGRESSION_MUTATION_ONLY', **evidence)))

    def test_both_exact_orders_and_complete_payloads(self):
        self.assertEqual(len(self.integrated_cases), 2)
        journal = run.Journal(self.area)
        for event, case in zip(self.integrated_cases, self.cases):
            self.assertEqual(event['case'], case)
            self.assertEqual(run.decode(journal.read(event['comparison']))['status'], 'PASS')
        for rank, values in enumerate((('lambda', 'rho'), ('rho', 'lambda'))):
            with self.subTest(rank=rank):
                self.assertEqual(self.comparisons[rank]['status'], 'PASS')
                self.assertEqual(self.comparisons[rank]['blocked'], [])
                expected = [dict(position=i, association=IDENTITY, decision=expected_decision(v))
                            for i, v in enumerate(values)]
                for side in ('tested', 'reference'):
                    trace = self.rows[side][rank]['consumption']
                    self.assertIs(trace['partition_called'], True)
                    self.assertTrue(trace['outcome_hook'])
                    actual = copy.deepcopy(trace['consumed_outcomes'])
                    wanted = copy.deepcopy(expected)
                    if side == 'tested':
                        for item in wanted:
                            item['decision'].pop('assignments_examined')
                    # Only the payload's internal sets are extensional; never sort the stream.
                    for a, e in zip(actual, wanted):
                        self.assertEqual(a['position'], e['position'])
                        self.assertEqual(a['association'], e['association'])
                        self.assertEqual(self.contract.ref.normalize_comparison(a['decision']),
                                         self.contract.ref.normalize_comparison(e['decision']))
                    self.assertEqual(len(actual), 2)
                    for item, wanted_item in zip(actual, wanted):
                        self.assertEqual(set(item['decision']), set(wanted_item['decision']))
                        if side == 'reference':
                            self.assertEqual(item['decision']['assignments_examined'], 27)
                self.assertIs(self.rows['reference'][rank]['consumption']['outcome_complete'], True)

    def test_candidate_universe_materials_and_exact_memberships(self):
        universe = [self.contract.ref.expected_relation(''.join(map(str, p)), self.inputs[0]['original'])
                    for p in itertools.permutations(range(3))]
        expected_classes = [dict(observable=dict(tag='ACCEPT', material=dict(l0=v, l1='0', l2='0')),
                                 members=[dict(association=IDENTITY, decision='d_' + v)])
                            for v in ('lambda', 'rho')]
        for side in ('tested', 'reference'):
            for rank in (0, 1):
                row = self.rows[side][rank]['result']
                self.assertEqual(row['candidate']['candidate_sets'],
                                 dict(U_H=universe, C_E=[IDENTITY], A_E=[IDENTITY]))
                material = row['material']
                self.assertEqual(self.contract.ref.normalize_comparison(material['observable_classes']),
                                 self.contract.ref.normalize_comparison(expected_classes))
                decisions = material['associations'][0]['decisions']
                self.assertEqual(self.contract.ref.normalize_comparison(decisions),
                    self.contract.ref.normalize_comparison([expected_decision(v) for v in ('lambda', 'rho')]))
                self.assertEqual(material['scientific_claim'], 'INCONCLUSIVE')
                self.assertEqual(material['independent_comparison'], 'PENDING')

    def test_persistent_rank_zero_one_zero(self):
        self.assertEqual([c['status'] for c in self.comparisons], ['PASS'] * 3)
        for side in ('tested', 'reference'):
            first, last = self.rows[side][0], self.rows[side][2]
            for field in ('result', 'consumption', 'work'):
                self.assertEqual(first[field], last[field])

    def test_replay_determinism_and_full_trace(self):
        for rank in (0, 1):
            replay = self.replays[rank]
            for side in ('tested', 'reference'):
                trace = self.rows[side][rank]['consumption']
                self.assertEqual(replay['consumed_outcome_order'][side], trace['consumed_outcomes'])
                self.assertEqual(replay['consumption_details'][side], trace)
                run.verify_file(self.area, self.processes[side]['stdout'])
                command = run.commands_for(self.area, self.meta, self.cases[rank])[0 if side == 'tested' else 1]
                frame = self.frames[rank][0 if side == 'tested' else 1]
                proc = run.run_process(self.area, command, frame, 60, f'replay-{rank}-{side}')
                self.assertEqual(proc['exit_status'], 0)
                repeated = run.decode(next(run.output_lines(self.area, proc['stdout']))[0])
                for field in ('result', 'consumption', 'work'):
                    self.assertEqual(repeated[field], self.rows[side][rank][field])

    def test_measured_work_without_fictitious_evaluations(self):
        for row in self.rows['reference']:
            work = row['work']
            self.assertEqual(work['reference_relation_classifications'], 512)
            self.assertEqual(work['candidate_evaluations'], 6)
            self.assertEqual(work['decision_assignment_checks'], 54)
            self.assertEqual(work['union_assignment_checks'], 27)
            self.assertEqual(work['baseline_decision_assignment_checks'], 54)
            self.assertEqual(work['baseline_union_assignment_checks'], 27)
            self.assertEqual(work['outcome_consumer_calls'], 1)
            self.assertEqual(work['outcomes_consumed'], 2)
            self.assertEqual(work['outcome_observable_calls'], 2)
        for row in self.rows['tested']:
            self.assertEqual(row['work']['material_evaluations'], 2)
            self.assertEqual(row['work']['direct_constructions'], 2)
        self.assertEqual(self.comparisons[0]['driver_verifier_work'],
                         dict(witnesses_checked=2, certificate_rows_checked=0))

    def test_observation_occurs_only_after_real_consumption(self):
        ref = self.contract.ref
        observed = []
        real_observable = ref.observable
        real_consumer = adapter.consume_ordered_outcomes
        active = {}

        def observe(outcome, query):
            trace = active['trace']
            self.assertIs(trace['partition_called'], True)
            self.assertIs(trace['outcome_complete'], False)
            self.assertEqual(trace['consumed_outcomes'][-1]['decision']['outcomes'], [outcome])
            observed.append(outcome['material']['l0'])
            return real_observable(outcome, query)

        def consume(reference, received, query, *, consumption, work):
            active['trace'] = consumption
            return real_consumer(reference, received, query, consumption=consumption, work=work)

        # Baseline evaluation is separate; observe the adapter path directly.
        fixture = copy.deepcopy(self.inputs[1]['transformed'])
        material = fixture.pop('material')
        candidate = ref.evaluate_candidate(fixture)
        with patch.object(ref, 'observable', side_effect=observe), \
                patch.object(adapter, 'consume_ordered_outcomes', side_effect=consume):
            trace, work = {}, {}
            adapter.evaluate_m04_outcome_order(ref, material, fixture, candidate, [1, 0],
                                               consumption=trace, work=work)
        self.assertEqual(observed, ['rho', 'lambda'])

    def test_wrong_consumption_order_with_correct_final_sets(self):
        for side in ('tested', 'reference'):
            with self.subTest(side=side):
                def mutate(row):
                    row['consumption']['consumed_outcomes'].reverse()
                    for i, item in enumerate(row['consumption']['consumed_outcomes']):
                        item['position'] = i
                self.assertEqual(self.compare(side, mutate)['status'], 'FAIL')

    def test_output_only_reordering_cannot_substitute_for_consumption(self):
        for side in ('tested', 'reference'):
            with self.subTest(side=side):
                def mutate(row):
                    row['consumption'] = copy.deepcopy(self.rows[side][0]['consumption'])
                    row['result']['material']['associations'][0]['outcomes'].reverse()
                self.assertEqual(self.compare(side, mutate, rank=1)['status'], 'FAIL')

    def test_actual_consumer_ignoring_requested_order_is_detected(self):
        module = self.contract.outcome_adapter
        real = module.consume_ordered_outcomes
        def ignore_order(reference, received, query, *, consumption, work):
            offered = sorted(received, key=lambda item: item['decision']['id'])
            return real(reference, offered, query, consumption=consumption, work=work)
        with patch.object(module, 'consume_ordered_outcomes', side_effect=ignore_order):
            reference = run.reference_evaluate(self.contract, self.cases[1], self.inputs[1])
        # All material outcomes and classes are still exactly correct.
        self.assertEqual(reference['result'], self.rows['reference'][1]['result'])
        comparison = run.compare_case(self.contract, self.cases[1], self.inputs[1],
                                       self.rows['tested'][1], reference)
        self.record_negative(dict(mutated_reference=reference, comparison=comparison))
        self.assertEqual(comparison['status'], 'FAIL')

    def test_omitted_duplicate_extra_and_wrong_position(self):
        mutations = [lambda t: t['consumed_outcomes'].pop(),
                     lambda t: t['consumed_outcomes'].__setitem__(1, copy.deepcopy(t['consumed_outcomes'][0])),
                     lambda t: t['consumed_outcomes'].append(copy.deepcopy(t['consumed_outcomes'][0])),
                     lambda t: t['consumed_outcomes'][0].__setitem__('position', 1),
                     lambda t: t['consumed_outcomes'][0].__setitem__('position', False)]
        for side, index in itertools.product(('tested', 'reference'), range(len(mutations))):
            with self.subTest(side=side, mutation=index):
                result = self.compare(side, lambda r: mutations[index](r['consumption']))
                self.assertEqual(result['status'], 'FAIL')

    def test_missing_hooks_and_incomplete_consumption_are_never_pass(self):
        for side in ('tested', 'reference'):
            fields = ['outcome_hook', 'partition_called', 'consumed_outcomes']
            if side == 'reference':
                fields.append('outcome_complete')
            for field in fields:
                with self.subTest(side=side, field=field):
                    result = self.compare(side, lambda r: r['consumption'].pop(field))
                    self.assertNotEqual(result['status'], 'PASS')
                    self.assertTrue(result['blocked'] or result['discrepancies'])
            for field, wrong_value in [('partition_called', False), ('outcome_hook', 'uninvoked-hook')]:
                with self.subTest(side=side, field=field, value=wrong_value):
                    result = self.compare(side, lambda r: r['consumption'].__setitem__(field, wrong_value))
                    self.assertEqual(result['status'], 'BLOCKED')

    def test_corrupt_consumed_payloads(self):
        def association(item):
            item['association'][0][1] = 'r1'
        def decision(item):
            item['decision']['authorization'] = 'unauthorized'
        def witness(item):
            item['decision']['witnesses'][0]['material']['l0'] = 'rho'
        def incomplete(item):
            item['decision'].pop('waived_intentions')
        for side, mutate in itertools.product(('tested', 'reference'), (association, decision, witness, incomplete)):
            with self.subTest(side=side, mutation=mutate.__name__):
                self.assertEqual(self.compare(side, lambda r: mutate(r['consumption']['consumed_outcomes'][0]))['status'], 'FAIL')

    def test_corrupt_material_values_and_class_memberships(self):
        def value(row):
            row['result']['material']['associations'][0]['decisions'][0]['outcomes'][0]['material']['l0'] = '0'
        def member(row):
            row['result']['material']['observable_classes'][0]['members'][0]['decision'] = 'd_rho'
        def observable(row):
            row['result']['material']['observable_classes'][0]['observable']['material']['l0'] = '0'
        for side, mutate in itertools.product(('tested', 'reference'), (value, member, observable)):
            with self.subTest(side=side, mutation=mutate.__name__):
                self.assertEqual(self.compare(side, mutate)['status'], 'FAIL')

    def test_reject_without_valid_certificate(self):
        for side in ('tested', 'reference'):
            def mutate(row):
                decision = row['result']['material']['associations'][0]['decisions'][0]
                decision['outcomes'] = [dict(tag='REJECT')]
                decision['witnesses'] = []
                decision['rejection_certificate'] = None
            with self.subTest(side=side):
                self.assertEqual(self.compare(side, mutate)['status'], 'FAIL')

    def test_premature_consumer_return_is_detected(self):
        module = self.contract.outcome_adapter
        real = module.consume_ordered_outcomes
        def short(reference, received, query, *, consumption, work):
            return real(reference, itertools.islice(received, 1), query,
                        consumption=consumption, work=work)
        with patch.object(module, 'consume_ordered_outcomes', side_effect=short):
            reference = run.reference_evaluate(self.contract, self.cases[1], self.inputs[1])
        result = run.compare_case(self.contract, self.cases[1], self.inputs[1], self.rows['tested'][1], reference)
        self.record_negative(dict(mutated_reference=reference, comparison=result))
        self.assertEqual(result['status'], 'FAIL')

    def test_interrupted_consumer_keeps_only_actual_prefix(self):
        def interrupted():
            yield dict(association=IDENTITY, decision=expected_decision('rho'))
            raise RuntimeError('premature termination')
        trace, work = {}, {}
        with self.assertRaisesRegex(RuntimeError, 'premature termination'):
            adapter.consume_ordered_outcomes(self.contract.ref, interrupted(), 'Q', consumption=trace, work=work)
        self.record_negative(dict(interrupted_trace=trace, work=work, exception='premature termination'))
        self.assertIs(trace['outcome_complete'], False)
        self.assertEqual(len(trace['consumed_outcomes']), 1)
        self.assertEqual(work['outcomes_consumed'], 1)
        self.assertEqual(work['outcome_observable_calls'], 1)

    def test_m01_m02_m03_surrounding_material_behavior(self):
        suite = next(s for s in self.contract.suites if s['id'] == 'association_orders')
        for name in ('M01', 'M02', 'M03'):
            for rank in (0, 719):
                with self.subTest(fixture=name, rank=rank):
                    case = self.contract.descriptor(suite, name, rank, 0)
                    inputs = self.contract.materialize(case)
                    frame = run.make_frames(case, inputs, 'neighbor')[0]
                    command = run.commands_for(self.area, self.meta, case)[0]
                    proc = run.run_process(self.area, command, frame, 60, f'{name}-{rank}')
                    self.assertEqual(proc['exit_status'], 0)
                    tested = run.decode(next(run.output_lines(self.area, proc['stdout']))[0])
                    reference = run.reference_evaluate(self.contract, case, inputs)
                    self.assertEqual(run.compare_case(self.contract, case, inputs, tested, reference)['status'], 'PASS')
                    self.assertIsNone(reference['consumption']['outcome_hook'])
                    self.assertEqual(reference['consumption']['consumed_outcomes'], [])

    def test_matrix_interface_and_source_identities_are_preserved(self):
        matrix = adapter.MatrixAdapter()
        first = matrix.evaluate('star/S_free', '65')
        second = matrix.evaluate('star/S_free', '65')
        self.assertEqual(first['candidate']['candidate_sets'], second['candidate']['candidate_sets'])
        self.assertEqual(first['work']['reference_relation_classifications'], 512)
        self.assertEqual(second['work']['reference_relation_classifications'], 0)
        self.assertEqual(first['work']['material_evaluations'], 0)
        identities = run.validate_sources(self.contract)
        self.assertTrue(identities['historical_and_current_are_distinct'])
        self.assertNotEqual(identities['historical_frozen_test']['sha256'],
                            identities['current_baseline_test']['sha256'])
        self.assertEqual(sum(s['required_cases'] or 0 for s in self.contract.suites), 529424)
        self.assertFalse(any(b['obligation'].startswith('material_outcome_orders') for b in run.BLOCKED))
        self.assertEqual(len(run.BLOCKED), 2)


if __name__ == '__main__':
    unittest.main()
