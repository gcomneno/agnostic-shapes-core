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

static int same_history(const State *a, const State *b)
{
    size_t i, j;

    if (a->count != b->count)
        return 0;

    for (i = 0; i < a->count; ++i) {
        if (a->nodes[i].historical_id != b->nodes[i].historical_id)
            return 0;

        for (j = 0; j < i; ++j)
            if (a->nodes[i].historical_id == a->nodes[j].historical_id)
                return 0;
    }

    return 1;
}

static int valid_tree(const State *s)
{
    size_t i, steps;
    int current;

    if (s->count == 0 || s->count > MAX_NODES)
        return 0;

    if (s->nodes[0].parent != NO_PARENT)
        return 0;

    for (i = 1; i < s->count; ++i) {
        if (s->nodes[i].parent < 0 ||
            (size_t)s->nodes[i].parent >= s->count)
            return 0;
    }

    for (i = 0; i < s->count; ++i) {
        current = (int)i;

        for (steps = 0; steps < s->count && current != 0; ++steps)
            current = s->nodes[current].parent;

        if (current != 0)
            return 0;
    }

    return 1;
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
    size_t moved = 0, edited = 0;
    size_t move_count = 0, edit_count = 0;
    State candidate;

    if (!base || !left || !right || !merged || !policy)
        return C1_UNSUPPORTED;

    if (!valid_tree(base) || !valid_tree(left) ||
        !valid_tree(right) ||
        !same_history(base, left) ||
        !same_history(base, right))
        return C1_INVALID;

    for (i = 0; i < base->count; ++i) {
        if (left->nodes[i].content != base->nodes[i].content ||
            right->nodes[i].parent != base->nodes[i].parent)
            return C1_UNSUPPORTED;

        if (left->nodes[i].parent != base->nodes[i].parent) {
            moved = i;
            ++move_count;
        }

        if (right->nodes[i].content != base->nodes[i].content) {
            edited = i;
            ++edit_count;
        }
    }

    if (move_count != 1 || edit_count != 1 || moved == 0)
        return C1_UNSUPPORTED;

    candidate = *left;
    candidate.nodes[edited].content = right->nodes[edited].content;

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
