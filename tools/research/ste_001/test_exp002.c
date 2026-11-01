#include "c1_realization.c"

#include <stdio.h>

enum { DRAFT = 1, FINAL = 2 };

static int accept(const State *state, void *context)
{
    (void)context;
    return valid_tree(state);
}

static int reject(const State *state, void *context)
{
    (void)state;
    (void)context;
    return 0;
}

static int check(const char *name, int condition)
{
    printf("%s_GATE=%s\n", name, condition ? "PASS" : "FAIL");
    return condition;
}

/* Reorder local storage while preserving historical incidences. */
static State permute(const State *source, const int order[3])
{
    State result = {0};
    int old_to_new[3];
    int i;

    result.count = source->count;

    for (i = 0; i < 3; ++i)
        old_to_new[order[i]] = i;

    for (i = 0; i < 3; ++i) {
        int old = order[i];
        int parent = source->nodes[old].parent;

        result.nodes[i] = source->nodes[old];
        result.nodes[i].parent =
            parent == NO_PARENT ? NO_PARENT : old_to_new[parent];
    }

    return result;
}

/* Compare logical states rather than their local array order. */
static int equivalent(const State *a, const State *b)
{
    size_t i;

    if (!valid_tree(a) || !valid_tree(b) ||
        !same_history(a, b))
        return 0;

    for (i = 0; i < a->count; ++i) {
        int j = find_id(b, a->nodes[i].historical_id);

        if (j < 0 ||
            a->nodes[i].content != b->nodes[j].content ||
            !same_parent(a, (int)i, b, j))
            return 0;
    }

    return 1;
}

int main(void)
{
    const int base_order[3] = {2, 0, 1};
    const int left_order[3] = {1, 2, 0};
    const int right_order[3] = {2, 1, 0};

    State base = {
        3, {
            {0, NO_PARENT, 0},
            {1, 0, DRAFT},
            {2, 0, 0}
        }
    };
    State left = base;
    State right = base;
    State expected;
    State pb, pl, pr, merged = {0};
    State invalid;
    int passed = 1;

    left.nodes[1].parent = 2;
    right.nodes[1].content = FINAL;

    expected = left;
    expected.nodes[1].content = FINAL;

    pb = permute(&base, base_order);
    pl = permute(&left, left_order);
    pr = permute(&right, right_order);

    passed &= check(
        "INDEPENDENT_PERMUTATIONS",
        reconcile_c1(&pb, &pl, &pr, accept, NULL, &merged)
            == C1_OK &&
        equivalent(&merged, &expected)
    );

    passed &= check(
        "ROOT_NOT_AT_ZERO",
        find_id(&pb, 0) != 0 &&
        find_id(&pr, 0) != 0 &&
        valid_tree(&pb) &&
        valid_tree(&pr)
    );

    invalid = pr;
    invalid.nodes[0].historical_id =
        invalid.nodes[1].historical_id;
    passed &= check(
        "DUPLICATE_ID",
        reconcile_c1(&pb, &pl, &invalid,
                     accept, NULL, &merged) == C1_INVALID
    );

    invalid = pr;
    invalid.nodes[0].historical_id = 99;
    passed &= check(
        "MISMATCHED_ID",
        reconcile_c1(&pb, &pl, &invalid,
                     accept, NULL, &merged) == C1_INVALID
    );

    invalid = pl;
    invalid.nodes[0].parent = 99;
    passed &= check(
        "INVALID_PARENT",
        reconcile_c1(&pb, &invalid, &pr,
                     accept, NULL, &merged) == C1_INVALID
    );

    invalid = pl;
    invalid.nodes[0].parent = 0;
    passed &= check(
        "SELF_CYCLE",
        reconcile_c1(&pb, &invalid, &pr,
                     accept, NULL, &merged) == C1_INVALID
    );

    invalid = pl;
    invalid.nodes[2].parent = 0;
    passed &= check(
        "DESCENDANT_CYCLE",
        reconcile_c1(&pb, &invalid, &pr,
                     accept, NULL, &merged) == C1_INVALID
    );

    invalid = pl;
    invalid.nodes[2].parent = 1;
    passed &= check(
        "ROOT_MOVE",
        reconcile_c1(&pb, &invalid, &pr,
                     accept, NULL, &merged) != C1_OK
    );

    passed &= check(
        "POLICY_REJECTION",
        reconcile_c1(&pb, &pl, &pr,
                     reject, NULL, &merged) == C1_POLICY_REJECTED
    );

    passed &= check(
        "MISSING_POLICY",
        reconcile_c1(&pb, &pl, &pr,
                     NULL, NULL, &merged) == C1_UNSUPPORTED
    );

    invalid = pl;
    invalid.nodes[0].content = 99;
    passed &= check(
        "UNDECLARED_LEFT_EDIT",
        reconcile_c1(&pb, &invalid, &pr,
                     accept, NULL, &merged) == C1_UNSUPPORTED
    );

    invalid = pr;
    invalid.nodes[1].parent = 0;
    passed &= check(
        "UNDECLARED_RIGHT_MOVE",
        reconcile_c1(&pb, &pl, &invalid,
                     accept, NULL, &merged) == C1_UNSUPPORTED
    );

    printf("EXP002_BEHAVIOR_GATE=%s\n",
           passed ? "PASS" : "FAIL");
    return passed ? 0 : 1;
}
