/*
 * STE EXP-007 / #415: bounded NON-MATRIX C11 adapter, not a campaign runner.
 * Scientific authority: EXP007_PROTOCOL.md V1; operational case encoding:
 * EXP007_CAMPAIGN_PLAN.json. No promotion to SHAPES/PETRA/TPI semantics.
 *
 * Build outside the repository:
 * cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 \
 *   tools/research/ste_001/exp007_c_adapter.c -o /tmp/exp007-c-adapter
 * See --help for the complete stream and result contracts.
 *
 * The immutable original scientific implementation is included below. This
 * file only transports declarations, supplies ordered consumers around its
 * direct constructor/certificate/equivalence primitives, and emits receipts.
 * No Python algorithm, expected candidate table, or reference output is used.
 * All transformations begin with a fresh original input. Strings are borrowed
 * from immutable declarations; copying their owning fixed structures therefore
 * cannot alias mutable input from another request. No allocation or file I/O
 * other than stdin/stdout, and no caches, subprocesses, clocks or random state.
 *
 * Qualification contract (freeze before running checks): compare named inputs
 * exactly with the existing independent reference; exercise nonidentity cases
 * in every transformation family, including rejection certificates after
 * relabeling and reordering; check actual consumer receipts, all three law
 * operations, replay, framing errors and recovery. Any exact semantic, receipt,
 * work, framing or exit disagreement fails the respective implementation gate.
 * Outcomes: bounded implementation checks passed/failed, or explicit unsupported
 * operation. None supplies campaign evidence. No exhaustive campaign is run.
 */
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <unistd.h>

#define HA_NO_MAIN
#include "historical_associations.c"

#define CA_SCHEMA "ste-exp007-c-adapter-v1"
#define CA_PLAN_SHA256 "f817bb6267f8eee2ddcc3bc24de498e00d19a412599d3df3ff31ce79f2e592bf"
#define CA_SOLVER_SHA256 "0ade79ad8d6465d1988f674f521a7d09585b7b3ac0ebc0b2abc7e0a69a0b63ce"
#define CA_FIXTURE_SHA256 "79ed7bb6b3cbb01c82b690d17a426a9453bbe52808cbadd8ca1385e3cfaf2e21"
enum { CA_FRAME = 512, CA_ID = 64, CA_TEXT = 192,
       CA_ALTERNATIVES = HA_CANDIDATES * HA_DECISIONS, CA_DOMAIN = 28 };

typedef enum {
    CA_NAMED, CA_SENSITIVITY, CA_AUXILIARY, CA_MATERIAL,
    CA_RECORD_ORDER, CA_DUPLICATE, CA_CANDIDATE_RENAME, CA_MATERIAL_RENAME,
    CA_LAYOUT, CA_ASSOCIATION_ORDER, CA_OUTCOME_ORDER, CA_LAWS
} CaSuite;

static const char *const ca_suite_names[] = {
    "named_candidates", "f12_sensitivity", "auxiliary_m04_association",
    "named_materials", "record_orders", "record_duplications",
    "candidate_relabelings", "material_relabelings", "vertex_layouts",
    "association_orders", "material_outcome_orders",
    "derived_observable_equivalence_laws"
};

typedef struct {
    char id[CA_ID + 1];
    CaSuite suite;
    HaSelection selection;
    unsigned rank;
} CaRequest;

/* Counts are per response. Inner immutable loops are accounted only from
 * their completed results, not projected suite sizes. See --help for scopes. */
typedef struct {
    size_t evaluator_calls, candidates_generated, candidate_evaluations;
    size_t evidence_predicate_calls, structure_predicate_calls, records_assessed;
    size_t material_consumer_calls, material_evaluations, direct_constructions;
    size_t certificate_reconstructions, certificates_generated, certificates_verified;
    size_t rejection_rows_generated, certificate_rows_verified;
    size_t witnesses_verified, witness_obligation_checks, partition_equivalence_calls;
    size_t law_checks, law_equivalence_calls;
} CaWork;

typedef struct {
    size_t record_count, association_count, outcome_count;
    HaRecord records[HA_RECORDS];
    HaAssociation associations[HA_CANDIDATES];
    HaAlternative outcomes[CA_ALTERNATIVES];
    bool candidate_called, material_called, partition_called;
} CaTrace;

typedef struct {
    HaInput input, original;
    HaNamedMaterial material;
    bool has_material;
    unsigned left_permutation[HA_VERTICES], right_permutation[HA_VERTICES];
    unsigned association_permutation[HA_CANDIDATES], outcome_permutation[HA_DECISIONS];
    HaCandidates candidates;
    HaMaterials materials;
    CaTrace trace;
    CaWork work;
    char case_id[CA_TEXT];
    unsigned law_kind, law_ranks[3], law_arity;
    HaAlternative law_operands[3];
    bool law_actual[3], law_expected[3], law_holds, operation_matches;
} CaCase;

static const unsigned ca_factorial[] = {1, 1, 2, 6, 24, 120, 720};

/* Permutation unranking is presentation transport, never candidate generation. */
static bool ca_permutation(unsigned n, unsigned rank, unsigned *out)
{
    unsigned pool[HA_CANDIDATES], i, j;
    if (n > HA_CANDIDATES || rank >= ca_factorial[n]) return false;
    for (i = 0; i < n; ++i) pool[i] = i;
    for (i = 0; i < n; ++i) {
        unsigned block = ca_factorial[n - i - 1], at = rank / block;
        rank %= block;
        out[i] = pool[at];
        for (j = at; j + 1 < n - i; ++j) pool[j] = pool[j + 1];
    }
    return true;
}

static bool ca_id_char(unsigned char c)
{
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
        (c >= '0' && c <= '9') || c == '.' || c == '_' || c == ':' || c == '-';
}

static void ca_identity(const char *line, size_t length, CaRequest *r)
{
    static const char prefix[] = "EXP007/1 ";
    size_t start = sizeof(prefix) - 1, end = start, i;
    if (length < start || memcmp(line, prefix, start) != 0) return;
    while (end < length && line[end] != ' ') ++end;
    if (end == start || end - start > CA_ID) return;
    for (i = start; i < end; ++i)
        if (!ca_id_char((unsigned char)line[i])) return;
    memcpy(r->id, line + start, end - start);
    r->id[end - start] = '\0';
}

static bool ca_one_of(const char *id, const char *const *ids, size_t n)
{
    return ha_find(ids, n, id) >= 0;
}

static const char *ca_select(CaRequest *r, const char *fixture)
{
    static const char *const records[] = {"F02", "F03", "F06", "F07", "F08", "F10", "F11", "F14"};
    static const char *const layouts[] = {"F01", "F09", "F10", "F11"};
    static const char *const supported_materials[] = {"M01", "M02", "M03", "M04"};
    unsigned limit = 1;
    bool allowed = false;
    if (r->suite == CA_LAWS) {
        if (!ha_equal(fixture, "Q")) return "UNSUPPORTED_FIXTURE_FOR_SUITE";
        return r->rank < 22764 ? NULL : "INVALID_VARIANT_RANK";
    }
    if (!ha_select(fixture, &r->selection)) return "UNSUPPORTED_FIXTURE";
    switch (r->suite) {
    case CA_NAMED:
        allowed = r->selection.material == NULL &&
            r->selection.candidate >= &ha_named_candidates[0] &&
            r->selection.candidate <= &ha_named_candidates[16];
        break;
    case CA_SENSITIVITY:
        allowed = ha_equal(fixture, "F12-ACCEPTED") || ha_equal(fixture, "F12-REJECTED");
        break;
    case CA_AUXILIARY: allowed = ha_equal(fixture, "M04-association"); break;
    case CA_MATERIAL: allowed = r->selection.material != NULL; break;
    case CA_RECORD_ORDER: case CA_DUPLICATE:
        allowed = ca_one_of(fixture, records, HA_LENGTH(records));
        if (r->suite == CA_RECORD_ORDER)
            limit = ca_factorial[r->selection.candidate->record_count];
        break;
    case CA_CANDIDATE_RENAME:
        allowed = r->selection.material == NULL && r->selection.candidate->invalid == 0 &&
            r->selection.candidate <= &ha_named_candidates[16];
        limit = 36;
        break;
    case CA_MATERIAL_RENAME:
        allowed = ca_one_of(fixture, supported_materials, HA_LENGTH(supported_materials));
        limit = 36;
        break;
    case CA_LAYOUT:
        allowed = ca_one_of(fixture, layouts, HA_LENGTH(layouts)); limit = 576; break;
    case CA_ASSOCIATION_ORDER:
        allowed = ca_one_of(fixture, supported_materials, 3); limit = 720; break;
    case CA_OUTCOME_ORDER: allowed = ha_equal(fixture, "M04"); limit = 2; break;
    case CA_LAWS: break;
    }
    if (!allowed) return "UNSUPPORTED_FIXTURE_FOR_SUITE";
    return r->rank < limit ? NULL : "INVALID_VARIANT_RANK";
}

static const char *ca_parse(char *line, size_t length, CaRequest *r)
{
    char *tokens[6];
    size_t i, count = 1;
    unsigned rank = 0;
    ca_identity(line, length, r);
    if (length == 0) return "MALFORMED_REQUEST";
    for (i = 0; i < length; ++i)
        if ((unsigned char)line[i] < 32 || (unsigned char)line[i] > 126)
            return "MALFORMED_REQUEST";
    line[length] = '\0';
    tokens[0] = line;
    for (i = 0; i < length; ++i)
        if (line[i] == ' ') {
            if (i == 0 || line[i - 1] == '\0' || i + 1 == length || count == 6)
                return "MALFORMED_REQUEST";
            line[i] = '\0'; tokens[count++] = line + i + 1;
        }
    if (count != 6) return "MALFORMED_REQUEST";
    if (!ha_equal(tokens[0], "EXP007/1")) return "UNSUPPORTED_VERSION";
    if (r->id[0] == '\0') return "INVALID_REQUEST_ID";
    if (!ha_equal(tokens[2], "EVAL")) return "UNSUPPORTED_OPERATION";
    for (i = 0; i < HA_LENGTH(ca_suite_names); ++i)
        if (ha_equal(tokens[3], ca_suite_names[i])) break;
    if (i == HA_LENGTH(ca_suite_names)) return "UNSUPPORTED_SUITE";
    r->suite = (CaSuite)i;
    if (tokens[5][0] == '0' && tokens[5][1] != '\0') return "INVALID_VARIANT_RANK";
    for (i = 0; tokens[5][i] != '\0'; ++i) {
        unsigned digit;
        if (tokens[5][i] < '0' || tokens[5][i] > '9') return "INVALID_VARIANT_RANK";
        digit = (unsigned)(tokens[5][i] - '0');
        if (rank > (UINT32_MAX - digit) / 10u) return "VARIANT_RANK_OVERFLOW";
        rank = 10u * rank + digit;
    }
    r->rank = rank;
    return ca_select(r, tokens[4]);
}

static const char *ca_rename_handle(const HaSnapshot *original, const unsigned *p,
                                   const char *handle)
{
    int i = ha_find(original->occurrences, HA_N, handle);
    return i < 0 ? handle : original->occurrences[p[i]];
}

static void ca_rename_snapshot(HaSnapshot *s, const HaSnapshot *original, const unsigned *p)
{
    size_t i;
    for (i = 0; i < HA_VERTICES; ++i)
        s->vertices[i] = ca_rename_handle(original, p, original->vertices[i]);
    for (i = 0; i < HA_N; ++i) {
        s->occurrences[i] = ca_rename_handle(original, p, original->occurrences[i]);
        s->edges[i].source = ca_rename_handle(original, p, original->edges[i].source);
        s->edges[i].target = ca_rename_handle(original, p, original->edges[i].target);
    }
}

static bool ca_construct_input(const CaRequest *r, CaCase *c)
{
    size_t i;
    int length;
    c->original = c->input = ha_named_input(r->selection.candidate);
    c->has_material = r->selection.material != NULL;
    if (c->has_material) c->material = *r->selection.material;
    for (i = 0; i < HA_VERTICES; ++i)
        c->left_permutation[i] = c->right_permutation[i] = (unsigned)i;
    for (i = 0; i < HA_CANDIDATES; ++i) c->association_permutation[i] = (unsigned)i;
    for (i = 0; i < HA_DECISIONS; ++i) c->outcome_permutation[i] = (unsigned)i;
    if (r->suite == CA_RECORD_ORDER) {
        unsigned p[HA_CANDIDATES];
        if (!ca_permutation((unsigned)c->input.record_count, r->rank, p)) return false;
        for (i = 0; i < c->input.record_count; ++i)
            c->input.records[i] = c->original.records[p[i]];
    } else if (r->suite == CA_DUPLICATE) {
        if (c->input.record_count > HA_RECORDS / 2) return false;
        for (i = 0; i < c->original.record_count; ++i) {
            c->input.records[2 * i] = c->original.records[i];
            c->input.records[2 * i + 1] = c->original.records[i];
        }
        c->input.record_count *= 2;
    } else if (r->suite == CA_CANDIDATE_RENAME || r->suite == CA_MATERIAL_RENAME) {
        if (!ca_permutation(HA_N, r->rank / 6, c->left_permutation) ||
            !ca_permutation(HA_N, r->rank % 6, c->right_permutation)) return false;
        ca_rename_snapshot(&c->input.left, &c->original.left, c->left_permutation);
        ca_rename_snapshot(&c->input.right, &c->original.right, c->right_permutation);
        for (i = 0; i < c->input.record_count; ++i) {
            HaRecord *e = &c->input.records[i];
            e->source = ca_rename_handle(&c->original.left, c->left_permutation, e->source);
            e->target = ca_rename_handle(&c->original.right, c->right_permutation, e->target);
            e->provenance.scope_source = e->source;
            e->provenance.scope_target = e->target;
        }
        if (c->has_material) {
            /* The occurrence presentation is itself transported, so initial
             * values stay at the same positions, now bound to renamed handles. */
            for (i = 0; i < c->material.input.update_count; ++i) {
                HaUpdate *u = &c->material.input.updates[i];
                u->target = u->side == HA_LEFT ?
                    ca_rename_handle(&c->original.left, c->left_permutation, u->target) :
                    ca_rename_handle(&c->original.right, c->right_permutation, u->target);
            }
        }
    } else if (r->suite == CA_LAYOUT) {
        if (!ca_permutation(HA_VERTICES, r->rank / 24, c->left_permutation) ||
            !ca_permutation(HA_VERTICES, r->rank % 24, c->right_permutation)) return false;
        for (i = 0; i < HA_VERTICES; ++i) {
            c->input.left.vertices[i] = c->original.left.vertices[c->left_permutation[i]];
            c->input.right.vertices[i] = c->original.right.vertices[c->right_permutation[i]];
        }
    } else if (r->suite == CA_ASSOCIATION_ORDER) {
        if (!ca_permutation(HA_CANDIDATES, r->rank, c->association_permutation)) return false;
    } else if (r->suite == CA_OUTCOME_ORDER) {
        if (!ca_permutation(HA_DECISIONS, r->rank, c->outcome_permutation)) return false;
    }
    length = snprintf(c->case_id, sizeof(c->case_id), "EXP007/C/V1/%s/%s/%06u",
                      ca_suite_names[r->suite], r->selection.id, r->rank);
    return length >= 0 && (size_t)length < sizeof(c->case_id);
}

/* Boundary receipt of the EXACT argument passed to the original evaluator.
 * There is no sort/dedup/normalization between this hook and ha_evaluate.
 * Its supported-input assessment loop visits every record in this order,
 * including repeated IDs, before its possibly short-circuiting predicates.
 * Invalid fixtures have a received argument, but zero assessed records. */
static HaCandidates ca_evaluate(const HaInput *received, CaTrace *trace, CaWork *w)
{
    HaCandidates out;
    size_t i;
    trace->candidate_called = true;
    trace->record_count = received->record_count;
    for (i = 0; i < received->record_count; ++i) trace->records[i] = received->records[i];
    ++w->evaluator_calls;
    out = ha_evaluate(received);
    w->candidates_generated += out.universe_count;
    w->candidate_evaluations += out.universe_count;
    w->evidence_predicate_calls += out.universe_count;
    w->structure_predicate_calls += out.universe_count;
    for (i = 0; i < 3; ++i) w->records_assessed += out.assessment_counts[i];
    return out;
}

static bool ca_witness_valid(const HaInput *in, const HaConstruction *a, CaWork *w)
{
    size_t i;
    if (!a->supported || !a->equalities_consistent) return false;
    for (i = 0; i < a->obligation_count; ++i) {
        int at = ha_find(in->left.occurrences, HA_N, a->obligations[i].target);
        ++w->witness_obligation_checks;
        if (at < 0 || a->values[at] != a->obligations[i].value) return false;
    }
    ++w->witnesses_verified;
    return true;
}

/* This path consumes caller-supplied, full concrete outcomes BEFORE forming
 * classes. The trace is copied at loop entry from the actually received item.
 * Values, association, decision, obligations and certificate all travel with
 * the item. No first-outcome selection or pre-partition quotient occurs. */
static bool ca_partition(HaMaterials *out, const HaAlternative *received, size_t count,
                          CaTrace *trace, CaWork *w)
{
    size_t i;
    if (count > CA_ALTERNATIVES) return false;
    trace->partition_called = true;
    for (i = 0; i < count; ++i) {
        size_t earlier;
        trace->outcomes[trace->outcome_count++] = received[i];
        out->alternatives[i] = received[i];
        if (!out->partition_complete) continue;
        for (earlier = 0; earlier < i; ++earlier) {
            ++w->partition_equivalence_calls;
            if (ha_same_outcome(&received[i], &out->alternatives[earlier])) break;
        }
        out->class_of[i] = earlier == i ? out->class_count++ : out->class_of[earlier];
    }
    return true;
}

/* Ordered scientific consumer local to this adapter. ha_material_evaluate
 * cannot accept an association array, so use its immutable direct primitives
 * rather than shuffling that function's already computed JSON/results. */
static bool ca_material_consume(const HaInput *in, const HaMaterial *m,
                                const HaAssociation *received, size_t count,
                                const size_t *universe_indices,
                                const unsigned outcome_order[HA_DECISIONS],
                                HaMaterials *out, CaTrace *trace, CaWork *w)
{
    HaAlternative constructed[CA_ALTERNATIVES] = {0}, offered[CA_ALTERNATIVES];
    size_t i, d;
    ++w->material_consumer_calls;
    trace->material_called = true;
    out->reason = ha_validate_material(in, m);
    if (out->reason != NULL) return true; /* e.g. M05-P: no material outcome. */
    if (count > HA_CANDIDATES) return false;
    out->policy_supported = true;
    out->observable_defined = m->observable_defined;
    for (i = 0; i < count; ++i) {
        bool rejected = true;
        if (universe_indices[i] >= HA_CANDIDATES) return false;
        trace->associations[trace->association_count++] = received[i];
        for (d = 0; d < m->decision_count; ++d) {
            HaAlternative *a = &constructed[out->alternative_count++];
            a->association = received[i];
            ++w->material_evaluations;
            ++w->direct_constructions;
            a->construction = ha_construct(in, &a->association, m, d);
            if (!a->construction.supported) return false;
            if (a->construction.equalities_consistent) {
                if (!ca_witness_valid(in, &a->construction, w)) return false;
                ++out->witness_count;
                rejected = false;
            } else {
                ++out->certificates_required;
                if (m->observable_defined) {
                    ++w->certificates_generated;
                    ha_rejection_rows(in, &a->association, &a->construction, &a->rejection);
                    w->rejection_rows_generated += a->rejection.row_count;
                    /* ha_certificate_valid makes one real ha_construct call.
                     * Count that separately from outcome construction. */
                    ++w->certificate_reconstructions;
                    a->rejection_certified = ha_certificate_valid(in, &a->association, m, d,
                                                                 &a->rejection);
                    if (!a->rejection_certified) return false;
                    ++w->certificates_verified;
                    w->certificate_rows_verified += a->rejection.row_count;
                    ++out->certificates_completed;
                } else {
                    ++out->uncertified_count;
                    rejected = false;
                }
            }
        }
        out->rejected_under_all_decisions[universe_indices[i]] = rejected;
        if (rejected) ++out->rejected_association_count;
    }
    out->partition_complete = out->observable_defined && out->uncertified_count == 0;
    /* Reorder full input items to the partition consumer, not serialized JSON.
     * M04 has exactly one association and two concrete authorized outcomes. */
    for (i = 0; i < out->alternative_count; ++i) {
        size_t base = i / m->decision_count * m->decision_count;
        size_t at = outcome_order[i % m->decision_count];
        if (at >= m->decision_count) return false;
        offered[i] = constructed[base + at];
    }
    return ca_partition(out, offered, out->alternative_count, trace, w);
}

/* Abstract defined Q carrier, not fabricated scientific material results.
 * REJECT uses the original operation's tag representation; it is not a claim
 * of rejection for any fixture, and has no material/certificate work credit. */
static HaAlternative ca_law_operand(unsigned rank)
{
    HaAlternative a = {0};
    size_t i;
    a.construction.supported = true;
    a.rejection_certified = rank == 0;
    a.construction.equalities_consistent = rank != 0;
    if (rank != 0) {
        --rank;
        for (i = HA_N; i > 0; --i) {
            a.construction.values[i - 1] = (HaValue)(rank % 3); rank /= 3;
        }
    }
    return a;
}

static bool ca_law_expected(const HaAlternative *a, const HaAlternative *b)
{
    size_t i;
    if (a->rejection_certified != b->rejection_certified) return false;
    if (a->rejection_certified) return true;
    for (i = 0; i < HA_N; ++i)
        if (a->construction.values[i] != b->construction.values[i]) return false;
    return true;
}

static bool ca_law(CaCase *c, unsigned rank)
{
    static const char *const laws[] = {"REFLEXIVITY", "SYMMETRY", "TRANSITIVITY"};
    unsigned pairs[3][2] = {{0, 0}, {0, 0}, {0, 0}}, calls = 1, i;
    char b[16] = "na", d[16] = "na";
    int length;
    c->law_arity = 1;
    if (rank < CA_DOMAIN) c->law_ranks[0] = rank;
    else if ((rank -= CA_DOMAIN) < CA_DOMAIN * CA_DOMAIN) {
        c->law_kind = 1; c->law_arity = calls = 2;
        c->law_ranks[0] = rank / CA_DOMAIN; c->law_ranks[1] = rank % CA_DOMAIN;
        pairs[0][1] = pairs[1][0] = 1;
    } else {
        rank -= CA_DOMAIN * CA_DOMAIN;
        c->law_kind = 2; c->law_arity = calls = 3;
        c->law_ranks[0] = rank / (CA_DOMAIN * CA_DOMAIN);
        c->law_ranks[1] = rank / CA_DOMAIN % CA_DOMAIN;
        c->law_ranks[2] = rank % CA_DOMAIN;
        pairs[0][1] = pairs[1][0] = 1; pairs[1][1] = pairs[2][1] = 2;
    }
    for (i = 0; i < c->law_arity; ++i) c->law_operands[i] = ca_law_operand(c->law_ranks[i]);
    c->operation_matches = true;
    for (i = 0; i < calls; ++i) {
        const HaAlternative *a = &c->law_operands[pairs[i][0]], *v = &c->law_operands[pairs[i][1]];
        ++c->work.law_equivalence_calls;
        c->law_actual[i] = ha_same_outcome(a, v);
        c->law_expected[i] = ca_law_expected(a, v);
        if (c->law_actual[i] != c->law_expected[i]) c->operation_matches = false;
    }
    c->law_holds = c->law_kind == 0 ? c->law_actual[0] : c->law_kind == 1 ?
        c->law_actual[0] == c->law_actual[1] :
        !(c->law_actual[0] && c->law_actual[1]) || c->law_actual[2];
    ++c->work.law_checks;
    if (c->law_arity >= 2) (void)snprintf(b, sizeof(b), "%u", c->law_ranks[1]);
    if (c->law_arity >= 3) (void)snprintf(d, sizeof(d), "%u", c->law_ranks[2]);
    length = snprintf(c->case_id, sizeof(c->case_id),
                      "EXP007/C/V1/derived-observable-laws/%s/%u/%s/%s",
                      laws[c->law_kind], c->law_ranks[0], b, d);
    return length >= 0 && (size_t)length < sizeof(c->case_id);
}

static bool ca_run(const CaRequest *r, CaCase *c)
{
    HaAssociation offered[HA_CANDIDATES];
    size_t universe_indices[HA_CANDIDATES];
    size_t i, count = 0;
    if (r->suite == CA_LAWS) {
        HaSelection base;
        if (!ha_select("F01", &base)) return false;
        c->input = ha_named_input(base.candidate);
        return ca_law(c, r->rank);
    }
    if (!ca_construct_input(r, c)) return false;
    c->candidates = ca_evaluate(&c->input, &c->trace, &c->work);
    if (!c->has_material) return true;
    if (!c->candidates.supported) return false;
    for (i = 0; i < c->candidates.universe_count; ++i) {
        size_t at = c->association_permutation[i];
        if (at >= c->candidates.universe_count) return false;
        if (c->candidates.evidence[at] && c->candidates.structure[at]) {
            universe_indices[count] = at;
            offered[count++] = c->candidates.universe[at];
        }
    }
    return ca_material_consume(&c->input, &c->material.input, offered, count,
                               universe_indices, c->outcome_permutation,
                               &c->materials, &c->trace, &c->work);
}

static void ca_snapshot(FILE *out, const HaSnapshot *s)
{
    size_t i;
    fputs("{\"id\":", out); ha_json_string(out, s->id);
    fputs(",\"root\":", out); ha_json_string(out, s->root);
    fputs(",\"vertices\":[", out);
    for (i = 0; i < s->vertex_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_string(out, s->vertices[i]);
    }
    fputs("],\"occurrences\":[", out);
    for (i = 0; i < s->occurrence_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_string(out, s->occurrences[i]);
    }
    fputs("],\"incidence\":[", out);
    for (i = 0; i < s->edge_count; ++i) {
        if (i != 0) fputc(',', out);
        fputc('[', out); ha_json_string(out, s->edges[i].source);
        fputc(',', out); ha_json_string(out, s->edges[i].target); fputc(']', out);
    }
    fputs("]}", out);
}

static void ca_strings(FILE *out, const char *const *strings, size_t count)
{
    size_t i;
    fputc('[', out);
    for (i = 0; i < count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_string(out, strings[i]);
    }
    fputc(']', out);
}

static void ca_material_input(FILE *out, const CaCase *c)
{
    const HaMaterial *m = &c->material.input;
    size_t i, side;
    fputs("{\"id\":", out); ha_json_string(out, c->material.id);
    fputs(",\"candidate_fixture\":", out); ha_json_string(out, c->material.candidate_id);
    fputs(",\"values\":[\"0\",\"lambda\",\"rho\"],\"initial\":{", out);
    for (side = 0; side < 2; ++side) {
        HaInput binding = c->input;
        binding.left = side == 0 ? c->input.left : c->input.right;
        fputs(side == 0 ? "\"left\":" : ",\"right\":", out);
        ha_json_map(out, &binding, m->initial[side]);
    }
    fputs("},\"updates\":[", out);
    for (i = 0; i < m->update_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_update(out, &m->updates[i]);
    }
    fputs("],\"policy\":", out);
    if (!m->policy_complete) fputs("null", out);
    else {
        fputs("{\"complete\":true,\"decisions\":[", out);
        for (i = 0; i < m->decision_count; ++i) {
            const HaDecision *d = &m->decisions[i];
            if (i != 0) fputc(',', out);
            fputs("{\"id\":", out); ha_json_string(out, d->id);
            fputs(",\"authorization\":", out); ha_json_string(out, d->authorization);
            fputs(",\"retained\":", out); ca_strings(out, d->retained, d->retained_count);
            fputs(",\"waived\":", out); ca_strings(out, d->waived, d->waived_count);
            fputc('}', out);
        }
        fputs("]}", out);
    }
    fputs(",\"query\":", out);
    ha_json_string(out, m->observable_defined ? "Q" : "Q_with_undeclared_extra_property");
    fputs(",\"independent_comparison\":", out); ha_json_string(out, c->material.comparison);
    fputc('}', out);
}

static void ca_json_input(FILE *out, const CaCase *c)
{
    size_t i;
    fputs("{\"snapshots\":{\"left\":", out); ca_snapshot(out, &c->input.left);
    fputs(",\"right\":", out); ca_snapshot(out, &c->input.right);
    fputs("},\"profile\":", out);
    ha_json_string(out, c->input.profile == HA_S_FREE ? "S_free" : "S_inc");
    fputs(",\"assumes_unchanged_incidence\":", out);
    ha_json_bool(out, c->input.assumes_unchanged_incidence);
    fputs(",\"evidence\":[", out);
    for (i = 0; i < c->input.record_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_record(out, &c->input.records[i]);
    }
    fputs("],\"material\":", out);
    if (c->has_material) ca_material_input(out, c); else fputs("null", out);
    fputc('}', out);
}

static void ca_mapping(FILE *out, const HaSnapshot *s, const unsigned *p, bool inverse)
{
    size_t i;
    fputc('{', out);
    ha_json_string(out, s->root); fputc(':', out); ha_json_string(out, s->root);
    for (i = 0; i < HA_N; ++i) {
        fputc(',', out); ha_json_string(out, s->occurrences[inverse ? p[i] : i]);
        fputc(':', out); ha_json_string(out, s->occurrences[inverse ? i : p[i]]);
    }
    fputc('}', out);
}

static void ca_json_transform(FILE *out, const CaRequest *r, const CaCase *c)
{
    bool rename = r->suite == CA_CANDIDATE_RENAME || r->suite == CA_MATERIAL_RENAME;
    unsigned identity[] = {0, 1, 2};
    const unsigned *left = rename ? c->left_permutation : identity;
    const unsigned *right = rename ? c->right_permutation : identity;
    fputs("{\"suite\":", out); ha_json_string(out, ca_suite_names[r->suite]);
    fputs(",\"left_transport\":", out); ca_mapping(out, &c->original.left, left, false);
    fputs(",\"right_transport\":", out); ca_mapping(out, &c->original.right, right, false);
    fputs(",\"left_inverse\":", out); ca_mapping(out, &c->original.left, left, true);
    fputs(",\"right_inverse\":", out); ca_mapping(out, &c->original.right, right, true);
    fputs(",\"left_vertex_layout\":", out);
    ca_strings(out, c->input.left.vertices, c->input.left.vertex_count);
    fputs(",\"right_vertex_layout\":", out);
    ca_strings(out, c->input.right.vertices, c->input.right.vertex_count);
    fputs(",\"composed\":false}", out);
}

static void ca_json_trace(FILE *out, const CaCase *c)
{
    const CaTrace *t = &c->trace;
    size_t i;
    fputs("{\"record_hook\":\"ca_evaluate/ha_evaluate-argument-before-assessment\","
          "\"association_hook\":\"ca_material_consume/received-item-before-construction\","
          "\"outcome_hook\":\"ca_partition/received-item-before-equivalence\","
          "\"candidate_called\":", out); ha_json_bool(out, t->candidate_called);
    fputs(",\"material_called\":", out); ha_json_bool(out, t->material_called);
    fputs(",\"partition_called\":", out); ha_json_bool(out, t->partition_called);
    fputs(",\"received_records\":[", out);
    for (i = 0; i < t->record_count; ++i) {
        if (i != 0) fputc(',', out);
        fprintf(out, "{\"position\":%zu,\"record\":", i);
        ha_json_record(out, &t->records[i]); fputc('}', out);
    }
    fputs("],\"records_assessed\":", out);
    if (c->candidates.supported) fprintf(out, "%zu", c->work.records_assessed);
    else fputs("0", out);
    fputs(",\"consumed_associations\":[", out);
    for (i = 0; i < t->association_count; ++i) {
        if (i != 0) fputc(',', out);
        fprintf(out, "{\"position\":%zu,\"association\":", i);
        ha_json_relation(out, &c->input, &t->associations[i]); fputc('}', out);
    }
    fputs("],\"consumed_outcomes\":[", out);
    for (i = 0; i < t->outcome_count; ++i) {
        const HaAlternative *a = &t->outcomes[i];
        if (i != 0) fputc(',', out);
        fprintf(out, "{\"position\":%zu,\"association\":", i);
        ha_json_relation(out, &c->input, &a->association);
        /* The full consumed item includes its decision, witness/certificate,
         * selectors and authorization, not just an order label. */
        fputs(",\"decision\":", out); ha_json_decision(out, &c->input, &c->material.input, a);
        fputc('}', out);
    }
    fputs("]}", out);
}

static void ca_json_work(FILE *out, const CaWork *w)
{
#define CA_COUNT(field) fprintf(out, "\"" #field "\":%zu,", w->field)
    fputc('{', out);
    CA_COUNT(evaluator_calls); CA_COUNT(candidates_generated); CA_COUNT(candidate_evaluations);
    CA_COUNT(evidence_predicate_calls); CA_COUNT(structure_predicate_calls); CA_COUNT(records_assessed);
    CA_COUNT(material_consumer_calls); CA_COUNT(material_evaluations); CA_COUNT(direct_constructions);
    CA_COUNT(certificate_reconstructions); CA_COUNT(certificates_generated); CA_COUNT(certificates_verified);
    CA_COUNT(rejection_rows_generated); CA_COUNT(certificate_rows_verified);
    CA_COUNT(witnesses_verified); CA_COUNT(witness_obligation_checks); CA_COUNT(partition_equivalence_calls);
    CA_COUNT(law_checks); CA_COUNT(law_equivalence_calls);
    fputs("\"reference_relation_classifications\":0,\"union_assignment_checks\":0,"
          "\"inner_predicate_record_tests\":null}", out);
#undef CA_COUNT
}

static void ca_json_law(FILE *out, const CaCase *c)
{
    static const char *const names[] = {"REFLEXIVITY", "SYMMETRY", "TRANSITIVITY"};
    unsigned i;
    fputs("{\"law\":", out); ha_json_string(out, names[c->law_kind]);
    fputs(",\"operation\":\"ha_same_outcome\",\"query\":\"Q\",\"operands\":[", out);
    for (i = 0; i < c->law_arity; ++i) {
        if (i != 0) fputc(',', out);
        fprintf(out, "{\"rank\":%u,\"observable\":", c->law_ranks[i]);
        ha_json_outcome(out, &c->input, &c->law_operands[i]); fputc('}', out);
    }
    fputs("],\"operation_results\":[", out);
    for (i = 0; i < c->law_arity; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_bool(out, c->law_actual[i]);
    }
    fputs("],\"expected_results\":[", out);
    for (i = 0; i < c->law_arity; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_bool(out, c->law_expected[i]);
    }
    fputs("],\"law_holds\":", out); ha_json_bool(out, c->law_holds);
    fputs(",\"operation_matches_extensional_equality\":", out);
    ha_json_bool(out, c->operation_matches); fputc('}', out);
}

/* Size bound: every emitted string comes from the fixed declarations except
 * request_id (64), case_id (191) and fixed error codes. At most six records,
 * six associations, twelve alternatives, 27 rows/certificate, five conjuncts
 * per row; certificates occur in both result and receipt. Even bounding every
 * fixed string by 256 bytes gives <2,000,000 bytes including LF. Input cannot
 * grow these bounds. No raw frame string is copied into a response. */
static bool ca_response(uint64_t ordinal, const CaRequest *r, const char *error, const CaCase *c)
{
    FILE *out = stdout;
    CaWork zero = {0};
    const CaWork *measured = c == NULL ? &zero : &c->work;
    bool law;
    int flushed;
    /* A failed constructor/certificate must never reach a serializer that
     * assumes complete supported alternatives, or become an invented ACCEPT. */
    if (error != NULL) c = NULL;
    law = c != NULL && r->suite == CA_LAWS;
    fputs("{\"schema\":\"" CA_SCHEMA "\",\"protocol_sha256\":\"" HA_PROTOCOL_SHA256
          "\",\"plan_sha256\":\"" CA_PLAN_SHA256 "\",\"solver_sha256\":\"" CA_SOLVER_SHA256
          "\",\"fixture_sha256\":\"" CA_FIXTURE_SHA256 "\","
          "\"qualification\":\"DRAFT_NOT_SCIENTIFICALLY_QUALIFIED\","
          "\"scientific_claim\":\"INCONCLUSIVE\",\"campaign_credit\":false,", out);
    fprintf(out, "\"request_index\":%" PRIu64 ",\"response_id\":%" PRIu64 ",\"request_id\":",
            ordinal, ordinal);
    ha_json_string(out, r->id[0] == '\0' ? NULL : r->id);
    fputs(",\"status\":", out);
    ha_json_string(out, error == NULL ? "EVALUATED" :
        strncmp(error, "UNSUPPORTED_", 12) == 0 ? "UNSUPPORTED" : "ERROR");
    fputs(",\"error_code\":", out); ha_json_string(out, error);
    fputs(",\"failure_class\":", out);
    ha_json_string(out, error == NULL ? NULL : "OPERATIONAL_FAILURE");
    fputs(",\"case_id\":", out); ha_json_string(out, c == NULL ? NULL : c->case_id);
    fputs(",\"suite_id\":", out); ha_json_string(out, c == NULL ? NULL : ca_suite_names[r->suite]);
    fputs(",\"fixture_id\":", out);
    ha_json_string(out, c == NULL ? NULL : law ? "Q" : r->selection.id);
    fputs(",\"variant_rank\":", out);
    if (c == NULL) fputs("null", out); else fprintf(out, "%u", r->rank);
    fputs(",\"input\":", out);
    if (c == NULL || law) fputs("null", out); else ca_json_input(out, c);
    fputs(",\"transformation\":", out);
    if (c == NULL || law) fputs("null", out); else ca_json_transform(out, r, c);
    fputs(",\"consumption\":", out);
    if (c == NULL || law) fputs("null", out); else ca_json_trace(out, c);
    fputs(",\"result\":", out);
    if (c == NULL || law) fputs("null", out);
    else {
        fputs("{\"id\":", out); ha_json_string(out, r->selection.id);
        fputs(",\"candidate\":", out); ha_json_candidates(out, &c->input, &c->candidates);
        if (c->has_material) {
            fputs(",\"material\":", out);
            ha_json_material(out, &c->input, &c->candidates, &c->material, &c->materials);
        }
        fputc('}', out);
    }
    fputs(",\"law\":", out);
    if (law) ca_json_law(out, c); else fputs("null", out);
    fputs(",\"work\":", out); ca_json_work(out, measured);
    fputs(",\"work_complete\":", out);
    ha_json_bool(out, error == NULL || strcmp(error, "INTERNAL_EVALUATOR_ERROR") != 0);
    fputs("}\n", out);
    flushed = fflush(out);
    return flushed == 0 && !ferror(out);
}

static int ca_help(void)
{
    static const char *const paragraphs[] = {
        "STE EXP-007 bounded non-matrix C11 adapter, #415.\n"
        "Build: cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 "
        "tools/research/ste_001/exp007_c_adapter.c -o /tmp/exp007-c-adapter\n"
        "Usage: exp007-c-adapter [--help]; otherwise sequential stdin/stdout.\n"
        "Accepted frame (exactly six printable ASCII tokens, single spaces):\n"
        "EXP007/1 <request_id> EVAL <suite_id> <fixture_id> <variant_rank> LF\n"
        "Example: EXP007/1 smoke EVAL association_orders M03 719\n"
        "ID: 1..64 of [A-Za-z0-9._:-]. Rank: canonical unsigned decimal, no sign,\n"
        "leading zero, float, coercion, quoting or comments. Max numeric value\n"
        "4294967295, checked before multiplication; suite bounds also apply.\n"
        "No leading/trailing/doubled spaces, CR, NUL, other controls or blank lines.\n"
        "Maximum frame: 512 bytes excluding LF. Oversize frames are drained with\n"
        "constant storage through LF and rejected, request_id=null. EOF fragment\n"
        "is TRUNCATED_REQUEST, or FRAME_TOO_LONG if oversized, never evaluation.\n"
        "One flushed compact JSON object plus LF per frame/fragment, at most\n"
        "2,000,000 bytes including LF (finite fixed-input bound, no dynamic input).\n"
        "No deduplication/history/cache; repeated IDs permitted. Frame ordinal is\n"
        "one-based uint64 including rejections; overflow stops with exit 1.\n\n",
        "Supported suites and exact fixture/rank domains:\n"
        "named_candidates: F01..F12, F14, F13-duplicated_handle, F13-foreign_handle,\n"
        "  F13-invalid_tree, F13-invalid_root; rank 0 (no F13 group shorthand).\n"
        "f12_sensitivity: F12-ACCEPTED, F12-REJECTED; rank 0.\n"
        "auxiliary_m04_association: M04-association; rank 0.\n"
        "named_materials: M01..M04, M05-P, M05-O, M05-I; rank 0.\n"
        "record_orders: F02,F03,F06,F07,F08,F10,F11,F14; rank 0..k!-1 for\n"
        "  original record counts k=1,2,2,2,3,2,3,2 respectively.\n"
        "record_duplications: same fixtures; rank 0; [e0,e0,e1,e1,...], same\n"
        "  stable IDs, contents and positions, no dedup before assessment.\n"
        "candidate_relabelings: F01..F12,F14; rank 0..35.\n"
        "material_relabelings: M01..M04; rank 0..35.\n"
        "vertex_layouts: F01,F09,F10,F11; rank 0..575.\n"
        "association_orders: M01,M02,M03; rank 0..719.\n"
        "material_outcome_orders: M04; rank 0..1.\n"
        "derived_observable_equivalence_laws: Q; rank 0..22763, one law per frame.\n"
        "Every permutation is zero-based lexicographic over original positions.\n"
        "Relabel rank=left_rank*6+right_rank; old occurrence i -> old p[i],\n"
        "including occurrence arrays, incidence, evidence/provenance selectors,\n"
        "initial-map keys and updates. Roots/snapshot identities stay designated.\n"
        "Layout rank=left_rank*24+right_rank; new vertices[i]=old vertices[p[i]],\n"
        "with unchanged concrete selectors/incidence and roots at any position.\n"
        "Association basis=012,021,102,120,201,210; all full alternatives enter\n"
        "the ordered material consumer before direct construction. M03 rejects\n"
        "are included. Outcome basis=d_lambda,d_rho; full constructed outcomes\n"
        "enter the partition consumer in that order/permutation, before equality.\n"
        "Suites start from fresh named inputs; no composed transformations.\n\n",
        "Laws: carrier ranks 0=REJECT; 1..27=ACCEPT maps in lexicographic product\n"
        "(0,lambda,rho) on concrete (l0,l1,l2). These are abstract observables,\n"
        "not scientific solver outcomes or certified fixture rejections.\n"
        "Request ranks 0..27: reflexivity a=rank. 28..811: symmetry, let\n"
        "x=rank-28, a=x/28,b=x%28. 812..22763: transitivity, x=rank-812,\n"
        "a=x/784,b=(x/28)%28,c=x%28. Integer division throughout.\n"
        "Calls are ha_same_outcome(a,a); (a,b),(b,a); or (a,b),(b,c),(a,c),\n"
        "respectively, eagerly executed. Check IDs follow plan derived law IDs.\n"
        "Actual Boolean results and independent tag/concrete-map expectations\n"
        "are both emitted. Undefined M05-O never enters this defined carrier.\n\n"
        "JSON schema ste-exp007-c-adapter-v1 (all envelopes):\n"
        "schema,protocol_sha256,plan_sha256,solver_sha256,fixture_sha256:string;\n"
        "qualification=DRAFT_NOT_SCIENTIFICALLY_QUALIFIED, scientific_claim=\n"
        "INCONCLUSIVE, campaign_credit=false; request_index=response_id:uint64;\n"
        "request_id:string|null (echo only a valid version/ID prefix);\n"
        "status:EVALUATED|ERROR|UNSUPPORTED; error_code:string|null;\n"
        "failure_class:null|OPERATIONAL_FAILURE; case_id,suite_id,fixture_id:\n"
        "string|null; variant_rank:uint|null; work:object; work_complete:bool.\n"
        "Scientific requests have input,transformation,consumption,result objects\n"
        "and law:null. Law requests have law:object and these four objects null.\n"
        "Operational rejection has these five fields null and zero work. Internal\n"
        "failure retains available work, null payloads, work_complete=false; exit 1.\n"
        "input={snapshots:{left,right},profile,assumes_unchanged_incidence,evidence,\n"
        "material}. Snapshot={id,root,vertices,occurrences,incidence:[directed pairs]}.\n"
        "Evidence entries={id,source,target,polarity,assessment,provenance:{origin,\n"
        "source,assessment_rule,assumed_trust,scope:{snapshots:[left_id,right_id],\n"
        "source,target}}}. Material=null or {id,candidate_fixture,values,initial:\n"
        "{left,right},updates:[{id,side,target,value,mandatory}],policy:null|\n"
        "{complete,decisions:[{id,authorization,retained:[IDs],waived:[IDs]}]},\n"
        "query,independent_comparison}. Initial maps bind concrete handles.\n\n",
        "transformation={suite,left_transport,right_transport,left_inverse,\n"
        "right_inverse,left_vertex_layout,right_vertex_layout,composed:false}.\n"
        "Transport maps include fixed roots, explicit identity when applicable.\n"
        "consumption={record_hook,association_hook,outcome_hook,candidate_called,\n"
        "material_called,partition_called,received_records:[{position,record}],\n"
        "records_assessed,consumed_associations:[{position,association}],\n"
        "consumed_outcomes:[{position,association,decision}]}. Positions zero-based.\n"
        "Record hook captures the exact ha_evaluate argument before its original\n"
        "assessment loop; invalid input has received records but no assessments.\n"
        "Predicates may short circuit: receipt is NOT a claim every predicate\n"
        "reads every record. Other hooks copy actual items at consuming loop entry.\n"
        "An uncalled consumer has called=false and empty receipts. Full outcome\n"
        "receipt decision uses the same decision schema as the material result.\n"
        "result is an existing ste-exp007-reference-v1 result row: {id,candidate,\n"
        "material?}, suitable for wrapping in that schema for exact comparison.\n"
        "candidate={status,diagnostics,conditional,candidate_sets:{U_H,C_E,A_E},\n"
        "counts:{U_H,C_E,A_E},relations_examined,assessment_counts:{ACCEPTED,\n"
        "REJECTED,UNRESOLVED},evidence_records,predicates:[{association,\n"
        "evidence_satisfied,structure_satisfied}]}; invalid input instead has\n"
        "null sets/counts/predicates/records/assessments/conditional, zero examined,\n"
        "reason:string, diagnostics=[INVALID_INPUT], status=UNSUPPORTED.\n"
        "Relations are arrays of concrete [source,target] pairs, never root pairs.\n"
        "material={scientific_claim,independent_comparison,policy_status,\n"
        "observable_status,diagnostics,associations,observable_classes,reason?}.\n"
        "Association={association,decisions,W_phi,rejected_under_all_decisions,\n"
        "outcomes:[{decision:ID,outcome}]}. Decision={id,authorization,\n"
        "retained_intentions,waived_intentions,obligations,W_phi_d,witnesses,\n"
        "rejection_certificate,outcomes}. Intentions use the update schema.\n"
        "Obligation={id,kind,target,value,intention?,side?,selector?}; IDs are\n"
        "update:<intention> or preserve:<concrete source>. Witness={material:map,\n"
        "satisfied:[conjunct IDs]}. A rejection certificate has all 27 rows\n"
        "{material:map,violated:[conjunct IDs]}; null for an accepting decision.\n"
        "Outcome={tag:REJECT} or {tag:ACCEPT,material:map}. W_phi/W_phi_d are\n"
        "extensional map arrays. Observable class={observable:outcome,members:\n"
        "[{association,decision:ID}]}. No decision, witness or authorization is lost.\n"
        "M05-P has null associations/classes and POLICY_UNSUPPORTED; M05-O keeps\n"
        "witnesses with null classes; M05-I keeps INCOMPLETE comparison.\n"
        "law={law,operation:ha_same_outcome,query:Q,operands:[{rank,observable}],\n"
        "operation_results:[bool],expected_results:[bool],law_holds:bool,\n"
        "operation_matches_extensional_equality:bool}. No generic PASS is emitted.\n\n",
        "work counters (nonnegative integers, per request, no campaign projections):\n"
        "evaluator_calls counts actual original candidate calls; candidates_generated,\n"
        "candidate_evaluations,evidence_predicate_calls,structure_predicate_calls\n"
        "account its completed universe (each immutable loop calls both predicates\n"
        "once). records_assessed is the completed original assessment count.\n"
        "material_consumer_calls includes policy-validation rejection;\n"
        "material_evaluations=direct_constructions counts actual ha_construct calls\n"
        "for outcomes. certificate_reconstructions counts additional ha_construct\n"
        "calls made inside ha_certificate_valid. Its internal validation/evidence/\n"
        "structure calls are outside candidate-loop predicate counters above.\n"
        "certificates_generated,certificates_verified and rejection_rows_generated,\n"
        "certificate_rows_verified count real completed generator/validator work;\n"
        "failed validation is fatal with work_complete=false, not a guessed count.\n"
        "witnesses_verified,witness_obligation_checks count explicit acceptance checks.\n"
        "partition_equivalence_calls counts ordered consumer comparisons;\n"
        "law_checks,law_equivalence_calls count the separate law operation.\n"
        "Serializer union/equality calls are excluded from these scoped counters.\n"
        "reference_relation_classifications=0 and union_assignment_checks=0: C11\n"
        "constructs directly, not via the independent reference search.\n"
        "inner_predicate_record_tests=null: unavailable instrumentation, not zero.\n\n"
        "Operational errors: MALFORMED_REQUEST, UNSUPPORTED_VERSION,\n"
        "INVALID_REQUEST_ID, UNSUPPORTED_OPERATION, UNSUPPORTED_SUITE,\n"
        "UNSUPPORTED_FIXTURE, UNSUPPORTED_FIXTURE_FOR_SUITE, INVALID_VARIANT_RANK,\n"
        "VARIANT_RANK_OVERFLOW, FRAME_TOO_LONG, TRUNCATED_REQUEST,\n"
        "UNSUPPORTED_ARGUMENTS. Later complete valid requests continue safely.\n"
        "INPUT_ERROR emits a fatal response if possible; INTERNAL_EVALUATOR_ERROR\n"
        "is fatal, with partial-work marker. EVALUATED includes scientific invalid,\n"
        "negative and inconclusive fixtures, distinct from transport rejection.\n"
        "Exit: 0 clean EOF with all requests evaluated; 2 any rejected request/\n"
        "argument; 1 setup/read/write/internal/ordinal failure. EINTR read retries;\n"
        "SIGPIPE ignored in main. Write/flush failure stops immediately, no more\n"
        "reads or stdout diagnostics. Forced termination may leave a partial line;\n"
        "require LF and process status. No request preempts an unfinished frame.\n"
        "--help is sole text-output mode. Same streams on restart give same bytes;\n"
        "in-process replay changes only request_index/response_id.\n\n"
        "Limitations/unsupported: matrix_star_s_free, matrix_f09_s_inc, arbitrary\n"
        "input/geometry/policies, composed suites, orchestration, ledgers, hashing\n"
        "local artifacts/executables, durable evidence, timeouts and campaign\n"
        "qualification. Hash fields are DECLARED build identities, not runtime\n"
        "verification; the later orchestrator must verify/bind all artifacts,\n"
        "compiler and binary. All twelve non-matrix suites are selectable, but\n"
        "selectability and bounded checks discharge no full-campaign obligation.\n"
        "EXP007_STATUS=INCONCLUSIVE; CAMPAIGN_EXECUTED=NO by this adapter.\n"
        "EXP004 historical completeness=INCONCLUSIVE, material equivalence=\n"
        "CALLER_ASSUMPTION. Provenance truth remains assumed.\n"
    };
    size_t i;
    for (i = 0; i < HA_LENGTH(paragraphs); ++i) fputs(paragraphs[i], stdout);
    return fflush(stdout) == 0 && !ferror(stdout) ? 0 : 1;
}

/* -1 fatal; 0 evaluated; 1 safely rejected. */
static int ca_frame(char *line, size_t length, const char *framing_error, uint64_t ordinal)
{
    CaRequest r = {0};
    CaCase c = {0};
    const char *error = framing_error;
    if (error == NULL) error = ca_parse(line, length, &r);
    else if (!ha_equal(error, "FRAME_TOO_LONG")) ca_identity(line, length, &r);
    if (error != NULL) return ca_response(ordinal, &r, error, NULL) ? 1 : -1;
    if (!ca_run(&r, &c)) {
        (void)ca_response(ordinal, &r, "INTERNAL_EVALUATOR_ERROR", &c);
        return -1;
    }
    return ca_response(ordinal, &r, NULL, &c) ? 0 : -1;
}

int main(int argc, char **argv)
{
    static char output_buffer[32768];
    char incoming[4096], line[CA_FRAME + 1];
    size_t length = 0;
    uint64_t ordinal = 0;
    bool oversized = false, rejected = false;
    (void)ha_cli; /* Retain the immutable include-only CLI without invoking it. */
    if (setvbuf(stdout, output_buffer, _IOFBF, sizeof(output_buffer)) != 0) return 1;
#ifdef SIGPIPE
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) return 1;
#endif
    if (argc == 2 && ha_equal(argv[1], "--help")) return ca_help();
    if (argc != 1) {
        CaRequest r = {0};
        return ca_response(1, &r, "UNSUPPORTED_ARGUMENTS", NULL) ? 2 : 1;
    }
    for (;;) {
        ssize_t count;
        size_t i;
        count = read(STDIN_FILENO, incoming, sizeof(incoming));
        if (count < 0) {
            if (errno == EINTR) continue;
            if (ordinal == UINT64_MAX) return 1;
            (void)ca_frame(line, oversized ? 0 : length, "INPUT_ERROR", ++ordinal);
            return 1;
        }
        if (count == 0) {
            if (length != 0 || oversized) {
                if (ordinal == UINT64_MAX) return 1;
                if (ca_frame(line, length, oversized ? "FRAME_TOO_LONG" : "TRUNCATED_REQUEST",
                             ++ordinal) < 0) return 1;
                rejected = true;
            }
            return rejected ? 2 : 0;
        }
        for (i = 0; i < (size_t)count; ++i) {
            if (incoming[i] == '\n') {
                int result;
                if (ordinal == UINT64_MAX) return 1;
                result = ca_frame(line, length, oversized ? "FRAME_TOO_LONG" : NULL, ++ordinal);
                if (result < 0) return 1;
                if (result > 0) rejected = true;
                length = 0; oversized = false;
            } else if (length < CA_FRAME) line[length++] = incoming[i];
            else oversized = true;
        }
    }
}
