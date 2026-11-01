/*
 * ASHES STE — EXP-005: historical DELETE versus content EDIT.
 *
 * Bounded single-leaf research model.
 * Historical identity and existence are explicitly supplied.
 * No SHAPES semantics or merged document construction.
 */
#include "ste.h"

#include <stdint.h>

typedef struct {
    uint32_t historical_id;
    int present;
    uint32_t content;
} C4State;

/*
 * BASE must contain the historical leaf.
 * Deleted-state content is intentionally ignored.
 *
 * Only opposing DELETE and EDIT intentions require policy.
 * STE_ALLOW classifies a policy-authorized resolution; it does
 * not prove that both original intentions survive unchanged.
 */
static SteResult c4_classify(
    const C4State *base,
    const C4State *left,
    const C4State *right,
    const StePolicy *policy
)
{
    int left_deleted;
    int right_deleted;
    int left_edited;
    int right_edited;
    SteEdit delete_edit;
    SteEdit content_edit;
    StePolicyDecision decision;

    if (base == NULL || left == NULL || right == NULL)
        return STE_UNSUPPORTED;

    if (base->historical_id != left->historical_id ||
        base->historical_id != right->historical_id)
        return STE_UNSUPPORTED;

    if (base->present != 1 ||
        (left->present != 0 && left->present != 1) ||
        (right->present != 0 && right->present != 1))
        return STE_UNSUPPORTED;

    left_deleted = left->present == 0;
    right_deleted = right->present == 0;

    left_edited = !left_deleted &&
                  left->content != base->content;
    right_edited = !right_deleted &&
                   right->content != base->content;

    if (!((left_deleted && right_edited) ||
          (right_deleted && left_edited)))
        return STE_COMPATIBLE;

    if (policy == NULL || policy->conflict == NULL)
        return STE_UNSUPPORTED;

    delete_edit = (SteEdit){
        STE_DELETE, base->historical_id, 0
    };

    content_edit = (SteEdit){
        STE_SET_PROPERTY,
        base->historical_id,
        left_edited ? left->content : right->content
    };

    if (left_deleted) {
        decision = policy->conflict(
            &delete_edit, &content_edit, policy->context
        );
    } else {
        decision = policy->conflict(
            &content_edit, &delete_edit, policy->context
        );
    }

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
 * No main() and no public API promotion.
 * test_c4_state.c will exercise the frozen C4 fixtures.
 */
