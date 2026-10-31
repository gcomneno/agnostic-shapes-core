#include "c1_realization.c"

#include <stdio.h>

enum { DRAFT = 1, FINAL = 2 };

static int accept(const State *state, void *context)
{
    (void)context;
    return valid_tree(state);
}

static int reject_final_under_q(const State *state, void *context)
{
    (void)context;
    return state->nodes[1].parent != 2 ||
           state->nodes[1].content != FINAL;
}

static int check(const char *name, int condition)
{
    printf("%s_GATE=%s\n", name, condition ? "PASS" : "FAIL");
    return condition;
}

int main(void)
{
    State base = {
        3, {
            {0, NO_PARENT, 0},
            {1, 0, DRAFT},
            {2, 0, 0}
        }
    };
    State left = base;
    State right = base;
    State merged = {0};
    State invalid;
    C1Result result;
    int passed = 1;

    left.nodes[1].parent = 2;
    right.nodes[1].content = FINAL;

    result = reconcile_c1(
        &base, &left, &right, accept, NULL, &merged
    );

    passed &= check(
        "C1_MERGE",
        result == C1_OK &&
        valid_tree(&merged) &&
        merged.count == 3 &&
        merged.nodes[0].historical_id == 0 &&
        merged.nodes[1].historical_id == 1 &&
        merged.nodes[2].historical_id == 2 &&
        merged.nodes[0].parent == NO_PARENT &&
        merged.nodes[1].parent == 2 &&
        merged.nodes[2].parent == 0 &&
        merged.nodes[1].content == FINAL
    );

    invalid = left;
    invalid.nodes[0].parent = 2;
    passed &= check(
        "N1_ROOT_MOVE",
        reconcile_c1(&base, &invalid, &right,
                     accept, NULL, &merged) != C1_OK
    );

    invalid = left;
    invalid.nodes[1].parent = 1;
    passed &= check(
        "N2_SELF_CYCLE",
        reconcile_c1(&base, &invalid, &right,
                     accept, NULL, &merged) != C1_OK
    );

    invalid = left;
    invalid.nodes[2].parent = 1;
    passed &= check(
        "N2_DESCENDANT_CYCLE",
        reconcile_c1(&base, &invalid, &right,
                     accept, NULL, &merged) != C1_OK
    );

    passed &= check(
        "N3_POLICY_REJECTION",
        reconcile_c1(&base, &left, &right,
                     reject_final_under_q, NULL, &merged)
            == C1_POLICY_REJECTED
    );

    invalid = right;
    invalid.nodes[1].historical_id = 99;
    passed &= check(
        "N4_HISTORICAL_IDENTITY",
        reconcile_c1(&base, &left, &invalid,
                     accept, NULL, &merged) != C1_OK
    );

    invalid = right;
    invalid.nodes[2].parent = 1;
    passed &= check(
        "RIGHT_UNDECLARED_MOVE",
        reconcile_c1(&base, &left, &invalid,
                     accept, NULL, &merged) != C1_OK
    );

    passed &= check(
        "MISSING_POLICY",
        reconcile_c1(&base, &left, &right,
                     NULL, NULL, &merged) == C1_UNSUPPORTED
    );

    printf("C1_BEHAVIOR_GATE=%s\n", passed ? "PASS" : "FAIL");
    return passed ? 0 : 1;
}
