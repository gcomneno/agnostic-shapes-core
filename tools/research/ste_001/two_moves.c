/*
 * ASHES STE — EXP-006: joint realization of two historical MOVEs.
 *
 * Experimental bounded model. No normative SHAPES operation.
 *
 * Reuse the existing C1 historical-tree representation and
 * validators without changing their implementation.
 */
#include "ste.h"
#include "c1_realization.c"

typedef enum {
    G6_PRESERVE_BOTH,
    G6_SELECT_LEFT,
    G6_SELECT_RIGHT,
    G6_UNDECIDED
} G6Policy;

/*
 * Find the single changed parent incidence in a branch.
 * Content must remain unchanged throughout this experiment.
 */
static int g6_find_move(const State *base, const State *branch)
{
    size_t i;
    int changed = -1;

    for (i = 0; i < base->count; ++i) {
        int bi = find_id(branch, base->nodes[i].historical_id);

        if (bi < 0 ||
            branch->nodes[bi].content != base->nodes[i].content)
            return -1;

        if (!same_parent(base, (int)i, branch, bi)) {
            if (base->nodes[i].parent == NO_PARENT ||
                changed >= 0)
                return -1;

            changed = (int)i;
        }
    }

    return changed;
}

/*
 * Copy a historical parent incidence into the candidate.
 * Both states have already passed the shared-history checks.
 */
static int g6_apply_parent(State *candidate,
                           const State *branch,
                           uint32_t subject)
{
    int ci = find_id(candidate, subject);
    int bi = find_id(branch, subject);
    int bp;
    int cp;

    if (ci < 0 || bi < 0)
        return 0;

    bp = branch->nodes[bi].parent;

    if (bp == NO_PARENT)
        return 0;

    cp = find_id(candidate, branch->nodes[bp].historical_id);

    if (cp < 0)
        return 0;

    candidate->nodes[ci].parent = cp;
    return 1;
}

/*
 * COMPATIBLE always requires a concrete valid witness.
 * Rejected/unsupported results never modify *merged.
 *
 * Identity is supplied externally and never inferred from
 * SHAPES form equality or local array positions.
 */
static SteResult g6_reconcile(
    const State *base,
    const State *left,
    const State *right,
    const G6Policy *policy,
    State *merged
)
{
    int li;
    int ri;
    State candidate;

    if (!base || !left || !right || !merged)
        return STE_UNSUPPORTED;

    if (!valid_tree(base) ||
        !valid_tree(left) ||
        !valid_tree(right) ||
        !same_history(base, left) ||
        !same_history(base, right))
        return STE_UNSUPPORTED;

    li = g6_find_move(base, left);
    ri = g6_find_move(base, right);

    if (li < 0 || ri < 0 || !policy)
        return STE_UNSUPPORTED;

    switch (*policy) {
    case G6_SELECT_LEFT:
        candidate = *left;
        break;

    case G6_SELECT_RIGHT:
        candidate = *right;
        break;

    case G6_PRESERVE_BOTH:
        candidate = *base;

        if (li == ri) {
            int lbi = find_id(left, base->nodes[li].historical_id);
            int rbi = find_id(right, base->nodes[ri].historical_id);

            if (!same_parent(left, lbi, right, rbi))
                return STE_CONFLICT;
        }

        if (!g6_apply_parent(
                &candidate, left, base->nodes[li].historical_id) ||
            !g6_apply_parent(
                &candidate, right, base->nodes[ri].historical_id))
            return STE_UNSUPPORTED;

        break;

    case G6_UNDECIDED:
        return STE_UNSUPPORTED;

    default:
        return STE_UNSUPPORTED;
    }

    if (!valid_tree(&candidate))
        return STE_CONFLICT;

    /*
     * For PRESERVE_BOTH, check both requested incidences
     * against the final concrete witness.
     */
    if (*policy == G6_PRESERVE_BOTH) {
        int cli = find_id(&candidate, base->nodes[li].historical_id);
        int cri = find_id(&candidate, base->nodes[ri].historical_id);
        int lli = find_id(left, base->nodes[li].historical_id);
        int rri = find_id(right, base->nodes[ri].historical_id);

        if (!same_parent(&candidate, cli, left, lli) ||
            !same_parent(&candidate, cri, right, rri))
            return STE_CONFLICT;
    }

    *merged = candidate;
    return STE_COMPATIBLE;
}

/* Tests will include this translation unit directly. */
