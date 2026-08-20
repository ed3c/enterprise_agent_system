# EAS-A GitHub advisory projection adapter

This directory implements issue #10's public GitHub projection lane.

## State machine

```text
SOURCE_REFERENCE_DECLARED
-> PROVIDER_AND_CAPABILITY_RESOLVED
-> ACCESS_POLICY_CHECKED
-> IMMUTABLE_OR_REVISIONED_SUBJECT_CAPTURED
-> CONTENT_DIGESTED
-> PROJECTION_RENDERED
-> FRESHNESS_CHECKED
-> STALE | CURRENT | REFUSED | ABSENT
```

GitHub projections bind repository/reference navigation to exact commit/tree plus a content digest. URLs, issue state, PR state, review state, Actions state, or branch names never become immutable identity by themselves.

Every rendered view has:

```text
projection_authority   ADVISORY_ONLY
canonical_state_mutation false
```

A closed issue or green workflow is observable publication metadata only; it does not grant implementation/runtime/effect/user/Human/merge/release/rollback closure.

`verify_eas_a.py` provides positive fixtures and fail-closed semantic mutations. EAS-C PR #20 is a process vocabulary dependency, not a Git parent of this sibling atom.
