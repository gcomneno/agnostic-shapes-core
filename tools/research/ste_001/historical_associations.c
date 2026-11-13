/*
 * ASHES / STE EXP-007: bounded nonnormative research component, ISO C11.
 * Standalone CLI, or include with HA_NO_MAIN for focused research tests.
 * All strings are borrowed, immutable, nonempty C strings. Counts describe
 * the populated entries of fixed-capacity arrays; validation precedes use.
 * Inputs (including updates/decisions) must outlive their returned results.
 * Handles compare by value, never by pointer or vertex storage position.
 * No allocation, oracle calls, fixture expectations, or STE classification.
 *
 * ha_construct() decides by solving equalities and frame rules directly.
 * Only after a contradiction is decided may certificate code traverse V^L.
 * Exact named-fixture serialization does not qualify the complete EXP-007
 * campaign; independent Python search remains separate.
 */
#include <stdbool.h>
#include <stddef.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>

enum { HA_N = 3, HA_VERTICES = 4, HA_CANDIDATES = 6,
       HA_RECORDS = 64, HA_UPDATES = 2, HA_DECISIONS = 2,
       HA_OBLIGATIONS = 5, HA_ASSIGNMENTS = 27 };

typedef struct { const char *source, *target; } HaEdge;
typedef struct {
    const char *id, *root;
    size_t vertex_count, occurrence_count, edge_count;
    const char *vertices[HA_VERTICES], *occurrences[HA_N];
    HaEdge edges[HA_N];
} HaSnapshot;

typedef enum { HA_REQUIRE, HA_EXCLUDE } HaPolarity;
typedef enum { HA_ACCEPTED, HA_REJECTED, HA_UNRESOLVED } HaAssessment;
typedef struct {
    const char *origin, *source, *assessment_rule, *assumed_trust;
    const char *snapshots[2], *scope_source, *scope_target;
} HaProvenance;
typedef struct {
    const char *id, *source, *target;
    HaPolarity polarity;
    HaAssessment assessment;
    HaProvenance provenance;
} HaRecord;
typedef enum { HA_S_FREE, HA_S_INC } HaProfile;
typedef struct {
    HaSnapshot left, right;
    HaProfile profile;
    bool assumes_unchanged_incidence;
    size_t record_count;
    HaRecord records[HA_RECORDS];
} HaInput;

/* Destinations are concrete handles; sources are the declared occurrence set. */
typedef struct { const char *destination[HA_N]; } HaAssociation;
enum {
    HA_MISSING_EVIDENCE = 1u,
    HA_ASSESSMENT_UNRESOLVED = 2u,
    HA_EVIDENCE_INCONSISTENT = 4u,
    HA_STRUCTURALLY_UNSATISFIABLE = 8u,
    HA_INVALID_INPUT = 16u
};
typedef struct {
    bool supported, conditional;
    const char *reason;
    unsigned diagnostics;
    size_t universe_count, evidence_count, admissible_count;
    size_t assessment_counts[3];
    HaAssociation universe[HA_CANDIDATES];
    bool evidence[HA_CANDIDATES], structure[HA_CANDIDATES];
} HaCandidates;

static bool ha_text(const char *s) { return s != NULL && s[0] != '\0'; }
static bool ha_equal(const char *a, const char *b)
{
    return a != NULL && b != NULL && strcmp(a, b) == 0;
}
static int ha_find(const char *const *items, size_t count, const char *handle)
{
    size_t i;
    for (i = 0; i < count; ++i)
        if (ha_equal(items[i], handle)) return (int)i;
    return -1;
}

static const char *ha_validate_snapshot(const HaSnapshot *s)
{
    size_t i, j, round;
    bool reached[HA_VERTICES] = {false};
    int root;
    if (!ha_text(s->id)) return "snapshot identity required";
    if (s->vertex_count != HA_VERTICES)
        return "exactly four vertex handles required";
    for (i = 0; i < HA_VERTICES; ++i) {
        if (!ha_text(s->vertices[i])) return "invalid vertex handle";
        for (j = 0; j < i; ++j)
            if (ha_equal(s->vertices[i], s->vertices[j]))
                return "duplicated vertex handle";
    }
    root = ha_find(s->vertices, HA_VERTICES, s->root);
    if (!ha_text(s->root) || root < 0) return "invalid designated root";
    if (s->occurrence_count != HA_N)
        return "exactly three distinct non-root occurrences required";
    for (i = 0; i < HA_N; ++i) {
        if (!ha_text(s->occurrences[i]) ||
            ha_find(s->vertices, HA_VERTICES, s->occurrences[i]) < 0 ||
            ha_equal(s->root, s->occurrences[i]))
            return "invalid non-root occurrence domain";
        for (j = 0; j < i; ++j)
            if (ha_equal(s->occurrences[i], s->occurrences[j]))
                return "exactly three distinct non-root occurrences required";
    }
    if (s->edge_count != HA_N) return "tree needs exactly three incidences";
    for (i = 0; i < HA_N; ++i) {
        const HaEdge *e = &s->edges[i];
        if (ha_find(s->vertices, HA_VERTICES, e->source) < 0 ||
            ha_find(s->vertices, HA_VERTICES, e->target) < 0 ||
            ha_equal(e->source, e->target))
            return "foreign vertex or self incidence";
        for (j = 0; j < i; ++j)
            if (ha_equal(e->source, s->edges[j].source) &&
                ha_equal(e->target, s->edges[j].target))
                return "duplicate incidence";
    }
    for (i = 0; i < HA_VERTICES; ++i) {
        size_t parents = 0;
        for (j = 0; j < HA_N; ++j)
            if (ha_equal(s->edges[j].target, s->vertices[i])) ++parents;
        if (parents != (i == (size_t)root ? 0u : 1u))
            return "invalid tree parent occupancy";
    }
    reached[root] = true;
    for (round = 0; round < HA_VERTICES; ++round)
        for (j = 0; j < HA_N; ++j) {
            int a = ha_find(s->vertices, HA_VERTICES, s->edges[j].source);
            int b = ha_find(s->vertices, HA_VERTICES, s->edges[j].target);
            if (reached[a]) reached[b] = true;
        }
    for (i = 0; i < HA_VERTICES; ++i)
        if (!reached[i])
            return "snapshot is not a rooted tree: unreachable/cyclic vertices";
    return NULL;
}

static bool ha_same_record(const HaRecord *a, const HaRecord *b)
{
    const HaProvenance *p = &a->provenance, *q = &b->provenance;
    return ha_equal(a->id, b->id) && ha_equal(a->source, b->source) &&
        ha_equal(a->target, b->target) && a->polarity == b->polarity &&
        a->assessment == b->assessment && ha_equal(p->origin, q->origin) &&
        ha_equal(p->source, q->source) &&
        ha_equal(p->assessment_rule, q->assessment_rule) &&
        ha_equal(p->assumed_trust, q->assumed_trust) &&
        ha_equal(p->snapshots[0], q->snapshots[0]) &&
        ha_equal(p->snapshots[1], q->snapshots[1]) &&
        ha_equal(p->scope_source, q->scope_source) &&
        ha_equal(p->scope_target, q->scope_target);
}

static const char *ha_validate(const HaInput *in)
{
    const char *reason;
    size_t i, j;
    reason = ha_validate_snapshot(&in->left);
    if (reason != NULL) return reason;
    reason = ha_validate_snapshot(&in->right);
    if (reason != NULL) return reason;
    if (ha_equal(in->left.id, in->right.id))
        return "snapshots require separate identities";
    for (i = 0; i < HA_VERTICES; ++i)
        if (ha_find(in->right.vertices, HA_VERTICES, in->left.vertices[i]) >= 0)
            return "cross-snapshot duplicate handle";
    if (in->profile != HA_S_FREE && in->profile != HA_S_INC)
        return "unsupported structural profile";
    if (in->profile == HA_S_INC && !in->assumes_unchanged_incidence)
        return "S_inc requires explicit authorization";
    if (in->record_count > HA_RECORDS)
        return "evidence outside bounded record domain";
    for (i = 0; i < in->record_count; ++i) {
        const HaRecord *r = &in->records[i];
        const HaProvenance *p = &r->provenance;
        if (!ha_text(r->id)) return "evidence record identity required";
        if (ha_find(in->left.occurrences, HA_N, r->source) < 0 ||
            ha_find(in->right.occurrences, HA_N, r->target) < 0)
            return "foreign evidence handle";
        if (r->polarity != HA_REQUIRE && r->polarity != HA_EXCLUDE)
            return "unsupported evidence polarity";
        if (r->assessment != HA_ACCEPTED && r->assessment != HA_REJECTED &&
            r->assessment != HA_UNRESOLVED)
            return "unsupported assessment status";
        if (!ha_text(p->origin) || !ha_text(p->source) ||
            !ha_text(p->assessment_rule) || !ha_text(p->assumed_trust))
            return "synthetic provenance and trust assumptions required";
        if (!ha_equal(p->snapshots[0], in->left.id) ||
            !ha_equal(p->snapshots[1], in->right.id) ||
            !ha_equal(p->scope_source, r->source) ||
            !ha_equal(p->scope_target, r->target))
            return "provenance scope must follow concrete selectors";
        for (j = 0; j < i; ++j)
            if (ha_equal(r->id, in->records[j].id) &&
                !ha_same_record(r, &in->records[j]))
                return "same evidence ID has contradictory presentations";
    }
    return NULL;
}

/* Construction of triples, independent of all evidence and incidence. */
static size_t ha_generate(const HaSnapshot *right, HaAssociation result[HA_CANDIDATES])
{
    size_t a, b, c, count = 0;
    for (a = 0; a < HA_N; ++a)
        for (b = 0; b < HA_N; ++b)
            for (c = 0; c < HA_N; ++c)
                if (!ha_equal(right->occurrences[a], right->occurrences[b]) &&
                    !ha_equal(right->occurrences[a], right->occurrences[c]) &&
                    !ha_equal(right->occurrences[b], right->occurrences[c])) {
                    result[count].destination[0] = right->occurrences[a];
                    result[count].destination[1] = right->occurrences[b];
                    result[count].destination[2] = right->occurrences[c];
                    ++count;
                }
    return count;
}

static bool ha_evidence(const HaInput *in, const HaAssociation *phi)
{
    size_t i;
    for (i = 0; i < in->record_count; ++i) {
        const HaRecord *r = &in->records[i];
        int source;
        bool present;
        if (r->assessment != HA_ACCEPTED) continue;
        source = ha_find(in->left.occurrences, HA_N, r->source);
        present = ha_equal(phi->destination[source], r->target);
        if ((r->polarity == HA_REQUIRE && !present) ||
            (r->polarity == HA_EXCLUDE && present)) return false;
    }
    return true;
}

static const char *ha_transport(const HaInput *in, const HaAssociation *phi,
                                const char *handle)
{
    int occurrence;
    if (ha_equal(handle, in->left.root)) return in->right.root;
    occurrence = ha_find(in->left.occurrences, HA_N, handle);
    return occurrence < 0 ? NULL : phi->destination[occurrence];
}

static bool ha_structure(const HaInput *in, const HaAssociation *phi)
{
    size_t i, j;
    if (in->profile == HA_S_FREE) return true;
    for (i = 0; i < HA_N; ++i) {
        bool found = false;
        const char *a = ha_transport(in, phi, in->left.edges[i].source);
        const char *b = ha_transport(in, phi, in->left.edges[i].target);
        for (j = 0; j < HA_N; ++j)
            if (ha_equal(a, in->right.edges[j].source) &&
                ha_equal(b, in->right.edges[j].target)) found = true;
        if (!found) return false;
    }
    return true;
}

HaCandidates ha_evaluate(const HaInput *in)
{
    HaCandidates out = {0};
    size_t i;
    out.reason = ha_validate(in);
    if (out.reason != NULL) {
        out.diagnostics = HA_INVALID_INPUT;
        return out;
    }
    out.supported = true;
    out.universe_count = ha_generate(&in->right, out.universe);
    for (i = 0; i < in->record_count; ++i)
        ++out.assessment_counts[in->records[i].assessment];
    out.conditional = out.assessment_counts[HA_UNRESOLVED] != 0;
    if (in->record_count == 0) out.diagnostics |= HA_MISSING_EVIDENCE;
    if (out.conditional) out.diagnostics |= HA_ASSESSMENT_UNRESOLVED;
    for (i = 0; i < out.universe_count; ++i) {
        out.evidence[i] = ha_evidence(in, &out.universe[i]);
        out.structure[i] = ha_structure(in, &out.universe[i]);
        if (out.evidence[i]) ++out.evidence_count;
        if (out.evidence[i] && out.structure[i]) ++out.admissible_count;
    }
    if (out.evidence_count == 0) out.diagnostics |= HA_EVIDENCE_INCONSISTENT;
    else if (out.admissible_count == 0)
        out.diagnostics |= HA_STRUCTURALLY_UNSATISFIABLE;
    return out;
}

typedef enum { HA_ZERO, HA_LAMBDA, HA_RHO } HaValue;
typedef enum { HA_LEFT, HA_RIGHT } HaSide;
typedef struct {
    const char *id, *target;
    HaSide side;
    HaValue value;
    bool mandatory;
} HaUpdate;
typedef struct {
    const char *id, *authorization;
    size_t retained_count, waived_count;
    const char *retained[HA_UPDATES], *waived[HA_UPDATES];
} HaDecision;
typedef struct {
    HaValue initial[2][HA_N];
    size_t update_count, decision_count;
    HaUpdate updates[HA_UPDATES];
    HaDecision decisions[HA_DECISIONS];
    bool policy_complete, observable_defined, independent_comparison_complete;
} HaMaterial;
typedef struct {
    /* Stable two-part IDs: ("update", intention ID) denotes update:<id>;
     * ("preserve", source handle) denotes preserve:<handle>. No array index
     * or pointer identity is part of a conjunct ID. Borrowing the components
     * avoids imposing a new string-length bound or allocating ID buffers. */
    const char *kind, *key;
} HaConjunctId;
typedef struct {
    /* NULL intention denotes the zero-preservation conjunct. */
    HaConjunctId id;
    const HaUpdate *intention;
    const char *target;
    HaValue value;
} HaObligation;
typedef struct {
    bool supported, equalities_consistent;
    const char *reason;
    const HaDecision *decision;
    HaValue values[HA_N];
    size_t obligation_count;
    HaObligation obligations[HA_OBLIGATIONS];
    /* The direct decision remains separate from its exhaustive certificate. */
} HaConstruction;

static const char *ha_validate_material(const HaInput *in, const HaMaterial *m)
{
    size_t i, j, side;
    if (ha_validate(in) != NULL) return "invalid candidate model";
    for (side = 0; side < 2; ++side)
        for (i = 0; i < HA_N; ++i)
            if (m->initial[side][i] != HA_ZERO)
                return "initial material must be 0 on non-root occurrences only";
    if (m->update_count < 1 || m->update_count > HA_UPDATES)
        return "unsupported update domain";
    for (i = 0; i < m->update_count; ++i) {
        const HaUpdate *u = &m->updates[i];
        const HaSnapshot *s;
        if (!ha_text(u->id)) return "intention IDs required";
        for (j = 0; j < i; ++j)
            if (ha_equal(u->id, m->updates[j].id)) return "duplicated intention ID";
        if (u->side != HA_LEFT && u->side != HA_RIGHT) return "invalid update side";
        s = u->side == HA_LEFT ? &in->left : &in->right;
        if (ha_find(s->occurrences, HA_N, u->target) < 0)
            return "foreign material selector";
        if (!u->mandatory || u->value < HA_ZERO || u->value > HA_RHO)
            return "only mandatory single-valued equality updates are supported";
    }
    if (!m->policy_complete) return "required complete retention/loss policy is absent";
    if (m->decision_count < 1 || m->decision_count > HA_DECISIONS)
        return "complete finite decision set required (one or two decisions)";
    for (i = 0; i < m->decision_count; ++i) {
        const HaDecision *d = &m->decisions[i];
        size_t k;
        if (!ha_text(d->id)) return "decision IDs required";
        if (!ha_text(d->authorization)) return "policy authorization required";
        for (j = 0; j < i; ++j)
            if (ha_equal(d->id, m->decisions[j].id)) return "duplicate policy decision";
        if (d->retained_count > HA_UPDATES || d->waived_count > HA_UPDATES ||
            d->retained_count + d->waived_count != m->update_count)
            return "each intention must be retained or explicitly waived, exactly once";
        for (k = 0; k < m->update_count; ++k) {
            size_t count = 0;
            for (j = 0; j < d->retained_count; ++j)
                if (ha_equal(d->retained[j], m->updates[k].id)) ++count;
            for (j = 0; j < d->waived_count; ++j)
                if (ha_equal(d->waived[j], m->updates[k].id)) ++count;
            if (count != 1)
                return "each intention must be retained or explicitly waived, exactly once";
        }
    }
    return NULL;
}

/* Direct equalities plus the frame rule; never search the 27 assignments. */
static HaConstruction ha_construct(const HaInput *in, const HaAssociation *phi,
                                    const HaMaterial *m, size_t decision)
{
    HaConstruction out = {0};
    bool targeted[HA_N] = {false};
    size_t i;
    out.reason = ha_validate_material(in, m);
    if (out.reason != NULL) return out;
    if (decision >= m->decision_count) {
        out.reason = "foreign policy decision";
        return out;
    }
    /* Do not trust a caller-supplied association or select an alternative. */
    for (i = 0; i < HA_N; ++i) {
        size_t j;
        if (ha_find(in->right.occurrences, HA_N, phi->destination[i]) < 0) {
            out.reason = "foreign association handle";
            return out;
        }
        for (j = 0; j < i; ++j)
            if (ha_equal(phi->destination[i], phi->destination[j])) {
                out.reason = "association is not bijective";
                return out;
            }
    }
    if (!ha_evidence(in, phi) || !ha_structure(in, phi)) {
        out.reason = "association is not admissible";
        return out;
    }
    out.supported = true;
    out.equalities_consistent = true;
    out.decision = &m->decisions[decision];
    for (i = 0; i < m->update_count; ++i) {
        const HaUpdate *u = &m->updates[i];
        HaObligation *o;
        int target;
        if (ha_find(out.decision->retained, out.decision->retained_count, u->id) < 0)
            continue;
        target = u->side == HA_LEFT ?
            ha_find(in->left.occurrences, HA_N, u->target) :
            ha_find(phi->destination, HA_N, u->target);
        o = &out.obligations[out.obligation_count++];
        o->id = (HaConjunctId){"update", u->id};
        o->intention = u;
        o->target = in->left.occurrences[target];
        o->value = u->value;
        if (targeted[target] && out.values[target] != u->value)
            out.equalities_consistent = false;
        out.values[target] = u->value;
        targeted[target] = true;
    }
    for (i = 0; i < HA_N; ++i)
        if (!targeted[i]) {
            HaObligation *o = &out.obligations[out.obligation_count++];
            o->target = in->left.occurrences[i];
            o->id = (HaConjunctId){"preserve", o->target};
            o->value = HA_ZERO;
        }
    return out;
}

typedef struct {
    HaValue values[HA_N];
    size_t violated_count;
    HaConjunctId violated[HA_OBLIGATIONS];
} HaRejectionRow;
typedef struct {
    /* Rows map these concrete sources to values. The surrounding alternative
     * and this binding retain the association and the full authorized policy,
     * including retained/waived intentions, rather than just an outcome tag. */
    const char *sources[HA_N];
    HaAssociation association;
    const HaDecision *decision;
    size_t row_count;
    HaRejectionRow rows[HA_ASSIGNMENTS];
} HaRejectionCertificate;

static bool ha_same_conjunct(HaConjunctId a, HaConjunctId b)
{
    return ha_equal(a.kind, b.kind) && ha_equal(a.key, b.key);
}

/* Recheck the certificate against the declared policy and transported
 * obligations. Neither a row count nor the generator's claims are trusted.
 * Re-solving the equations here guards the already determined contradiction;
 * the row traversal verifies evidence only and never selects an outcome. */
static bool ha_certificate_valid(const HaInput *in, const HaAssociation *phi,
                                 const HaMaterial *m, size_t decision,
                                 const HaRejectionCertificate *certificate)
{
    HaConstruction direct = ha_construct(in, phi, m, decision);
    bool seen[HA_ASSIGNMENTS] = {false};
    size_t i, j;
    if (!direct.supported || direct.equalities_consistent || !m->observable_defined)
        return false;
    if (certificate->decision != direct.decision ||
        certificate->row_count != HA_ASSIGNMENTS) return false;
    for (i = 0; i < HA_N; ++i)
        if (!ha_equal(certificate->sources[i], in->left.occurrences[i]) ||
            !ha_equal(certificate->association.destination[i], phi->destination[i]))
            return false;
    for (i = 0; i < certificate->row_count; ++i) {
        const HaRejectionRow *row = &certificate->rows[i];
        size_t code = 0, expected_count = 0;
        if (row->violated_count == 0 || row->violated_count > direct.obligation_count)
            return false;
        for (j = 0; j < HA_N; ++j) {
            if (row->values[j] < HA_ZERO || row->values[j] > HA_RHO) return false;
            code = 3 * code + (size_t)row->values[j];
        }
        if (seen[code]) return false;
        seen[code] = true;
        for (j = 0; j < direct.obligation_count; ++j) {
            const HaObligation *o = &direct.obligations[j];
            int target = ha_find(in->left.occurrences, HA_N, o->target);
            size_t k, matches = 0;
            bool violated = row->values[target] != o->value;
            for (k = 0; k < row->violated_count; ++k)
                if (ha_same_conjunct(row->violated[k], o->id)) ++matches;
            if (matches != (violated ? 1u : 0u)) return false;
            if (violated) ++expected_count;
        }
        /* Also excludes undeclared identifiers and extra duplicated entries. */
        if (expected_count != row->violated_count) return false;
    }
    for (i = 0; i < HA_ASSIGNMENTS; ++i)
        if (!seen[i]) return false;
    return true;
}

/* Materialize the bounded proof only AFTER the direct solver has rejected.
 * Accepted or unsupported constructions never traverse the material carrier. */
static void ha_rejection_rows(const HaInput *in, const HaAssociation *phi,
                              const HaConstruction *direct,
                              HaRejectionCertificate *certificate)
{
    size_t i, j;
    *certificate = (HaRejectionCertificate){0};
    if (!direct->supported || direct->equalities_consistent) return;
    certificate->decision = direct->decision;
    certificate->association = *phi;
    for (i = 0; i < HA_N; ++i) certificate->sources[i] = in->left.occurrences[i];
    for (i = 0; i < HA_ASSIGNMENTS; ++i) {
        HaRejectionRow *row = &certificate->rows[certificate->row_count++];
        size_t code = i;
        for (j = HA_N; j > 0; --j) {
            row->values[j - 1] = (HaValue)(code % 3);
            code /= 3;
        }
        for (j = 0; j < direct->obligation_count; ++j) {
            const HaObligation *o = &direct->obligations[j];
            int target = ha_find(in->left.occurrences, HA_N, o->target);
            if (row->values[target] != o->value)
                row->violated[row->violated_count++] = o->id;
        }
    }
}

typedef struct {
    HaAssociation association;
    HaConstruction construction;
    bool rejection_certified;
    HaRejectionCertificate rejection;
} HaAlternative;
typedef struct {
    bool policy_supported, observable_defined, partition_complete;
    const char *reason;
    size_t alternative_count, witness_count, uncertified_count, class_count;
    size_t certificates_required, certificates_completed, rejected_association_count;
    /* Indexed by the six generated associations, not by observable class. */
    bool rejected_under_all_decisions[HA_CANDIDATES];
    HaAlternative alternatives[HA_CANDIDATES * HA_DECISIONS];
    size_t class_of[HA_CANDIDATES * HA_DECISIONS];
    /* Scientific claim remains INCONCLUSIVE: qualification is incomplete. */
} HaMaterials;

static bool ha_same_outcome(const HaAlternative *a, const HaAlternative *b)
{
    size_t i;
    if (a->rejection_certified || b->rejection_certified)
        return a->rejection_certified && b->rejection_certified;
    for (i = 0; i < HA_N; ++i)
        if (a->construction.values[i] != b->construction.values[i]) return false;
    return true;
}

/* Preserve all associations and all declared decisions, without preference. */
HaMaterials ha_material_evaluate(const HaInput *in, const HaMaterial *m)
{
    HaMaterials out = {0};
    HaCandidates candidates;
    size_t i, d;
    out.reason = ha_validate_material(in, m);
    if (out.reason != NULL) return out;
    candidates = ha_evaluate(in);
    out.policy_supported = true;
    out.observable_defined = m->observable_defined;
    for (i = 0; i < candidates.universe_count; ++i) {
        bool all_decisions_rejected = true;
        if (!candidates.evidence[i] || !candidates.structure[i]) continue;
        for (d = 0; d < m->decision_count; ++d) {
            HaAlternative *a = &out.alternatives[out.alternative_count++];
            a->association = candidates.universe[i];
            a->construction = ha_construct(in, &a->association, m, d);
            if (a->construction.supported && a->construction.equalities_consistent)
                ++out.witness_count;
            else if (a->construction.supported) {
                ++out.certificates_required;
                if (m->observable_defined) {
                    ha_rejection_rows(in, &a->association, &a->construction, &a->rejection);
                    a->rejection_certified = ha_certificate_valid(
                        in, &a->association, m, d, &a->rejection);
                }
                if (a->rejection_certified) ++out.certificates_completed;
            }
            if (!a->construction.supported ||
                (!a->construction.equalities_consistent && !a->rejection_certified))
                ++out.uncertified_count;
            if (!a->rejection_certified) all_decisions_rejected = false;
        }
        out.rejected_under_all_decisions[i] = all_decisions_rejected;
        if (all_decisions_rejected) ++out.rejected_association_count;
    }
    out.partition_complete = out.observable_defined && out.uncertified_count == 0;
    if (!out.partition_complete) return out;
    for (i = 0; i < out.alternative_count; ++i) {
        size_t earlier;
        for (earlier = 0; earlier < i; ++earlier)
            if (ha_same_outcome(&out.alternatives[i], &out.alternatives[earlier])) break;
        out.class_of[i] = earlier == i ? out.class_count++ : out.class_of[earlier];
    }
    return out;
}

/* Named input declarations copied from EXP007_FIXTURES.json (not expected
 * sets, outcomes, or oracle results). No arbitrary JSON/manifest input is
 * accepted. Changes to the frozen inputs require a separate contract change.
 * The independent comparison detects drift in these declarations.
 */
#define HA_PROTOCOL_SHA256 "61a586c706cf5e3cfb78ffbfd835dcbdc060c4c46f6cc427fbf2379a095664f1"
#define HA_SCHEMA "ste-exp007-reference-v1"
enum { HA_MAX_CASES = 64 };

typedef struct {
    const char *id;
    unsigned shape, invalid; /* 0 stars, 1 F09 geometry, 2 historical MOVE */
    HaProfile profile;
    bool unchanged;
    size_t record_count;
    HaRecord records[HA_N];
} HaNamedCandidate;

#define HA_DECL_RECORD(id_, s_, t_, p_, a_, provenance_source_) \
    {id_, s_, t_, p_, a_, {"EXP-007 fixture declaration", provenance_source_, \
     "External synthetic assessment uses the declared status; no inference of historical truth.", \
     "Assumed solely for this finite model; provenance truth is not independently verified.", \
     {"snapshot_L", "snapshot_R"}, s_, t_}}
static const HaNamedCandidate ha_named_candidates[] = {
    {"F01", 0, 0, HA_S_FREE, false, 0, {
        {0}
    }},
    {"F02", 0, 0, HA_S_FREE, false, 1, {
        HA_DECL_RECORD("F02/E01", "l0", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F02"),
    }},
    {"F03", 0, 0, HA_S_FREE, false, 2, {
        HA_DECL_RECORD("F03/E01", "l0", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F03"),
        HA_DECL_RECORD("F03/E02", "l1", "r1", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F03"),
    }},
    {"F04", 0, 0, HA_S_FREE, false, 1, {
        HA_DECL_RECORD("F04/E01", "l0", "r0", HA_EXCLUDE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F04"),
    }},
    {"F05", 0, 0, HA_S_FREE, false, 1, {
        HA_DECL_RECORD("F05/E01", "l0", "r0", HA_REQUIRE, HA_REJECTED,
                       "EXP007_PROTOCOL.md section 7 / F05"),
    }},
    {"F06", 0, 0, HA_S_FREE, false, 2, {
        HA_DECL_RECORD("F06/E01", "l0", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F06"),
        HA_DECL_RECORD("F06/E02", "l0", "r1", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F06"),
    }},
    {"F07", 0, 0, HA_S_FREE, false, 2, {
        HA_DECL_RECORD("F07/E01", "l0", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F07"),
        HA_DECL_RECORD("F07/E02", "l0", "r0", HA_EXCLUDE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F07"),
    }},
    {"F08", 0, 0, HA_S_FREE, false, 3, {
        HA_DECL_RECORD("F08/E01", "l0", "r0", HA_EXCLUDE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F08"),
        HA_DECL_RECORD("F08/E02", "l0", "r1", HA_EXCLUDE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F08"),
        HA_DECL_RECORD("F08/E03", "l0", "r2", HA_EXCLUDE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F08"),
    }},
    {"F09", 1, 0, HA_S_INC, true, 0, {
        {0}
    }},
    {"F10", 1, 0, HA_S_INC, true, 2, {
        HA_DECL_RECORD("F10/E01", "l0", "r2", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F10"),
        HA_DECL_RECORD("F10/E02", "l1", "r1", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F10"),
    }},
    {"F11", 2, 0, HA_S_FREE, false, 3, {
        HA_DECL_RECORD("F11/E01", "a_L", "a_R", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F11"),
        HA_DECL_RECORD("F11/E02", "p_L", "p_R", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F11"),
        HA_DECL_RECORD("F11/E03", "q_L", "q_R", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F11"),
    }},
    {"F12", 0, 0, HA_S_FREE, false, 1, {
        HA_DECL_RECORD("F12/E01", "l0", "r0", HA_REQUIRE, HA_UNRESOLVED,
                       "EXP007_PROTOCOL.md section 7 / F12"),
    }},
    {"F13-duplicated_handle", 0, 1, HA_S_FREE, false, 0, {
        {0}
    }},
    {"F13-foreign_handle", 0, 2, HA_S_FREE, false, 1, {
        HA_DECL_RECORD("F13-foreign_handle/E01", "l_foreign", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F13-foreign_handle"),
    }},
    {"F13-invalid_tree", 0, 3, HA_S_FREE, false, 0, {
        {0}
    }},
    {"F13-invalid_root", 0, 4, HA_S_FREE, false, 0, {
        {0}
    }},
    {"F14", 0, 0, HA_S_FREE, false, 2, {
        HA_DECL_RECORD("F14/E01", "l0", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F14"),
        HA_DECL_RECORD("F14/E02", "l1", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F14"),
    }},
    {"F12-ACCEPTED", 0, 0, HA_S_FREE, false, 1, {
        HA_DECL_RECORD("F12-ACCEPTED/E01", "l0", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 7 / F12-ACCEPTED"),
    }},
    {"F12-REJECTED", 0, 0, HA_S_FREE, false, 1, {
        HA_DECL_RECORD("F12-REJECTED/E01", "l0", "r0", HA_REQUIRE, HA_REJECTED,
                       "EXP007_PROTOCOL.md section 7 / F12-REJECTED"),
    }},
    {"M04-association", 0, 0, HA_S_FREE, false, 3, {
        HA_DECL_RECORD("M04-association/E01", "l0", "r0", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 11 / M04"),
        HA_DECL_RECORD("M04-association/E02", "l1", "r1", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 11 / M04"),
        HA_DECL_RECORD("M04-association/E03", "l2", "r2", HA_REQUIRE, HA_ACCEPTED,
                       "EXP007_PROTOCOL.md section 11 / M04"),
    }},
};
#undef HA_DECL_RECORD

typedef struct {
    const char *id, *candidate_id, *comparison;
    HaMaterial input;
} HaNamedMaterial;
static const HaNamedMaterial ha_named_materials[] = {
    {"M01", "F01", "PENDING", {
        .policy_complete = true, .observable_defined = true,
        .update_count = 1, .updates = {
            {"left_lambda", "l0", HA_LEFT, HA_LAMBDA, true},
        },
        .decision_count = 1, .decisions = {
            {"strict", "All updates mandatory; no intention loss authorized.",
             1, 0, {"left_lambda"}, {NULL}},
        },
    }},
    {"M02", "F01", "PENDING", {
        .policy_complete = true, .observable_defined = true,
        .update_count = 1, .updates = {
            {"right_rho", "r0", HA_RIGHT, HA_RHO, true},
        },
        .decision_count = 1, .decisions = {
            {"strict", "All updates mandatory; no intention loss authorized.",
             1, 0, {"right_rho"}, {NULL}},
        },
    }},
    {"M03", "F01", "PENDING", {
        .policy_complete = true, .observable_defined = true,
        .update_count = 2, .updates = {
            {"left_lambda", "l0", HA_LEFT, HA_LAMBDA, true},
            {"right_rho", "r0", HA_RIGHT, HA_RHO, true},
        },
        .decision_count = 1, .decisions = {
            {"strict", "All updates mandatory; no intention loss authorized.",
             2, 0, {"left_lambda", "right_rho"}, {NULL}},
        },
    }},
    {"M04", "M04-association", "PENDING", {
        .policy_complete = true, .observable_defined = true,
        .update_count = 2, .updates = {
            {"left_lambda", "l0", HA_LEFT, HA_LAMBDA, true},
            {"right_rho", "r0", HA_RIGHT, HA_RHO, true},
        },
        .decision_count = 2, .decisions = {
            {"d_lambda", "M04 explicitly authorizes waiving rho while retaining lambda.",
             1, 1, {"left_lambda"}, {"right_rho"}},
            {"d_rho", "M04 explicitly authorizes waiving lambda while retaining rho.",
             1, 1, {"right_rho"}, {"left_lambda"}},
        },
    }},
    {"M05-P", "M04-association", "PENDING", {
        .policy_complete = false, .observable_defined = true,
        .update_count = 2, .updates = {
            {"left_lambda", "l0", HA_LEFT, HA_LAMBDA, true},
            {"right_rho", "r0", HA_RIGHT, HA_RHO, true},
        },
    }},
    {"M05-O", "F01", "PENDING", {
        .policy_complete = true, .observable_defined = false,
        .update_count = 1, .updates = {
            {"left_lambda", "l0", HA_LEFT, HA_LAMBDA, true},
        },
        .decision_count = 1, .decisions = {
            {"strict", "All updates mandatory; no intention loss authorized.",
             1, 0, {"left_lambda"}, {NULL}},
        },
    }},
    {"M05-I", "F01", "INCOMPLETE", {
        .policy_complete = true, .observable_defined = true,
        .update_count = 1, .updates = {
            {"left_lambda", "l0", HA_LEFT, HA_LAMBDA, true},
        },
        .decision_count = 1, .decisions = {
            {"strict", "All updates mandatory; no intention loss authorized.",
             1, 0, {"left_lambda"}, {NULL}},
        },
    }},
};

#define HA_LENGTH(a) (sizeof(a) / sizeof((a)[0]))

static HaInput ha_named_input(const HaNamedCandidate *declaration)
{
    HaInput in = {0};
    static const char *const handles[2][2][HA_N] = {
        {{"l0", "l1", "l2"}, {"r0", "r1", "r2"}},
        {{"a_L", "p_L", "q_L"}, {"a_R", "p_R", "q_R"}}
    };
    size_t side, i;
    for (side = 0; side < 2; ++side) {
        HaSnapshot *s = side == 0 ? &in.left : &in.right;
        s->id = side == 0 ? "snapshot_L" : "snapshot_R";
        s->root = side == 0 ? "root_L" : "root_R";
        s->vertex_count = HA_VERTICES;
        s->occurrence_count = s->edge_count = HA_N;
        s->vertices[0] = s->root;
        for (i = 0; i < HA_N; ++i) {
            s->vertices[i + 1] = s->occurrences[i] = handles[declaration->shape == 2][side][i];
            s->edges[i] = (HaEdge){s->root, s->occurrences[i]};
        }
        if (declaration->shape != 0)
            s->edges[1].source = s->occurrences[declaration->shape == 2 && side == 1 ? 2 : 0];
    }
    in.profile = declaration->profile;
    in.assumes_unchanged_incidence = declaration->unchanged;
    in.record_count = declaration->record_count;
    for (i = 0; i < in.record_count; ++i) in.records[i] = declaration->records[i];
    if (declaration->invalid == 1) in.left.vertices[2] = "l0";
    if (declaration->invalid == 3) {
        in.left.edges[0] = (HaEdge){"root_L", "l2"};
        in.left.edges[1] = (HaEdge){"l0", "l1"};
        in.left.edges[2] = (HaEdge){"l1", "l0"};
    }
    if (declaration->invalid == 4) in.left.root = "outside_snapshot";
    return in;
}

/* Small output-only encoder. All result strings are frozen ASCII declarations
 * or validated component strings. Caller arguments are never used as formats.
 * FILE errors are checked by the CLI after flushing. No JSON parser or heap.
 */
static void ha_json_contents(FILE *out, const char *s)
{
    const unsigned char *p = (const unsigned char *)s;
    for (; *p != 0; ++p) {
        if (*p == '"' || *p == '\\') { fputc('\\', out); fputc(*p, out); }
        else if (*p < 32) fprintf(out, "\\u%04x", (unsigned)*p);
        else fputc(*p, out);
    }
}

static void ha_json_string(FILE *out, const char *s)
{
    if (s == NULL) { fputs("null", out); return; }
    fputc('"', out); ha_json_contents(out, s); fputc('"', out);
}

static void ha_json_bool(FILE *out, bool value) { fputs(value ? "true" : "false", out); }

static void ha_json_relation(FILE *out, const HaInput *in, const HaAssociation *phi)
{
    size_t i;
    fputc('[', out);
    for (i = 0; i < HA_N; ++i) {
        if (i != 0) fputc(',', out);
        fputc('[', out); ha_json_string(out, in->left.occurrences[i]);
        fputc(',', out); ha_json_string(out, phi->destination[i]); fputc(']', out);
    }
    fputc(']', out);
}

static void ha_json_conjunct_id(FILE *out, HaConjunctId id)
{
    /* Components are separately borrowed; no temporary concatenation buffer. */
    fputc('"', out); ha_json_contents(out, id.kind); fputc(':', out);
    ha_json_contents(out, id.key); fputc('"', out);
}

static void ha_json_record(FILE *out, const HaRecord *r)
{
    static const char *const assessments[] = {"ACCEPTED", "REJECTED", "UNRESOLVED"};
    const HaProvenance *p = &r->provenance;
    fputs("{\"id\":", out); ha_json_string(out, r->id);
    fputs(",\"source\":", out); ha_json_string(out, r->source);
    fputs(",\"target\":", out); ha_json_string(out, r->target);
    fputs(",\"polarity\":", out); ha_json_string(out, r->polarity == HA_REQUIRE ? "REQUIRE" : "EXCLUDE");
    fputs(",\"assessment\":", out); ha_json_string(out, assessments[r->assessment]);
    fputs(",\"provenance\":{\"origin\":", out); ha_json_string(out, p->origin);
    fputs(",\"source\":", out); ha_json_string(out, p->source);
    fputs(",\"assessment_rule\":", out); ha_json_string(out, p->assessment_rule);
    fputs(",\"assumed_trust\":", out); ha_json_string(out, p->assumed_trust);
    fputs(",\"scope\":{\"snapshots\":[", out); ha_json_string(out, p->snapshots[0]);
    fputc(',', out); ha_json_string(out, p->snapshots[1]);
    fputs("],\"source\":", out); ha_json_string(out, p->scope_source);
    fputs(",\"target\":", out); ha_json_string(out, p->scope_target);
    fputs("}}}", out);
}

static void ha_json_candidates(FILE *out, const HaInput *in, const HaCandidates *c)
{
    static const struct { unsigned bit; const char *text; } diagnostics[] = {
        {HA_MISSING_EVIDENCE, "MISSING_EVIDENCE"},
        {HA_ASSESSMENT_UNRESOLVED, "ASSESSMENT_UNRESOLVED"},
        {HA_EVIDENCE_INCONSISTENT, "EVIDENCE_INCONSISTENT"},
        {HA_STRUCTURALLY_UNSATISFIABLE, "STRUCTURALLY_UNSATISFIABLE"},
        {HA_INVALID_INPUT, "INVALID_INPUT"}
    };
    static const char *const names[] = {"U_H", "C_E", "A_E"};
    size_t i, set;
    bool comma = false;
    fputs("{\"status\":", out); ha_json_string(out, c->supported ? "SUPPORTED" : "UNSUPPORTED");
    fputs(",\"diagnostics\":[", out);
    for (i = 0; i < HA_LENGTH(diagnostics); ++i)
        if (c->diagnostics & diagnostics[i].bit) {
            if (comma) fputc(',', out);
            ha_json_string(out, diagnostics[i].text); comma = true;
        }
    fputs("],\"conditional\":", out);
    if (!c->supported) {
        fputs("null,\"candidate_sets\":null,\"counts\":null,\"predicates\":null,"
              "\"evidence_records\":null,\"assessment_counts\":null,\"relations_examined\":0,\"reason\":", out);
        ha_json_string(out, c->reason); fputc('}', out); return;
    }
    ha_json_bool(out, c->conditional);
    fputs(",\"candidate_sets\":{", out);
    for (set = 0; set < 3; ++set) {
        if (set != 0) fputc(',', out);
        ha_json_string(out, names[set]); fputs(":[", out); comma = false;
        for (i = 0; i < c->universe_count; ++i) {
            if (set >= 1 && !c->evidence[i]) continue;
            if (set == 2 && !c->structure[i]) continue;
            if (comma) fputc(',', out);
            ha_json_relation(out, in, &c->universe[i]); comma = true;
        }
        fputc(']', out);
    }
    fprintf(out, "},\"counts\":{\"U_H\":%zu,\"C_E\":%zu,\"A_E\":%zu},"
            "\"relations_examined\":%zu,\"assessment_counts\":{\"ACCEPTED\":%zu,"
            "\"REJECTED\":%zu,\"UNRESOLVED\":%zu},\"evidence_records\":[",
            c->universe_count, c->evidence_count, c->admissible_count, c->universe_count,
            c->assessment_counts[HA_ACCEPTED], c->assessment_counts[HA_REJECTED],
            c->assessment_counts[HA_UNRESOLVED]);
    for (i = 0; i < in->record_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_record(out, &in->records[i]);
    }
    fputs("],\"predicates\":[", out);
    for (i = 0; i < c->universe_count; ++i) {
        if (i != 0) fputc(',', out);
        fputs("{\"association\":", out); ha_json_relation(out, in, &c->universe[i]);
        fputs(",\"evidence_satisfied\":", out); ha_json_bool(out, c->evidence[i]);
        fputs(",\"structure_satisfied\":", out); ha_json_bool(out, c->structure[i]); fputc('}', out);
    }
    fputs("]}", out);
}

static void ha_json_map(FILE *out, const HaInput *in, const HaValue values[HA_N])
{
    static const char *const symbols[] = {"0", "lambda", "rho"};
    size_t i;
    fputc('{', out);
    for (i = 0; i < HA_N; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_string(out, in->left.occurrences[i]); fputc(':', out);
        ha_json_string(out, symbols[values[i]]);
    }
    fputc('}', out);
}

static void ha_json_outcome(FILE *out, const HaInput *in, const HaAlternative *a)
{
    if (a->rejection_certified) fputs("{\"tag\":\"REJECT\"}", out);
    else {
        fputs("{\"tag\":\"ACCEPT\",\"material\":", out);
        ha_json_map(out, in, a->construction.values); fputc('}', out);
    }
}

static void ha_json_update(FILE *out, const HaUpdate *u)
{
    static const char *const symbols[] = {"0", "lambda", "rho"};
    fputs("{\"id\":", out); ha_json_string(out, u->id);
    fputs(",\"side\":", out); ha_json_string(out, u->side == HA_LEFT ? "left" : "right");
    fputs(",\"target\":", out); ha_json_string(out, u->target);
    fputs(",\"value\":", out); ha_json_string(out, symbols[u->value]);
    fputs(",\"mandatory\":true}", out);
}

static void ha_json_obligation(FILE *out, const HaObligation *o)
{
    static const char *const symbols[] = {"0", "lambda", "rho"};
    fputs("{\"id\":", out); ha_json_conjunct_id(out, o->id);
    fputs(",\"kind\":", out); ha_json_string(out, o->intention == NULL ? "PRESERVE" : "UPDATE");
    if (o->intention != NULL) {
        fputs(",\"intention\":", out); ha_json_string(out, o->intention->id);
        fputs(",\"side\":", out); ha_json_string(out, o->intention->side == HA_LEFT ? "left" : "right");
        fputs(",\"selector\":", out); ha_json_string(out, o->intention->target);
    }
    fputs(",\"target\":", out); ha_json_string(out, o->target);
    fputs(",\"value\":", out); ha_json_string(out, symbols[o->value]); fputc('}', out);
}

static void ha_json_decision(FILE *out, const HaInput *in, const HaMaterial *m,
                             const HaAlternative *a)
{
    const HaConstruction *c = &a->construction;
    const HaDecision *d = c->decision;
    size_t i, kind;
    fputs("{\"id\":", out); ha_json_string(out, d->id);
    fputs(",\"authorization\":", out); ha_json_string(out, d->authorization);
    for (kind = 0; kind < 2; ++kind) {
        bool comma = false;
        fputs(kind == 0 ? ",\"retained_intentions\":[" : ",\"waived_intentions\":[", out);
        for (i = 0; i < m->update_count; ++i) {
            const HaUpdate *u = &m->updates[i];
            if (ha_find(kind == 0 ? d->retained : d->waived,
                        kind == 0 ? d->retained_count : d->waived_count, u->id) < 0) continue;
            if (comma) fputc(',', out);
            ha_json_update(out, u); comma = true;
        }
        fputc(']', out);
    }
    fputs(",\"obligations\":[", out);
    for (i = 0; i < c->obligation_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_obligation(out, &c->obligations[i]);
    }
    fputs("],\"W_phi_d\":[", out);
    if (c->equalities_consistent) ha_json_map(out, in, c->values);
    fputs("],\"witnesses\":[", out);
    if (c->equalities_consistent) {
        fputs("{\"material\":", out); ha_json_map(out, in, c->values);
        fputs(",\"satisfied\":[", out);
        for (i = 0; i < c->obligation_count; ++i) {
            if (i != 0) fputc(',', out);
            ha_json_conjunct_id(out, c->obligations[i].id);
        }
        fputs("]}", out);
    }
    fputs("],\"rejection_certificate\":", out);
    if (!a->rejection_certified) fputs("null", out);
    else {
        fputc('[', out);
        for (i = 0; i < a->rejection.row_count; ++i) {
            const HaRejectionRow *row = &a->rejection.rows[i];
            size_t j;
            if (i != 0) fputc(',', out);
            fputs("{\"material\":", out); ha_json_map(out, in, row->values);
            fputs(",\"violated\":[", out);
            for (j = 0; j < row->violated_count; ++j) {
                if (j != 0) fputc(',', out);
                ha_json_conjunct_id(out, row->violated[j]);
            }
            fputs("]}", out);
        }
        fputc(']', out);
    }
    fputs(",\"outcomes\":[", out); ha_json_outcome(out, in, a); fputs("]}", out);
}

static void ha_json_material(FILE *out, const HaInput *in, const HaCandidates *c,
                             const HaNamedMaterial *named, const HaMaterials *result)
{
    const HaMaterial *m = &named->input;
    size_t i, j, k;
    bool comma = false;
    fputs("{\"scientific_claim\":\"INCONCLUSIVE\",\"independent_comparison\":", out);
    ha_json_string(out, named->comparison);
    if (!result->policy_supported) {
        fputs(",\"policy_status\":\"UNSUPPORTED\",\"observable_status\":\"NOT_EVALUATED\","
              "\"diagnostics\":[\"POLICY_UNSUPPORTED\"],\"associations\":null,"
              "\"observable_classes\":null,\"reason\":", out);
        ha_json_string(out, result->reason); fputc('}', out); return;
    }
    fputs(",\"policy_status\":\"SUPPORTED\",\"observable_status\":", out);
    ha_json_string(out, result->observable_defined ? "DEFINED" : "OBSERVABLE_UNDEFINED");
    fputs(",\"diagnostics\":[", out);
    if (!result->observable_defined) {
        ha_json_string(out, "OBSERVABLE_UNDEFINED"); comma = true;
    }
    if (ha_equal(named->comparison, "INCOMPLETE")) {
        if (comma) fputc(',', out);
        ha_json_string(out, "INDEPENDENT_COMPARISON_INCOMPLETE"); comma = true;
    }
    if (c->conditional) {
        if (comma) fputc(',', out);
        ha_json_string(out, "ASSESSMENT_UNRESOLVED"); comma = true;
    }
    if (c->admissible_count == 0) {
        if (comma) fputc(',', out);
        ha_json_string(out, "NO_ADMISSIBLE_ASSOCIATIONS");
    }
    fputs("],\"associations\":[", out);
    /* Alternatives are the Cartesian association/decision result of the
     * component. Group for serialization without discarding any decision.
     * W_phi is an extensional union; the decision outcome records stay distinct.
     */
    for (i = 0; i < result->alternative_count; i += m->decision_count) {
        bool rejected = true;
        if (i != 0) fputc(',', out);
        fputs("{\"association\":", out); ha_json_relation(out, in, &result->alternatives[i].association);
        fputs(",\"decisions\":[", out);
        for (j = i; j < i + m->decision_count; ++j) {
            if (j != i) fputc(',', out);
            ha_json_decision(out, in, m, &result->alternatives[j]);
            if (!result->alternatives[j].rejection_certified) rejected = false;
        }
        fputs("],\"W_phi\":[", out); comma = false;
        for (j = i; j < i + m->decision_count; ++j) {
            const HaAlternative *a = &result->alternatives[j];
            if (!a->construction.equalities_consistent) continue;
            for (k = i; k < j; ++k)
                if (result->alternatives[k].construction.equalities_consistent &&
                    ha_same_outcome(a, &result->alternatives[k])) break;
            if (k != j) continue;
            if (comma) fputc(',', out);
            ha_json_map(out, in, a->construction.values); comma = true;
        }
        fputs("],\"rejected_under_all_decisions\":", out); ha_json_bool(out, rejected);
        fputs(",\"outcomes\":[", out);
        for (j = i; j < i + m->decision_count; ++j) {
            const HaAlternative *a = &result->alternatives[j];
            if (j != i) fputc(',', out);
            fputs("{\"decision\":", out); ha_json_string(out, a->construction.decision->id);
            fputs(",\"outcome\":", out); ha_json_outcome(out, in, a); fputc('}', out);
        }
        fputs("]}", out);
    }
    fputs("],\"observable_classes\":", out);
    if (!result->observable_defined) { fputs("null}", out); return; }
    fputc('[', out);
    for (i = 0; i < result->class_count; ++i) {
        for (j = 0; j < result->alternative_count; ++j)
            if (result->class_of[j] == i) break;
        if (i != 0) fputc(',', out);
        fputs("{\"observable\":", out); ha_json_outcome(out, in, &result->alternatives[j]);
        fputs(",\"members\":[", out); comma = false;
        for (j = 0; j < result->alternative_count; ++j) {
            const HaAlternative *a = &result->alternatives[j];
            if (result->class_of[j] != i) continue;
            if (comma) fputc(',', out);
            fputs("{\"association\":", out); ha_json_relation(out, in, &a->association);
            fputs(",\"decision\":", out); ha_json_string(out, a->construction.decision->id);
            fputc('}', out); comma = true;
        }
        fputs("]}", out);
    }
    fputs("]}", out);
}

typedef struct {
    const char *id;
    const HaNamedCandidate *candidate;
    const HaNamedMaterial *material;
} HaSelection;

static bool ha_select(const char *id, HaSelection *selection)
{
    size_t i;
    const char *candidate_id = id;
    *selection = (HaSelection){0};
    for (i = 0; i < HA_LENGTH(ha_named_materials); ++i)
        if (ha_equal(id, ha_named_materials[i].id)) {
            selection->material = &ha_named_materials[i];
            candidate_id = selection->material->candidate_id;
            break;
        }
    for (i = 0; i < HA_LENGTH(ha_named_candidates); ++i)
        if (ha_equal(candidate_id, ha_named_candidates[i].id)) {
            selection->id = id;
            selection->candidate = &ha_named_candidates[i];
            return true;
        }
    return false;
}

static int ha_cli_error(FILE *err, const char *reason, int status)
{
    fputs(status == 2 ? "{\"status\":\"UNSUPPORTED\",\"diagnostics\":[\"INVALID_INPUT\"],\"reason\":" :
          "{\"status\":\"FAIL\",\"diagnostics\":[\"SELF_CHECK_FAILED\"],\"reason\":", err);
    ha_json_string(err, reason);
    fputs(",\"qualification\":\"NOT_QUALIFIED_PHASE_A\"}\n", err);
    return status;
}

/* Deliberately bounded CLI subset: --fixture ID... (F13/M05 group expansion),
 * --list, --help. No --manifest, --compare, JSON input, abbreviated options or
 * argument repair. Use exp007_reference.py --fixture ... --compare C11.json.
 * Validate the entire selection BEFORE any stdout; fixture-level unsupported
 * results (F13/M05-P) are successful bounded operations, as in the reference.
 * 0: operation succeeded; 1: internal verification/output failure;
 * 2: malformed or unsupported request. Metadata/counters are implementation-owned.
 */
static int ha_cli(int argc, char **argv, FILE *out, FILE *err)
{
    HaSelection selections[HA_MAX_CASES];
    size_t count = 0, i, j;
    bool listing = argc == 2 && ha_equal(argv[1], "--list");
    if (argc == 2 && ha_equal(argv[1], "--help")) {
        fputs("Usage: historical_associations --fixture ID [ID ...] | --list | --help\n"
              "Named frozen inputs only; F13 and M05 expand their variants.\n"
              "Compare with exp007_reference.py --fixture ID ... --compare /tmp/c11.json\n"
              "Exit: 0 bounded operation; 1 verification/output failure; 2 invalid request.\n", out);
        if (fflush(out) != 0 || ferror(out))
            return ha_cli_error(err, "output write failed", 1);
        return 0;
    }
    if (!listing) {
        if (argc < 3 || !ha_equal(argv[1], "--fixture"))
            return ha_cli_error(err, "use --fixture ID [ID ...], --list or --help", 2);
        for (i = 2; i < (size_t)argc; ++i) {
            static const char *const f13[] = {"F13-duplicated_handle", "F13-foreign_handle",
                                             "F13-invalid_tree", "F13-invalid_root"};
            static const char *const m05[] = {"M05-P", "M05-O", "M05-I"};
            const char *single[] = {argv[i]};
            const char *const *ids = single;
            size_t n = 1, k;
            if (ha_equal(argv[i], "F13")) { ids = f13; n = HA_LENGTH(f13); }
            if (ha_equal(argv[i], "M05")) { ids = m05; n = HA_LENGTH(m05); }
            for (k = 0; k < n; ++k) {
                if (count >= HA_MAX_CASES)
                    return ha_cli_error(err, "fixture selections must be distinct and bounded", 2);
                if (!ha_select(ids[k], &selections[count]))
                    return ha_cli_error(err, "unknown fixture selection or unsupported option", 2);
                for (j = 0; j < count; ++j)
                    if (ha_equal(ids[k], selections[j].id))
                        return ha_cli_error(err, "fixture selections must be distinct and bounded", 2);
                ++count;
            }
        }
        /* Preflight certificates before emitting any part of a result. */
        for (i = 0; i < count; ++i)
            if (selections[i].material != NULL) {
                HaInput in = ha_named_input(selections[i].candidate);
                HaMaterials material = ha_material_evaluate(&in, &selections[i].material->input);
                if (material.uncertified_count != 0)
                    return ha_cli_error(err, "material alternative lacks verified evidence", 1);
            }
    }
    fputs("{\"schema\":\"" HA_SCHEMA "\",\"protocol_sha256\":\"" HA_PROTOCOL_SHA256 "\","
          "\"qualification\":\"NOT_QUALIFIED_PHASE_A\","
          "\"metadata\":{\"implementation\":\"C11 bounded named fixtures; direct construction\"}", out);
    if (listing) {
        fputs(",\"fixtures\":[\"F13\",\"M05\"", out);
        for (i = 0; i < HA_LENGTH(ha_named_candidates); ++i) {
            fputc(',', out); ha_json_string(out, ha_named_candidates[i].id);
        }
        for (i = 0; i < HA_LENGTH(ha_named_materials); ++i) {
            fputc(',', out); ha_json_string(out, ha_named_materials[i].id);
        }
        fputc(']', out);
    } else {
        fputs(",\"results\":[", out);
        for (i = 0; i < count; ++i) {
            HaInput in = ha_named_input(selections[i].candidate);
            HaCandidates candidate = ha_evaluate(&in);
            if (i != 0) fputc(',', out);
            fputs("{\"id\":", out); ha_json_string(out, selections[i].id);
            fputs(",\"candidate\":", out); ha_json_candidates(out, &in, &candidate);
            if (selections[i].material != NULL) {
                HaMaterials material = ha_material_evaluate(&in, &selections[i].material->input);
                fputs(",\"material\":", out);
                ha_json_material(out, &in, &candidate, selections[i].material, &material);
            }
            fputc('}', out);
        }
        fputc(']', out);
    }
    fputs("}\n", out);
    if (fflush(out) != 0 || ferror(out)) return ha_cli_error(err, "output write failed", 1);
    return 0;
}

#ifndef HA_NO_MAIN
int main(int argc, char **argv)
{
#ifdef SIGPIPE
    /* CLI boundary only: let stdio detect broken pipes without a handler. */
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR)
        return ha_cli_error(stderr, "SIGPIPE setup failed", 1);
#endif
    return ha_cli(argc, argv, stdout, stderr);
}
#endif
