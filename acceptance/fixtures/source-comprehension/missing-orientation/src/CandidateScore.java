package example;

public final class CandidateScore {
    public int score(boolean eligible, int priority) {
        return eligible ? priority : Integer.MIN_VALUE;
    }
}
