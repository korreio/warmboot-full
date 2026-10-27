# Deadline policy

## Monotonic budget

One monotonic budget spans all retry attempts so retries cannot extend the caller's
deadline. Exhaustion stops before a new external attempt begins.
