#ifndef ASHES_STE_H
#define ASHES_STE_H

#include <stddef.h>
#include <stdint.h>

/*
 * EXP-001: experimental classification of competing transformations.
 *
 * Occurrence identifiers describe externally supplied historical
 * associations. They are NOT intrinsic SHAPES identities.
 *
 * Property values are opaque tokens. Their meaning and compatibility
 * belong to the interpretation.
 */

typedef enum {
    STE_MOVE,
    STE_DELETE,
    STE_SET_PROPERTY
} SteEditKind;

typedef struct {
    SteEditKind kind;
    uint32_t subject;
    uint32_t argument;
} SteEdit;

typedef struct {
    const SteEdit *edits;
    size_t count;
} SteBranch;

typedef struct {
    SteBranch left;
    SteBranch right;
} SteAlternative;

typedef enum {
    STE_ALLOW,
    STE_REJECT,
    STE_POLICY_UNSUPPORTED
} StePolicyDecision;

/*
 * Called for potentially interacting edits.
 *
 * ALLOW means that the interpretation accepts preserving both edits
 * under the supplied scenario. REJECT forbids their combination.
 * Neither decision is inferred from SHAPES equality.
 */
typedef StePolicyDecision (*SteConflictPolicy)(
    const SteEdit *left,
    const SteEdit *right,
    void *context
);

typedef struct {
    SteConflictPolicy conflict;
    void *context;
} StePolicy;

typedef enum {
    STE_COMPATIBLE,
    STE_CONFLICT,
    STE_AMBIGUOUS,
    STE_UNSUPPORTED
} SteResult;

/*
 * Each alternative represents one externally admissible historical
 * association of the two branches.
 *
 * Distinct alternatives must not be selected by array position.
 * If alternatives entail different material classifications, the
 * result is AMBIGUOUS.
 *
 * EXP-001 does not reconstruct an output document or establish
 * completeness of the supplied alternatives.
 */
SteResult ste_classify(
    const SteAlternative *alternatives,
    size_t count,
    const StePolicy *policy
);

const char *ste_result_name(SteResult result);

#endif
