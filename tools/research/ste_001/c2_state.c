/*
 * ASHES STE — EXP-003: state-based C2 classification.
 *
 * Experimental single-property model. Historical IDs and opaque
 * property values are supplied by the caller, not by SHAPES.
 *
 * Classification only: no merged value is constructed.
 */
#include "ste.h"

#include <stdint.h>

typedef struct {
    uint32_t historical_id;
    uint32_t value;
} C2State;

/*
 * Each state represents the same historical subject and property.
 * A change is determined exclusively by comparison against BASE.
 *
 * Policy consultation is required only when both branches actually
 * change the property to different resulting values.
 */
static SteResult c2_classify(
    const C2State *base,
    const C2State *left,
    const C2State *right,
    const StePolicy *policy
)
{
    int left_changed;
    int right_changed;
    SteEdit left_edit;
    SteEdit right_edit;
    StePolicyDecision decision;

    if (base == NULL || left == NULL || right == NULL)
        return STE_UNSUPPORTED;

    if (base->historical_id != left->historical_id ||
        base->historical_id != right->historical_id)
        return STE_UNSUPPORTED;

    left_changed = left->value != base->value;
    right_changed = right->value != base->value;

    if (!left_changed || !right_changed ||
        left->value == right->value)
        return STE_COMPATIBLE;

    if (policy == NULL || policy->conflict == NULL)
        return STE_UNSUPPORTED;

    left_edit = (SteEdit){
        STE_SET_PROPERTY, base->historical_id, left->value
    };
    right_edit = (SteEdit){
        STE_SET_PROPERTY, base->historical_id, right->value
    };

    decision = policy->conflict(
        &left_edit, &right_edit, policy->context
    );

    switch (decision) {
    case STE_ALLOW:
        return STE_COMPATIBLE;
    case STE_REJECT:
        return STE_CONFLICT;
    case STE_POLICY_UNSUPPORTED:
        return STE_UNSUPPORTED;
    }

    return STE_UNSUPPORTED;
}

/*
 * This research unit deliberately has no main().
 * test_c2_state.c supplies the frozen behavioral fixtures.
 */
