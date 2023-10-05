# Starting SLM-UI manually 

SLM-UI containers are automatically started by the SLM-UI installer. But, if it is not running on the host, users need to manually start it using the following commands.

1.  Initially, run `<swarm-learning>/slm-ui/scripts/run-postgres -pw" supersecretpassword"`. \(`supersecretpassword` is a default database password. User can change this default database password using external tools like pgAdmin\).

2.  Then, run `<swarm-learning>/slm-ui/scripts/run-slm-ui -pw" supersecretpassword"`. Most of the other arguments of the above commands are optional. If you have changed the defaults, then you can use the following arguments to specify them.

The following arguments are the optional arguments for `run-postgres`:

|Argument|Description|
|--------|-----------|
|<code>-d&vert;--data</code>`<dir>`| Directory where DB data will be persisted to default: `/opt/hpe/swarm-learning/slm-ui/data`|
|<code>-u&vert;--user</code>`<string>`|Postgres database username. default: `postgres`|
|<code>-pw&vert;--password</code>`<string>`|Postgres database password. This is a mandatory argument.|
|<code>-po&vert;--port</code>`<number>`|Postgres database port. default: 5432|
|<code>-n&vert;--network</code>`<string>`|Docker network where database and SLM-UI communicate. default: `slm-ui-network`|
|<code>-h&vert;--help&vert;/</code>`h`|help|

The following arguments are the optional arguments for `run-slm-ui`:

|Argument|Description|
|--------|-----------|
|<code>-nw&vert;--network</code>`<name>`|Docker network where SLM-UI and database communicate. default: `slm-ui-network`|
|<code>-l&vert;--log</code>`<dir>`|Directory where log files will be saved to. default: `./logs`|
|<code>-pu&vert;--public-cert</code>`<name>`|Public Certificate Name.|
|<code>-pr&vert;--private-cert</code>`<name>`|Private Certificate Name.|
|<code>-ca&vert;--ca-cert</code>`<name>`|Certificate Authority Certificate Name.|
|<code>-h&vert;--help</code>`/h`|help|

**Parent topic:**[Running Swarm Learning examples using SLM-UI](Running_Swarm_Learning_examples_using_SLM-UI.md)

