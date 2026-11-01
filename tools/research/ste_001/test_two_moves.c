/*
 * ASHES STE — EXP-006 frozen behavioral evidence.
 * Ten controls G1-G10, fixed before execution.
 */
#include "two_moves.c"

#include <stdio.h>
#include <string.h>

static int checks = 0;
static int failures = 0;

static void check_result(
    const char *name,
    SteResult actual,
    SteResult expected,
    const State *output,
    const State *initial,
    const State *witness
)
{
    int result_ok = actual == expected;
    int output_ok;

    if (actual == STE_COMPATIBLE && witness != NULL) {
        output_ok = valid_tree(output) &&
                    memcmp(output, witness, sizeof *output) == 0;
    } else {
        output_ok = memcmp(output, initial, sizeof *output) == 0;
    }

    ++checks;

    if (!result_ok || !output_ok)
        ++failures;

    printf("%s_GATE=%s result=%s witness=%s\n",
           name,
           result_ok && output_ok ? "PASS" : "FAIL",
           result_ok ? "EXPECTED" : "MISMATCH",
           output_ok ? "PASS" : "FAIL");
}

static State initial_output(void)
{
    State result = {0};

    result.count = 1;
    result.nodes[0].historical_id = 999;
    result.nodes[0].parent = NO_PARENT;
    result.nodes[0].content = 777;

    return result;
}

int main(void)
{
    const State base = {
        .count = 3,
        .nodes = {
            {0, NO_PARENT, 0},
            {1, 0, 0},
            {2, 0, 0}
        }
    };

    const State left = {
        .count = 3,
        .nodes = {
            {0, NO_PARENT, 0},
            {1, 2, 0},
            {2, 0, 0}
        }
    };

    const State right = {
        .count = 3,
        .nodes = {
            {0, NO_PARENT, 0},
            {1, 0, 0},
            {2, 1, 0}
        }
    };

    const State base4 = {
        .count = 4,
        .nodes = {
            {0, NO_PARENT, 0},
            {1, 0, 0},
            {2, 0, 0},
            {3, 0, 0}
        }
    };

    const State left4 = {
        .count = 4,
        .nodes = {
            {0, NO_PARENT, 0},
            {1, 2, 0},
            {2, 0, 0},
            {3, 0, 0}
        }
    };

    const State right4 = {
        .count = 4,
        .nodes = {
            {0, NO_PARENT, 0},
            {1, 0, 0},
            {2, 0, 0},
            {3, 2, 0}
        }
    };

    const State combined4 = {
        .count = 4,
        .nodes = {
            {0, NO_PARENT, 0},
            {1, 2, 0},
            {2, 0, 0},
            {3, 2, 0}
        }
    };

    State invalid = left;
    State mismatch = right;
    State output;
    State initial;
    SteResult result;

    const G6Policy preserve = G6_PRESERVE_BOTH;
    const G6Policy select_left = G6_SELECT_LEFT;
    const G6Policy select_right = G6_SELECT_RIGHT;
    const G6Policy undecided = G6_UNDECIDED;

#define RUN(NAME, BASE, LEFT, RIGHT, POLICY, EXPECTED, WITNESS) \
    do { \
        initial = initial_output(); \
        output = initial; \
        result = g6_reconcile((BASE), (LEFT), (RIGHT), \
                              (POLICY), &output); \
        check_result((NAME), result, (EXPECTED), \
                     &output, &initial, (WITNESS)); \
    } while (0)

    RUN("G1_CYCLIC_BOTH",
        &base, &left, &right, &preserve,
        STE_CONFLICT, NULL);

    RUN("G2_CYCLIC_SELECT_LEFT",
        &base, &left, &right, &select_left,
        STE_COMPATIBLE, &left);

    RUN("G3_CYCLIC_SELECT_RIGHT",
        &base, &left, &right, &select_right,
        STE_COMPATIBLE, &right);

    RUN("G4_CYCLIC_NO_POLICY",
        &base, &left, &right, NULL,
        STE_UNSUPPORTED, NULL);

    RUN("G5_CYCLIC_UNDECIDED",
        &base, &left, &right, &undecided,
        STE_UNSUPPORTED, NULL);

    RUN("G6_ACYCLIC_BOTH",
        &base4, &left4, &right4, &preserve,
        STE_COMPATIBLE, &combined4);

    /* A malformed supplied branch contains p <-> q. */
    invalid.nodes[2].parent = 1;

    RUN("G7_INVALID_BRANCH",
        &base, &invalid, &right, &preserve,
        STE_UNSUPPORTED, NULL);

    /* Historical subject 2 is replaced by subject 42. */
    mismatch.nodes[2].historical_id = 42;

    RUN("G8_IDENTITY_MISMATCH",
        &base, &left, &mismatch, &preserve,
        STE_UNSUPPORTED, NULL);

    RUN("G9_MISSING_INPUT",
        NULL, &left, &right, &preserve,
        STE_UNSUPPORTED, NULL);

    /*
     * Independent witness check: PRESERVE_BOTH must not
     * silently return either individual branch.
     */
    RUN("G10_NO_SILENT_SELECTION",
        &base, &left, &right, &preserve,
        STE_CONFLICT, NULL);

#undef RUN

    printf("FROZEN_CASES=%d/10\n", checks - failures);
    printf("EXP006_BEHAVIOR_GATE=%s\n",
           checks == 10 && failures == 0 ? "PASS" : "FAIL");

    return checks == 10 && failures == 0 ? 0 : 1;
}
