#include "ste.h"

/*
 * EXP-001 — bounded reconciliation classification.
 *
 * The caller supplies candidate historical associations.
 * The kernel neither discovers those associations nor infers
 * domain semantics from structural equality.
 */

static int valid_edit(const SteEdit *edit)
{
    if (edit == NULL) {
        return 0;
    }

    switch (edit->kind) {
    case STE_MOVE:
    case STE_DELETE:
    case STE_SET_PROPERTY:
        return 1;
    }

    return 0;
}

static int valid_branch(const SteBranch *branch)
{
    size_t i;

    if (branch->count != 0 && branch->edits == NULL) {
        return 0;
    }

    for (i = 0; i < branch->count; ++i) {
        if (!valid_edit(&branch->edits[i])) {
            return 0;
        }
    }

    return 1;
}

static SteResult classify_alternative(
    const SteAlternative *alternative,
    const StePolicy *policy
)
{
    size_t i;
    size_t j;

    if (!valid_branch(&alternative->left) ||
        !valid_branch(&alternative->right)) {
        return STE_UNSUPPORTED;
    }

    /*
     * Both branches are retained as input intentions.
     * No automatic conflict-resolution or edit dropping occurs.
     *
     * Every cross-branch pair is delegated to the interpretation.
     * This includes distinct subjects: domain-wide constraints
     * may cause otherwise disjoint changes to interact.
     */
    if (alternative->left.count != 0 &&
        alternative->right.count != 0 &&
        (policy == NULL || policy->conflict == NULL)) {
        return STE_UNSUPPORTED;
    }

    for (i = 0; i < alternative->left.count; ++i) {
        for (j = 0; j < alternative->right.count; ++j) {
            StePolicyDecision decision = policy->conflict(
                &alternative->left.edits[i],
                &alternative->right.edits[j],
                policy->context
            );

            switch (decision) {
            case STE_ALLOW:
                break;

            case STE_REJECT:
                return STE_CONFLICT;

            case STE_POLICY_UNSUPPORTED:
                return STE_UNSUPPORTED;

            default:
                return STE_UNSUPPORTED;
            }
        }
    }

    /*
     * EXP-001 assumes the supplied alternatives and individual
     * branch intentions have already been validated by the caller.
     *
     * Pairwise ALLOW is only a candidate acceptance under that
     * assumption, not proof of a valid merged output.
     */
    return STE_COMPATIBLE;
}

SteResult ste_classify(
    const SteAlternative *alternatives,
    size_t count,
    const StePolicy *policy
)
{
    size_t i;
    SteResult first;

    if (count == 0 || alternatives == NULL) {
        return STE_UNSUPPORTED;
    }

    first = classify_alternative(&alternatives[0], policy);

    if (first == STE_UNSUPPORTED) {
        return STE_UNSUPPORTED;
    }

    for (i = 1; i < count; ++i) {
        SteResult current = classify_alternative(
            &alternatives[i], policy
        );

        /*
         * Unknown evidence prevents a definitive classification.
         * We do not choose an alternative by array position.
         */
        if (current == STE_UNSUPPORTED) {
            return STE_UNSUPPORTED;
        }

        if (current != first) {
            return STE_AMBIGUOUS;
        }
    }

    return first;
}

const char *ste_result_name(SteResult result)
{
    switch (result) {
    case STE_COMPATIBLE:
        return "COMPATIBLE";
    case STE_CONFLICT:
        return "CONFLICT";
    case STE_AMBIGUOUS:
        return "AMBIGUOUS";
    case STE_UNSUPPORTED:
        return "UNSUPPORTED";
    }

    return "UNSUPPORTED";
}
