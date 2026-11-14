/*
 * ASHES / STE EXP-007 Phase C: DRAFT bounded persistent matrix worker.
 * Scientific authority: frozen EXP007_PROTOCOL.md V1. Operational encoding:
 * EXP007_CAMPAIGN_PLAN.json, input_encoding (hash pinned below).
 * This is an input/output adapter, not a campaign driver or qualification.
 * EXP-007 remains INCONCLUSIVE; EXP-004 historical completeness remains
 * INCONCLUSIVE and material equivalence remains CALLER_ASSUMPTION.
 *
 * Build (products outside the repository):
 * cc -std=c11 -Wall -Wextra -Wpedantic -Werror -O2 \
 *    tools/research/ste_001/exp007_campaign.c -o /tmp/exp007-campaign
 *
 * Streaming protocol ste-exp007-worker-v1, no command-line options:
 *   EXP007/1 <request_id> EVAL <instance_id> <config_id> LF
 * Example (no space before LF):
 *   EXP007/1 smoke-01 EVAL star/S_free 65
 * Exactly five tokens, separated by exactly one ASCII space, no leading or
 * trailing whitespace, CR, NUL, quoting, comments, or blank lines. A frame
 * is at most 512 bytes excluding LF. request_id has 1..64 ASCII characters
 * from [A-Za-z0-9._:-]. config_id is canonical decimal 0..262143 (no sign,
 * leading zeros, or numeric coercion). instance_id is exactly star/S_free
 * or F09-geometry/S_inc; selecting the latter explicitly authorizes the
 * frozen unchanged-incidence assumption. No caller-supplied geometry or
 * evidence overrides exist. Operations other than EVAL, including MATERIAL,
 * produce UNSUPPORTED_OPERATION, never a fabricated material result.
 *
 * Each LF-terminated frame gets exactly one flushed JSON object plus LF on
 * stdout, including rejected frames. An EOF fragment gets TRUNCATED_REQUEST,
 * never evaluation; an oversized fragment instead gets FRAME_TOO_LONG.
 * Oversized frames are drained through LF with constant storage and rejected;
 * their request_id is null. A normal malformed frame
 * echoes request_id only if its first two tokens form a valid version/ID
 * prefix (even when its remainder is invalid). Otherwise request_id is null.
 * response_id and request_index are the same one-based frame/fragment ordinal
 * within this process, including errors. Caller IDs may repeat for replay;
 * no unbounded deduplication history is retained. The future orchestrator
 * owns unique execution IDs, run/attempt binding, ledgers, and suite credit.
 * case_id uses the plan's stable MATRIX case namespace, not its dry-run
 * namespace: receiving a result alone discharges no campaign obligation.
 * Restarting the same input stream produces identical output bytes.
 *
 * EVALUATED means the C evaluator returned supported data, including empty
 * C_E/A_E and negative diagnostics. It never means scientific PASS. Errors
 * have candidate:null and zero work unless an evaluator call actually ran.
 * candidate uses the existing exact C serializer: concrete pair sets U_H,
 * C_E, A_E, per-candidate predicates, all evidence/provenance, assessments,
 * diagnostics, and relations_examined. input retains roots, snapshot IDs,
 * incidence, occurrence order and profile authorization; roots are not pairs.
 * pair_states is in i=3*source_index+target_index order.
 * Work is per request, not cumulative or a projected coverage obligation.
 * evaluator_calls counts actual calls made here. The remaining counters use
 * the returned universe_count and assessment_counts: in frozen ha_evaluate,
 * every generated candidate executes both predicates once, independently of
 * evidence success, and each record is assessed once. These are whole
 * candidate/predicate calls, not inner record tests, triple loop iterations,
 * timing measurements, or Python's 512 relation classifications. No solver
 * is run again merely to calculate counters. Reference/material work is 0.
 *
 * Process contract: clean EOF exits 0 if all frames were evaluated, otherwise
 * 2 if any request was rejected. Input/output/setup/internal errors exit 1.
 * EINTR on read is retried, preserving the partial frame. Other read errors
 * emit INPUT_ERROR for the pending input attempt, then exit 1 if output works.
 * SIGPIPE is ignored only in main; broken pipes/write/flush failures exit 1
 * immediately, with no further reads or attempted error response on stdout.
 * Every response checks sticky FILE write errors AND fflush, including writes
 * inside the reused serializer. A failed write may leave an incomplete final
 * JSON line: the receiver must require both LF framing and process success;
 * it must not interpret a prefix as a result. Other signals retain inherited
 * dispositions; forced termination promises no response for pending input.
 * No request can preempt a partial frame; the sender must finish it or close
 * input. At UINT64_MAX responses, further input fails closed with exit 1.
 * stdout contains only protocol responses; no startup, help or exit summary.
 *
 * Fixed-size C storage, no allocation, files, oracle execution, fixture JSON
 * parsing, local caches, or material processing. A private fixed stdio buffer
 * is supplied; response size is bounded by 18 fixed-provenance records and
 * six candidates. Protocol/plan hashes are DECLARED build identities, not a
 * claim that this executable verified local artifacts: the future runner
 * must hash its inputs and bind source, compiler and executable externally.
 *
 * Bounded implementation verification scope (not a new scientific experiment):
 * both frozen instances x {0,1,2,3,5,63,64,65,272,262143}; exact base-4 and
 * provenance checks, stream accounting/replay and malformed/process probes.
 * Falsifiers: any encoding, exact set/predicate, identity, diagnosis, work,
 * framing, or exit-status disagreement. Outcomes are implementation checks
 * passed/failed or an explicitly unsupported comparison, never qualification.
 */
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <unistd.h>

#define HA_NO_MAIN
#include "historical_associations.c"

#define CW_SCHEMA "ste-exp007-worker-v1"
#define CW_PLAN_SHA256 "f817bb6267f8eee2ddcc3bc24de498e00d19a412599d3df3ff31ce79f2e592bf"
enum { CW_LINE = 512, CW_ID = 64, CW_RECORDS = 18, CW_TEXT = 128 };

typedef struct {
    const char *id, *token, *fixture, *suite;
} CwInstance;

static const CwInstance cw_instances[] = {
    {"star/S_free", "star-s-free", "F01", "matrix_star_s_free"},
    {"F09-geometry/S_inc", "f09-s-inc", "F09", "matrix_f09_s_inc"}
};

typedef struct {
    char request_id[CW_ID + 1];
    const CwInstance *instance;
    unsigned config;
} CwRequest;

typedef struct {
    HaInput input;
    unsigned states[HA_N * HA_N];
    char ids[CW_RECORDS][CW_TEXT];
    char sources[CW_RECORDS][CW_TEXT];
    char case_id[CW_TEXT];
} CwCase;

static bool cw_id_character(unsigned char c)
{
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
        (c >= '0' && c <= '9') || c == '.' || c == '_' || c == ':' || c == '-';
}

/* Recover identity without ever treating NUL as the end of a binary frame. */
static void cw_identity(const char *line, size_t length, CwRequest *request)
{
    static const char prefix[] = "EXP007/1 ";
    size_t start = sizeof(prefix) - 1, end = start, i;
    if (length < start || memcmp(line, prefix, start) != 0) return;
    while (end < length && line[end] != ' ') ++end;
    if (end == start || end - start > CW_ID) return;
    for (i = start; i < end; ++i)
        if (!cw_id_character((unsigned char)line[i])) return;
    memcpy(request->request_id, line + start, end - start);
    request->request_id[end - start] = '\0';
}

static const char *cw_parse(char *line, size_t length, CwRequest *request)
{
    char *tokens[5];
    size_t i, count = 1;
    unsigned value = 0;
    cw_identity(line, length, request);
    if (length == 0) return "MALFORMED_REQUEST";
    for (i = 0; i < length; ++i)
        if ((unsigned char)line[i] < 32 || (unsigned char)line[i] > 126)
            return "MALFORMED_REQUEST";
    line[length] = '\0';
    tokens[0] = line;
    for (i = 0; i < length; ++i)
        if (line[i] == ' ') {
            if (i == 0 || line[i - 1] == '\0' || i + 1 == length || count == 5)
                return "MALFORMED_REQUEST";
            line[i] = '\0';
            tokens[count++] = line + i + 1;
        }
    if (count != 5) return "MALFORMED_REQUEST";
    if (strcmp(tokens[0], "EXP007/1") != 0) return "UNSUPPORTED_VERSION";
    if (request->request_id[0] == '\0') return "INVALID_REQUEST_ID";
    if (strcmp(tokens[2], "EVAL") != 0) return "UNSUPPORTED_OPERATION";
    for (i = 0; i < HA_LENGTH(cw_instances); ++i)
        if (strcmp(tokens[3], cw_instances[i].id) == 0)
            request->instance = &cw_instances[i];
    if (request->instance == NULL) return "UNSUPPORTED_INSTANCE";
    if (tokens[4][0] == '\0' || (tokens[4][0] == '0' && tokens[4][1] != '\0'))
        return "INVALID_CONFIG_ID";
    for (i = 0; tokens[4][i] != '\0'; ++i) {
        unsigned digit;
        if (tokens[4][i] < '0' || tokens[4][i] > '9') return "INVALID_CONFIG_ID";
        digit = (unsigned)(tokens[4][i] - '0');
        if (value > (262143u - digit) / 10u) return "INVALID_CONFIG_ID";
        value = 10u * value + digit;
    }
    request->config = value;
    return NULL;
}

static bool cw_formatted(int length, size_t capacity)
{
    return length >= 0 && (size_t)length < capacity;
}

/* Input adapter only: no candidate generation, filters, or structural tests. */
static bool cw_construct(const CwRequest *request, CwCase *work)
{
    HaSelection selection;
    unsigned digits = request->config;
    size_t i;
    *work = (CwCase){0};
    if (!ha_select(request->instance->fixture, &selection) ||
        selection.candidate == NULL || selection.material != NULL) return false;
    work->input = ha_named_input(selection.candidate);
    if (work->input.record_count != 0) return false;
    if (!cw_formatted(snprintf(work->case_id, sizeof(work->case_id),
            "EXP007/C/V1/%s/%s/%06u", request->instance->suite,
            request->instance->id, request->config), sizeof(work->case_id))) return false;
    for (i = 0; i < HA_N * HA_N; ++i) {
        unsigned polarity;
        unsigned state = digits % 4u;
        digits /= 4u;
        work->states[i] = state;
        for (polarity = 1; polarity <= 2; ++polarity) {
            size_t n;
            HaRecord *record;
            const char *name;
            if ((state & polarity) == 0) continue;
            n = work->input.record_count;
            if (n >= CW_RECORDS || n >= HA_RECORDS) return false;
            name = polarity == 1 ? "REQUIRE" : "EXCLUDE";
            if (!cw_formatted(snprintf(work->ids[n], sizeof(work->ids[n]),
                    "EXP007/C/V1/matrix/%s/%06u/pair/%zu/%s",
                    request->instance->token, request->config, i, name),
                    sizeof(work->ids[n]))) return false;
            if (!cw_formatted(snprintf(work->sources[n], sizeof(work->sources[n]),
                    "EXP007_PROTOCOL.md section 6 / %s / config/%06u / pair/%zu",
                    request->instance->token, request->config, i),
                    sizeof(work->sources[n]))) return false;
            record = &work->input.records[n];
            record->id = work->ids[n];
            record->source = work->input.left.occurrences[i / HA_N];
            record->target = work->input.right.occurrences[i % HA_N];
            record->polarity = polarity == 1 ? HA_REQUIRE : HA_EXCLUDE;
            record->assessment = HA_ACCEPTED;
            record->provenance = (HaProvenance){
                "EXP-007 synthetic accepted-polarity matrix", work->sources[n],
                "External synthetic assessment is ACCEPTED for every matrix REQUIRE/EXCLUDE, by frozen section 6 declaration.",
                "Assumed solely for this finite model; provenance truth is not independently verified.",
                {work->input.left.id, work->input.right.id}, record->source, record->target
            };
            ++work->input.record_count;
        }
    }
    return digits == 0;
}

static void cw_snapshot(FILE *out, const HaSnapshot *snapshot)
{
    size_t i;
    fputs("{\"id\":", out); ha_json_string(out, snapshot->id);
    fputs(",\"root\":", out); ha_json_string(out, snapshot->root);
    fputs(",\"vertices\":[", out);
    for (i = 0; i < snapshot->vertex_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_string(out, snapshot->vertices[i]);
    }
    fputs("],\"occurrences\":[", out);
    for (i = 0; i < snapshot->occurrence_count; ++i) {
        if (i != 0) fputc(',', out);
        ha_json_string(out, snapshot->occurrences[i]);
    }
    fputs("],\"incidence\":[", out);
    for (i = 0; i < snapshot->edge_count; ++i) {
        if (i != 0) fputc(',', out);
        fputc('[', out); ha_json_string(out, snapshot->edges[i].source);
        fputc(',', out); ha_json_string(out, snapshot->edges[i].target);
        fputc(']', out);
    }
    fputs("]}", out);
}

static bool cw_response(uint64_t ordinal, const CwRequest *request,
                        const char *error, const CwCase *work,
                        const HaCandidates *candidate, unsigned evaluator_calls)
{
    FILE *out = stdout;
    size_t generated = candidate == NULL ? 0 : candidate->universe_count;
    size_t assessed = candidate == NULL ? 0 :
        candidate->assessment_counts[HA_ACCEPTED] +
        candidate->assessment_counts[HA_REJECTED] +
        candidate->assessment_counts[HA_UNRESOLVED];
    bool unsupported = error != NULL && strncmp(error, "UNSUPPORTED_", 12) == 0;
    int flushed;
    fputs("{\"schema\":\"" CW_SCHEMA "\",\"protocol_sha256\":\"" HA_PROTOCOL_SHA256
          "\",\"plan_sha256\":\"" CW_PLAN_SHA256
          "\",\"qualification\":\"DRAFT_NOT_SCIENTIFICALLY_QUALIFIED\",", out);
    fprintf(out, "\"request_index\":%" PRIu64 ",\"response_id\":%" PRIu64 ",\"request_id\":",
            ordinal, ordinal);
    ha_json_string(out, request->request_id[0] == '\0' ? NULL : request->request_id);
    fputs(",\"status\":", out);
    ha_json_string(out, error == NULL ? "EVALUATED" : unsupported ? "UNSUPPORTED" : "ERROR");
    fputs(",\"error_code\":", out); ha_json_string(out, error);
    fputs(",\"case_id\":", out); ha_json_string(out, work == NULL ? NULL : work->case_id);
    fputs(",\"instance_id\":", out);
    ha_json_string(out, work == NULL ? NULL : request->instance->id);
    fputs(",\"config_id\":", out);
    if (work == NULL) fputs("null", out); else fprintf(out, "%u", request->config);
    fputs(",\"input\":", out);
    if (work == NULL) fputs("null", out);
    else {
        size_t i;
        fputs("{\"snapshots\":{\"left\":", out); cw_snapshot(out, &work->input.left);
        fputs(",\"right\":", out); cw_snapshot(out, &work->input.right);
        fputs("},\"profile\":", out);
        ha_json_string(out, work->input.profile == HA_S_FREE ? "S_free" : "S_inc");
        fputs(",\"assumes_unchanged_incidence\":", out);
        ha_json_bool(out, work->input.assumes_unchanged_incidence);
        fputs(",\"pair_states\":[", out);
        for (i = 0; i < HA_N * HA_N; ++i) {
            if (i != 0) fputc(',', out);
            fprintf(out, "%u", work->states[i]);
        }
        fputs("]}", out);
    }
    fputs(",\"candidate\":", out);
    if (candidate == NULL) fputs("null", out);
    else ha_json_candidates(out, &work->input, candidate);
    fprintf(out, ",\"work\":{\"evaluator_calls\":%u,\"candidates_generated\":%zu,"
            "\"candidate_evaluations\":%zu,\"evidence_predicate_calls\":%zu,"
            "\"structure_predicate_calls\":%zu,\"records_assessed\":%zu,"
            "\"reference_relation_classifications\":0,\"material_evaluations\":0}}\n",
            evaluator_calls, generated, generated, generated, generated, assessed);
    /* ferror is sticky: covers every write, including inherited JSON helpers.
     * Flush even when a previous write failed; never clear output errors. */
    flushed = fflush(out);
    return flushed == 0 && !ferror(out);
}

/* Return -1 on fatal failure; 0 evaluated; 1 rejected without evaluation. */
static int cw_frame(char *line, size_t length, const char *framing_error,
                    uint64_t ordinal)
{
    CwRequest request = {0};
    CwCase work;
    HaCandidates candidate;
    const char *error = framing_error;
    if (error == NULL) error = cw_parse(line, length, &request);
    else if (strcmp(error, "FRAME_TOO_LONG") != 0)
        cw_identity(line, length, &request);
    if (error != NULL)
        return cw_response(ordinal, &request, error, NULL, NULL, 0) ? 1 : -1;
    if (!cw_construct(&request, &work)) {
        if (!cw_response(ordinal, &request, "INTERNAL_CONSTRUCTION_ERROR", NULL, NULL, 0))
            return -1;
        return -1;
    }
    candidate = ha_evaluate(&work.input);
    if (!candidate.supported) {
        if (!cw_response(ordinal, &request, "INTERNAL_EVALUATOR_ERROR", &work, &candidate, 1))
            return -1;
        return -1;
    }
    return cw_response(ordinal, &request, NULL, &work, &candidate, 1) ? 0 : -1;
}

int main(int argc, char **argv)
{
    static char output_buffer[32768];
    char incoming[4096], line[CW_LINE + 1];
    size_t length = 0;
    uint64_t ordinal = 0;
    bool oversized = false, rejected = false;
    (void)ha_cli; /* Include-only seam: retain unused CLI without calling it. */
    (void)argv;
    if (setvbuf(stdout, output_buffer, _IOFBF, sizeof(output_buffer)) != 0) return 1;
#ifdef SIGPIPE
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) return 1;
#endif
    if (argc != 1) {
        CwRequest request = {0};
        return cw_response(1, &request, "UNSUPPORTED_ARGUMENTS", NULL, NULL, 0) ? 2 : 1;
    }
    for (;;) {
        ssize_t count;
        size_t i;
        if (ordinal == UINT64_MAX) return 1;
        count = read(STDIN_FILENO, incoming, sizeof(incoming));
        if (count < 0) {
            if (errno == EINTR) continue;
            if (cw_frame(line, oversized ? 0 : length, "INPUT_ERROR", ++ordinal) < 0)
                return 1;
            return 1;
        }
        if (count == 0) {
            if (length != 0 || oversized) {
                if (cw_frame(line, length, oversized ? "FRAME_TOO_LONG" : "TRUNCATED_REQUEST",
                             ++ordinal) < 0) return 1;
                rejected = true;
            }
            return rejected ? 2 : 0;
        }
        for (i = 0; i < (size_t)count; ++i) {
            if (incoming[i] == '\n') {
                int result;
                if (ordinal == UINT64_MAX) return 1;
                result = cw_frame(line, length, oversized ? "FRAME_TOO_LONG" : NULL, ++ordinal);
                if (result < 0) return 1;
                if (result > 0) rejected = true;
                length = 0;
                oversized = false;
            } else if (length < CW_LINE) line[length++] = incoming[i];
            else oversized = true;
        }
    }
}
