# Stack comparison example

Owner: `stack-portfolio-owner`. This is teaching evidence for one offline text
function; the reference shapes are illustrative.

## Reference service

`REFERENCE_SERVICE` offers service and runtime separation. No remote caller or
persistence requirement exists for this objective.

## Reference application

`REFERENCE_APP` offers interactive interface and data boundaries. UI, browser and
database maintenance do not serve a local function.

## How to compare a small combination

`SMALL_COMBINATION` selects only the needed pieces, but cross-runtime composition still
needs an actual caller. The Python standard-library slice covers Unicode transformation
and a local CLI; its interpreter lifecycle remains, and no service or second runtime is
inherited.

`STACK-01 — CHOOSE SMALL PYTHON BOUNDARY`: select the smallest boundary that serves
the accepted outcome. Revisit a larger architecture only when its caller and ongoing
cost are justified. The [study](../studies/2026-07-31-technology-options.md) and
[ADR](../adr/0001-python-standard-library-core.md) own the example decision.
