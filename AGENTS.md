\# Agent Rules



Use one task at a time.



Never:

\- analyze all of app.py in one pass

\- run persistent servers without timeout

\- mix unrelated changes

\- refactor business logic without approval



Before editing:

1\. identify target lines/functions

2\. propose minimal plan

3\. wait for confirmation if risk is medium/high



After editing:

1\. list files changed

2\. run AST validation

3\. explain risks

