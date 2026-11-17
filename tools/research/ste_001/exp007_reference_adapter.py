#!/usr/bin/env python3
r"""STE EXP-007 Phase C: independent, bounded Python MATRIX adapter.

Run with Python 3 (standard library only), from any working directory:
  python3 -B tools/research/ste_001/exp007_reference_adapter.py --help
  printf 'EXP007/1 smoke EVAL star/S_free 65\n' | python3 -B \
    tools/research/ste_001/exp007_reference_adapter.py

With no arguments, read the C worker's ste-exp007-worker-v1 request framing:
  EXP007/1 <request_id> EVAL <instance_id> <config_id> LF
Exactly five printable ASCII tokens separated by single spaces; no leading or
trailing whitespace, CR, NUL, quoting, comments or blank lines. request_id is
1..64 characters from [A-Za-z0-9._:-]. Only star/S_free (matrix_star_s_free)
and F09-geometry/S_inc (matrix_f09_s_inc) are supported. The latter selection
explicitly authorizes unchanged incidence. config_id is canonical unsigned
decimal 0..262143: no signs, leading zeroes, floats or coercion. Each of the
NINE pair positions i=3*source_index+target_index has one of FOUR states,
(config_id // 4**i) % 4: NONE, REQUIRE, EXCLUDE, REQUIRE_AND_EXCLUDE.
Every emitted record is ACCEPTED, with the plan's exact identity/provenance.

One compact, sorted-key JSON object plus LF is written immediately per frame.
Response schema: ste-exp007-reference-adapter-v1. Candidate fields have the
reference's serialization contract: concrete U_H/C_E/A_E, all six predicates,
assessment counts, presented evidence and diagnostics. input retains designated
roots, snapshot identities, geometry, profile authorization and all nine states.
case_id uses the MATRIX namespace; campaign_credit is always false. EVALUATED
means supported computation, including empty sets and negative diagnostics;
it never means scientific PASS. Transport/adapter failures have candidate:null,
error_code and failure_class=OPERATIONAL_FAILURE, never scientific diagnostics.
request_index=response_id is the one-based frame/EOF-fragment ordinal, including
errors. IDs may repeat; there is no deduplication or durable execution history.

Frames are bounded to 512 bytes excluding LF. Oversized frames are drained in
constant storage and rejected as FRAME_TOO_LONG with request_id:null. EOF with
a partial frame produces TRUNCATED_REQUEST (or FRAME_TOO_LONG); no evaluation.
Normal malformed frames echo an ID only when the version/ID prefix is valid.
Errors do not reset ordinals or caches; subsequent complete frames still run.
No request can preempt an unfinished frame. Maximum ordinal is 2**64-1.
Output is bounded to 2,000,000 bytes per response. Require complete LF framing
and check process exit: clean EOF is 0, any rejected frame/arguments is 2,
setup/read/write/internal failure is 1. INPUT_ERROR ends the process after its
response if output works. EINTR reads retry. Broken pipes/failed writes stop
without further reads or attempted stdout diagnostics. SIGPIPE is ignored at
entry; other signals keep inherited behavior. Forced termination can leave a
partial response. --help is the sole text-output mode; other arguments reject.
Interpreter bootstrap failures can precede any adapter JSON response.

The pinned protocol, plan, fixtures and Python reference are verified at setup.
No C source, binary, expected candidate table or permutation generator is read
by the evaluator. Each instance lazily runs reference.evaluate_candidate on its
validated, evidence-free geometry: the reference scans all 512 relations using
row/column occupancy and computes all six structure predicates. The two-entry
process-local cache retains only this finite classification, not configurations.
Each request has fresh evidence, calls reference.validate_candidate and calls
reference.evidence_satisfied once for each independently recognized relation.
Only output assembly/diagnostics are adapted from the reference contract.

work is PER RESPONSE, never projected coverage or timing. candidate_evaluations,
evidence_predicate_calls and records_assessed describe the current configuration;
cache_candidate_evaluations and cache_evidence_predicate_calls describe the
separate empty-evidence baseline computation (six and twelve on a cache miss,
as the pinned reference checks evidence twice). structure_predicate_calls and
reference_relation_classifications are six and 512 on a miss, zero on a hit.
candidates_generated counts recognized bijections only, not relation visits.
cached_bijections_used and cached_structure_results_used are six per evaluation,
including the constructing request; cache_hits counts only pre-existing entries.
candidate.relations_examined is actual new relation work: 512 on a miss, zero
on reuse. input_validations includes the reference's baseline validation on a
miss. Work includes baseline computation even though it grants no suite case.
Preflight hashing/parsing is setup, not candidate work. On an internal exception
work_complete=false: partial inner reference work is unavailable, not estimated.
Identical streams restarted against identical artifacts produce identical bytes;
replays inside a process have identical scientific fields but different work
when cache state differs. No bytecode or other files are written, even without -B.

Python seam: MatrixAdapter().evaluate(instance_id, config_id_string) returns a
fresh result payload, raising RequestError for invalid selectors. The CLI adds
framing/identity fields. One adapter belongs to one sequential stream; concurrent
sharing is unsupported. Returned objects never alias the private geometry cache.

LIMITATIONS: matrix only; no material solver, transformations, arbitrary geometry,
assessment overrides, orchestrator, ledger, evidence storage, resume or campaign
execution. The caller owns run/attempt binding, executable/interpreter hashes,
timeouts and durable raw receipts. No campaign qualification or general history,
merge or provenance-truth claim. EXP007_STATUS=INCONCLUSIVE; EXP-004 historical
completeness stays INCONCLUSIVE, material equivalence CALLER_ASSUMPTION.
"""

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import sys

# Set before loading the existing reference, also for imports without python -B.
sys.dont_write_bytecode = True

BASE = Path(__file__).resolve().parent
SCHEMA = 'ste-exp007-reference-adapter-v1'
PROTOCOL_SHA256 = '61a586c706cf5e3cfb78ffbfd835dcbdc060c4c46f6cc427fbf2379a095664f1'
PLAN_SHA256 = 'f817bb6267f8eee2ddcc3bc24de498e00d19a412599d3df3ff31ce79f2e592bf'
MAX_FRAME = 512
MAX_RESPONSE = 2_000_000
MAX_ORDINAL = (1 << 64) - 1
ID_PATTERN = re.compile(rb'[A-Za-z0-9._:-]{1,64}')
CONFIG_PATTERN = re.compile(r'(?:0|[1-9][0-9]{0,5})', re.ASCII)
INSTANCES = {
    'star/S_free': ('matrix_star_s_free', 'F01'),
    'F09-geometry/S_inc': ('matrix_f09_s_inc', 'F09'),
}
WORK_FIELDS = (
    'evaluator_calls', 'reference_evaluator_calls', 'input_validations',
    'reference_relation_classifications', 'candidates_generated',
    'candidate_evaluations', 'evidence_predicate_calls', 'records_assessed',
    'cache_candidate_evaluations', 'cache_evidence_predicate_calls',
    'structure_predicate_calls', 'cache_builds', 'cache_hits',
    'cached_bijections_used', 'cached_structure_results_used', 'material_evaluations',
)


class RequestError(ValueError):
    """A rejected selector/frame, distinct from any scientific outcome."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def checked_bytes(name, expected):
    with (BASE / name).open('rb') as stream:
        raw = stream.read(MAX_RESPONSE + 1)
    if len(raw) > MAX_RESPONSE or hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('artifact identity mismatch: ' + name)
    return raw


def selectors(instance, config):
    if not isinstance(instance, str) or instance not in INSTANCES:
        raise RequestError('UNSUPPORTED_INSTANCE')
    if (not isinstance(config, str) or CONFIG_PATTERN.fullmatch(config) is None
            or int(config) > 262143):
        raise RequestError('INVALID_CONFIG_ID')
    return int(config)


def request_identity(raw):
    if raw.startswith(b'EXP007/1 '):
        token = raw[len(b'EXP007/1 '):].split(b' ', 1)[0]
        if ID_PATTERN.fullmatch(token):
            return token.decode('ascii')
    return None


def parse_request(raw):
    if not raw or any(c < 32 or c > 126 for c in raw):
        raise RequestError('MALFORMED_REQUEST')
    tokens = raw.split(b' ')
    if len(tokens) != 5 or any(not token for token in tokens):
        raise RequestError('MALFORMED_REQUEST')
    version, identifier, operation, instance, config = tokens
    if version != b'EXP007/1':
        raise RequestError('UNSUPPORTED_VERSION')
    if not ID_PATTERN.fullmatch(identifier):
        raise RequestError('INVALID_REQUEST_ID')
    if operation != b'EVAL':
        raise RequestError('UNSUPPORTED_OPERATION')
    instance, config = instance.decode('ascii'), config.decode('ascii')
    selectors(instance, config)
    return instance, config


class MatrixAdapter:
    """Independent reference functions plus bounded declarative input transport."""

    def __init__(self):
        plan = json.loads(checked_bytes('EXP007_CAMPAIGN_PLAN.json', PLAN_SHA256),
                          object_pairs_hook=unique_keys)
        checked_bytes('EXP007_PROTOCOL.md', PROTOCOL_SHA256)
        artifacts = {Path(a['path']).name: a['sha256']
                     for a in plan['implementation_identity']['read_only_artifacts']}
        fixture_raw = checked_bytes('EXP007_FIXTURES.json', artifacts['EXP007_FIXTURES.json'])
        reference_raw = checked_bytes('exp007_reference.py', artifacts['exp007_reference.py'])
        # Execute the exact bytes just verified, avoiding a second source read.
        spec = importlib.util.spec_from_file_location('_exp007_reference', BASE / 'exp007_reference.py')
        self._reference = importlib.util.module_from_spec(spec)
        exec(compile(reference_raw, str(spec.origin), 'exec'), self._reference.__dict__)
        manifest = json.loads(fixture_raw, object_pairs_hook=unique_keys)
        if (manifest['protocol']['sha256'] != PROTOCOL_SHA256
                or manifest['protocol']['freeze_commit'] != self._reference.FREEZE_COMMIT):
            raise ValueError('fixture protocol identity mismatch')
        self._encoding = plan['input_encoding']
        self._bases = {}
        for instance, (suite, fixture_id) in INSTANCES.items():
            declared = next(s for s in plan['suites'] if s['id'] == suite)
            fixture = next(f for f in manifest['candidate_fixtures'] if f['id'] == fixture_id)
            if declared['instance_id'] != instance or declared['original_candidate_fixture'] != fixture_id:
                raise ValueError('matrix instance identity mismatch')
            # Whitelist inputs: never pass expectations or unrelated fixtures to the oracle.
            self._bases[instance] = copy.deepcopy({k: fixture[k] for k in (
                'id', 'snapshots', 'profile', 'assumes_unchanged_incidence', 'evidence')})
            if fixture['evidence']:
                raise ValueError('matrix base must have no evidence')
        self._cache = {}
        self.identities = dict(fixture_sha256=artifacts['EXP007_FIXTURES.json'],
                               reference_sha256=artifacts['exp007_reference.py'])

    def _construct(self, instance, config):
        fixture = copy.deepcopy(self._bases[instance])
        emission = self._encoding['record_emission']
        token = emission['instance_tokens'][instance]
        states = [(config // 4**i) % 4 for i in range(9)]
        records = []
        for i, state in enumerate(states):
            source, target = self._encoding['pair_order'][i]
            for polarity in self._encoding['states'][state]['emitted_polarities']:
                fields = dict(instance_token=token, config_id=config, i=i, polarity=polarity)
                declared = emission['provenance']
                records.append(dict(
                    id=emission['id_format'].format(**fields), source=source, target=target,
                    polarity=polarity, assessment=emission['assessment'],
                    provenance=dict(
                        origin=declared['origin'], source=declared['source_format'].format(**fields),
                        assessment_rule=declared['assessment_rule'], assumed_trust=declared['assumed_trust'],
                        scope=dict(snapshots=[fixture['snapshots'][s]['id'] for s in ('left', 'right')],
                                   source=source, target=target))))
        fixture['evidence'] = records
        return fixture, states

    def evaluate(self, instance_id, config_id, *, work=None):
        """Canonical string selectors only. No output, file writes or C execution."""
        config = selectors(instance_id, config_id)
        work = {k: 0 for k in WORK_FIELDS} if work is None else work
        work['evaluator_calls'] += 1
        fixture, states = self._construct(instance_id, config)
        ref = self._reference
        work['input_validations'] += 1
        ref.validate_candidate(fixture)
        if instance_id not in self._cache:
            work['reference_evaluator_calls'] += 1
            work['input_validations'] += 1
            baseline = ref.evaluate_candidate(self._bases[instance_id])
            if baseline['status'] != 'SUPPORTED':
                raise ValueError('reference rejected pinned matrix geometry')
            work['reference_relation_classifications'] += baseline['relations_examined']
            size = len(baseline['candidate_sets']['U_H'])
            work['candidates_generated'] += size
            work['cache_candidate_evaluations'] += size
            work['cache_evidence_predicate_calls'] += 2 * size
            work['structure_predicate_calls'] += size
            self._cache[instance_id] = baseline
            work['cache_builds'] += 1
        else:
            work['cache_hits'] += 1
        candidate = copy.deepcopy(self._cache[instance_id])
        evidence, admissible = [], []
        for predicate in candidate['predicates']:
            relation = frozenset(tuple(pair) for pair in predicate['association'])
            work['candidate_evaluations'] += 1
            work['evidence_predicate_calls'] += 1
            work['cached_bijections_used'] += 1
            work['cached_structure_results_used'] += 1
            satisfied = ref.evidence_satisfied(relation, fixture['evidence'])
            predicate['evidence_satisfied'] = satisfied
            if satisfied:
                evidence.append(predicate['association'])
                if predicate['structure_satisfied']:
                    admissible.append(predicate['association'])
        candidate['candidate_sets'].update(C_E=ref.ordered(evidence), A_E=ref.ordered(admissible))
        candidate['counts'] = {k: len(v) for k, v in candidate['candidate_sets'].items()}
        records = fixture['evidence']
        candidate['assessment_counts'] = {status: sum(e['assessment'] == status for e in records)
                                          for status in ('ACCEPTED', 'REJECTED', 'UNRESOLVED')}
        work['records_assessed'] += len(records)
        candidate['conditional'] = bool(candidate['assessment_counts']['UNRESOLVED'])
        candidate['evidence_records'] = copy.deepcopy(records)
        diagnostics = []
        if not records:
            diagnostics.append('MISSING_EVIDENCE')
        if candidate['conditional']:
            diagnostics.append('ASSESSMENT_UNRESOLVED')
        if not evidence:
            diagnostics.append('EVIDENCE_INCONSISTENT')
        elif not admissible:
            diagnostics.append('STRUCTURALLY_UNSATISFIABLE')
        candidate['diagnostics'] = sorted(diagnostics)
        candidate['relations_examined'] = work['reference_relation_classifications']
        return dict(
            case_id=f'EXP007/C/V1/{INSTANCES[instance_id][0]}/{instance_id}/{config:06d}',
            instance_id=instance_id, config_id=config,
            input=dict(snapshots=fixture['snapshots'], profile=fixture['profile'],
                       assumes_unchanged_incidence=fixture['assumes_unchanged_incidence'], pair_states=states),
            candidate=candidate, work=work)


def response(ordinal, identifier, error=None):
    return dict(schema=SCHEMA, protocol_sha256=PROTOCOL_SHA256, plan_sha256=PLAN_SHA256,
                qualification='DRAFT_NOT_SCIENTIFICALLY_QUALIFIED', scientific_claim='INCONCLUSIVE',
                campaign_credit=False, request_index=ordinal, response_id=ordinal, request_id=identifier,
                status=('EVALUATED' if error is None else
                        'UNSUPPORTED' if error.startswith('UNSUPPORTED_') else 'ERROR'),
                error_code=error, failure_class=None if error is None else 'OPERATIONAL_FAILURE',
                case_id=None, instance_id=None, config_id=None, input=None, candidate=None,
                work={k: 0 for k in WORK_FIELDS}, work_complete=True)


def frames():
    """Fixed prefix + fixed read chunk; oversized input never accumulates."""
    prefix, oversized = bytearray(), False
    while True:
        try:
            incoming = os.read(0, 4096)
        except InterruptedError:
            continue
        except OSError:
            yield bytes(prefix), 'INPUT_ERROR'
            return
        if not incoming:
            if prefix or oversized:
                yield bytes(prefix), 'FRAME_TOO_LONG' if oversized else 'TRUNCATED_REQUEST'
            return
        for byte in incoming:
            if byte == 10:
                yield bytes(prefix), 'FRAME_TOO_LONG' if oversized else None
                prefix.clear()
                oversized = False
            elif len(prefix) < MAX_FRAME:
                prefix.append(byte)
            else:
                oversized = True


def write_bytes(raw):
    remaining = memoryview(raw)
    while remaining:
        try:
            written = os.write(1, remaining)
        except InterruptedError:
            continue
        if written <= 0:
            raise OSError('output write made no progress')
        remaining = remaining[written:]


def write_response(value):
    raw = (canonical(value) + '\n').encode('ascii')
    if len(raw) > MAX_RESPONSE:
        raise OSError('response exceeds bounded size')
    write_bytes(raw)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ['--help']:
        write_bytes((__doc__ + '\n').encode('utf-8'))
        return 0
    if argv:
        write_response(response(1, None, 'UNSUPPORTED_ARGUMENTS'))
        return 2
    try:
        adapter = MatrixAdapter()
    except Exception as error:
        write_response(response(1, None, 'SETUP_ERROR'))
        print('SETUP_ERROR: ' + str(error), file=sys.stderr)
        return 1
    rejected, ordinal = False, 0
    for raw, framing_error in frames():
        if ordinal == MAX_ORDINAL:
            return 1
        ordinal += 1
        identifier = None if framing_error == 'FRAME_TOO_LONG' else request_identity(raw)
        output = response(ordinal, identifier)
        fatal = False
        try:
            if framing_error:
                raise RequestError(framing_error)
            instance, config = parse_request(raw)
            output.update(adapter.evaluate(instance, config, work=output['work']))
        except RequestError as error:
            output = response(ordinal, identifier, str(error))
            rejected = True
            fatal = str(error) == 'INPUT_ERROR'
        except Exception as error:
            measured = output['work']
            output = response(ordinal, identifier, 'INTERNAL_EVALUATOR_ERROR')
            output.update(work=measured, work_complete=False)
            print('INTERNAL_EVALUATOR_ERROR: ' + type(error).__name__, file=sys.stderr)
            fatal = True
        output.update(adapter.identities)
        write_response(output)
        if fatal:
            return 1
    return 2 if rejected else 0


if __name__ == '__main__':
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        sys.exit(main())
    except OSError:
        # A failed write may have emitted a prefix; never append an error to it.
        sys.exit(1)
