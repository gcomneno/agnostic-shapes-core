/*
 * ASHES STE — C1 historical MOVE plus content update.
 * Experimental pointed realization, not a SHAPES operator.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

enum { MAX_NODES = 16, NO_PARENT = -1 };

typedef struct {
    uint32_t historical_id;
    int parent;
    int content;
} Node;

typedef struct {
    size_t count;
    Node nodes[MAX_NODES];
} State;

typedef enum {
    C1_OK,
    C1_INVALID,
    C1_UNSUPPORTED,
    C1_POLICY_REJECTED
} C1Result;

typedef int (*C1Policy)(const State *, void *);

/* Historical identity is supplied, not inferred from structure. */
static int find_id(const State *s, uint32_t id)
{
    size_t i;

    for (i = 0; i < s->count; ++i)
        if (s->nodes[i].historical_id == id)
            return (int)i;

    return -1;
}

static int unique_ids(const State *s)
{
    size_t i, j;

    for (i = 0; i < s->count; ++i)
        for (j = 0; j < i; ++j)
            if (s->nodes[i].historical_id == s->nodes[j].historical_id)
                return 0;

    return 1;
}

static int same_history(const State *a, const State *b)
{
    size_t i;

    if (a->count != b->count ||
        !unique_ids(a) || !unique_ids(b))
        return 0;

    for (i = 0; i < a->count; ++i)
        if (find_id(b, a->nodes[i].historical_id) < 0)
            return 0;

    return 1;
}

static int valid_tree(const State *s)
{
    size_t i, steps;
    int root = -1;
    int current;

    if (s->count == 0 || s->count > MAX_NODES)
        return 0;

    for (i = 0; i < s->count; ++i) {
        int parent = s->nodes[i].parent;

        if (parent == NO_PARENT) {
            if (root >= 0)
                return 0;
            root = (int)i;
        } else if (parent < 0 || (size_t)parent >= s->count) {
            return 0;
        }
    }

    if (root < 0)
        return 0;

    for (i = 0; i < s->count; ++i) {
        current = (int)i;

        for (steps = 0; steps < s->count &&
             current != root; ++steps)
            current = s->nodes[current].parent;

        if (current != root)
            return 0;
    }

    return 1;
}

/* Compare parent identities, never parent-array positions. */
static int same_parent(const State *a, int ai,
                       const State *b, int bi)
{
    int ap = a->nodes[ai].parent;
    int bp = b->nodes[bi].parent;

    if (ap == NO_PARENT || bp == NO_PARENT)
        return ap == NO_PARENT && bp == NO_PARENT;

    return a->nodes[ap].historical_id ==
           b->nodes[bp].historical_id;
}

/*
 * The caller explicitly supplies historical node associations.
 * LEFT must change exactly one parent incidence.
 * RIGHT must change exactly one content value.
 */
static C1Result reconcile_c1(
    const State *base,
    const State *left,
    const State *right,
    C1Policy policy,
    void *context,
    State *merged
)
{
    size_t i;
    size_t move_count = 0, edit_count = 0;
    int edited_left = -1;
    int edited_right = -1;
    State candidate;

    if (!base || !left || !right || !merged || !policy)
        return C1_UNSUPPORTED;

    if (!valid_tree(base) || !valid_tree(left) ||
        !valid_tree(right) ||
        !same_history(base, left) ||
        !same_history(base, right))
        return C1_INVALID;

    for (i = 0; i < base->count; ++i) {
        uint32_t id = base->nodes[i].historical_id;
        int li = find_id(left, id);
        int ri = find_id(right, id);

        if (left->nodes[li].content != base->nodes[i].content ||
            !same_parent(base, (int)i, right, ri))
            return C1_UNSUPPORTED;

        if (!same_parent(base, (int)i, left, li)) {
            if (base->nodes[i].parent == NO_PARENT)
                return C1_UNSUPPORTED;
            ++move_count;
        }

        if (right->nodes[ri].content != base->nodes[i].content) {
            edited_left = li;
            edited_right = ri;
            ++edit_count;
        }
    }

    if (move_count != 1 || edit_count != 1)
        return C1_UNSUPPORTED;

    candidate = *left;
    candidate.nodes[edited_left].content =
        right->nodes[edited_right].content;

    if (!valid_tree(&candidate))
        return C1_INVALID;

    if (!policy(&candidate, context))
        return C1_POLICY_REJECTED;

    *merged = candidate;
    return C1_OK;
}

/*
 * This compilation unit deliberately contains no main().
 * The executable tests will be supplied separately.
 *
 * In EXP-001 all node identities are caller-supplied;
 * the implementation neither discovers them nor proves
 * that the input alternatives are historically complete.
 */
