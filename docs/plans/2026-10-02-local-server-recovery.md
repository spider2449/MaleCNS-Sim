# Local server recovery

Observed: port 8765 serves an older route table, returning 404 for run-status.js and compare.js. The supplied session token returns 403 for /api/runs. The service reports no active run.

Start the current workspace application on an available loopback port without stopping the existing server or losing its in-memory history. Verify static assets and authenticated run history, then provide the new session URL. No scientific runs, commits, or pushes.

## Startup comparison

Compare process command lines and start times, served asset digests, and loaded package paths. Test the current LocalServer on a free fixed port with no scientific execution and close it after requests. Check fixed-port 8765 collision without stopping the existing process.

Findings: both listeners use the same Python executable and workspace launcher. Port 8765 was started on 2026-10-01 at 16:47:55; port 50457 was started on 2026-10-02 at 09:20:49. The server source was updated on 2026-10-02 at 09:11. The old listener serves current index.html and app.js from disk but retains the earlier Python route table, returning 404 for the new scripts. A temporary current-version fixed-port 8767 server returned 200 for /, /run-status.js, /compare.js, and authenticated /api/runs, then shut down. Port 0 only asks the OS to select a port; it does not change application routes or authentication. The original token was rejected by the old listener in the preceding check.

The initial fresh-port asset comparison timed out on 50457 in this turn, so no claim is made about its present responsiveness. A bind-only check of 8765 succeeded on this Windows environment; do not claim that occupied-port rejection was demonstrated. No existing listener was stopped and no scientific run was started.
