package example;

/** Owns lease renewal and fenced write admission. */
public final class FencedLease {
    public boolean mayWrite(long presentedToken, long currentToken) {
        return presentedToken == currentToken;
    }
}
