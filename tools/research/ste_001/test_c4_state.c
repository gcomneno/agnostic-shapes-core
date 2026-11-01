#include "c4_state.c"

#include <stdio.h>

enum { DRAFT = 1, FINAL = 2 };

typedef struct {
    unsigned calls;
    StePolicyDecision decision;
} PolicyContext;

static StePolicyDecision decide(
    const SteEdit *left,
    const SteEdit *right,
    void *context
)
{
    PolicyContext *ctx = context;

    ++ctx->calls;

    if (left->subject != right->subject)
        return STE_POLICY_UNSUPPORTED;

    if ((left->kind == STE_DELETE &&
         right->kind == STE_SET_PROPERTY) ||
        (left->kind == STE_SET_PROPERTY &&
         right->kind == STE_DELETE))
        return ctx->decision;

    return STE_POLICY_UNSUPPORTED;
}

static int check(
    const char *name,
    SteResult actual,
    SteResult expected,
    unsigned calls,
    unsigned expected_calls
)
{
    int pass = actual == expected && calls == expected_calls;

    printf("%s_GATE=%s expected=%s actual=%s calls=%u\n",
           name,
           pass ? "PASS" : "FAIL",
           ste_result_name(expected),
           ste_result_name(actual),
           calls);

    return pass;
}

int main(void)
{
    const C4State base = {1, 1, DRAFT};
    const C4State deleted = {1, 0, 0};
    const C4State edited = {1, 1, FINAL};
    const C4State mismatched = {99, 1, FINAL};
    const C4State invalid_base = {1, 0, DRAFT};
    const C4State invalid_presence = {1, 2, FINAL};
    const C4State residual_tombstone = {1, 0, 999};

    PolicyContext ctx = {0, STE_REJECT};
    const StePolicy policy = {decide, &ctx};
    SteResult actual;
    int passed = 1;

#define RUN_CASE(NAME, LEFT, RIGHT, DECISION, EXPECTED, CALLS) \
    do { \
        ctx.calls = 0; \
        ctx.decision = (DECISION); \
        actual = c4_classify(&base, (LEFT), (RIGHT), &policy); \
        passed &= check((NAME), actual, (EXPECTED), \
                        ctx.calls, (CALLS)); \
    } while (0)

    RUN_CASE("C4_DELETE_EDIT_REJECT",
             &deleted, &edited, STE_REJECT, STE_CONFLICT, 1);

    RUN_CASE("C4_DELETE_EDIT_ALLOW",
             &deleted, &edited, STE_ALLOW, STE_COMPATIBLE, 1);

    RUN_CASE("C4_REVERSED_BRANCHES",
             &edited, &deleted, STE_REJECT, STE_CONFLICT, 1);

    RUN_CASE("C4_DELETE_ONLY",
             &deleted, &base, STE_REJECT, STE_COMPATIBLE, 0);

    RUN_CASE("C4_EDIT_ONLY",
             &base, &edited, STE_REJECT, STE_COMPATIBLE, 0);

    RUN_CASE("C4_BOTH_DELETE",
             &deleted, &deleted, STE_REJECT, STE_COMPATIBLE, 0);

    RUN_CASE("C4_BOTH_SAME_EDIT",
             &edited, &edited, STE_REJECT, STE_COMPATIBLE, 0);

    RUN_CASE("C4_UNCHANGED",
             &base, &base, STE_REJECT, STE_COMPATIBLE, 0);

    ctx.calls = 0;
    actual = c4_classify(&base, &deleted, &edited, NULL);
    passed &= check("C4_MISSING_POLICY", actual,
                    STE_UNSUPPORTED, ctx.calls, 0);

    RUN_CASE("C4_UNDECIDED_POLICY",
             &deleted, &edited, STE_POLICY_UNSUPPORTED,
             STE_UNSUPPORTED, 1);

    RUN_CASE("C4_IDENTITY_MISMATCH",
             &deleted, &mismatched, STE_REJECT,
             STE_UNSUPPORTED, 0);

    ctx.calls = 0;
    actual = c4_classify(&base, NULL, &edited, &policy);
    passed &= check("C4_MISSING_STATE", actual,
                    STE_UNSUPPORTED, ctx.calls, 0);

    ctx.calls = 0;
    actual = c4_classify(&invalid_base, &deleted,
                         &edited, &policy);
    passed &= check("C4_INVALID_BASE", actual,
                    STE_UNSUPPORTED, ctx.calls, 0);

    RUN_CASE("C4_INVALID_TOMBSTONE",
             &residual_tombstone, &edited,
             STE_REJECT, STE_CONFLICT, 1);

#undef RUN_CASE

    /*
     * Additional presence-domain assertion, not counted among
     * the fourteen frozen fixture names.
     */
    ctx.calls = 0;
    if (c4_classify(&base, &invalid_presence,
                    &edited, &policy) != STE_UNSUPPORTED ||
        ctx.calls != 0) {
        puts("PRESENCE_DOMAIN_GATE=FAIL");
        passed = 0;
    } else {
        puts("PRESENCE_DOMAIN_GATE=PASS");
    }

    printf("EXP005_BEHAVIOR_GATE=%s\n",
           passed ? "PASS" : "FAIL");

    return passed ? 0 : 1;
}
