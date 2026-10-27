package example;

/**
 * Coordinates the request deadline budget shared by retry attempts.
 *
 * <p>All stored and returned durations are monotonic milliseconds; wall-clock time
 * cannot extend a request. Budget exhaustion fails closed before another attempt starts.
 * See docs/adr/0001-deadline-policy.md#monotonic-budget for the cross-service choice.
 */
public final class DeadlineBudget {
    private long remainingMillis;

    public DeadlineBudget(long remainingMillis) {
        this.remainingMillis = remainingMillis;
    }

    public boolean tryConsume(long elapsedMillis) {
        remainingMillis -= elapsedMillis;
        return remainingMillis > 0;
    }
}
