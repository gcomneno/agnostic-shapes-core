#include "ste.h"

#include <stdio.h>

/*
 * EXP-001 fixtures.
 * Subjects are supplied historical identifiers, not SHAPES IDs.
 * Policies are interpretation-owned and intentionally local to tests.
 */

static StePolicyDecision document_policy(
    const SteEdit *left,
    const SteEdit *right,
    void *context
)
{
    (void)context;

    if (left->kind == STE_MOVE &&
        right->kind == STE_SET_PROPERTY) {
        return STE_ALLOW;
    }

    if (left->subject == right->subject &&
        left->kind == STE_SET_PROPERTY &&
        right->kind == STE_SET_PROPERTY &&
        left->argument != right->argument) {
        return STE_REJECT;
    }

    if (left->subject == right->subject &&
        left->kind == STE_DELETE &&
        right->kind == STE_SET_PROPERTY) {
        return STE_REJECT;
    }

    return STE_ALLOW;
}

static StePolicyDecision unsupported_policy(
    const SteEdit *left,
    const SteEdit *right,
    void *context
)
{
    (void)left;
    (void)right;
    (void)context;
    return STE_POLICY_UNSUPPORTED;
}

static int check(
    const char *name,
    const SteAlternative *alternatives,
    size_t count,
    const StePolicy *policy,
    SteResult expected
)
{
    SteResult actual = ste_classify(alternatives, count, policy);
    int pass = actual == expected;

    printf("%s_GATE=%s expected=%s actual=%s\n",
           name,
           pass ? "PASS" : "FAIL",
           ste_result_name(expected),
           ste_result_name(actual));

    return pass;
}

int main(void)
{
    const StePolicy policy = {document_policy, NULL};
    const StePolicy undecided = {unsupported_policy, NULL};

    /* C1: historical MOVE and accepted content update. */
    const SteEdit c1_left[] = {{STE_MOVE, 1, 2}};
    const SteEdit c1_right[] = {{STE_SET_PROPERTY, 1, 9}};
    const SteAlternative c1[] = {
        {{c1_left, 1}, {c1_right, 1}}
    };

    /* C2: incompatible updates to the same identified property. */
    const SteEdit c2_left[] = {{STE_SET_PROPERTY, 1, 1}};
    const SteEdit c2_right[] = {{STE_SET_PROPERTY, 1, 2}};
    const SteAlternative c2[] = {
        {{c2_left, 1}, {c2_right, 1}}
    };

    /*
     * C3: two externally admissible historical associations.
     * Same subject conflicts; different subjects are permitted.
     */
    const SteEdit c3_left[] = {{STE_SET_PROPERTY, 1, 1}};
    const SteEdit c3_same[] = {{STE_SET_PROPERTY, 1, 2}};
    const SteEdit c3_other[] = {{STE_SET_PROPERTY, 2, 2}};
    const SteAlternative c3[] = {
        {{c3_left, 1}, {c3_same, 1}},
        {{c3_left, 1}, {c3_other, 1}}
    };

    /* C4: historical deletion versus modification of that section. */
    const SteEdit c4_left[] = {{STE_DELETE, 1, 0}};
    const SteEdit c4_right[] = {{STE_SET_PROPERTY, 1, 5}};
    const SteAlternative c4[] = {
        {{c4_left, 1}, {c4_right, 1}}
    };

    int failures = 0;

    failures += !check("C1", c1, 1, &policy, STE_COMPATIBLE);
    failures += !check("C2", c2, 1, &policy, STE_CONFLICT);
    failures += !check("C3", c3, 2, &policy, STE_AMBIGUOUS);
    failures += !check("C4", c4, 1, &policy, STE_CONFLICT);

    failures += !check("MISSING_POLICY", c1, 1, NULL,
                       STE_UNSUPPORTED);
    failures += !check("UNSUPPORTED_POLICY", c1, 1, &undecided,
                       STE_UNSUPPORTED);

    printf("EXP001_CLASSIFIER_GATE=%s\n",
           failures == 0 ? "PASS" : "FAIL");

    return failures == 0 ? 0 : 1;
}
