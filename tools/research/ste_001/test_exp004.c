#include "ste.h"

#include <stdio.h>

/*
 * EXP-004: evidence-admissible associations are supplied.
 * Their completeness and historical provenance are NOT inferred.
 */
static StePolicyDecision exclusive_policy(
    const SteEdit *left, const SteEdit *right, void *context)
{
    (void)context;

    if (left->kind != STE_SET_PROPERTY ||
        right->kind != STE_SET_PROPERTY)
        return STE_POLICY_UNSUPPORTED;

    if (left->subject == right->subject &&
        left->argument != right->argument)
        return STE_REJECT;

    return STE_ALLOW;
}

static StePolicyDecision undecided_policy(
    const SteEdit *left, const SteEdit *right, void *context)
{
    (void)left;
    (void)right;
    (void)context;
    return STE_POLICY_UNSUPPORTED;
}

static int check(const char *name, SteResult actual,
                 SteResult expected)
{
    int pass = actual == expected;
    printf("%s_GATE=%s expected=%s actual=%s\n",
           name, pass ? "PASS" : "FAIL",
           ste_result_name(expected), ste_result_name(actual));
    return pass;
}

int main(void)
{
    const SteEdit left[] = {{STE_SET_PROPERTY, 1, 10}};
    const SteEdit right_same[] = {{STE_SET_PROPERTY, 1, 20}};
    const SteEdit right_distinct[] = {{STE_SET_PROPERTY, 2, 20}};
    const SteEdit invalid[] = {{(SteEditKind)999, 2, 20}};

    const SteAlternative same = {
        {left, 1}, {right_same, 1}
    };
    const SteAlternative distinct = {
        {left, 1}, {right_distinct, 1}
    };
    const SteAlternative alternatives[] = {same, distinct};
    const SteAlternative reversed[] = {distinct, same};
    const SteAlternative harmless[] = {distinct, distinct};
    const SteAlternative malformed = {
        {left, 1}, {invalid, 1}
    };

    const StePolicy policy = {exclusive_policy, NULL};
    const StePolicy undecided = {undecided_policy, NULL};

    int passed = 1;

    passed &= check("C3_CONSEQUENTIAL",
                    ste_classify(alternatives, 2, &policy),
                    STE_AMBIGUOUS);

    passed &= check("C3_REVERSED_ORDER",
                    ste_classify(reversed, 2, &policy),
                    STE_AMBIGUOUS);

    passed &= check("C3_SINGLE_SAME",
                    ste_classify(&same, 1, &policy),
                    STE_CONFLICT);

    passed &= check("C3_SINGLE_DISTINCT",
                    ste_classify(&distinct, 1, &policy),
                    STE_COMPATIBLE);

    /*
     * Both supplied candidates are identical. Equality of their
     * requested material outcomes is a fixture assumption,
     * not something ste_classify proves.
     */
    passed &= check("C3_HARMLESS_MULTIPLICITY",
                    ste_classify(harmless, 2, &policy),
                    STE_COMPATIBLE);

    passed &= check("C3_MISSING_POLICY",
                    ste_classify(alternatives, 2, NULL),
                    STE_UNSUPPORTED);

    passed &= check("C3_UNDECIDED_POLICY",
                    ste_classify(alternatives, 2, &undecided),
                    STE_UNSUPPORTED);

    passed &= check("C3_NO_ALTERNATIVES",
                    ste_classify(NULL, 0, &policy),
                    STE_UNSUPPORTED);

    passed &= check("C3_INVALID_ALTERNATIVE",
                    ste_classify(&malformed, 1, &policy),
                    STE_UNSUPPORTED);

    puts("C3_INCOMPLETE_EVIDENCE_GATE=INCONCLUSIVE");
    puts("HISTORICAL_COMPLETENESS=NOT_ESTABLISHED");
    puts("MATERIAL_OUTCOME_EQUIVALENCE=CALLER_ASSUMPTION");

    printf("EXP004_BEHAVIOR_GATE=%s\n",
           passed ? "PASS" : "FAIL");

    return passed ? 0 : 1;
}
