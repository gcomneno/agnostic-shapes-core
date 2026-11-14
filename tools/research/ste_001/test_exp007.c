/*
 * EXP-007 bounded focused checks; C self-test and separate CLI comparison driver.
 * Build from the repository root, with all products outside the repository:
 *   cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 \
 *      tools/research/ste_001/test_exp007.c -o /tmp/test_exp007
 *   /tmp/test_exp007 --self-test
 *
 * No arguments or --self-test runs the focused C checks. Other ordinary
 * arguments use the component's named-fixture CLI. --cli-test-script emits the
 * standard-library Python process regression driver stored below (no oracle
 * imports, no generated repository files). Run from the repository root:
 *   cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 \
 *      tools/research/ste_001/historical_associations.c -o /tmp/exp007-cli
 *   /tmp/test_exp007 --cli-test-script | python3 -B - /tmp/exp007-cli
 * To also run the 54 isolated worker configurations and persistent recovery:
 *   cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 \
 *      tools/research/ste_001/exp007_campaign.c -o /tmp/exp007-campaign
 *   /tmp/test_exp007 --cli-test-script | python3 -B - /tmp/exp007-cli \
 *      tools/research/ste_001/exp007_reference.py /tmp/exp007-campaign
 * The optional worker path follows the existing optional reference path.
 * Omitting it preserves the focused CLI driver and explicitly skips worker gates.
 * All test additions live here; the worker and reference remain unmodified.
 * Exit 0 is bounded success, 1 check/output failure, 2 unsupported arguments.
 * Scientific qualification remains separately INCONCLUSIVE.
 * Expectations below are test-only independent tables from protocol sections
 * 7 and 11. The component never reads this file or a fixture expected field.
 */
#include <stdio.h>
#define HA_NO_MAIN
#include "historical_associations.c"

static unsigned assertions, failures, completed_cases, inconclusive;
static unsigned certificates_completed;
enum { CERTIFICATES_REQUIRED = 2 };
static void gate(const char *name, unsigned before);

#define CHECK(condition) do { \
    ++assertions; \
    if (!(condition)) { \
        ++failures; \
        fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #condition); \
    } \
} while (0)

static const char *const codes[HA_CANDIDATES] = {
    "012", "021", "102", "120", "201", "210"
};

static HaSnapshot snapshot(bool right)
{
    HaSnapshot s = {0};
    size_t i;
    const char *const left[] = {"l0", "l1", "l2"};
    const char *const target[] = {"r0", "r1", "r2"};
    s.id = right ? "snapshot_R" : "snapshot_L";
    s.root = right ? "root_R" : "root_L";
    s.vertex_count = HA_VERTICES;
    s.occurrence_count = HA_N;
    s.edge_count = HA_N;
    s.vertices[0] = s.root;
    for (i = 0; i < HA_N; ++i) {
        s.vertices[i + 1] = s.occurrences[i] = right ? target[i] : left[i];
        s.edges[i] = (HaEdge){s.root, s.occurrences[i]};
    }
    return s;
}

static HaInput stars(void)
{
    HaInput in = {0};
    in.left = snapshot(false);
    in.right = snapshot(true);
    in.profile = HA_S_FREE;
    return in;
}

static void record(HaInput *in, const char *id, size_t left, size_t right,
                   HaPolarity polarity, HaAssessment assessment)
{
    HaRecord *r = &in->records[in->record_count++];
    *r = (HaRecord){0};
    r->id = id;
    r->source = in->left.occurrences[left];
    r->target = in->right.occurrences[right];
    r->polarity = polarity;
    r->assessment = assessment;
    r->provenance = (HaProvenance){
        "EXP-007 fixture declaration", "focused synthetic declaration",
        "Use the explicitly declared external assessment",
        "Assumed solely for the frozen finite model",
        {in->left.id, in->right.id}, r->source, r->target
    };
}

static HaInput candidate_fixture(unsigned number)
{
    HaInput in = stars();
    switch (number) {
    case 2: case 3: case 6: case 7: case 14:
        record(&in, "e1", 0, 0, HA_REQUIRE, HA_ACCEPTED);
        if (number == 3) record(&in, "e2", 1, 1, HA_REQUIRE, HA_ACCEPTED);
        if (number == 6) record(&in, "e2", 0, 1, HA_REQUIRE, HA_ACCEPTED);
        if (number == 7) record(&in, "e2", 0, 0, HA_EXCLUDE, HA_ACCEPTED);
        if (number == 14) record(&in, "e2", 1, 0, HA_REQUIRE, HA_ACCEPTED);
        break;
    case 4: record(&in, "e1", 0, 0, HA_EXCLUDE, HA_ACCEPTED); break;
    case 5: record(&in, "e1", 0, 0, HA_REQUIRE, HA_REJECTED); break;
    case 8:
        record(&in, "e1", 0, 0, HA_EXCLUDE, HA_ACCEPTED);
        record(&in, "e2", 0, 1, HA_EXCLUDE, HA_ACCEPTED);
        record(&in, "e3", 0, 2, HA_EXCLUDE, HA_ACCEPTED);
        break;
    case 9: case 10: case 11:
        in.left.edges[1].source = in.left.occurrences[0];
        in.right.edges[1].source = in.right.occurrences[number == 11 ? 2 : 0];
        if (number == 11) {
            record(&in, "a", 0, 0, HA_REQUIRE, HA_ACCEPTED);
            record(&in, "p", 1, 1, HA_REQUIRE, HA_ACCEPTED);
            record(&in, "q", 2, 2, HA_REQUIRE, HA_ACCEPTED);
        } else {
            in.profile = HA_S_INC;
            in.assumes_unchanged_incidence = true;
            if (number == 10) {
                record(&in, "e1", 0, 2, HA_REQUIRE, HA_ACCEPTED);
                record(&in, "e2", 1, 1, HA_REQUIRE, HA_ACCEPTED);
            }
        }
        break;
    case 12: record(&in, "e1", 0, 0, HA_REQUIRE, HA_UNRESOLVED); break;
    default: break;
    }
    return in;
}

/* Test encoding only. Actual matching compares complete concrete relations. */
static int association_code(const HaInput *in, const HaAssociation *phi)
{
    char encoding[HA_N + 1] = {0};
    size_t i;
    for (i = 0; i < HA_N; ++i) {
        int index = ha_find(in->right.occurrences, HA_N, phi->destination[i]);
        if (index < 0) return -1;
        encoding[i] = (char)('0' + index);
    }
    for (i = 0; i < HA_CANDIDATES; ++i)
        if (strcmp(encoding, codes[i]) == 0) return (int)i;
    return -1;
}

static void exact_candidates(const HaInput *in, unsigned evidence,
                              unsigned admissible, unsigned diagnostics)
{
    HaCandidates got = ha_evaluate(in);
    unsigned seen = 0, got_e = 0, got_a = 0;
    size_t i, e_count = 0, a_count = 0;
    CHECK(got.supported);
    CHECK(got.reason == NULL);
    CHECK(got.universe_count == HA_CANDIDATES);
    CHECK(got.diagnostics == diagnostics);
    for (i = 0; i < got.universe_count; ++i) {
        int code = association_code(in, &got.universe[i]);
        unsigned bit;
        CHECK(code >= 0);
        if (code < 0) continue;
        bit = 1u << (unsigned)code;
        CHECK((seen & bit) == 0);
        seen |= bit;
        if (got.evidence[i]) { got_e |= bit; ++e_count; }
        if (got.evidence[i] && got.structure[i]) { got_a |= bit; ++a_count; }
    }
    CHECK(seen == 63u);
    CHECK(got_e == evidence);
    CHECK(got_a == admissible);
    CHECK(got.evidence_count == e_count);
    CHECK(got.admissible_count == a_count);
    CHECK(got.conditional == ((diagnostics & HA_ASSESSMENT_UNRESOLVED) != 0));
    ++completed_cases;
}

static void invalid(const HaInput *in, const char *reason)
{
    HaCandidates got = ha_evaluate(in);
    CHECK(!got.supported);
    CHECK(got.reason != NULL);
    if (reason != NULL) {
        if (!ha_equal(got.reason, reason))
            fprintf(stderr, "diagnostic mismatch: expected %s; received %s\n",
                    reason, got.reason != NULL ? got.reason : "NULL");
        CHECK(ha_equal(got.reason, reason));
    }
    CHECK(got.diagnostics == HA_INVALID_INPUT);
    CHECK(got.universe_count == 0);
    CHECK(got.evidence_count == 0);
    CHECK(got.admissible_count == 0);
    CHECK(!got.conditional);
    ++completed_cases;
}

static void named_candidates(void)
{
    static const struct {
        unsigned fixture, evidence, admissible, diagnostics;
    } expected[] = {
        {1, 63, 63, HA_MISSING_EVIDENCE}, {2, 3, 3, 0}, {3, 1, 1, 0},
        {4, 60, 60, 0}, {5, 63, 63, 0}, {6, 0, 0, HA_EVIDENCE_INCONSISTENT},
        {7, 0, 0, HA_EVIDENCE_INCONSISTENT}, {8, 0, 0, HA_EVIDENCE_INCONSISTENT},
        {9, 63, 1, HA_MISSING_EVIDENCE}, {10, 32, 0, HA_STRUCTURALLY_UNSATISFIABLE},
        {11, 1, 1, 0}, {12, 63, 63, HA_ASSESSMENT_UNRESOLVED},
        {14, 0, 0, HA_EVIDENCE_INCONSISTENT}
    };
    size_t i;
    for (i = 0; i < sizeof expected / sizeof expected[0]; ++i) {
        HaInput in = candidate_fixture(expected[i].fixture);
        HaCandidates got;
        exact_candidates(&in, expected[i].evidence, expected[i].admissible,
                          expected[i].diagnostics);
        got = ha_evaluate(&in);
        CHECK(got.assessment_counts[HA_ACCEPTED] ==
              (expected[i].fixture == 5 || expected[i].fixture == 12 ? 0u : in.record_count));
        CHECK(got.assessment_counts[HA_REJECTED] == (expected[i].fixture == 5 ? 1u : 0u));
        CHECK(got.assessment_counts[HA_UNRESOLVED] == (expected[i].fixture == 12 ? 1u : 0u));
    }
    {
        HaInput in = candidate_fixture(12);
        in.records[0].assessment = HA_ACCEPTED;
        exact_candidates(&in, 3, 3, 0);
        in.records[0].assessment = HA_REJECTED;
        exact_candidates(&in, 63, 63, 0);
    }
    /* R04 control: the historical MOVE is supported by S_free; under the
     * separately authorized S_inc its identity is structurally impossible. */
    {
        HaInput in = candidate_fixture(11);
        in.profile = HA_S_INC;
        in.assumes_unchanged_incidence = true;
        exact_candidates(&in, 1, 0, HA_STRUCTURALLY_UNSATISFIABLE);
        in.record_count = 0;
        exact_candidates(&in, 63, 32, HA_MISSING_EVIDENCE);
    }
}

static void malformed_candidates(void)
{
    HaInput in = stars();
    in.left.vertices[2] = in.left.vertices[1];
    invalid(&in, "duplicated vertex handle");
    in = stars();
    record(&in, "foreign", 0, 0, HA_REQUIRE, HA_ACCEPTED);
    in.records[0].source = "l_foreign";
    invalid(&in, "foreign evidence handle");
    in = stars();
    in.left.edges[0] = (HaEdge){"root_L", "l2"};
    in.left.edges[1] = (HaEdge){"l0", "l1"};
    in.left.edges[2] = (HaEdge){"l1", "l0"};
    invalid(&in, "snapshot is not a rooted tree: unreachable/cyclic vertices");
    in = stars();
    in.left.root = "outside";
    invalid(&in, "invalid designated root");
    in = candidate_fixture(2);
    in.records[0].polarity = (HaPolarity)99;
    invalid(&in, "unsupported evidence polarity");
    in = candidate_fixture(2);
    in.records[0].assessment = (HaAssessment)-1;
    invalid(&in, "unsupported assessment status");
    in = candidate_fixture(2);
    in.records[0].provenance.assessment_rule = "";
    invalid(&in, "synthetic provenance and trust assumptions required");
    in = candidate_fixture(2);
    in.records[0].provenance.assumed_trust = NULL;
    invalid(&in, "synthetic provenance and trust assumptions required");
    in = candidate_fixture(2);
    in.records[0].provenance.scope_target = "r1";
    invalid(&in, "provenance scope must follow concrete selectors");
    in = candidate_fixture(2);
    in.records[0].provenance.snapshots[0] = "snapshot_R";
    invalid(&in, "provenance scope must follow concrete selectors");
    in = candidate_fixture(2);
    in.records[1] = in.records[0];
    in.records[1].assessment = HA_REJECTED;
    in.record_count = 2;
    invalid(&in, "same evidence ID has contradictory presentations");
    in = stars();
    in.right.vertices[1] = "l0";
    in.right.occurrences[0] = "l0";
    in.right.edges[0].target = "l0";
    invalid(&in, "cross-snapshot duplicate handle");
    in = stars();
    in.profile = HA_S_INC;
    invalid(&in, "S_inc requires explicit authorization");
    in = stars();
    in.left.edges[1] = in.left.edges[0];
    invalid(&in, "duplicate incidence");
    in = stars();
    in.left.edges[1].source = "l1";
    invalid(&in, "foreign vertex or self incidence");
    in = stars();
    in.left.edges[1].source = "l0";
    in.left.edges[1].target = "root_L";
    invalid(&in, "invalid tree parent occupancy");
    in = stars();
    in.left.occurrence_count = 4;
    invalid(&in, "exactly three distinct non-root occurrences required");
    in = stars();
    in.record_count = HA_RECORDS + 1;
    invalid(&in, "evidence outside bounded record domain");
}

/* Only a focused subset of presentation transformations, not the frozen
 * exhaustive order/layout/renaming suites. Concrete handles stay unchanged. */
static void presentation_probes(void)
{
    HaInput in = candidate_fixture(11);
    HaRecord swap;
    const char *handle;
    size_t i;
    swap = in.records[0]; in.records[0] = in.records[2]; in.records[2] = swap;
    exact_candidates(&in, 1, 1, 0);
    for (i = in.record_count; i > 0; --i) {
        in.records[2 * (i - 1)] = in.records[i - 1];
        in.records[2 * (i - 1) + 1] = in.records[i - 1];
    }
    in.record_count *= 2;
    exact_candidates(&in, 1, 1, 0);
    in = candidate_fixture(9);
    handle = in.left.vertices[0]; in.left.vertices[0] = in.left.vertices[3];
    in.left.vertices[3] = handle;
    handle = in.right.vertices[0]; in.right.vertices[0] = in.right.vertices[2];
    in.right.vertices[2] = handle;
    exact_candidates(&in, 63, 1, HA_MISSING_EVIDENCE);
    in = candidate_fixture(2);
    in.records[0].assessment = HA_UNRESOLVED;
    record(&in, "inconsistent1", 1, 0, HA_REQUIRE, HA_ACCEPTED);
    record(&in, "inconsistent2", 2, 0, HA_REQUIRE, HA_ACCEPTED);
    exact_candidates(&in, 0, 0, HA_ASSESSMENT_UNRESOLVED | HA_EVIDENCE_INCONSISTENT);
}

static HaMaterial material_fixture(unsigned number)
{
    HaMaterial m = {0};
    m.policy_complete = true;
    m.observable_defined = true;
    m.decision_count = 1;
    m.decisions[0].id = "strict";
    m.decisions[0].authorization = "All updates mandatory; no intention loss authorized.";
    if (number != 2) {
        m.updates[m.update_count++] = (HaUpdate){
            "left_lambda", "l0", HA_LEFT, HA_LAMBDA, true
        };
    }
    if (number != 1) {
        m.updates[m.update_count++] = (HaUpdate){
            "right_rho", "r0", HA_RIGHT, HA_RHO, true
        };
    }
    m.decisions[0].retained_count = m.update_count;
    m.decisions[0].retained[0] = m.updates[0].id;
    if (m.update_count == 2) m.decisions[0].retained[1] = m.updates[1].id;
    if (number == 4) {
        m.decision_count = 2;
        m.decisions[0] = (HaDecision){"d_lambda",
            "M04 explicitly authorizes waiving rho while retaining lambda.",
            1, 1, {"left_lambda", NULL}, {"right_rho", NULL}};
        m.decisions[1] = (HaDecision){"d_rho",
            "M04 explicitly authorizes waiving lambda while retaining rho.",
            1, 1, {"right_rho", NULL}, {"left_lambda", NULL}};
    }
    return m;
}

static HaInput identity_stars(void)
{
    HaInput in = stars();
    record(&in, "i0", 0, 0, HA_REQUIRE, HA_ACCEPTED);
    record(&in, "i1", 1, 1, HA_REQUIRE, HA_ACCEPTED);
    record(&in, "i2", 2, 2, HA_REQUIRE, HA_ACCEPTED);
    return in;
}

static bool witness_valid(const HaInput *in, const HaConstruction *c)
{
    size_t i;
    if (!c->supported || !c->equalities_consistent) return false;
    for (i = 0; i < c->obligation_count; ++i) {
        int target = ha_find(in->left.occurrences, HA_N, c->obligations[i].target);
        if (target < 0 || c->values[target] != c->obligations[i].value) return false;
    }
    return true;
}

/* Independent test checks: cardinality, range and pairwise distinctness prove
 * coverage of V^L. No dependence on row order or production's ternary coding. */
static bool certificate_covers_domain(const HaRejectionCertificate *certificate)
{
    size_t i, j, k;
    if (certificate->row_count != 27) return false;
    for (i = 0; i < certificate->row_count; ++i) {
        for (k = 0; k < HA_N; ++k)
            if (certificate->rows[i].values[k] < HA_ZERO ||
                certificate->rows[i].values[k] > HA_RHO) return false;
        for (j = 0; j < i; ++j) {
            bool same = true;
            for (k = 0; k < HA_N; ++k)
                if (certificate->rows[i].values[k] != certificate->rows[j].values[k])
                    same = false;
            if (same) return false;
        }
    }
    return true;
}

static size_t mentions(const HaRejectionRow *row, const char *kind, const char *key)
{
    size_t i, count = 0;
    for (i = 0; i < row->violated_count; ++i)
        if (ha_equal(row->violated[i].kind, kind) && ha_equal(row->violated[i].key, key))
            ++count;
    return count;
}

/* Evaluate declared equalities and frame rules in each supplied row, without
 * reading construction.obligations or calling the material solver. This is a
 * certificate check, not a material decision algorithm or a Python oracle port. */
static bool declared_certificate_valid(const HaInput *in, const HaAssociation *phi,
                                       const HaMaterial *m, size_t decision,
                                       const HaRejectionCertificate *certificate)
{
    const HaDecision *d;
    size_t i, source;
    if (!m->policy_complete || !m->observable_defined || decision >= m->decision_count ||
        !certificate_covers_domain(certificate)) return false;
    d = &m->decisions[decision];
    if (certificate->decision != d) return false;
    for (source = 0; source < HA_N; ++source)
        if (!ha_equal(certificate->sources[source], in->left.occurrences[source]) ||
            !ha_equal(certificate->association.destination[source], phi->destination[source]))
            return false;
    for (i = 0; i < certificate->row_count; ++i) {
        const HaRejectionRow *row = &certificate->rows[i];
        bool targeted[HA_N] = {false};
        size_t update, expected = 0;
        if (row->violated_count == 0 || row->violated_count > HA_OBLIGATIONS) return false;
        for (update = 0; update < m->update_count; ++update) {
            const HaUpdate *u = &m->updates[update];
            bool violated = false;
            if (ha_find(d->retained, d->retained_count, u->id) < 0) continue;
            for (source = 0; source < HA_N; ++source) {
                const char *selector = u->side == HA_LEFT ?
                    in->left.occurrences[source] : phi->destination[source];
                if (ha_equal(selector, u->target)) {
                    targeted[source] = true;
                    violated = row->values[source] != u->value;
                }
            }
            if (mentions(row, "update", u->id) != (violated ? 1u : 0u)) return false;
            if (violated) ++expected;
        }
        for (source = 0; source < HA_N; ++source) {
            bool violated = !targeted[source] && row->values[source] != HA_ZERO;
            if (mentions(row, "preserve", in->left.occurrences[source]) !=
                (violated ? 1u : 0u)) return false;
            if (violated) ++expected;
        }
        if (expected == 0 || expected != row->violated_count) return false;
    }
    return true;
}

static void invalid_certificate(const HaInput *in, const HaAssociation *phi,
                                 const HaMaterial *m, size_t decision,
                                 const HaRejectionCertificate *certificate)
{
    CHECK(!declared_certificate_valid(in, phi, m, decision, certificate));
    CHECK(!ha_certificate_valid(in, phi, m, decision, certificate));
}

static void rejection_certificates(void)
{
    HaInput in = stars();
    HaMaterial m = material_fixture(3);
    HaMaterials got = ha_material_evaluate(&in, &m);
    HaRejectionCertificate bad;
    const HaAlternative *a = &got.alternatives[0];
    unsigned before = failures;
    size_t i;
    CHECK(got.alternative_count == 6);
    CHECK(got.certificates_required == 2 && got.certificates_completed == 2);
    for (i = 0; i < 2; ++i) {
        const HaAlternative *rejected = &got.alternatives[i];
        CHECK(association_code(&in, &rejected->association) == (int)i);
        CHECK(certificate_covers_domain(&rejected->rejection));
    }
    bad = a->rejection;
    --bad.row_count;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    ++bad.row_count;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[26] = bad.rows[0]; /* 27 rows, one duplicate and one missing map. */
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[0].values[0] = (HaValue)3;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[0].values[0] = (HaValue)-1;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    /* The proof is a set of rows, not a specific presentation order. */
    bad = a->rejection;
    for (i = 0; i < 13; ++i) {
        HaRejectionRow swap = bad.rows[i];
        bad.rows[i] = bad.rows[26 - i]; bad.rows[26 - i] = swap;
    }
    CHECK(declared_certificate_valid(&in, &a->association, &m, 0, &bad));
    CHECK(ha_certificate_valid(&in, &a->association, &m, 0, &bad));
    gate("CERTIFICATE_COVERAGE_GATE", before);

    before = failures;
    for (i = 0; i < 2; ++i) {
        const HaAlternative *rejected = &got.alternatives[i];
        bool valid = declared_certificate_valid(&in, &rejected->association,
                                                &m, 0, &rejected->rejection);
        CHECK(valid);
        CHECK(ha_certificate_valid(&in, &rejected->association, &m, 0,
                                   &rejected->rejection));
        if (valid && rejected->rejection_certified) ++certificates_completed;
    }
    /* Frozen M03 obligations: conflicting updates at l0, preserve l1 and l2.
     * Explicit examples ensure preservation is checked as well as equality. */
    CHECK(mentions(&a->rejection.rows[0], "update", "left_lambda") == 1);
    CHECK(mentions(&a->rejection.rows[0], "update", "right_rho") == 1);
    CHECK(a->rejection.rows[0].violated_count == 2); /* (0,0,0) */
    CHECK(mentions(&a->rejection.rows[13], "update", "left_lambda") == 0);
    CHECK(mentions(&a->rejection.rows[13], "update", "right_rho") == 1);
    CHECK(mentions(&a->rejection.rows[13], "preserve", "l1") == 1);
    CHECK(mentions(&a->rejection.rows[13], "preserve", "l2") == 1);
    CHECK(a->rejection.rows[13].violated_count == 3); /* (lambda,lambda,lambda) */
    bad = a->rejection;
    bad.rows[0].violated_count = 0;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    --bad.rows[0].violated_count; /* Omitted mandatory equality. */
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[0].violated[1] = bad.rows[0].violated[0];
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[0].violated[0] = (HaConjunctId){"preserve", "l1"}; /* Satisfied. */
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[0].violated[0] = (HaConjunctId){"update", "undeclared"};
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[0].violated[0].kind = "unknown";
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    --bad.rows[13].violated_count; /* Omitted zero-preservation obligation. */
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.rows[0].violated_count = HA_OBLIGATIONS + 1;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.sources[0] = "foreign";
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.association = got.alternatives[1].association;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    bad = a->rejection;
    bad.decision = NULL;
    invalid_certificate(&in, &a->association, &m, 0, &bad);
    /* A certificate cannot turn an accepting association into a rejection. */
    bad = a->rejection;
    bad.association = got.alternatives[2].association;
    invalid_certificate(&in, &got.alternatives[2].association, &m, 0, &bad);
    gate("CERTIFICATE_CONJUNCT_GATE", before);
    ++completed_cases;
}

static void named_materials(void)
{
    /* Exact complete material maps from the frozen table; construction code
     * never consults them. -1 denotes a required certified rejection. */
    static const int expected[3][HA_CANDIDATES][HA_N] = {
        {{1,0,0},{1,0,0},{1,0,0},{1,0,0},{1,0,0},{1,0,0}},
        {{2,0,0},{2,0,0},{0,2,0},{0,0,2},{0,2,0},{0,0,2}},
        {{-1,-1,-1},{-1,-1,-1},{1,2,0},{1,0,2},{1,2,0},{1,0,2}}
    };
    unsigned number;
    for (number = 1; number <= 3; ++number) {
        unsigned before = failures;
        HaInput in = stars();
        HaMaterial m = material_fixture(number);
        HaMaterials got = ha_material_evaluate(&in, &m);
        unsigned seen = 0;
        size_t i;
        CHECK(got.policy_supported && got.observable_defined);
        CHECK(got.alternative_count == 6);
        CHECK(got.witness_count == (number == 3 ? 4u : 6u));
        CHECK(got.uncertified_count == 0);
        CHECK(got.partition_complete);
        CHECK(got.class_count == (number == 1 ? 1u : 3u));
        CHECK(got.certificates_required == (number == 3 ? 2u : 0u));
        CHECK(got.certificates_completed == got.certificates_required);
        CHECK(got.rejected_association_count == (number == 3 ? 2u : 0u));
        for (i = 0; i < got.alternative_count; ++i) {
            const HaConstruction *c = &got.alternatives[i].construction;
            int code = association_code(&in, &got.alternatives[i].association);
            size_t cell;
            CHECK(code >= 0);
            if (code < 0) continue;
            CHECK((seen & (1u << (unsigned)code)) == 0);
            seen |= 1u << (unsigned)code;
            CHECK(c->supported);
            CHECK(ha_equal(c->decision->id, "strict"));
            CHECK(c->decision->waived_count == 0);
            CHECK(c->decision->retained_count == m.update_count);
            CHECK(c->equalities_consistent == (expected[number - 1][code][0] >= 0));
            if (expected[number - 1][code][0] < 0) {
                CHECK(!witness_valid(&in, c));
                CHECK(got.alternatives[i].rejection_certified);
                CHECK(got.rejected_under_all_decisions[code]);
                CHECK(got.alternatives[i].rejection.row_count == HA_ASSIGNMENTS);
                continue;
            }
            CHECK(!got.alternatives[i].rejection_certified);
            CHECK(got.alternatives[i].rejection.row_count == 0);
            CHECK(!got.rejected_under_all_decisions[code]);
            CHECK(witness_valid(&in, c));
            for (cell = 0; cell < HA_N; ++cell)
                CHECK((int)c->values[cell] == expected[number - 1][code][cell]);
        }
        CHECK(seen == 63u);
        if (number == 3) {
            CHECK(got.class_of[0] == got.class_of[1]);
            CHECK(got.class_of[2] == got.class_of[4]);
            CHECK(got.class_of[3] == got.class_of[5]);
            CHECK(got.class_of[0] != got.class_of[2]);
            CHECK(got.class_of[0] != got.class_of[3]);
            CHECK(got.class_of[2] != got.class_of[3]);
            gate("M03_REJECTION_GATE", before);
        }
        ++completed_cases;
    }
    {
        unsigned before = failures;
        HaInput in = identity_stars();
        HaMaterial m = material_fixture(4);
        HaMaterials got = ha_material_evaluate(&in, &m);
        unsigned decisions_seen = 0;
        size_t i;
        CHECK(got.policy_supported && got.partition_complete);
        CHECK(got.alternative_count == 2 && got.witness_count == 2);
        CHECK(got.class_count == 2 && got.uncertified_count == 0);
        CHECK(got.certificates_required == 0 && got.certificates_completed == 0);
        CHECK(got.rejected_association_count == 0);
        for (i = 0; i < got.alternative_count; ++i) {
            const HaConstruction *c = &got.alternatives[i].construction;
            CHECK(association_code(&in, &got.alternatives[i].association) == 0);
            CHECK(witness_valid(&in, c));
            CHECK(!got.alternatives[i].rejection_certified);
            CHECK(got.alternatives[i].rejection.row_count == 0);
            CHECK(c->decision->retained_count == 1 && c->decision->waived_count == 1);
            CHECK(c->obligation_count == 3);
            CHECK(c->values[1] == HA_ZERO && c->values[2] == HA_ZERO);
            if (ha_equal(c->decision->id, "d_lambda")) {
                CHECK((decisions_seen & 1u) == 0); decisions_seen |= 1u;
                CHECK(c->values[0] == HA_LAMBDA);
                CHECK(ha_equal(c->decision->retained[0], "left_lambda"));
                CHECK(ha_equal(c->decision->waived[0], "right_rho"));
            } else {
                CHECK(ha_equal(c->decision->id, "d_rho"));
                CHECK((decisions_seen & 2u) == 0); decisions_seen |= 2u;
                CHECK(c->values[0] == HA_RHO);
                CHECK(ha_equal(c->decision->retained[0], "right_rho"));
                CHECK(ha_equal(c->decision->waived[0], "left_lambda"));
            }
        }
        CHECK(decisions_seen == 3);
        /* Reverse declared decisions: the complete observable maps survive. */
        {
            HaDecision swap = m.decisions[0];
            m.decisions[0] = m.decisions[1]; m.decisions[1] = swap;
            got = ha_material_evaluate(&in, &m);
            CHECK(got.alternative_count == 2 && got.class_count == 2);
            CHECK(got.alternatives[0].construction.values[0] == HA_RHO);
            CHECK(got.alternatives[1].construction.values[0] == HA_LAMBDA);
            CHECK(got.certificates_required == 0 && got.rejected_association_count == 0);
        }
        gate("M04_PRESERVATION_GATE", before);
        ++completed_cases;
    }
}

static void material_boundaries(void)
{
    HaInput in = identity_stars();
    HaMaterial m = material_fixture(4);
    HaMaterials got;
    m.policy_complete = false;
    got = ha_material_evaluate(&in, &m);
    CHECK(!got.policy_supported && !got.partition_complete);
    CHECK(got.alternative_count == 0 && got.witness_count == 0);
    CHECK(got.certificates_required == 0 && got.certificates_completed == 0);
    CHECK(got.rejected_association_count == 0);
    CHECK(ha_equal(got.reason, "required complete retention/loss policy is absent"));
    ++inconclusive; ++completed_cases;
    in = stars(); m = material_fixture(1); m.observable_defined = false;
    got = ha_material_evaluate(&in, &m);
    CHECK(got.policy_supported && !got.observable_defined && !got.partition_complete);
    CHECK(got.witness_count == 6 && got.alternative_count == 6 && got.class_count == 0);
    CHECK(got.certificates_completed == 0 && got.rejected_association_count == 0);
    ++inconclusive; ++completed_cases;
    m = material_fixture(1); m.independent_comparison_complete = false;
    got = ha_material_evaluate(&in, &m);
    CHECK(got.policy_supported && got.partition_complete && got.class_count == 1);
    CHECK(got.witness_count == 6);
    ++inconclusive; ++completed_cases;
    m = material_fixture(1); m.updates[0].target = "root_L";
    CHECK(ha_equal(ha_validate_material(&in, &m), "foreign material selector"));
    m = material_fixture(1); m.updates[0].mandatory = false;
    CHECK(ha_validate_material(&in, &m) != NULL);
    m = material_fixture(1); m.updates[0].value = (HaValue)99;
    CHECK(ha_validate_material(&in, &m) != NULL);
    m = material_fixture(1); m.decisions[0].retained_count = 0;
    CHECK(ha_validate_material(&in, &m) != NULL);
    m = material_fixture(1); m.decisions[0].authorization = "";
    CHECK(ha_validate_material(&in, &m) != NULL);
    m = material_fixture(4); m.decisions[0].waived[0] = "left_lambda";
    CHECK(ha_validate_material(&in, &m) != NULL);
    m = material_fixture(1); m.initial[HA_RIGHT][2] = HA_RHO;
    CHECK(ha_validate_material(&in, &m) != NULL);
    /* Equal values targeting the same cell remain satisfiable; zero writes
     * are updates, and do not turn into preservation or unauthorized losses. */
    m = material_fixture(3); m.updates[1].value = HA_LAMBDA;
    {
        HaCandidates c = ha_evaluate(&in);
        HaConstruction result = ha_construct(&in, &c.universe[0], &m, 0);
        CHECK(witness_valid(&in, &result));
        CHECK(result.obligation_count == 4);
        CHECK(result.values[0] == HA_LAMBDA);
        m.updates[0].value = m.updates[1].value = HA_ZERO;
        result = ha_construct(&in, &c.universe[0], &m, 0);
        CHECK(witness_valid(&in, &result));
        CHECK(result.values[0] == HA_ZERO && result.obligation_count == 4);
        c.universe[0].destination[1] = "r0";
        result = ha_construct(&in, &c.universe[0], &m, 0);
        CHECK(!result.supported && ha_equal(result.reason, "association is not bijective"));
    }
    ++completed_cases;
}

/* Focused API boundary probes, not extra frozen fixtures or a campaign.
 * In particular, a rejected decision must not erase an accepting alternative. */
static void certificate_policy_probes(void)
{
    HaInput in = identity_stars();
    HaMaterial m = material_fixture(3), authorized_losses = material_fixture(4);
    HaMaterials got;
    HaCandidates candidates = ha_evaluate(&in);
    HaConstruction direct = ha_construct(&in, &candidates.universe[0], &m, 0);
    HaRejectionCertificate certificate = {0};
    CHECK(direct.supported && !direct.equalities_consistent);
    CHECK(direct.obligation_count == 4);
    CHECK(ha_equal(direct.obligations[0].target, "l0") &&
          ha_equal(direct.obligations[1].target, "l0"));
    CHECK(direct.obligations[0].value == HA_LAMBDA &&
          direct.obligations[1].value == HA_RHO);
    ha_rejection_rows(&in, &candidates.universe[0], &direct, &certificate);
    CHECK(declared_certificate_valid(&in, &candidates.universe[0], &m, 0, &certificate));
    CHECK(ha_certificate_valid(&in, &candidates.universe[0], &m, 0, &certificate));

    m.decision_count = 2;
    m.decisions[1] = authorized_losses.decisions[0];
    got = ha_material_evaluate(&in, &m);
    CHECK(got.policy_supported && got.partition_complete);
    CHECK(got.alternative_count == 2 && got.witness_count == 1 && got.class_count == 2);
    CHECK(got.certificates_required == 1 && got.certificates_completed == 1);
    CHECK(got.uncertified_count == 0 && got.rejected_association_count == 0);
    CHECK(!got.rejected_under_all_decisions[0]);
    CHECK(got.alternatives[0].rejection_certified);
    CHECK(!got.alternatives[1].rejection_certified);
    CHECK(witness_valid(&in, &got.alternatives[1].construction));
    invalid_certificate(&in, &got.alternatives[0].association, &m, 1,
                        &got.alternatives[0].rejection);
    {
        HaDecision swap = m.decisions[0];
        m.decisions[0] = m.decisions[1]; m.decisions[1] = swap;
        got = ha_material_evaluate(&in, &m);
        CHECK(got.alternative_count == 2 && got.witness_count == 1 && got.class_count == 2);
        CHECK(got.certificates_completed == 1 && got.rejected_association_count == 0);
        CHECK(witness_valid(&in, &got.alternatives[0].construction));
        CHECK(got.alternatives[1].rejection_certified);
    }
    m.decisions[0] = m.decisions[1];
    m.decisions[1].id = "second_explicit_strict_decision";
    got = ha_material_evaluate(&in, &m);
    CHECK(got.alternative_count == 2 && got.witness_count == 0 && got.class_count == 1);
    CHECK(got.certificates_required == 2 && got.certificates_completed == 2);
    CHECK(got.rejected_association_count == 1 && got.rejected_under_all_decisions[0]);
    CHECK(declared_certificate_valid(&in, &got.alternatives[0].association, &m, 0,
                                     &got.alternatives[0].rejection));
    CHECK(declared_certificate_valid(&in, &got.alternatives[1].association, &m, 1,
                                     &got.alternatives[1].rejection));
    /* A policy with an unaccounted-for intention is unsupported, not REJECT. */
    m.decisions[1].retained_count = 1;
    got = ha_material_evaluate(&in, &m);
    CHECK(!got.policy_supported && got.alternative_count == 0);
    CHECK(got.certificates_completed == 0 && got.rejected_association_count == 0);

    m = material_fixture(1);
    direct = ha_construct(&in, &candidates.universe[0], &m, 0);
    ha_rejection_rows(&in, &candidates.universe[0], &direct, &certificate);
    CHECK(witness_valid(&in, &direct) && certificate.row_count == 0);
    m.policy_complete = false;
    direct = ha_construct(&in, &candidates.universe[0], &m, 0);
    ha_rejection_rows(&in, &candidates.universe[0], &direct, &certificate);
    CHECK(!direct.supported && certificate.row_count == 0);
    CHECK(!ha_certificate_valid(&in, &candidates.universe[0], &m, 0, &certificate));

    m = material_fixture(3); m.observable_defined = false;
    got = ha_material_evaluate(&in, &m);
    CHECK(got.policy_supported && !got.observable_defined && !got.partition_complete);
    CHECK(got.certificates_required == 1 && got.certificates_completed == 0);
    CHECK(got.uncertified_count == 1 && got.rejected_association_count == 0);
    CHECK(!got.alternatives[0].rejection_certified && got.class_count == 0);
    CHECK(got.alternatives[0].rejection.row_count == 0);
    CHECK(!ha_certificate_valid(&in, &candidates.universe[0], &m, 0, &certificate));

    /* Move the collision to l2 through inverse transport of r1 under 021.
     * This must change preservation IDs and targets, without hard-coding l0. */
    in = stars(); candidates = ha_evaluate(&in); m = material_fixture(3);
    m.updates[0].target = "l2";
    m.updates[1].target = "r1";
    direct = ha_construct(&in, &candidates.universe[1], &m, 0);
    CHECK(direct.supported && !direct.equalities_consistent);
    ha_rejection_rows(&in, &candidates.universe[1], &direct, &certificate);
    CHECK(declared_certificate_valid(&in, &candidates.universe[1], &m, 0, &certificate));
    CHECK(ha_certificate_valid(&in, &candidates.universe[1], &m, 0, &certificate));
    CHECK(mentions(&certificate.rows[13], "preserve", "l0") == 1);
    CHECK(mentions(&certificate.rows[13], "preserve", "l1") == 1);
    CHECK(mentions(&certificate.rows[13], "preserve", "l2") == 0);
    {
        HaUpdate swap = m.updates[0];
        m.updates[0] = m.updates[1]; m.updates[1] = swap;
        /* Stable conjunct IDs survive update-array reordering. */
        CHECK(declared_certificate_valid(&in, &candidates.universe[1], &m, 0, &certificate));
        CHECK(ha_certificate_valid(&in, &candidates.universe[1], &m, 0, &certificate));
    }
    ++completed_cases;
}

static void gate(const char *name, unsigned before)
{
    printf("%s=%s assertions=%u\n", name, failures == before ? "PASS" : "FAIL", assertions);
}

/* Emitted test driver, not runtime component logic. Python is used here only
 * for process/JSON assertions and the existing external comparison interface.
 * Every submitted C result is obtained before the first reference invocation.
 */
static int cli_test_script(void)
{
    static const char *const lines[] = {
        "\"\"\"Focused process tests, emitted by test_exp007 --cli-test-script.\n",
        "\n",
        "No oracle logic is imported. All C outputs are captured first, then the frozen\n",
        "reference CLI compares the submitted envelopes. Mutations exercise the existing\n",
        "comparison's ability to reject exact-set/record disagreements. No full campaign.\n",
        "\"\"\"\n",
        "import copy\n",
        "import itertools\n",
        "import json\n",
        "import os\n",
        "from pathlib import Path\n",
        "import subprocess\n",
        "import sys\n",
        "import tempfile\n",
        "\n",
        "binary = str(Path(sys.argv[1]).resolve())\n",
        "reference = str(Path(sys.argv[2] if len(sys.argv) > 2 else\n",
        "                     'tools/research/ste_001/exp007_reference.py').resolve())\n",
        "checks = 0\n",
        "process_counts = dict(c11=0, oracle=0)\n",
        "\n",
        "\n",
        "def check(condition, reason):\n",
        "    global checks\n",
        "    checks += 1\n",
        "    if not condition:\n",
        "        raise AssertionError(reason)\n",
        "\n",
        "\n",
        "def c_run(args):\n",
        "    process_counts['c11'] += 1\n",
        "    return subprocess.run([binary, *args], capture_output=True, text=True, check=False)\n",
        "\n",
        "\n",
        "def decoded(process):\n",
        "    check(process.returncode == 0, 'bounded CLI failure: ' + process.stderr)\n",
        "    check(process.stderr == '', 'unexpected stderr')\n",
        "    return json.loads(process.stdout)\n",
        "\n",
        "\n",
        "names = ([f'F{i:02}' for i in range(1, 15)] +\n",
        "         ['F12-ACCEPTED', 'F12-REJECTED', 'M04-association',\n",
        "          'M01', 'M02', 'M03', 'M04', 'M05'])\n",
        "# C generation precedes every use of the Python reference, including --list.\n",
        "batch_process = c_run(['--fixture', *names])\n",
        "batch = decoded(batch_process)\n",
        "repeated = c_run(['--fixture', *names])\n",
        "check(repeated.returncode == 0 and repeated.stderr == '' and\n",
        "      repeated.stdout == batch_process.stdout, 'nondeterministic repeated output')\n",
        "listed = decoded(c_run(['--list']))\n",
        "helped = c_run(['--help'])\n",
        "check(helped.returncode == 0 and helped.stderr == '' and 'Usage:' in helped.stdout,\n",
        "      'help contract')\n",
        "ids = [r['id'] for r in batch['results']]\n",
        "check(len(ids) == 27 and len(set(ids)) == 27, 'named variant coverage')\n",
        "check(set(listed['fixtures']) == set(ids) | {'F13', 'M05'}, 'list coverage')\n",
        "by_id = {r['id']: r for r in batch['results']}\n",
        "individuals = []\n",
        "for identifier in ids:\n",
        "    process = c_run(['--fixture', identifier])\n",
        "    result = decoded(process)\n",
        "    check(result['results'] == [by_id[identifier]], 'individual/batch disagreement: ' + identifier)\n",
        "    individuals.append((identifier, result))\n",
        "reverse = decoded(c_run(['--fixture', *reversed(ids)]))\n",
        "check({r['id']: r for r in reverse['results']} == by_id, 'selection order changed records')\n",
        "check(batch['schema'] == 'ste-exp007-reference-v1' and batch['protocol_sha256'] ==\n",
        "      '61a586c706cf5e3cfb78ffbfd835dcbdc060c4c46f6cc427fbf2379a095664f1', 'envelope identity')\n",
        "check(batch['qualification'] == 'NOT_QUALIFIED_PHASE_A', 'qualification overclaim')\n",
        "for result in batch['results']:\n",
        "    c = result['candidate']\n",
        "    if c['status'] == 'SUPPORTED':\n",
        "        check(c['relations_examined'] == 6, 'C11 must report its own generator work')\n",
        "        for key, relations in c['candidate_sets'].items():\n",
        "            encoded = [json.dumps(sorted(r)) for r in relations]\n",
        "            check(len(set(encoded)) == len(encoded), 'duplicate candidate in ' + key)\n",
        "            check(len(relations) == c['counts'][key], 'count/set disagreement')\n",
        "    else:\n",
        "        check(c['candidate_sets'] is None and c['counts'] is None and\n",
        "              c['predicates'] is None and c['evidence_records'] is None and\n",
        "              c['assessment_counts'] is None and c['conditional'] is None and\n",
        "              c['relations_examined'] == 0 and c['diagnostics'] == ['INVALID_INPUT'],\n",
        "              'invalid fixture was enumerated or repaired')\n",
        "    if 'material' in result:\n",
        "        check(result['material']['scientific_claim'] == 'INCONCLUSIVE', 'scientific overclaim')\n",
        "\n",
        "# Independently validate both M03 certificates, including frame conjuncts.\n",
        "certificates = 0\n",
        "for association in by_id['M03']['material']['associations']:\n",
        "    for d in association['decisions']:\n",
        "        cert = d['rejection_certificate']\n",
        "        if cert is None:\n",
        "            check(len(d['witnesses']) == 1 and d['outcomes'][0]['tag'] == 'ACCEPT',\n",
        "                  'accepting decision lost its witness')\n",
        "            continue\n",
        "        certificates += 1\n",
        "        check(association['rejected_under_all_decisions'] and d['outcomes'] == [{'tag': 'REJECT'}]\n",
        "              and d['W_phi_d'] == [] and d['witnesses'] == [], 'rejection representation')\n",
        "        expected_ids = {'update:left_lambda', 'update:right_rho', 'preserve:l1', 'preserve:l2'}\n",
        "        check({o['id'] for o in d['obligations']} == expected_ids, 'M03 conjunct identity')\n",
        "        check(len(cert) == 27 and {tuple(row['material'][s] for s in ('l0', 'l1', 'l2'))\n",
        "                                 for row in cert} == set(itertools.product(('0', 'lambda', 'rho'), repeat=3)),\n",
        "              'incomplete or repeated certificate maps')\n",
        "        for row in cert:\n",
        "            material = row['material']\n",
        "            expected = [key for key, target, value in\n",
        "                        [('update:left_lambda', 'l0', 'lambda'), ('update:right_rho', 'l0', 'rho'),\n",
        "                         ('preserve:l1', 'l1', '0'), ('preserve:l2', 'l2', '0')]\n",
        "                        if material[target] != value]\n",
        "            check(bool(expected) and sorted(row['violated']) == sorted(expected),\n",
        "                  'incorrect violated conjuncts')\n",
        "check(certificates == 2, 'both M03 certificates required')\n",
        "\n",
        "malformed = [[], ['--fixture'], ['--unknown'], ['--self-test'], ['--fi', 'F01'],\n",
        "             ['--fixture', ''], ['--fixture', 'F00'], ['--fixture', 'F1'],\n",
        "             ['--fixture', 'M06'], ['--fixture', 'F01', 'unknown'],\n",
        "             ['--fixture', 'F01', 'F01'], ['--fixture', 'F13', 'F13-invalid_tree'],\n",
        "             ['--fixture', 'M05-P', 'M05'], ['--fixture', 'M05', 'M05'],\n",
        "             ['--fixture', 'F01', '--list'], ['--list', 'F01'],\n",
        "             ['--manifest', '/tmp/unsupported'], ['--compare', '/tmp/unsupported'],\n",
        "             ['--fixture', 'F01', '--compare', '/tmp/unsupported'],\n",
        "             ['--fixture', '--', 'F01'], ['--fixture=F01'], ['--fixture', ' F01'],\n",
        "             ['--fixture', 'F01\\n'], ['--fixture', '\"\\\\\\n'],\n",
        "             ['--fixture', 'F01', '--fixture', 'F02'], ['--help', 'extra'],\n",
        "             ['--fixture', *(['F01'] * 65)]]\n",
        "for args in malformed:\n",
        "    process = c_run(args)\n",
        "    check(process.returncode == 2 and process.stdout == '', 'malformed request status/stdout')\n",
        "    error = json.loads(process.stderr)\n",
        "    check(error['status'] == 'UNSUPPORTED' and error['diagnostics'] == ['INVALID_INPUT'] and\n",
        "          isinstance(error['reason'], str) and bool(error['reason']) and\n",
        "          error['qualification'] == 'NOT_QUALIFIED_PHASE_A', 'malformed diagnostic')\n",
        "\n",
        "# A valid request whose output cannot be written has defined failure status.\n",
        "# /dev/full is available on the Linux test host; this creates no repository file.\n",
        "check(Path('/dev/full').exists(), 'output failure probe requires /dev/full')\n",
        "with open('/dev/full', 'w') as sink:\n",
        "    process_counts['c11'] += 1\n",
        "    failed_output = subprocess.run([binary, '--fixture', 'M03'], stdout=sink,\n",
        "                                   stderr=subprocess.PIPE, text=True, check=False)\n",
        "check(failed_output.returncode == 1 and\n",
        "      json.loads(failed_output.stderr)['diagnostics'] == ['SELF_CHECK_FAILED'] and\n",
        "      json.loads(failed_output.stderr)['reason'] == 'output write failed',\n",
        "      'output failure status/diagnostic')\n",
        "\n",
        "io_error = dict(status='FAIL', diagnostics=['SELF_CHECK_FAILED'],\n",
        "                reason='output write failed', qualification='NOT_QUALIFIED_PHASE_A')\n",
        "with open('/dev/full', 'w') as sink:\n",
        "    process_counts['c11'] += 1\n",
        "    failed_help = subprocess.run([binary, '--help'], stdout=sink,\n",
        "                                 stderr=subprocess.PIPE, text=True, check=False)\n",
        "check(failed_help.returncode == 1, 'help output failure status')\n",
        "check(json.loads(failed_help.stderr or 'null') == io_error, 'help output failure diagnostic')\n",
        "\n",
        "check(sys.platform.startswith('linux'), 'closed-pipe regression requires Linux')\n",
        "# Close the only reader BEFORE spawning: no scheduling race or pipe-size assumption.\n",
        "read_fd, write_fd = os.pipe()\n",
        "os.close(read_fd)\n",
        "try:\n",
        "    process_counts['c11'] += 1\n",
        "    # Restore SIGPIPE before exec; Python's inherited SIG_IGN must not hide the bug.\n",
        "    closed_pipe = subprocess.run([binary, '--fixture', 'M03'], stdout=write_fd,\n",
        "                                 stderr=subprocess.PIPE, text=True, check=False,\n",
        "                                 restore_signals=True, timeout=10)\n",
        "finally:\n",
        "    os.close(write_fd)\n",
        "check(closed_pipe.returncode == 1, 'closed pipe status (must not terminate through SIGPIPE)')\n",
        "check(json.loads(closed_pipe.stderr or 'null') == io_error, 'closed pipe diagnostic')\n",
        "print('HELP_WRITE_FAILURE_GATE=PASS process_status=' + str(failed_help.returncode))\n",
        "print('CLOSED_PIPE_GATE=PASS process_status=' + str(closed_pipe.returncode))\n",
        "print('EXISTING_IO_REGRESSION_GATE=PASS process_status=' + str(failed_output.returncode))\n",
        "\n",
        "# All submitted records above were independently produced before oracle use.\n",
        "def oracle(args):\n",
        "    process_counts['oracle'] += 1\n",
        "    return subprocess.run([sys.executable, '-B', reference, *args], capture_output=True,\n",
        "                          text=True, check=False)\n",
        "\n",
        "\n",
        "with tempfile.TemporaryDirectory(prefix='exp007-cli-', dir='/tmp') as directory:\n",
        "    path = Path(directory) / 'c11.json'\n",
        "\n",
        "    def compare(selection, submitted, expected_status):\n",
        "        path.write_text(json.dumps(submitted), encoding='utf-8')\n",
        "        process = oracle(['--fixture', *selection, '--compare', str(path)])\n",
        "        check(process.returncode == expected_status and process.stderr == '', 'comparison exit contract')\n",
        "        report = json.loads(process.stdout)['comparison']\n",
        "        check(report['status'] == ('PASS' if expected_status == 0 else 'FAIL'), 'comparison status')\n",
        "        return report\n",
        "\n",
        "    report = compare(names, batch, 0)\n",
        "    check(report['compared_fixtures'] == 27 and report['failures'] == [], 'exact named comparison')\n",
        "    for identifier, submitted in individuals:\n",
        "        compare([identifier], submitted, 0)\n",
        "    reference_list = decoded(oracle(['--list']))\n",
        "    check(set(reference_list['fixtures']) == set(listed['fixtures']), 'reference list disagreement')\n",
        "\n",
        "    # Each mutation starts with real C output, without recalculating it in Python.\n",
        "    mutations = []\n",
        "\n",
        "    def mutation(label, fixture, mutate, expected_kind='EXACT_RESULT_MISMATCH', required=None):\n",
        "        submitted = copy.deepcopy(batch)\n",
        "        result = next(r for r in submitted['results'] if r['id'] == fixture)\n",
        "        mutate(result)\n",
        "        mutations.append((label, submitted, expected_kind, required))\n",
        "\n",
        "    mutation('candidate false negative', 'F02',\n",
        "             lambda r: r['candidate']['candidate_sets']['C_E'].pop(), None, 'false_negatives')\n",
        "    mutation('candidate false positive', 'F02',\n",
        "             lambda r: r['candidate']['candidate_sets']['A_E'].append(\n",
        "                 copy.deepcopy(r['candidate']['candidate_sets']['U_H'][2])), None, 'false_positives')\n",
        "    mutation('candidate duplicate', 'F02',\n",
        "             lambda r: r['candidate']['candidate_sets']['U_H'].append(\n",
        "                 copy.deepcopy(r['candidate']['candidate_sets']['U_H'][0])), 'DUPLICATES')\n",
        "    mutation('relation orientation', 'F02',\n",
        "             lambda r: r['candidate']['candidate_sets']['A_E'][0][0].reverse())\n",
        "    mutation('diagnostic distinction', 'F10',\n",
        "             lambda r: r['candidate'].__setitem__('diagnostics', ['EVIDENCE_INCONSISTENT']))\n",
        "    mutation('assessment conditionality', 'F12',\n",
        "             lambda r: r['candidate'].__setitem__('conditional', False))\n",
        "    mutation('provenance orientation', 'F11',\n",
        "             lambda r: r['candidate']['evidence_records'][0]['provenance']['scope']['snapshots'].reverse())\n",
        "    mutation('M04 missing decision', 'M04',\n",
        "             lambda r: r['material']['associations'][0]['decisions'].pop(), 'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('M02 material map', 'M02',\n",
        "             lambda r: r['material']['associations'][0]['decisions'][0]['outcomes'][0]['material'].\n",
        "             __setitem__('l0', 'lambda'), 'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('M04 authorization', 'M04',\n",
        "             lambda r: r['material']['associations'][0]['decisions'][0].__setitem__('authorization', 'invented'),\n",
        "             'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('M04 waived intention', 'M04',\n",
        "             lambda r: r['material']['associations'][0]['decisions'][0].__setitem__('waived_intentions', []),\n",
        "             'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('M01 witness obligations', 'M01',\n",
        "             lambda r: r['material']['associations'][0]['decisions'][0]['witnesses'][0]['satisfied'].pop(),\n",
        "             'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('M03 missing certificate row', 'M03',\n",
        "             lambda r: r['material']['associations'][0]['decisions'][0]['rejection_certificate'].pop(),\n",
        "             'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('M03 repeated certificate row', 'M03',\n",
        "             lambda r: r['material']['associations'][0]['decisions'][0]['rejection_certificate'].__setitem__(\n",
        "                 1, copy.deepcopy(r['material']['associations'][0]['decisions'][0]['rejection_certificate'][0])),\n",
        "             'DUPLICATES')\n",
        "    mutation('M03 violated conjunct omission', 'M03',\n",
        "             lambda r: r['material']['associations'][1]['decisions'][0]['rejection_certificate'][0]['violated'].pop(),\n",
        "             'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('M03 unbound conjunct', 'M03',\n",
        "             lambda r: r['material']['associations'][1]['decisions'][0]['rejection_certificate'][0]['violated'].\n",
        "             append('update:undeclared'), 'MATERIAL_DECISION_MISMATCH')\n",
        "    mutation('observable partition', 'M02',\n",
        "             lambda r: r['material']['observable_classes'][0]['members'].pop())\n",
        "    mutation('M05 unsupported vs reject', 'M05-P',\n",
        "             lambda r: r['material'].__setitem__('associations', []))\n",
        "    for label, submitted, kind, required in mutations:\n",
        "        report = compare(names, submitted, 1)\n",
        "        check(any((kind is None or f.get('kind') == kind) and\n",
        "                  (required is None or bool(f.get(required))) for f in report['failures']),\n",
        "              'independent mismatch not detected: ' + label)\n",
        "\n",
        "    # Presentation permutations are boundary probes, not the deferred suites.\n",
        "    reordered = copy.deepcopy(batch)\n",
        "    reordered['results'].reverse()\n",
        "    for result in reordered['results']:\n",
        "        c = result['candidate']\n",
        "        if c['candidate_sets'] is not None:\n",
        "            for relations in c['candidate_sets'].values():\n",
        "                relations.reverse()\n",
        "                for relation in relations:\n",
        "                    relation.reverse()\n",
        "        if 'material' in result and result['material']['associations'] is not None:\n",
        "            for association in result['material']['associations']:\n",
        "                association['decisions'].reverse()\n",
        "                association['outcomes'].reverse()\n",
        "    compare(names, reordered, 0)\n",
        "\n",
        "for gate in ('C11_CLI_SCHEMA_GATE', 'CANDIDATE_COMPARISON_GATE', 'DIAGNOSTIC_COMPARISON_GATE',\n",
        "             'MATERIAL_COMPARISON_GATE', 'CERTIFICATE_COMPARISON_GATE', 'MALFORMED_CLI_GATE',\n",
        "             'FOCUSED_REGRESSION_GATE', 'INDEPENDENCE_GATE'):\n",
        "    print(gate + '=PASS_BOUNDED_CHECKS_ONLY')\n",
        "print('ACTUAL_TEST_COUNTS ' + json.dumps(dict(checks=checks, named_variants=27,\n",
        "      exact_named_comparison_calls=28, repeated_output_pairs=1, malformed_requests=len(malformed), output_failure_probes=3,\n",
        "      mismatch_probes=len(mutations), presentation_probes=1, certified_rejections=certificates,\n",
        "      certificate_rows=54, processes=process_counts), sort_keys=True))\n",
        "print('REMAINING_OBLIGATIONS full_polarity_campaign=NOT_RUN transformation_suites=NOT_RUN '\n",
        "      'EXP007=INCONCLUSIVE EXP004=INCONCLUSIVE/CALLER_ASSUMPTION')\n",
        "\n",
        "# Bounded worker regressions only. Freeze the scope before execution:\n",
        "# 9 pairs x 3 non-NONE states x 2 instances; one max/error/zero stream.\n",
        "# Any full-response mismatch falsifies the check; no campaign credit follows.\n",
        "if len(sys.argv) > 3:\n",
        "    worker = str(Path(sys.argv[3]).resolve())\n",
        "    worker_start = checks\n",
        "    worker_processes = 0\n",
        "    instances = {\n",
        "        'star/S_free': ('star-s-free', 'matrix_star_s_free', False),\n",
        "        'F09-geometry/S_inc': ('f09-s-inc', 'matrix_f09_s_inc', True),\n",
        "    }\n",
        "\n",
        "    def worker_run(frames, status):\n",
        "        global worker_processes\n",
        "        worker_processes += 1\n",
        "        process = subprocess.run([worker], input=''.join(frames), capture_output=True,\n",
        "                                 text=True, check=False, timeout=10)\n",
        "        check(process.returncode == status and process.stderr == '', 'worker process contract')\n",
        "        check(process.stdout.endswith('\\n'), 'worker response missing final LF')\n",
        "        responses = [json.loads(line) for line in process.stdout.splitlines()]\n",
        "        check(len(responses) == len(frames), 'worker must respond once per frame')\n",
        "        return responses\n",
        "\n",
        "    def envelope(identifier, ordinal):\n",
        "        return dict(schema='ste-exp007-worker-v1',\n",
        "                    protocol_sha256='61a586c706cf5e3cfb78ffbfd835dcbdc060c4c46f6cc427fbf2379a095664f1',\n",
        "                    plan_sha256='f817bb6267f8eee2ddcc3bc24de498e00d19a412599d3df3ff31ce79f2e592bf',\n",
        "                    qualification='DRAFT_NOT_SCIENTIFICALLY_QUALIFIED',\n",
        "                    request_index=ordinal, response_id=ordinal, request_id=identifier)\n",
        "\n",
        "    def work_counts(records, evaluated=True):\n",
        "        n = 6 if evaluated else 0\n",
        "        return dict(evaluator_calls=int(evaluated), candidates_generated=n,\n",
        "                    candidate_evaluations=n, evidence_predicate_calls=n,\n",
        "                    structure_predicate_calls=n, records_assessed=records,\n",
        "                    reference_relation_classifications=0, material_evaluations=0)\n",
        "\n",
        "    # Expectations use declared states, never states/records read from the worker.\n",
        "    # Concrete permutations and the independently checked F09 identity table\n",
        "    # implement protocol sections 6-8, not the worker's base-4 decoder/filters.\n",
        "    def expected_valid(instance, config, states, identifier, ordinal=1):\n",
        "        token, suite, incidence = instances[instance]\n",
        "        snapshots = {}\n",
        "        for side, letter, prefix in (('left', 'L', 'l'), ('right', 'R', 'r')):\n",
        "            root = 'root_' + letter\n",
        "            occurrences = [prefix + str(i) for i in range(3)]\n",
        "            edges = [[root, occurrence] for occurrence in occurrences]\n",
        "            if incidence:\n",
        "                edges[1] = [occurrences[0], occurrences[1]]\n",
        "            snapshots[side] = dict(id='snapshot_' + letter, root=root,\n",
        "                                   vertices=[root, *occurrences], occurrences=occurrences,\n",
        "                                   incidence=edges)\n",
        "        records = []\n",
        "        polarities = {0: (), 1: ('REQUIRE',), 2: ('EXCLUDE',), 3: ('REQUIRE', 'EXCLUDE')}\n",
        "        for i, state in enumerate(states):\n",
        "            source, target = 'l' + str(i // 3), 'r' + str(i % 3)\n",
        "            for polarity in polarities[state]:\n",
        "                records.append(dict(\n",
        "                    id=f'EXP007/C/V1/matrix/{token}/{config:06d}/pair/{i}/{polarity}',\n",
        "                    source=source, target=target, polarity=polarity, assessment='ACCEPTED',\n",
        "                    provenance=dict(\n",
        "                        origin='EXP-007 synthetic accepted-polarity matrix',\n",
        "                        source=f'EXP007_PROTOCOL.md section 6 / {token} / config/{config:06d} / pair/{i}',\n",
        "                        assessment_rule='External synthetic assessment is ACCEPTED for every matrix REQUIRE/EXCLUDE, by frozen section 6 declaration.',\n",
        "                        assumed_trust='Assumed solely for this finite model; provenance truth is not independently verified.',\n",
        "                        scope=dict(snapshots=['snapshot_L', 'snapshot_R'], source=source, target=target))))\n",
        "        sets = dict(U_H=[], C_E=[], A_E=[])\n",
        "        predicates = []\n",
        "        for permutation in itertools.permutations(range(3)):\n",
        "            relation = [['l' + str(i), 'r' + str(j)] for i, j in enumerate(permutation)]\n",
        "            evidence = all(state == 0 or (state == 1 and [source, target] in relation) or\n",
        "                           (state == 2 and [source, target] not in relation)\n",
        "                           for (source, target), state in zip(itertools.product(\n",
        "                               ('l0', 'l1', 'l2'), ('r0', 'r1', 'r2')), states))\n",
        "            structure = not incidence or permutation == (0, 1, 2)\n",
        "            sets['U_H'].append(relation)\n",
        "            if evidence:\n",
        "                sets['C_E'].append(relation)\n",
        "                if structure:\n",
        "                    sets['A_E'].append(relation)\n",
        "            predicates.append(dict(association=relation, evidence_satisfied=evidence,\n",
        "                                   structure_satisfied=structure))\n",
        "        diagnostics = []\n",
        "        if not records:\n",
        "            diagnostics.append('MISSING_EVIDENCE')\n",
        "        if not sets['C_E']:\n",
        "            diagnostics.append('EVIDENCE_INCONSISTENT')\n",
        "        elif not sets['A_E']:\n",
        "            diagnostics.append('STRUCTURALLY_UNSATISFIABLE')\n",
        "        result = envelope(identifier, ordinal)\n",
        "        result.update(status='EVALUATED', error_code=None,\n",
        "                      case_id=f'EXP007/C/V1/{suite}/{instance}/{config:06d}',\n",
        "                      instance_id=instance, config_id=config,\n",
        "                      input=dict(snapshots=snapshots, profile='S_inc' if incidence else 'S_free',\n",
        "                                 assumes_unchanged_incidence=incidence, pair_states=states),\n",
        "                      candidate=dict(status='SUPPORTED', diagnostics=diagnostics, conditional=False,\n",
        "                                     candidate_sets=sets, counts={k: len(v) for k, v in sets.items()},\n",
        "                                     relations_examined=6, assessment_counts=dict(\n",
        "                                         ACCEPTED=len(records), REJECTED=0, UNRESOLVED=0),\n",
        "                                     evidence_records=records, predicates=predicates),\n",
        "                      work=work_counts(len(records)))\n",
        "        return result\n",
        "\n",
        "    def normalized(response):\n",
        "        result = copy.deepcopy(response)\n",
        "        candidate = result['candidate']\n",
        "        if candidate is not None:\n",
        "            # Sort lists, never deduplicate: repeated pairs/candidates still fail.\n",
        "            for name, relations in candidate['candidate_sets'].items():\n",
        "                candidate['candidate_sets'][name] = sorted(sorted(r) for r in relations)\n",
        "            for predicate in candidate['predicates']:\n",
        "                predicate['association'].sort()\n",
        "            candidate['predicates'].sort(key=lambda p: p['association'])\n",
        "        return result\n",
        "\n",
        "    isolated = []\n",
        "    for instance in instances:\n",
        "        for pair in range(9):\n",
        "            for state in (1, 2, 3):\n",
        "                states = [0] * 9\n",
        "                states[pair] = state\n",
        "                config = state * 4 ** pair\n",
        "                identifier = f'isolated-{len(isolated) + 1}'\n",
        "                response, = worker_run([f'EXP007/1 {identifier} EVAL {instance} {config}\\n'], 0)\n",
        "                check(normalized(response) == normalized(expected_valid(\n",
        "                    instance, config, states, identifier)),\n",
        "                    f'isolated full response mismatch: {instance} pair={pair} state={state}')\n",
        "                isolated.append((instance, pair, state))\n",
        "    check(len(isolated) == 54 and len(set(isolated)) == 54, 'isolated coverage must be exactly 54')\n",
        "    isolated_checks = checks - worker_start\n",
        "    print('ISOLATED_54_GATE=PASS configurations=54 checks=' + str(isolated_checks))\n",
        "\n",
        "    recovery_start = checks\n",
        "    instance = 'F09-geometry/S_inc'\n",
        "    # ONE subprocess receives all three frames; rejected input must not reset\n",
        "    # ordinals or leak the preceding 18 records into the recovered NONE case.\n",
        "    frames = [f'EXP007/1 recovery-max EVAL {instance} 262143\\n',\n",
        "              f'EXP007/1 recovery-bad EVAL {instance} 00\\n',\n",
        "              f'EXP007/1 recovery-zero EVAL {instance} 0\\n']\n",
        "    responses = worker_run(frames, 2)\n",
        "    error = envelope('recovery-bad', 2)\n",
        "    error.update(status='ERROR', error_code='INVALID_CONFIG_ID', case_id=None,\n",
        "                 instance_id=None, config_id=None, input=None, candidate=None,\n",
        "                 work=work_counts(0, evaluated=False))\n",
        "    check(responses[1] == error, 'persistent malformed diagnostic/identity/order')\n",
        "    for index, config, states, identifier in ((0, 262143, [3] * 9, 'recovery-max'),\n",
        "                                               (2, 0, [0] * 9, 'recovery-zero')):\n",
        "        check(normalized(responses[index]) == normalized(expected_valid(\n",
        "            instance, config, states, identifier, index + 1)), 'persistent full valid evaluation')\n",
        "        separate, = worker_run([frames[index]], 0)\n",
        "        check(normalized(separate) == normalized(expected_valid(\n",
        "            instance, config, states, identifier)), 'separate full valid evaluation')\n",
        "        replay = copy.deepcopy(responses[index])\n",
        "        # Only the per-process ordinals differ; compare every other field.\n",
        "        replay.update(request_index=1, response_id=1)\n",
        "        check(normalized(replay) == normalized(separate), 'persistent worker state leakage')\n",
        "    recovery_checks = checks - recovery_start\n",
        "    print('PERSISTENT_RECOVERY_GATE=PASS stream_processes=1 responses=3 checks=' + str(recovery_checks))\n",
        "    print('EXACT_COMPARISON_GATE=PASS full_responses records provenance assessments sets predicates work')\n",
        "    print('TEST_REPRODUCIBILITY_GATE=PASS embedded_driver=--cli-test-script python=-B')\n",
        "    print('STE_WORKER_TEST_COUNTS ' + json.dumps(dict(\n",
        "        added_checks=checks - worker_start, isolated_checks=isolated_checks,\n",
        "        isolated_configurations=len(isolated), recovery_checks=recovery_checks,\n",
        "        persistent_sequences=1, persistent_responses=3, separate_evaluations=2,\n",
        "        worker_processes=worker_processes, total_python_checks=checks), sort_keys=True))\n",
        "else:\n",
        "    print('STE_WORKER_GATES=NOT_RUN supply CLI_BINARY REFERENCE_PY WORKER_BINARY to the emitted driver')\n",
    };
    size_t i;
    for (i = 0; i < HA_LENGTH(lines); ++i) fputs(lines[i], stdout);
    return fflush(stdout) == 0 && !ferror(stdout) ? 0 : 1;
}

int main(int argc, char **argv)
{
    unsigned before;
    int exit_status;
#ifdef SIGPIPE
    /* This test executable also exposes the CLI; keep signal policy at entry. */
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR)
        return ha_cli_error(stderr, "SIGPIPE setup failed", 1);
#endif
    if (argc == 2 && strcmp(argv[1], "--cli-test-script") == 0)
        return cli_test_script();
    if (argc > 1 && (argc != 2 || strcmp(argv[1], "--self-test") != 0))
        return ha_cli(argc, argv, stdout, stderr);
    before = failures;
    named_candidates(); malformed_candidates(); presentation_probes();
    gate("C11_GENERATOR_EVIDENCE_STRUCTURAL_FOCUSED_GATE", before);
    before = failures;
    named_materials(); material_boundaries();
    gate("DIRECT_DECISION_GATE", before);
    rejection_certificates();
    before = failures;
    certificate_policy_probes();
    gate("CERTIFICATE_POLICY_BOUNDARY_GATE", before);
    printf("REJECTION_CERTIFICATES completed=%u required=%u\n",
           certificates_completed, CERTIFICATES_REQUIRED);
    printf("ARITHMETIC_ASSERTIONS passed=%u failed=%u total=%u\n",
           assertions - failures, failures, assertions);
    printf("FOCUSED_REGRESSION_GATE=%s assertions=%u failures=%u completed_cases=%u "
           "scientifically_inconclusive_cases=%u\n",
           failures == 0 ? "PASS_CHECKS_ONLY" : "FAIL", assertions, failures,
           completed_cases, inconclusive);
    puts("REMAINING_INCONCLUSIVE_OBLIGATIONS exact_CLI_comparison=SEPARATE_DRIVER "
         "full_frozen_coverage=NOT_RUN policy_missing=UNSUPPORTED "
         "extra_observable=UNDEFINED");
    puts("EXP007_QUALIFICATION=INCONCLUSIVE full_campaign=NOT_RUN "
         "independent_comparison=NOT_RUN_BY_C_SELF_TEST");
    puts("EXP004_HISTORICAL_COMPLETENESS=INCONCLUSIVE "
         "EXP004_MATERIAL_EQUIVALENCE=CALLER_ASSUMPTION");
    /* Successful bounded operation is distinct from scientific qualification. */
    exit_status = failures == 0 && certificates_completed == CERTIFICATES_REQUIRED ? 0 : 1;
    printf("PROCESS_EXIT_STATUS=%d\n", exit_status);
    return exit_status;
}
