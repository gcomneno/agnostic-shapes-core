#include "c2_state.c"

#include <stdio.h>

typedef struct {
    int calls;
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

    if (left->kind != STE_SET_PROPERTY ||
        right->kind != STE_SET_PROPERTY ||
        left->subject != right->subject)
        return STE_POLICY_UNSUPPORTED;

    return ctx->decision;
}

static int check(
    const char *name,
    SteResult actual,
    SteResult expected,
    int actual_calls,
    int expected_calls
)
{
    int pass = actual == expected &&
               actual_calls == expected_calls;

    printf("%s_GATE=%s expected=%s actual=%s calls=%d\n",
           name, pass ? "PASS" : "FAIL",
           ste_result_name(expected),
           ste_result_name(actual),
           actual_calls);
    return pass;
}

int main(void)
{
    const C2State base = {1, 0};
    const C2State one = {1, 1};
    const C2State two = {1, 2};
    const C2State wrong_id = {99, 2};

    PolicyContext ctx = {0, STE_REJECT};
    StePolicy policy = {decide, &ctx};
    SteResult result;
    int passed = 1;

    ctx.calls = 0;
    ctx.decision = STE_REJECT;
    result = c2_classify(&base, &one, &two, &policy);
    passed &= check("C2_DIVERGENT", result,
                    STE_CONFLICT, ctx.calls, 1);

    ctx.calls = 0;
    result = c2_classify(&base, &one, &one, &policy);
    passed &= check("SAME_UPDATE", result,
                    STE_COMPATIBLE, ctx.calls, 0);

    ctx.calls = 0;
    result = c2_classify(&base, &one, &base, &policy);
    passed &= check("LEFT_ONLY", result,
                    STE_COMPATIBLE, ctx.calls, 0);

    ctx.calls = 0;
    result = c2_classify(&base, &base, &two, &policy);
    passed &= check("RIGHT_ONLY", result,
                    STE_COMPATIBLE, ctx.calls, 0);

    ctx.calls = 0;
    result = c2_classify(&base, &base, &base, &policy);
    passed &= check("UNCHANGED", result,
                    STE_COMPATIBLE, ctx.calls, 0);

    ctx.calls = 0;
    ctx.decision = STE_ALLOW;
    result = c2_classify(&base, &one, &two, &policy);
    passed &= check("POLICY_ALLOW", result,
                    STE_COMPATIBLE, ctx.calls, 1);

    ctx.calls = 0;
    ctx.decision = STE_POLICY_UNSUPPORTED;
    result = c2_classify(&base, &one, &two, &policy);
    passed &= check("POLICY_UNSUPPORTED", result,
                    STE_UNSUPPORTED, ctx.calls, 1);

    result = c2_classify(&base, &one, &two, NULL);
    passed &= check("MISSING_POLICY", result,
                    STE_UNSUPPORTED, 0, 0);

    ctx.calls = 0;
    result = c2_classify(&base, &one, &wrong_id, &policy);
    passed &= check("IDENTITY_MISMATCH", result,
                    STE_UNSUPPORTED, ctx.calls, 0);

    ctx.calls = 0;
    result = c2_classify(NULL, &one, &two, &policy);
    passed &= check("INVALID_INPUT", result,
                    STE_UNSUPPORTED, ctx.calls, 0);

    printf("EXP003_BEHAVIOR_GATE=%s\n",
           passed ? "PASS" : "FAIL");
    return passed ? 0 : 1;
}
